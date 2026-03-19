# Architecture Plan: 0537 — Project-Specific Skill Generation + Public Docs Cross-References

## Overview

This increment adds four new subsystems to SpecWeave: (1) a signal collector that detects recurring patterns from living docs output on increment closure, (2) a suggestion engine that surfaces qualifying patterns to the user, (3) a `/sw:skill-gen` Claude Code skill that generates project-local SKILL.md files via Anthropic's skill-creator, and (4) a drift detector that warns when project-local skills reference stale codebase state. Additionally, all 26 existing SKILL.md files gain `## Resources` sections linking to their public docs, and a new Docusaurus page documents the feature.

---

## ADR Review

No existing ADRs conflict with this design. Relevant ADRs considered:

- **ADR-0017 (Self-Reflection Architecture)**: The signal collector extends the existing reflection subsystem concept (skill-memories) but operates at a different layer -- pattern detection from markdown output rather than in-conversation corrections.
- **ADR-0010 (Append-Only Increments)**: Signal data is additive (append increment IDs to existing signals), consistent with append-only philosophy.
- **ADR-0015 (Hybrid Plugin System)**: `/sw:skill-gen` is a Claude Code skill (SKILL.md), not a CLI command, aligning with the hybrid approach where AI-facing features live as skills.

---

## Architecture Decisions

### AD-1: Signal Collector Reads Markdown, Not In-Memory Types

The signal collector reads `.specweave/docs/internal/` markdown files (module overviews, API surfaces, ADRs, skill-memories) rather than importing TypeScript analyzer types. This keeps the collector decoupled from analyzer internals and allows it to work even if the analyzer changes its output format, since markdown is the stable contract.

**Trade-off**: Markdown parsing is less precise than typed data access, but the signal collector is advisory (confidence-scored suggestions), so approximate extraction is acceptable.

### AD-2: Signal State as a Single JSON File

Signals are stored in `.specweave/state/skill-signals.json` with a versioned schema (`version: "1.0"`). This is simpler than a per-signal file approach and keeps all signal state in one place for easy inspection and backup.

**Concurrency**: Last-write-wins. Acceptable because signal data is additive (re-detected on next closure) and concurrent closures are rare.

**Schema**:

```
skill-signals.json
─────────────────────────────────────────
version     "1.0"
signals[]   Array of SignalEntry

SignalEntry
─────────────────────────────────────────
id            string     UUID or slug
pattern       string     Short name ("error-boundary-pattern")
category      string     Category slug for dedup ("error-handling")
description   string     Human-readable description
incrementIds  string[]   Increment IDs where observed
firstSeen     string     ISO date
lastSeen      string     ISO date
confidence    number     0.0-1.0
evidence      string[]   File paths / snippets as evidence
suggested     boolean    Has this been surfaced as a suggestion?
declined      boolean    Has the user declined this?
generated     boolean    Has a skill been generated from this?
```

### AD-3: Hook Wiring Strategy

Two hook integration points, both error-isolated:

1. **Signal collection + suggestion**: Wired into `LifecycleHookDispatcher.onIncrementDone()` as a new STEP 4 after retry queue drain. Runs after living docs sync completes (needs fresh analysis output). Error-isolated: catch + log, never blocks closure.

2. **Drift detection**: Wired into `LivingDocsSync.syncIncrement()` at the end of a successful sync. Runs only when `.claude/skills/*.md` files exist. Error-isolated: catch + log, never blocks sync.

**Why after onIncrementDone STEP 3 (retry drain)?** Signal collection depends on up-to-date living docs. By running after STEP 1 (living docs sync), the collector reads the freshest analysis. It runs after STEP 3 because it is non-critical and should not delay the core closure+sync pipeline.

### AD-4: Skill Generation via External Plugin Delegation

`/sw:skill-gen` does NOT implement skill creation logic. It delegates to Anthropic's official `skill-creator` plugin at `~/.claude/plugins/cache/claude-plugins-official/skill-creator/`. The skill-gen SKILL.md:

