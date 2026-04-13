# Implementation Plan: Rubric Quality Contracts for Increment Closure

## Overview

Add `rubric.md` as a first-class quality contract file to the increment lifecycle. A new `src/core/rubric/` module provides parsing, generation, three-tier inheritance merge, and evaluation. The rubric is auto-generated from spec.md ACs during planning, consumed by `completion-validator.ts` during closure, and referenced by skill prompts (grill, code-reviewer, done) for structured evaluation.

The design follows existing patterns: a standalone core module with pure functions, lazy-imported by the completion validator, with no changes to the happy path when rubric.md is absent (backward compatible).

## Architecture

### Module Structure: `src/core/rubric/`

```
src/core/rubric/
  types.ts              # RubricCriterion, RubricDocument, Severity, EvaluatorId, CriterionResult
  rubric-parser.ts      # Parse rubric.md markdown → RubricDocument
  rubric-generator.ts   # Extract ACs from spec.md → generate rubric.md
  rubric-evaluator.ts   # Map gate report JSON to criterion pass/fail
  rubric-merger.ts      # Three-tier inheritance merge (global → project → increment)
  index.ts              # Re-exports
```

**Total estimated new code**: ~800 lines across 6 files (well under 1500/file limit).

### Component Diagram

```
spec.md ACs ──────┐
                   ▼
          rubric-generator.ts ──→ rubric.md (increment-level)
                   ▲
global rubric.md ──┤
project rubric.md ─┘  (via rubric-merger.ts)

rubric.md ──→ rubric-parser.ts ──→ RubricDocument
                                        │
gate reports (JSON) ──→ rubric-evaluator.ts
                                        │
                                        ▼
                              CriterionResult[]
                                        │
                         completion-validator.ts
                              (blocking/advisory)
```

### Data Model

#### `types.ts` — Core Types

```typescript
/** Two severity levels only — no scoring */
export type RubricSeverity = 'blocking' | 'advisory';

/** Which gate evaluates this criterion */
export type EvaluatorId =
  | 'sw:grill'
  | 'sw:code-reviewer'
  | 'sw:judge-llm'
  | 'coverage'
  | 'manual';

/** A single rubric criterion parsed from markdown */
export interface RubricCriterion {
  /** Unique ID, e.g. "R-001" */
  id: string;
  /** Human-readable title */
  title: string;
  /** Which ACs this traces to, e.g. ["AC-US1-01", "AC-US1-02"] */
  sourceACs: string[];
  /** Which gate evaluates this */
  evaluator: EvaluatorId;
  /** What to verify — free text */
  verify: string;
  /** Pass/fail threshold description */
  threshold: string;
  /** blocking = must pass for closure, advisory = warning only */
  severity: RubricSeverity;
  /** Category grouping */
  category: RubricCategory;
  /** Evaluation result (set by evaluator, null before evaluation) */
  result: CriterionResult | null;
}

export type RubricCategory =
  | 'functional-correctness'
  | 'test-coverage'
  | 'code-quality'
  | 'security'
  | 'performance'
  | 'documentation'
  | 'independent-evaluation';

/** Pass/fail result for a single criterion */
export interface CriterionResult {
  status: 'pass' | 'fail' | 'skip';
  /** Why it passed/failed — evidence from gate report */
  evidence: string;
  /** ISO-8601 timestamp of evaluation */
  evaluatedAt: string;
}

/** Complete parsed rubric document */
export interface RubricDocument {
  /** Increment ID from frontmatter */
  incrementId: string;
  /** Title from frontmatter */
  title: string;
  /** Generation timestamp */
  generated: string;
  /** Source description */
  source: string;
  /** Schema version */
  version: string;
  /** All criteria */
  criteria: RubricCriterion[];
}

/** Merge layer for three-tier inheritance */
export interface RubricLayer {
  /** Where this layer lives on disk */
  path: string;
  /** Parsed criteria from this layer */
  criteria: RubricCriterion[];
}
```

### Component Details

#### 1. `rubric-parser.ts` — Markdown → Structured Data

**Approach**: Line-by-line state machine (not regex soup). Mirrors the existing `parseAllACsWithPriority` pattern in `completion-validator.ts`.

**State machine states**:
1. `SCANNING` — looking for `### R-NNN:` header
2. `IN_CRITERION` — collecting fields (`- **Source**:`, `- **Evaluator**:`, etc.)
3. `IN_FRONTMATTER` — parsing YAML frontmatter between `---` markers

