# Architecture Plan: 0548 — Skill-Gen Auto-Install, Dedup, Docs

## Overview

Three independent workstreams that improve the skill-gen developer experience:
1. **Auto-install**: Ensure Anthropic's skill-creator is present after `specweave init` / `update-instructions`
2. **Dedup**: Inject existing rules into the LLM prompt so pattern detection skips already-documented conventions
3. **Docs rewrite**: Replace the stale keyword-matching documentation with the current LLM-based architecture

All three touch different files with no cross-dependencies, so they can be implemented in parallel.

---

## C1: Auto-Install Skill-Creator

### Current State

- `installAllPlugins()` in `src/cli/helpers/init/plugin-installer.ts` iterates `marketplace.json` and copies SpecWeave's own skills into `.claude/skills/` via `copyPluginSkillsToProject()`
- Anthropic's skill-creator is a **third-party** skill (lives in `claude-plugins-official/skill-creator` or is installed via `claude install-skill`)
- The SKILL.md in `plugins/specweave/skills/skill-gen/SKILL.md` (Step 4) checks only `~/.claude/plugins/cache/claude-plugins-official/skill-creator` -- no local fallback

### Design Decision: File Copy vs `claude install-skill`

The spec says "installed locally via `claude install-skill` CLI". However, the current plugin architecture (since v1.0.535) abandoned CLI-based installation in favor of direct file copy. Using `claude install-skill` would:
- Reintroduce an external CLI dependency that was deliberately removed
- Be the only code path in init that shells out to `claude`
- Fail silently in CI environments where `claude` is not available

**Decision**: Use `claude install-skill` as specified, since skill-creator is a **third-party** Anthropic skill (not a SpecWeave plugin). SpecWeave's own skills are copied; external skills require the CLI. The non-blocking error handling (AC-US1-03) mitigates the CLI dependency risk.

### Component: `ensureSkillCreator()`

New function in `src/cli/helpers/init/skill-creator-installer.ts`:

```
ensureSkillCreator(projectRoot: string): Promise<{ installed: boolean; skipped: boolean; error?: string }>
```

**Algorithm**:
1. Check local path: `<projectRoot>/.claude/skills/skill-creator/SKILL.md`
   - If exists (or is a symlink that resolves) -> return `{ installed: false, skipped: true }`
2. Check `claude` CLI availability: `which claude` (or `where claude` on Windows)
   - If missing -> warn, return `{ installed: false, skipped: false, error: 'claude CLI not found' }`
3. Run `claude install-skill <GITHUB_URL>` with a 30-second timeout
   - URL: configurable via `config.json` field `skillGen.skillCreatorUrl` with default `https://github.com/anthropics/claude-code/tree/main/skill-creator`
   - On success -> return `{ installed: true, skipped: false }`
   - On failure -> warn (log stderr), return `{ installed: false, skipped: false, error: <message> }`
4. Never throw -- all errors caught and logged as warnings

### Integration Points

| Call site | When | Condition |
|-----------|------|-----------|
| `init.ts` (after `installAllPlugins`) | Init completes | `toolName === 'claude' && !continueExisting` |
| `update-instructions.ts` (end of function) | Update runs | `.claude/skills/skill-creator/SKILL.md` missing |

### SKILL.md Lookup Update

In `plugins/specweave/skills/skill-gen/SKILL.md`, Step 4 changes from:

```bash
# OLD: global-only lookup
SKILL_CREATOR_PATH=$(find ~/.claude/plugins/cache/claude-plugins-official/skill-creator ...)
```

To:

```bash
# NEW: local-first, then global fallback
SKILL_CREATOR_PATH=".claude/skills/skill-creator/SKILL.md"
if [ ! -f "$SKILL_CREATOR_PATH" ]; then
  SKILL_CREATOR_PATH=$(find ~/.claude/plugins/cache/claude-plugins-official/skill-creator -name "SKILL.md" -maxdepth 3 2>/dev/null | head -1)
fi
```

### Error Handling