1. Reads `skill-signals.json` and displays qualifying patterns
2. Accepts user selection
3. Provides context (evidence, pattern description) to the skill-creator
4. Updates signal state (`generated: true`) after success

This avoids duplicating skill creation logic and benefits from upstream improvements to the skill-creator.

### AD-5: Drift Detection Scope

Drift detection compares `.claude/skills/*.md` file contents against current living docs analysis output. It looks for:

- Module names referenced in skill content that no longer appear in module overview files
- File paths referenced that no longer exist
- API surface names that no longer appear in API surface docs

This is a text-matching heuristic, not a semantic analysis. False positives are expected and acceptable since drift detection is warn-only.

### AD-6: Configuration Model

`SkillGenConfig` is added as an optional property on `SpecWeaveConfig`:

```
SkillGenConfig
─────────────────────────────────────────
detection          "on-close" | "off"     Default: "on-close"
suggest            boolean                Default: true
minSignalCount     number                 Default: 3
declinedSuggestions string[]              Default: []
maxSignals         number                 Default: 100
```

Defaults are applied when `skillGen` is absent from config.json, matching the existing pattern used by `GrillConfig`, `ContextBudgetConfig`, etc.

---

## Component Design

### C-1: SignalCollector (`src/core/skill-gen/signal-collector.ts`)

**Responsibility**: Read living docs markdown output, extract recurring patterns, update `skill-signals.json`.

```
Input:  projectRoot, incrementId
Output: Updated skill-signals.json

Steps:
1. Read living docs files from .specweave/docs/internal/
   - Module overviews (*.md in module analysis dirs)
   - API surface files
   - ADR files
   - Skill-memory files (.specweave/skill-memories/*.md)
2. Extract patterns using category-based heuristics:
   - Error handling patterns (try/catch conventions, error boundaries)
   - Naming conventions (file naming, variable naming patterns)
   - Architecture patterns (module organization, dependency injection)
   - Testing patterns (mock patterns, test organization)
   - Integration patterns (API client patterns, auth flows)
3. Load existing signals from skill-signals.json
4. For each detected pattern:
   - Match by category slug against existing signals
   - If new: create signal entry with confidence=0.3, incrementIds=[current]
   - If existing: append incrementId, refresh lastSeen, bump confidence
5. Cap at maxSignals (prune lowest-confidence when exceeded)
6. Write updated skill-signals.json
```

**Error handling**: Wrap entire flow in try/catch. On corrupted signals file, backup to `.bak` and create fresh. On missing living docs, exit silently.

### C-2: SuggestionEngine (`src/core/skill-gen/suggestion-engine.ts`)

**Responsibility**: Evaluate signals against config thresholds and print a single suggestion.

```
Input:  projectRoot (reads config + skill-signals.json)
Output: Console message (at most 1 line) or nothing

Steps:
1. Read SkillGenConfig from config.json (apply defaults)
2. If suggest=false, return immediately
3. Read skill-signals.json
4. Filter signals: incrementIds.length >= minSignalCount
                   AND declined=false
                   AND generated=false
                   AND id NOT in declinedSuggestions
5. Sort by confidence DESC
6. If any qualify: print suggestion for the top one
7. Mark suggested=true on that signal
```

### C-3: DriftDetector (`src/core/skill-gen/drift-detector.ts`)

**Responsibility**: Compare project-local skill contents against current living docs state.

```
Input:  projectRoot
Output: Console warnings (0 or more lines)

Steps:
1. Glob .claude/skills/*.md
2. If none found, return silently
3. Read current living docs analysis output (module overviews, API surfaces)
4. For each skill file:
   a. Extract referenced module names, file paths, API names
   b. Check each against current analysis
   c. Collect stale references
5. Print warnings for skills with stale references
```

### C-4: SkillGenSkill (`plugins/specweave/skills/skill-gen/SKILL.md`)