**Key design decisions**:
- Frontmatter parsed with simple key-value extraction (no YAML library dependency)
- Category inferred from parent `## Section` heading
- Result field parsed from `- **Result**: [x] PASS` or `- **Result**: [ ] FAIL`
- Tolerant parsing: missing fields get sensible defaults (severity defaults to `blocking`, evaluator defaults to `sw:grill`)

**Public API**:
```typescript
export function parseRubric(content: string): RubricDocument;
export function parseRubricFile(filePath: string): Promise<RubricDocument>;
```

#### 2. `rubric-generator.ts` — Spec.md ACs → rubric.md

**Approach**: Reads spec.md, extracts all ACs with their user story grouping, generates rubric criteria organized by category.

**Generation rules**:
1. Each AC group (by user story) becomes one or more `R-NNN` criteria under "Functional Correctness"
2. Project-level defaults always appended:
   - `R-NNN: Unit test coverage meets target [blocking]` (evaluator: `coverage`)
   - `R-NNN: No critical/high code review findings [blocking]` (evaluator: `sw:code-reviewer`)
   - `R-NNN: Ship readiness [blocking]` (evaluator: `sw:grill`)
   - `R-NNN: LLM judge verdict [blocking]` (evaluator: `sw:judge-llm`)
3. IDs are sequential within the document: R-001, R-002, ...

**AC extraction reuse**: Uses the same `parseAllACsWithPriority` method already in `completion-validator.ts`, extracted to a shared utility if needed, or called directly via the static method.

**Public API**:
```typescript
export function generateRubric(
  incrementId: string,
  specContent: string,
  options?: { coverageTarget?: number; title?: string }
): string;  // Returns markdown string

export async function generateRubricFile(
  incrementId: string,
  incrementPath: string,
  options?: { coverageTarget?: number }
): Promise<void>;  // Writes rubric.md to disk
```

#### 3. `rubric-merger.ts` — Three-Tier Inheritance

**Three tiers** (lowest to highest priority):
1. **Global**: `.specweave/rubric.md` — org-wide defaults (e.g., "all increments must have test coverage >= 90%")
2. **Project**: `.specweave/rubric-{project}.md` or `workspace.repos[N].rubricPath` — per-project overrides
3. **Increment**: `.specweave/increments/NNNN-name/rubric.md` — increment-specific (auto-generated + customized)

**Merge algorithm**:
1. Parse all three layers (any can be absent)
2. Increment criteria take precedence by ID — if R-001 exists at increment level, it replaces global/project R-001
3. Criteria from higher tiers (global, project) that don't conflict are appended
4. De-duplication by criterion ID
5. Category ordering preserved: functional-correctness → test-coverage → code-quality → security → performance → documentation → independent-evaluation

**Key constraint**: Merge is read-only. It produces a merged `RubricDocument` in memory for evaluation. It never writes back to any layer.

**Public API**:
```typescript
export async function mergeRubricLayers(
  projectRoot: string,
  incrementId: string,
  incrementPath: string,
  options?: { projectId?: string }
): Promise<RubricDocument | null>;  // null if no rubric.md at any tier
```

#### 4. `rubric-evaluator.ts` — Gate Reports → Criterion Results

**Approach**: Maps each criterion's `evaluator` field to the corresponding gate report JSON, extracts pass/fail.

**Evaluator mapping**:

| Evaluator | Report File | Pass Condition |
|-----------|------------|----------------|
| `sw:grill` | `reports/grill-report.json` | AC in `acCompliance.results` with `status: "pass"` |
| `sw:code-reviewer` | `reports/code-review-report.json` | `summary.critical === 0 && summary.high === 0 && summary.medium === 0` |
| `sw:judge-llm` | `reports/judge-llm-report.json` | `verdict !== "REJECTED"` |
| `coverage` | Coverage report (Istanbul/c8/lcov) | Coverage >= threshold |
| `manual` | N/A | Skipped (result: `skip`) |

**For functional criteria (evaluator: `sw:grill`)**: The evaluator inspects `grill-report.json → acCompliance.results[]` and matches `acId` values from the criterion's `sourceACs` array. If all referenced ACs have `status: "pass"`, the criterion passes.

**For aggregate criteria** (code-quality, test-coverage): The evaluator checks the summary field of the relevant report.

**Public API**:
```typescript
export async function evaluateRubric(
  rubric: RubricDocument,
  reportsDir: string,
  options?: { projectRoot?: string }
): Promise<RubricDocument>;  // Returns rubric with results populated

export interface RubricEvaluationSummary {
  total: number;
  blocking: { total: number; passed: number; failed: number };
  advisory: { total: number; passed: number; failed: number };
  verdict: 'PASS' | 'FAIL';  // FAIL if any blocking criterion failed
}

export function summarizeResults(rubric: RubricDocument): RubricEvaluationSummary;
```