All paths are non-blocking. Init always completes. Warning messages:
- `[skill-gen] claude CLI not found -- skill-creator auto-install skipped`
- `[skill-gen] skill-creator install failed: <reason> -- run 'claude install-skill ...' manually`
- No warning when skill-creator already exists (silent skip per AC-US1-02)

---

## C2: Deduplication Awareness in Pattern Detection

### Current State

`SignalCollector.buildPrompt()` (line 244 of signal-collector.ts) constructs a prompt with only `<documents>` -- the living docs content. No awareness of existing rules.

### Design: Dedup Context Injection

New method `collectExistingRules()` reads rule files and appends them to the LLM prompt in a `<existing-rules>` block so the LLM can avoid duplicating known patterns.

### Component: `RuleCollector`

New module `src/core/skill-gen/rule-collector.ts`:

```
collectExistingRules(projectRoot: string): Promise<{ content: string; fileCount: number; tokenCount: number }>
```

**Files scanned** (in order):
1. `CLAUDE.md` (project root)
2. `.cursorrules` (project root)
3. `.cursor/rules/*.mdc` (all files)
4. `.github/copilot-instructions.md`
5. `.claude/skills/**/*.md` (all skill SKILL.md files)

**Truncation strategy**:
- Hard cap: 10K tokens (estimateTokenCount from utils.ts -- `ceil(chars/4)`)
- Per-file cap: 2K tokens (prevents one massive file from consuming the budget)
- Priority: files ordered by recency (mtime), newest first
- Empty files (0 bytes): skipped entirely (AC-US2-03 edge case)
- Security: skip any file matching `*.env*`, `credentials*`, `secret*` patterns

**Output format** (appended to prompt):
```
<existing-rules>
These rules are ALREADY documented in the project. Do NOT suggest patterns that duplicate these existing rules.

--- file: CLAUDE.md ---
<truncated content>

--- file: .claude/skills/error-handling/SKILL.md ---
<truncated content>
</existing-rules>
```

### Integration into `buildPrompt()`

`SignalCollector.buildPrompt()` gains an optional `existingRules?: string` parameter:

```typescript
private buildPrompt(
  docs: Array<{ path: string; content: string }>,
  existingRules?: string
): string {
  const docBlocks = docs
    .map(d => `--- file: ${d.path} ---\n${d.content}`)
    .join('\n');

  let prompt = `Analyze these project documents and identify recurring patterns.
For each pattern provide: category, name, description, evidence.

Do NOT suggest patterns that are already covered by existing project rules
(shown in the <existing-rules> section if present).

<documents>
${docBlocks}
</documents>`;

  if (existingRules) {
    prompt += `\n\n${existingRules}`;
  }

  return prompt;
}
```

The callers (`detectPatternsLLM`) pass the rules through:
```typescript
const rules = await this.ruleCollector.collectExistingRules(this.projectRoot);
// ...
const prompt = this.buildPrompt(docs, rules.content || undefined);
```

### Slug-Level Dedup Guard (AC-US2-04)

In `SKILL.md` Step 5 (skill-gen skill), before delegating to skill-creator, check:

```bash
SKILL_DIR=".claude/skills/${PATTERN_SLUG}"
if [ -d "$SKILL_DIR" ] && [ -f "$SKILL_DIR/SKILL.md" ]; then
  echo "Skill '${PATTERN_SLUG}' already exists at $SKILL_DIR/SKILL.md -- skipping"
  # Mark signal as generated in skill-signals.json
  exit 0
fi
```

This is a fast file-existence check, separate from the LLM-level dedup.

### Data Flow

```
increment closes
    |
    v
SignalCollector.collect()
    |
    +-- collectMarkdownFiles()     -> living docs
    +-- ruleCollector.collect()    -> existing rules (new)
    |
    v
detectPatternsLLM()
    |
    +-- buildPrompt(docs, rules)   -> prompt with <existing-rules> (modified)
    |
    v
LLM response (patterns already filtered by dedup context)
    |
    v
upsertSignal() -> skill-signals.json
```