**Responsibility**: User-facing `/sw:skill-gen` skill that orchestrates pattern display and skill generation.

```
User invokes /sw:skill-gen
1. Read skill-signals.json
2. Display qualifying patterns (incrementIds.length >= minSignalCount)
   - Show even declined patterns (user may reconsider)
3. User selects a pattern
4. Check skill-creator plugin exists at expected path
5. Provide context to skill-creator: pattern name, description, evidence, category
6. skill-creator generates SKILL.md with evals/benchmarks
7. Write to .claude/skills/{pattern-slug}.md
8. Update signal: generated=true
```

### C-5: Config Type Extension (`src/core/config/types.ts`)

Add `SkillGenConfig` interface and `skillGen?: SkillGenConfig` to `SpecWeaveConfig`.

### C-6: Docs Page (`docs-site/docs/skills/extensible/skill-generation.md`)

Docusaurus markdown page covering:
- Signal detection lifecycle
- Configuration options
- `/sw:skill-gen` usage
- Drift detection
- Signal schema reference

Registered in `sidebars.ts` under the Extensible Skills category.

### C-7: Resources Section Updater (one-time manual edit)

Append `## Resources` sections to all 26 existing SKILL.md files in `plugins/specweave/skills/`. Each section links to the corresponding `verified-skill.com/docs/skills/...` page. Idempotent -- checks for existing `## Resources` before appending.

---

## Data Flow

```
Increment Closure Flow:
+-----------------------+
|  completeIncrement    |
+-----------+-----------+
            |
            v
+-------------------------------+
| LifecycleHookDispatcher       |
|   .onIncrementDone()          |
|                               |
| STEP 1: Living docs sync      |
| STEP 2: GitHub/JIRA/ADO sync  |
| STEP 3: Retry queue drain     |
| STEP 4: Signal collection     |--> SignalCollector.collect()
|         + suggestion          |--> SuggestionEngine.evaluate()
+-------------------------------+

Living Docs Sync Flow:
+------------------------+
| LivingDocsSync         |
|   .syncIncrement()     |
|                        |
| ... existing sync      |
| ... at end:            |
| DriftDetector.check()  |--> Warn on stale skill references
+------------------------+

On-Demand Skill Generation:
+------------------------+
| User: /sw:skill-gen    |
+-----------+------------+
            |
            v
+------------------------+     +-----------------------+
| skill-gen SKILL.md     |---->| skill-creator plugin  |
| (read signals,         |     | (Anthropic official)  |
|  display patterns,     |     | generates SKILL.md    |
|  delegate to creator)  |     | with evals+benchmarks |
+------------------------+     +-----------------------+
            |
            v
+------------------------+
| .claude/skills/        |
|   {pattern}.md         |
+------------------------+
```

---

## File Structure

New files:

```
repositories/anton-abyzov/specweave/
  src/core/skill-gen/
    signal-collector.ts       # C-1: Pattern detection from living docs
    suggestion-engine.ts      # C-2: Threshold evaluation + console output
    drift-detector.ts         # C-3: Stale reference detection
    types.ts                  # Shared types (SignalEntry, SignalStore)
    __tests__/
      signal-collector.test.ts
      suggestion-engine.test.ts
      drift-detector.test.ts
  plugins/specweave/skills/skill-gen/
    SKILL.md                  # C-4: /sw:skill-gen skill definition
  docs-site/docs/skills/extensible/
    skill-generation.md       # C-6: Public docs page
```

Modified files:

```
  src/core/config/types.ts            # C-5: Add SkillGenConfig
  src/core/hooks/LifecycleHookDispatcher.ts  # Wire STEP 4
  src/core/living-docs/living-docs-sync.ts   # Wire drift detection
  docs-site/sidebars.ts              # Register new docs page
  plugins/specweave/skills/*/SKILL.md # C-7: Add ## Resources to all 26
```

---

## Integration Points

### LifecycleHookDispatcher.onIncrementDone() -- STEP 4

