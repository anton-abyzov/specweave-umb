# Implementation Plan: Obsidian Brain Skill + Skill Studio Agent-Aware Extension

## Overview

Two independent workstreams, both scoped to the vskill repo (`repositories/anton-abyzov/vskill/`):

1. **Obsidian Brain Skill** (WS1) — a parametric vskill plugin skill (`personal/obsidian-brain`) that teaches any AI agent autonomous Obsidian vault management using the PARA + LLM Wiki pattern. Three operations (ingest, query, lint), scheduled via CronCreate, with credential detection and filesystem-only operation.

2. **Skill Studio Agent-Aware Routing** (WS2) — extend the existing Skill Studio creation pipeline with agent-aware conditional prompt augmentation and a target-agent selection UI, so generated skills work correctly on non-Claude agents.

Both workstreams share no code dependencies and can be implemented in parallel.

---

## Architecture

### Component 1: Obsidian Brain Skill

**Project**: vskill
**Location**: `plugins/personal/skills/obsidian-brain/`

```
plugins/personal/skills/obsidian-brain/
├── SKILL.md                    # Main skill definition (<500 lines)
├── references/
│   ├── vault-schema.md         # 3-layer PARA + wiki architecture
│   ├── routing-rules.md        # PARA routing table (parametric)
│   ├── wiki-format.md          # Frontmatter types, naming, linking conventions
│   └── cron-setup.md           # Schedule config + pre-flight checks
├── scripts/
│   ├── detect-changes.sh       # Inbox file count + recent modifications
│   ├── update-index.sh         # Regenerate wiki/index.md from wiki pages
│   └── lint-check.sh           # Orphan detection, missing cross-refs, backlog count
└── evals/
    └── evals.json              # Test cases for ingest, query, lint operations
```

**Design rationale**: The skill is a _composition layer_. It does NOT implement Obsidian operations itself — it teaches the agent the vault schema and decision procedures. The agent uses standard filesystem tools (Read, Write, Glob, Grep, Bash) to perform operations.

**Key design decisions**:

| Decision | Choice | Rationale | Satisfies |
|----------|--------|-----------|-----------|
| Plugin placement | `personal/` (existing plugin with `greet-anton`) | Personal vault management skill; `personal/` plugin already exists | AC-US1-01 |
| Vault paths | Parametric config block (`vault_path`, `para_folders`, `wiki_dir`, `inbox_dir`, `log_file`, `index_file`) | Different users have different vault locations; no hardcoded paths | AC-US1-02, AC-US1-06 |
| References split | 4 reference files matching spec | Keeps SKILL.md under 500 lines; agents load references on demand | AC-US1-03 |
| Scripts | Shell scripts for deterministic operations | Fast, predictable, no LLM cost for file counting and index generation | AC-US1-04 |
| Filesystem-only | Read, Write, Glob, Grep, Bash — no Obsidian CLI/app dependency | Works without Obsidian running; vault is just a folder of markdown files | FR-001, AC-US3-03 |
| No git operations | Skill never touches `.git/` or runs git commands on vault | Obsidian Sync handles sync; git would corrupt sync state | FR-002 |
| SKILL.md format | agentskills.io standard (YAML frontmatter + markdown body) | Consistent with existing vskill skills | FR-004 |