---

## C3: Documentation Rewrite

### Files Modified

1. **`docs-site/docs/skills/extensible/skill-generation.md`** -- Full rewrite
2. **`README.md`** -- Update skill-gen section (3-4 sentences)

### New Documentation Structure

```
# Project-Specific Skill Generation

## Overview (what + why)
## Prerequisites
  - Living docs enabled
  - LLM config in config.json
  - skill-creator (auto-installed via init)
## How It Works
  ### Signal Detection (LLM-based)
    - Runs on increment closure
    - LLM analyzes living docs for recurring patterns
    - Dynamic categories (not hardcoded keyword lists)
    - File-based confidence scoring
  ### Deduplication
    - Checks existing CLAUDE.md, .cursorrules, skills
    - Prevents duplicate suggestions
  ### Suggestions
    - Max 1 per closure, confidence-gated, declinable
  ### Seed Mode (--seed)
    - Solves cold start problem
    - Command example: specweave skill-gen --seed
    - Scans all living docs in one pass
## Walkthrough Example
  - Express+React+Zod project
  - init -> seed -> detect -> suggest -> generate -> eval
## Configuration
## Signal Schema
## Drift Detection
## The Progression (correction -> memory -> signal -> suggestion -> skill)
```

### Key Differences from Current Docs

| Current | New |
|---------|-----|
| Lists hardcoded categories (error handling, API patterns...) | Explains LLM discovers categories dynamically |
| No mention of --seed mode | Documents --seed with command example |
| No prerequisites section | Lists living docs, LLM config, skill-creator |
| No dedup mention | Documents dedup behavior |
| No walkthrough | Full Express+React+Zod example flow |
| Implies keyword matching | Explicitly describes LLM-based analysis |

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| `claude install-skill` interface changes | Wrap in try/catch; make URL configurable; timeout at 30s |
| Dedup prompt bloat | Hard cap 10K tokens; per-file cap 2K; monitor in tests |
| Rule files contain secrets | Explicit skip list for .env/credentials patterns |
| Concurrent init + skill-creator install | File-existence check is idempotent; `claude install-skill` is also idempotent |

## Testing Strategy

| Component | Test Type | Key Cases |
|-----------|-----------|-----------|
| `ensureSkillCreator()` | Unit (Vitest) | Already exists (skip), CLI missing (warn), install success, install failure, symlink, permissions |
| `RuleCollector` | Unit (Vitest) | No rules, single file, multiple files, truncation at 10K, empty file skip, security filter |
| `buildPrompt()` with rules | Unit (Vitest) | With rules, without rules, rules exceed cap |
| Slug dedup guard | Eval case in SKILL.md evals | Existing skill slug -> skip |
| Documentation | Manual review | Accuracy against current codebase |

## Files to Create/Modify

### New Files
- `src/cli/helpers/init/skill-creator-installer.ts` -- ensureSkillCreator()
- `src/core/skill-gen/rule-collector.ts` -- collectExistingRules()
- `tests/unit/skill-gen/rule-collector.test.ts`
- `tests/unit/init/skill-creator-installer.test.ts`

### Modified Files
- `src/cli/commands/init.ts` -- call ensureSkillCreator() after installAllPlugins
- `src/cli/commands/update-instructions.ts` -- call ensureSkillCreator() at end
- `src/cli/helpers/init/index.ts` -- export ensureSkillCreator
- `src/core/skill-gen/signal-collector.ts` -- inject RuleCollector, modify buildPrompt()
- `plugins/specweave/skills/skill-gen/SKILL.md` -- local-first lookup, slug dedup guard
- `docs-site/docs/skills/extensible/skill-generation.md` -- full rewrite
- `README.md` -- update skill-gen blurb

## Recommended Domain Skills

No domain skills needed. All work is in the SpecWeave CLI codebase (Node.js/TypeScript) and documentation (Markdown). The standard `sw:do` workflow with TDD cycle is sufficient.