After the retry queue drain (STEP 3, line ~327), add a new block:

```typescript
// STEP 4: Signal collection + suggestion (non-blocking, error-isolated)
try {
  const { SignalCollector } = await import('../../skill-gen/signal-collector.js');
  const { SuggestionEngine } = await import('../../skill-gen/suggestion-engine.js');

  const collector = new SignalCollector(projectRoot);
  await collector.collect(incrementId);

  const engine = new SuggestionEngine(projectRoot);
  await engine.evaluate();
} catch (error) {
  LifecycleHookDispatcher.logError('onIncrementDone:skillSignals', error);
}
```

Dynamic imports keep the signal collector tree-shakeable and avoid loading it when the feature is disabled.

### LivingDocsSync.syncIncrement() -- Drift Check

At the end of a successful sync (before returning `result`), add:

```typescript
// Drift detection for project-local skills (error-isolated)
try {
  const { DriftDetector } = await import('../skill-gen/drift-detector.js');
  const detector = new DriftDetector(this.projectRoot);
  await detector.check();
} catch (error) {
  this.logger.log(`[DriftDetector] Warning: ${error instanceof Error ? error.message : error}`);
}
```

### Config Type

In `src/core/config/types.ts`, add:

```typescript
export interface SkillGenConfig {
  /** Pattern detection trigger: "on-close" runs on increment completion, "off" disables */
  detection?: 'on-close' | 'off';
  /** Whether to print suggestions when patterns qualify */
  suggest?: boolean;
  /** Minimum number of increments a pattern must appear in before qualifying */
  minSignalCount?: number;
  /** Pattern IDs permanently excluded from suggestions (still visible in /sw:skill-gen) */
  declinedSuggestions?: string[];
  /** Maximum number of signals to retain (prunes lowest-confidence when exceeded) */
  maxSignals?: number;
}
```

Add to `SpecWeaveConfig`:

```typescript
/** Skill generation configuration (v1.0.XXX+) */
skillGen?: SkillGenConfig;
```

No changes to `DEFAULT_CONFIG` needed -- defaults are applied inline in the collector/engine when the config key is absent.

---

## Performance Budget

- **Signal collection**: Target < 2s. Reading ~20-50 markdown files from `.specweave/docs/internal/` is fast. Pattern extraction is string matching, not LLM calls.
- **Suggestion engine**: Negligible (read JSON + filter + console.log).
- **Drift detection**: Target < 1s. Reads `.claude/skills/` (typically 0-5 files) and compares against already-loaded analysis.
- **Total added latency to increment closure**: < 2.5s in the worst case, within the NFR budget.

---

## Testing Strategy

- **Unit tests**: Each module (signal-collector, suggestion-engine, drift-detector) gets dedicated Vitest tests with filesystem mocking via `vi.hoisted()` + `vi.mock()`.
- **Integration test**: End-to-end flow from `onIncrementDone()` through signal collection + suggestion, using `_bypassTestGuard`.
- **Eval**: `evals.json` for the `/sw:skill-gen` skill following the pattern in `plugins/specweave/skills/e2e/evals/evals.json`.

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Signal collector produces noise | Conservative defaults: minSignalCount=3, confidence starts at 0.3, max 1 suggestion per closure |
| Skill-creator plugin missing | `/sw:skill-gen` checks path existence, prints install instructions if absent |
| Large signals file | Cap at 100 entries, prune lowest-confidence when exceeded |
| Drift detection false positives | Warn-only, never blocks, users learn to tune or ignore |
| Breaking LifecycleHookDispatcher | Error-isolated import + try/catch, same pattern as existing steps |

---

## Domain Skill Delegation

No domain skills needed. This is a core TypeScript module addition within the SpecWeave CLI codebase. The implementation uses:
- TypeScript/ESM (existing stack)
- Vitest for tests (existing stack)
- Docusaurus for docs (existing stack)

No frontend, backend framework, or external service skills apply.