**Parametric config block** (resolved at runtime from vault's own CLAUDE.md):

```yaml
# Config block in SKILL.md — user fills these during setup
vault_path: "~/Projects/Obsidian/personal-docs"
para_folders:
  projects: "001 Projects"
  areas: "002 Areas"
  resources: "003 Resources"
  archive: "004 Archive"
wiki_dir: "wiki"
inbox_dir: "raw/inbox"
log_file: "wiki/log.md"
index_file: "wiki/index.md"
credentials_folder: "003 Resources/credentials"
```

**Three operations**:

1. **Ingest** (US-002): Read inbox → create/update wiki pages → update index → log entries → route originals to PARA folders. Credential detection halts ingestion for sensitive files, routes to credentials folder.
2. **Query** (US-003): Read index → identify relevant pages → synthesize answer with wikilink citations → optionally file as synthesis wiki page.
3. **Lint** (US-004): Run `lint-check.sh` for deterministic checks + LLM analysis for semantic checks → severity-categorized report → log findings.

**Credential detection pattern** (AC-US2-04):
- Regex patterns: API key formats, `password:`, `token:`, `secret:`, AWS/GCP key patterns
- On match: STOP ingestion for that file, move to `credentials_folder`, log `!cred` warning
- Never creates wiki page from credential content

**Scheduled operation** (US-005):
- CronCreate: 4x/day configurable in `references/cron-setup.md`
- Pre-flight checks: vault path accessible, inbox file count, last-run timestamp
- Priority: ingest first (if inbox has files) → lint (if threshold or weekly cadence) → index rebuild
- Every run logs start/operations/completion to vault log file; errors use `!error` prefix

**Wiki page size limit** (FR-005): Pages created during ingest capped at 1500 lines. If content exceeds limit, split into multiple pages with `(part N)` suffix and cross-references.

### Component 2: Skill Studio Agent-Aware Routing

**Project**: vskill

The existing skill creation pipeline generates SKILL.md files optimized for Claude Code. This extension adds agent-aware conditional prompt augmentation so skills generated for non-Claude agents omit Claude-specific features (slash commands, hooks, MCP references).

**Strategy**: Conditional augmentation of existing `BODY_SYSTEM_PROMPT` (FR-003). The existing prompt IS the Claude Code path. When `targetAgents` includes non-Claude agents, an agent-context section is appended instructing the LLM to adapt output. No separate prompt-per-agent architecture.

**Files modified/created**:

```
src/agents/
├── agents-registry.ts          # MODIFIED: Add filterAgentsByFeatures(), getAgentCreationProfile()

src/eval-server/
├── skill-create-routes.ts      # MODIFIED: Accept targetAgents, inject agent context into prompt
├── api-routes.ts               # MODIFIED: Add GET /api/agents/installed endpoint

src/installer/
├── canonical.ts                # MODIFIED: Filter agents by target-agents frontmatter
├── frontmatter.ts              # MODIFIED: Support target-agents field parsing

src/eval-ui/src/
├── pages/CreateSkillPage.tsx   # MODIFIED: Add agent selection section
├── components/
│   └── AgentSelector.tsx       # NEW: Checkbox group with feature compatibility indicators
├── hooks/
│   └── useCreateSkill.ts       # MODIFIED: Pass targetAgents to generation API
```

**Data flow**:

```
User describes skill + selects target agents (checkboxes)
        │
        ▼
AgentSelector (UI checkboxes) ── targetAgents: string[] ──► useCreateSkill hook
                                                                  │
                                                                  ▼
                                                     POST /api/skills/generate
                                                       { ..., targetAgents: ["cursor", "codex"] }
                                                                  │
                                                                  ▼
                                                     skill-create-routes.ts
                                                     (BODY_SYSTEM_PROMPT + agent context section)
                                                                  │
                                                                  ▼
                                                     LLM generates SKILL.md
                                                     (adapted for target agents)
                                                                  │
                                                                  ▼
                                                     SSE stream → UI shows result
                                                     target-agents frontmatter included
```

**Agent context injection** (appended to BODY_SYSTEM_PROMPT when non-Claude agents selected):

```
## Target Agent Constraints

This skill targets: {agent_names}

Feature availability for target agents:
{feature_matrix}

IMPORTANT CONSTRAINTS:
- {if no slashCommands}: Do NOT reference slash commands (/command syntax) in the skill body
- {if no hooks}: Do NOT include hook examples or lifecycle hook references
- {if no mcp}: Do NOT reference MCP tools; use CLI/filesystem alternatives only
- {if no customSystemPrompt}: Keep the skill as plain instructions without system prompt framing

Generate a skill body that works across ALL target agents by using only universally available features.
```

**New types** (AC-US6-02, AC-US6-03):

```typescript
// In agents-registry.ts
export interface AgentCreationProfile {
  agent: AgentDefinition;
  stripFields: string[];          // Claude-specific frontmatter to remove
  addGuidance: string[];          // Agent-specific instructions to inject
  featureSupport: FeatureSupport; // Snapshot for generation context
}

export function filterAgentsByFeatures(
  features: Partial<FeatureSupport>
): AgentDefinition[];

export function getAgentCreationProfile(
  agentId: string
): AgentCreationProfile | undefined;
```

**API contracts**:

Modified endpoint: `POST /api/skills/generate` (SSE)
```typescript
interface GenerateSkillRequest {
  prompt: string;
  provider?: ProviderName;
  model?: string;
  targetAgents?: string[];  // NEW: Agent IDs from AGENTS_REGISTRY
}
```

New endpoint: `GET /api/agents/installed`
```typescript
interface InstalledAgentsResponse {
  agents: Array<{
    id: string;
    displayName: string;
    featureSupport: FeatureSupport;
    isUniversal: boolean;
    installed: boolean;           // AC-US8-02
  }>;
  suggested: string;              // Best guess for primary target agent
}
```

**Frontmatter extension** (AC-US8-03):
```yaml
---
description: "My skill description"
target-agents: claude-code, cursor, cline   # NEW optional field
---
```

When `target-agents` is present in SKILL.md, `canonical.ts` filters `agents` array to only install to matching agent directories instead of all detected agents.

**Key design decisions**:

| Decision | Choice | Rationale | Satisfies |
|----------|--------|-----------|-----------|
| Adaptation point | Conditional prompt augmentation (NOT post-generation transform) | Spec FR-003: "One prompt, conditionally extended." LLM handles adaptation during generation, more natural output | FR-003, AC-US7-02, AC-US7-03 |
| Agent selector UI | Checkboxes in `CreateSkillPage.tsx` with feature indicators | Multi-select needed for cross-platform skills; checkboxes show compatibility at a glance | AC-US9-01, AC-US9-02 |
| Default behavior | No `targetAgents` = Claude Code path (unchanged prompt) | Backward compatible; existing flow untouched | AC-US7-01 |
| Registry reuse | Import from existing `agents-registry.ts` | No duplication; single source of truth for 49 agents | AC-US6-01 |
| Installed/known | Endpoint returns all known + installed flag | UI can show "install Cursor to unlock" guidance | AC-US8-02 |
| targetAgents type | `string[]` (array) | Support multi-agent targeting in single generation | AC-US7-04 |

### Data Model

No database changes. Data additions:

1. **SKILL.md** for obsidian-brain (new file in plugin source)
2. **4 reference files** (vault-schema.md, routing-rules.md, wiki-format.md, cron-setup.md)
3. **3 shell scripts** (detect-changes.sh, update-index.sh, lint-check.sh)
4. **evals.json** (eval definitions for obsidian-brain)
5. **`targetAgents` field** added to `GenerateSkillRequest` interface (optional `string[]`)
6. **`AgentCreationProfile` type** added to `agents-registry.ts`
7. **`target-agents` frontmatter field** added to `frontmatter.ts` parsing
8. **`AgentSelector.tsx`** new React component

---

## Technology Stack

- **Language/Framework**: TypeScript (ESM, `.js` import extensions per vskill `nodenext` convention)
- **UI**: React (existing eval-ui stack)
- **Server**: Existing eval-server custom HTTP router (not Express)
- **Scripts**: Bash (portable POSIX-compatible)
- **Testing**: Vitest (unit + integration), evals (skill quality)
- **No new npm dependencies**: All functionality builds on existing modules

---

## Implementation Phases

### Phase 1: Obsidian Brain Skill (Independent — US-001 through US-005)

1. Create `plugins/personal/skills/obsidian-brain/SKILL.md` with parametric config, three operations, credential detection
2. Create `references/vault-schema.md` — 3-layer architecture (PARA + wiki + raw)
3. Create `references/routing-rules.md` — parametric PARA routing table
4. Create `references/wiki-format.md` — frontmatter types, naming conventions, linking
5. Create `references/cron-setup.md` — CronCreate schedule config + pre-flight checks
6. Create `scripts/detect-changes.sh` — inbox file count + recent modifications
7. Create `scripts/update-index.sh` — regenerate wiki/index.md from wiki pages
8. Create `scripts/lint-check.sh` — orphan detection, missing cross-refs, inbox backlog
9. Create `evals/evals.json` — test cases for ingest, query, lint, credential detection
10. Run evals to establish baseline

### Phase 2: Agent Registry Extension (US-006)

1. Add `AgentCreationProfile` interface to `agents-registry.ts`
2. Implement `filterAgentsByFeatures()` — filter by partial feature match
3. Implement `getAgentCreationProfile()` — return stripFields, addGuidance, featureSupport
4. Unit tests for new functions

### Phase 3: Agent-Aware Generation (US-007, US-008)

1. Add `targetAgents?: string[]` to `GenerateSkillRequest` in `skill-create-routes.ts`
2. Implement agent-context section builder — derives constraints from `featureSupport` matrix
3. Inject agent context into `BODY_SYSTEM_PROMPT` when non-Claude agents targeted
4. Add `GET /api/agents/installed` endpoint to `api-routes.ts`
5. Add `target-agents` frontmatter support to `frontmatter.ts`
6. Update `canonical.ts` to filter agents by `target-agents` during install
7. Unit tests for context builder, endpoint, and frontmatter parsing

### Phase 4: Agent Selection UI (US-009)

1. Create `AgentSelector.tsx` — checkbox group with feature compatibility indicators
2. Integrate into `CreateSkillPage.tsx` — agent selection section with grouping
3. Update `useCreateSkill.ts` — pass `targetAgents` to generation API
4. Wire `target-agents` into generated SKILL.md frontmatter

---

## Testing Strategy

### Obsidian Brain Skill (WS1)
- **Evals** (primary): 5-7 eval scenarios testing ingest workflow, query synthesis, lint detection, credential guard, scheduled operation documentation
- **Unit tests**: None needed for SKILL.md (pure markdown skill)
- **Script tests**: Shell scripts tested via `bash -n` (syntax check) + manual test with sample vault structure
- **Manual verification**: Install skill, run against actual vault (6,700+ notes), verify inbox clearing + wiki page creation

### Agent-Aware Routing (WS2)
- **Unit tests**: `agents-registry.test.ts` — `filterAgentsByFeatures()`, `getAgentCreationProfile()` return correct results
- **Unit tests**: `skill-create-routes.test.ts` — generation with `targetAgents` produces agent-context-aware prompt
- **Unit tests**: `frontmatter.test.ts` — `target-agents` field parsing and round-trip
- **Unit tests**: `canonical.test.ts` — install filtering by `target-agents`
- **Integration tests**: Generate skill targeting Cursor → verify no slash command references in output
- **Integration tests**: Generate skill targeting Codex → verify no hooks/MCP references
- **Component tests**: `AgentSelector.test.tsx` — render with mock agents, selection changes propagate
- **Manual verification**: Generate skill in Studio UI, select different agents, inspect output differences

---

## Technical Challenges

### Challenge 1: Agent-Context Prompt Quality
**Problem**: Appending agent constraints to BODY_SYSTEM_PROMPT could confuse the LLM or produce lower-quality output for multi-agent targets.
**Solution**: Keep constraints minimal and specific. Only state what to avoid (subtractive), not what to add. Test with at least 3 agent combinations to validate output quality.
**Risk**: Medium. Mitigated by eval testing and fallback to Claude-only generation if quality drops.

### Challenge 2: Credential Detection False Positives
**Problem**: Regex-based credential detection may flag legitimate content (e.g., API documentation) as credentials.
**Solution**: Use conservative patterns (key format + value format, not just keyword matching). Log flagged files with reason, don't delete. User reviews and re-ingests false positives manually.
**Risk**: Low. False positives are safe (file preserved in credentials folder); false negatives are the real risk.

### Challenge 3: Wiki Page Size Control
**Problem**: Large source files could produce wiki pages exceeding 1500-line limit (FR-005).
**Solution**: SKILL.md instructs the agent to check line count after wiki page generation. If over limit, split into multiple pages with `(part N)` suffix and add cross-references between parts.
**Risk**: Low. Agent handles splitting with clear instructions.

### Challenge 4: Shell Script Portability
**Problem**: Scripts must work across macOS and Linux (common vskill user environments).
**Solution**: Use POSIX-compatible syntax only. No `bash`-isms. Test on both macOS (BSD tools) and Linux (GNU tools). Use `find`, `wc`, `grep` with portable flags.
**Risk**: Low. Operations are simple (file counting, text matching).