### Integration Points

#### 5. `completion-validator.ts` — Exact Insertion Location

The rubric validation inserts **after** the existing quality gate report validation (line ~192) and **before** the test coverage validation (line ~197). This is the natural position because rubric evaluation consumes gate reports that were just validated.

```typescript
// NEW: Rubric quality contract validation
// Inserted after quality gate report validation (line ~192)
// and before test coverage validation (line ~197)
try {
  const { mergeRubricLayers } = await import('../rubric/rubric-merger.js');
  const { evaluateRubric, summarizeResults } = await import('../rubric/rubric-evaluator.js');

  const rubric = await mergeRubricLayers(
    resolveEffectiveRoot(), incrementId, incrementPath
  );

  if (rubric) {
    const evaluated = await evaluateRubric(rubric, reportsDir);
    const summary = summarizeResults(evaluated);

    if (summary.blocking.failed > 0) {
      const failedCriteria = evaluated.criteria
        .filter(c => c.severity === 'blocking' && c.result?.status === 'fail');
      errors.push(
        `Rubric: ${summary.blocking.failed} blocking criteria failed:\n` +
        failedCriteria.map(c =>
          `    ${c.id}: ${c.title} — ${c.result?.evidence || 'no evidence'}`
        ).join('\n')
      );
    }

    if (summary.advisory.failed > 0) {
      warnings.push(
        `Rubric: ${summary.advisory.failed} advisory criteria did not pass`
      );
    }
  }
  // No rubric.md at any tier = zero behavior change (backward compatible)
} catch (error) {
  logger.warn(`Rubric validation failed: ${error instanceof Error ? error.message : String(error)}`);
  warnings.push('Rubric validation skipped due to error');
}
```

**Backward compatibility**: The entire rubric block is wrapped in a null check (`if (rubric)`). If no rubric.md exists at any tier, the function returns `null` and the block is skipped entirely. Zero behavior change for existing increments.

#### 6. `template-creator.ts` — Rubric Generation During Planning

After spec.md is written by the PM skill (not during initial template creation), the rubric is generated. The natural trigger is when the planner agent (sw-planner) finishes generating tasks.md.

**Option A (recommended)**: Add rubric generation to `sw-planner.md` as a final step — after writing tasks.md, the planner calls `rubric-generator.ts` to produce rubric.md.

**Option B**: Add a post-planning lifecycle hook in `LifecycleHookDispatcher.onIncrementPlanned()` that generates rubric.md if spec.md has real content.

**Recommendation**: Option A is simpler and doesn't add hook complexity. The planner already reads spec.md and understands ACs — generating the rubric is a natural extension.

#### 7. Skill Definition References

The following skill definitions (markdown prompts) should reference rubric.md:

1. **`plugins/specweave/skills/done/SKILL.md`**: Add a step between Step 4 (Grill) and Step 5 (Judge-LLM) or make it part of Gate 0 (Step 8):
   - "Read rubric.md if present. After all gate reports are generated, rubric evaluation is automatic via `specweave complete`."

2. **`plugins/specweave/skills/grill/SKILL.md`**: In Phase 0 (Spec Compliance), add:
   - "If rubric.md exists, load it and verify that each functional criterion maps to your AC compliance results."

3. **`plugins/specweave/agents/sw-planner.md`**: Add final step:
   - "After writing tasks.md, generate rubric.md from spec.md ACs."

**Note**: These are prompt-level instructions, not code changes. They guide the AI agents to be rubric-aware.

## Technology Stack

- **Language**: TypeScript (strict mode, ESM)
- **Import extensions**: `.js` (per project convention)
- **Testing**: Vitest
- **Dependencies**: None new — uses only Node.js built-ins (fs, path) and existing SpecWeave utilities

## Architecture Decisions

### ADR-0248: Rubric Quality Contracts

**Decision**: Add `rubric.md` as a structured quality contract consumed by the closure pipeline.

**Why not JSON?** The rubric must be human-readable and editable by PMs and architects. Markdown with structured headers (like the existing format in increment 0625) is the natural choice. Gate reports remain JSON — the evaluator bridges the two.

**Why three tiers, not two?** Global rubric captures org-wide standards (e.g., "all increments need >= 90% coverage"). Project rubric captures per-repo standards (e.g., "API projects need security audit"). Increment rubric captures feature-specific criteria from ACs. Without all three, either standards are duplicated per-increment or per-increment customization is impossible.

**Why pass/fail only, no scoring?** Scoring invites gaming ("it's 79, close enough to 80"). Binary pass/fail with clear thresholds is unambiguous. The rubric says what must be true; the evaluator checks if it is true.

**Why lazy-import in completion-validator?** The rubric module is only needed during closure. Lazy import avoids adding to startup time for non-closure operations (same pattern used for `ExternalToolDriftDetector`, `validateCoverage`).

**Why evaluator matches on AC IDs, not criterion IDs?** Gate reports (grill, code-reviewer) already track AC compliance by AC-ID. The rubric criterion's `sourceACs` field creates the bridge without requiring gate tools to know about rubric IDs.

## Implementation Phases

### Phase 1: Core Module (types + parser + generator)
- `types.ts` — all interfaces and types
- `rubric-parser.ts` — markdown → RubricDocument
- `rubric-generator.ts` — spec.md ACs → rubric.md markdown
- Unit tests for parser and generator

### Phase 2: Merge + Evaluate
- `rubric-merger.ts` — three-tier inheritance merge
- `rubric-evaluator.ts` — gate report JSON → criterion results
- Unit tests for merger and evaluator with fixture data

### Phase 3: Integration
- Insert rubric validation into `completion-validator.ts` (lines 192-197 area)
- Add rubric generation step to sw-planner agent prompt
- Update done/grill skill prompts to reference rubric.md

### Phase 4: Template Wiring
- Add rubric.md to `template-creator.ts` (optional — generate empty placeholder or skip)
- Verify backward compatibility: increments without rubric.md pass closure unchanged

## Testing Strategy

- **Unit tests**: Parser (valid rubric, malformed rubric, empty rubric, missing frontmatter), Generator (spec with 1 AC, 20 ACs, no ACs), Merger (all-three-tiers, missing-tiers, ID-conflict-resolution), Evaluator (all-pass, some-fail, missing-reports, corrupt-reports)
- **Integration tests**: Full pipeline — generate from spec.md → parse → merge → evaluate against fixture gate reports → verify pass/fail
- **Backward compatibility test**: Run `validateCompletion` on an increment with no rubric.md → verify identical behavior to current

## Technical Challenges

### Challenge 1: Grill Report AC Compliance Mapping
**Problem**: The evaluator needs to match rubric criterion `sourceACs` (e.g., `["AC-US1-01", "AC-US1-02"]`) to grill report `acCompliance.results[].acId`. AC ID formats must match exactly.
**Solution**: Normalize AC IDs in both parser and evaluator (strip whitespace, uppercase). The grill report already uses the canonical `AC-USN-NN` format.
**Risk**: Low — format is well-established across the codebase.

### Challenge 2: Three-Tier File Discovery
**Problem**: Finding the right rubric files across global, project, and increment tiers when project ID may or may not be set.
**Solution**: `mergeRubricLayers` checks fixed paths: `.specweave/rubric.md` (global), `.specweave/rubric-{projectId}.md` (project, only if projectId known from metadata), `.specweave/increments/NNNN/rubric.md` (increment). Missing files are silently skipped.
**Risk**: Low — same pattern used by config resolution.

### Challenge 3: Evaluation Without Gate Reports
**Problem**: rubric-evaluator runs during `validateCompletion`, which also validates that gate reports exist. If gate reports are missing, rubric evaluation can't map results.
**Solution**: Rubric validation runs after quality gate report validation. If gate reports are missing, the existing validator already blocks closure. Rubric evaluator marks criteria as `skip` when their evaluator's report is absent, with a warning.
**Risk**: None — the ordering naturally handles this.

## File Impact Summary

| File | Change |
|------|--------|
| `src/core/rubric/types.ts` | NEW — ~80 lines |
| `src/core/rubric/rubric-parser.ts` | NEW — ~150 lines |
| `src/core/rubric/rubric-generator.ts` | NEW — ~200 lines |
| `src/core/rubric/rubric-merger.ts` | NEW — ~100 lines |
| `src/core/rubric/rubric-evaluator.ts` | NEW — ~200 lines |
| `src/core/rubric/index.ts` | NEW — ~10 lines |
| `src/core/increment/completion-validator.ts` | MODIFY — add ~30 lines at line ~192 |
| `plugins/specweave/agents/sw-planner.md` | MODIFY — add rubric generation step |
| `plugins/specweave/skills/done/SKILL.md` | MODIFY — reference rubric in Gate 0 |
| `plugins/specweave/skills/grill/SKILL.md` | MODIFY — reference rubric in Phase 0 |
