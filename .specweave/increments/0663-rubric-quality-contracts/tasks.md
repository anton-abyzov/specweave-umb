# Tasks: Rubric Quality Contracts for Increment Closure

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable (safe to run concurrently)
- `[ ]`: Not started | `[x]`: Completed
- **TDD mode** — tests FIRST, then implementation (RED → GREEN → REFACTOR)
- Model hints: `haiku` (simple CRUD/types), `sonnet` (default), `opus` (complex logic)

---

## Phase 1: Core Module — Types + Parser [AGENT-A]

> All Phase 1 tasks target `repositories/anton-abyzov/specweave/src/core/rubric/`

---

### T-001: Define rubric type system
**User Story**: US-001
**Satisfies ACs**: AC-US1-08
**Status**: [x] completed
**Model**: haiku

**Description**: Create `src/core/rubric/types.ts` with all shared TypeScript interfaces and type aliases. This is the foundation — all other modules import from here.

**Implementation Details**:
- `RubricSeverity = 'blocking' | 'advisory'`
- `EvaluatorId = 'sw:grill' | 'sw:code-reviewer' | 'sw:judge-llm' | 'coverage' | 'manual'`
- `RubricCategory` union (functional-correctness, test-coverage, code-quality, security, performance, documentation, independent-evaluation)
- `CriterionResult { status: 'pass' | 'fail' | 'skip'; evidence: string; evaluatedAt: string }`
- `RubricCriterion { id, title, sourceACs, evaluator, verify, threshold, severity, category, result }`
- `RubricDocument { incrementId, title, generated, source, version, criteria }`
- `RubricLayer { path, criteria }`
- `RubricParseError extends Error { lineNumber: number; rawLine: string }`

**Test Plan**:
- **File**: `src/core/rubric/__tests__/types.test.ts`
- **Tests**:
  - **TC-001**: Types are assignable (compile-time check via `satisfies`)
    - Given the `RubricCriterion` interface
    - When a literal object satisfies all required fields
    - Then TypeScript compilation succeeds with no errors

**Dependencies**: None

---

### T-002: Write failing tests for RubricParser (TDD RED)
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Status**: [x] completed
**Model**: sonnet

**Description**: Write comprehensive Vitest tests for `rubric-parser.ts` BEFORE implementing it. All tests must fail (red phase).

**Test Plan**:
- **File**: `src/core/rubric/__tests__/rubric-parser.test.ts`
- **Tests**:
  - **TC-001**: Parse complete valid rubric.md → RubricDocument
    - Given a well-formed rubric.md with frontmatter and 3 criteria across 2 categories
    - When `parseRubric(content)` is called
    - Then it returns a `RubricDocument` with `incrementId`, `title`, `generated`, and 3 `criteria` entries
  - **TC-002**: Parse criterion header with `[blocking]` severity
    - Given a line `### R-001: No critical findings [blocking]`
    - When parsed
    - Then `criterion.id === 'R-001'`, `criterion.title === 'No critical findings'`, `criterion.severity === 'blocking'`
  - **TC-003**: Parse criterion header with `[advisory]` severity
    - Given a line `### R-005: Advisory check [advisory]`
    - When parsed
    - Then `criterion.severity === 'advisory'`
  - **TC-004**: Parse all three Result states
    - Given `- **Result**: [ ] PENDING`
    - When parsed
    - Then `result` is `null` (PENDING = no result yet)
    - Given `- **Result**: [x] PASS`
    - When parsed
    - Then `result.status === 'pass'`
    - Given `- **Result**: [!] FAIL — 2 critical findings`
    - When parsed
    - Then `result.status === 'fail'` and `result.evidence === '2 critical findings'`
  - **TC-005**: Parse Evaluator field with all supported values
    - Given `- **Evaluator**: sw:grill`
    - When parsed
    - Then `criterion.evaluator === 'sw:grill'`
    - Repeat for `sw:code-reviewer`, `sw:judge-llm`, `coverage`, `manual`
  - **TC-006**: Parse Source field with multiple AC IDs
    - Given `- **Source**: AC-US1-01, AC-US1-02`
    - When parsed
    - Then `criterion.sourceACs` is `['AC-US1-01', 'AC-US1-02']`
  - **TC-007**: Parse single-AC Source field
    - Given `- **Source**: AC-US3-01`
    - When parsed
    - Then `criterion.sourceACs` is `['AC-US3-01']`
  - **TC-008**: Throw RubricParseError on malformed frontmatter
    - Given rubric.md with missing closing `---` for frontmatter
    - When `parseRubric(content)` is called
    - Then it throws `RubricParseError` with a `.lineNumber` property set
  - **TC-009**: Parse category from `## Section` heading
    - Given a rubric.md with `## Functional Correctness` section containing 2 criteria
    - When parsed
    - Then both criteria have `category === 'functional-correctness'`
  - **TC-010**: Parse Verify and Threshold fields
    - Given a criterion with `- **Verify**: All ACs pass` and `- **Threshold**: 100% pass rate`
    - When parsed
    - Then `criterion.verify === 'All ACs pass'` and `criterion.threshold === '100% pass rate'`
  - **TC-011**: Parse rubric.md with no criteria (empty document)
    - Given a valid frontmatter and no `### R-` headers
    - When parsed
    - Then `RubricDocument.criteria` is an empty array (no error)

**Dependencies**: T-001

---

### T-003: Implement RubricParser (TDD GREEN)
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08
**Status**: [x] completed
**Model**: sonnet

**Description**: Implement `src/core/rubric/rubric-parser.ts` line-by-line state machine to make all T-002 tests pass.

**Implementation Details**:
- State machine with states: `SCANNING_FRONTMATTER`, `IN_FRONTMATTER`, `SCANNING`, `IN_CRITERION`
- Frontmatter: simple key-value extraction between `---` markers (no YAML library)
- Category: inferred from last seen `## Heading` (convert to kebab-case)
- Criterion header regex: `/^### (R-[A-Z0-9-]+):\s+(.+?)\s+\[(blocking|advisory)\]$/`
- Result field: match `[x]`, `[ ]`, `[!]` then capture optional ` — reason` text
- Source field: split on `,` and trim each AC ID
- Evaluator field: trim and validate against `EvaluatorId` union; unknown evaluators accepted (tolerant)
- Missing fields: severity defaults to `'blocking'`, evaluator defaults to `'sw:grill'`, sourceACs defaults to `[]`
- Exports: `parseRubric(content: string): RubricDocument` and `parseRubricFile(filePath: string): Promise<RubricDocument>`

**Test Plan**:
- Run `npx vitest run src/core/rubric/__tests__/rubric-parser.test.ts` — all TC-001 through TC-011 must pass

**Dependencies**: T-001, T-002

---

### T-004: Write failing tests for RubricGenerator (TDD RED)
**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-06, AC-US2-07, AC-US2-08
**Status**: [x] completed
**Model**: sonnet

**Description**: Write Vitest tests for `rubric-generator.ts` BEFORE implementing it.

**Test Plan**:
- **File**: `src/core/rubric/__tests__/rubric-generator.test.ts`
- **Tests**:
  - **TC-001**: Generate rubric from spec with N ACs
    - Given a spec.md string with 3 ACs in 1 user story
    - When `generateRubric('0663-test', specContent)` is called
    - Then the returned string contains at least 3 `### R-` criteria headers
  - **TC-002**: Generated criterion references its source AC
    - Given a spec.md with AC `AC-US1-01`
    - When a rubric is generated
    - Then at least one criterion has `- **Source**: AC-US1-01` in its body
  - **TC-003**: Generated rubric includes standard categories
    - Given any spec.md content
    - When `generateRubric` is called
    - Then the output contains `## Test Coverage`, `## Code Quality`, and `## Independent Evaluation` sections
  - **TC-004**: Generated rubric has valid YAML frontmatter
    - Given a spec.md and `incrementId: '0663-test'`
    - When `generateRubric` is called
    - Then the output starts with `---` and contains `increment: 0663-test`, a `generated:` ISO timestamp, `status: pending`, and `version:`
  - **TC-005**: All generated criteria have PENDING result
    - Given any spec.md
    - When `generateRubric` is called and result is parsed
    - Then every `RubricCriterion.result` is `null` (PENDING)
  - **TC-006**: Coverage threshold from options
    - Given `options: { coverageTarget: 90 }`
    - When `generateRubric` is called
    - Then the test-coverage criterion threshold contains `>= 90%`
  - **TC-007**: Empty spec.md generates only standard categories
    - Given an empty string or spec.md with no ACs
    - When `generateRubric` is called
    - Then the rubric contains at least the 3 standard category criteria but no `- **Source**: AC-` entries
  - **TC-008**: Criterion IDs are sequential R-001, R-002, ...
    - Given a spec with 2 ACs
    - When rubric is generated and parsed
    - Then criterion IDs start at `R-001` and increment without gaps

**Dependencies**: T-001, T-003

---

### T-005: Implement RubricGenerator (TDD GREEN)
**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-06, AC-US2-07, AC-US2-08
**Status**: [x] completed
**Model**: sonnet

**Description**: Implement `src/core/rubric/rubric-generator.ts` to make all T-004 tests pass.

**Implementation Details**:
- AC extraction: parse `- [ ] **AC-US\d+-\d+**:` patterns from spec.md (same approach as `completion-validator.ts`)
- Group ACs by user story; generate one criterion per AC (or one per US for large USes)
- Assign evaluator: functional-correctness → `sw:grill`, test-coverage → `coverage`, code-quality → `sw:code-reviewer`, independent-evaluation → `sw:grill` (ship readiness) and `sw:judge-llm` (verdict)
- ID counter: start at 1, pad to 3 digits, e.g., `R-001`
- Frontmatter: include `increment`, `title`, `generated` (ISO-8601 via `new Date().toISOString()`), `source: spec.md`, `version: '1.0'`, `status: pending`
- Standard criteria always appended:
  - `R-NNN: Unit test coverage meets target [blocking]` (evaluator: `coverage`, threshold: `>= ${coverageTarget ?? 90}% line coverage`)
  - `R-NNN: No critical or high code review findings [blocking]` (evaluator: `sw:code-reviewer`)
  - `R-NNN: Ship readiness verified [blocking]` (evaluator: `sw:grill`)
  - `R-NNN: LLM judge verdict acceptable [blocking]` (evaluator: `sw:judge-llm`)
- Public exports: `generateRubric(incrementId, specContent, options?)` returning markdown string; `generateRubricFile(incrementId, incrementPath, options?)` writing rubric.md to disk (uses `fs.promises.writeFile`)

**Test Plan**:
- Run `npx vitest run src/core/rubric/__tests__/rubric-generator.test.ts` — all TC-001 through TC-008 must pass

**Dependencies**: T-001, T-004

---

## Phase 2: Merge + Evaluate [AGENT-B] (parallel with Phase 1 after T-001)

> Phase 2 tasks also target `src/core/rubric/` but depend only on T-001 for types.

---

### T-006: Write failing tests for RubricMerger (TDD RED)
**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Model**: sonnet

**Description**: Write Vitest tests for `rubric-merger.ts` BEFORE implementing it. Uses fixture rubric.md files in `src/core/rubric/__tests__/fixtures/`.

**Test Plan**:
- **File**: `src/core/rubric/__tests__/rubric-merger.test.ts`
- **Fixtures** (create in `src/core/rubric/__tests__/fixtures/`):
  - `global-defaults.md` — contains R-D01 (blocking, threshold: ">= 90%"), R-D02 (blocking)
  - `project-overrides.md` — contains R-D01 with different threshold ">= 95%" (override)
  - `increment-rubric.md` — contains R-001, R-002 (spec-derived) and R-D01 (further override)
- **Tests**:
  - **TC-001**: Global only — no project, no increment overrides
    - Given only `global-defaults.md` exists at global tier
    - When `mergeRubricLayers(projectRoot, incrementId, incrementPath)` is called
    - Then returned RubricDocument contains R-D01 and R-D02 from global
  - **TC-002**: Project overrides global on ID collision
    - Given global has R-D01 (threshold >= 90%) and project has R-D01 (threshold >= 95%)
    - When merged
    - Then R-D01 in result has threshold ">= 95%" (project wins)
  - **TC-003**: Increment overrides project on ID collision
    - Given project has R-D01 (threshold >= 95%) and increment has R-D01 (threshold >= 80%)
    - When merged
    - Then R-D01 in result has threshold ">= 80%" (increment wins)
  - **TC-004**: Non-conflicting criteria from all tiers are combined
    - Given global has R-D01, project has R-D02, increment has R-001
    - When merged
    - Then result contains all three: R-D01 (global), R-D02 (project), R-001 (increment)
  - **TC-005**: No rubric files at any tier → returns null
    - Given no `rubric.md` or `rubric-defaults.md` files exist anywhere
    - When `mergeRubricLayers` is called
    - Then it returns `null` (no error thrown)
  - **TC-006**: Missing global tier is silently skipped
    - Given only increment `rubric.md` exists
    - When merged
    - Then result contains only increment criteria (no error for missing global)
  - **TC-007**: Whole-criterion replacement — no field-level merge
    - Given global R-D01 has fields: `severity: blocking, verify: 'check A', threshold: '90%'`
    - And project R-D01 has fields: `severity: advisory, verify: 'check B'` (threshold absent)
    - When merged
    - Then project R-D01 is used entirely — result does NOT inherit `threshold: '90%'` from global

**Dependencies**: T-001, T-003

---

### T-007: Implement RubricMerger (TDD GREEN)
**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Model**: sonnet

**Description**: Implement `src/core/rubric/rubric-merger.ts` to make all T-006 tests pass.

**Implementation Details**:
- File discovery (in order, lowest-to-highest priority):
  1. Global: `{projectRoot}/plugins/specweave/defaults/rubric-defaults.md`
  2. Project: `{projectRoot}/.specweave/rubric-defaults.md`
  3. Increment: `{incrementPath}/rubric.md`
- Parse each file that exists using `parseRubricFile` (from rubric-parser.ts)
- Merge algorithm: build a `Map<string, RubricCriterion>` starting from global criteria, then overwrite with project criteria (same key = replace entirely), then overwrite with increment criteria
- Preserve category ordering: functional-correctness → test-coverage → code-quality → security → performance → documentation → independent-evaluation
- Missing files: silently skip (no throw)
- All tiers absent: return `null`
- Output: merged `RubricDocument` (in-memory only — never writes to disk)
- Public export: `mergeRubricLayers(projectRoot, incrementId, incrementPath, options?): Promise<RubricDocument | null>`

**Test Plan**:
- Run `npx vitest run src/core/rubric/__tests__/rubric-merger.test.ts` — all TC-001 through TC-007 must pass

**Dependencies**: T-001, T-003, T-006

---

### T-008: Write failing tests for RubricEvaluator (TDD RED)
**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
**Status**: [x] completed
**Model**: sonnet

**Description**: Write Vitest tests for `rubric-evaluator.ts` BEFORE implementing it. Uses fixture gate report JSON files.

**Test Plan**:
- **File**: `src/core/rubric/__tests__/rubric-evaluator.test.ts`
- **Fixtures** (create in `src/core/rubric/__tests__/fixtures/reports/`):
  - `grill-report.json` — contains `acCompliance.results` with AC-US1-01 (pass), AC-US1-02 (fail), `shipReadiness: 'READY'`
  - `code-review-report.json` — contains `summary: { critical: 0, high: 0, medium: 1, low: 2 }`
  - `judge-llm-report.json` — contains `verdict: 'APPROVED'`
  - `grill-report-fail.json` — `shipReadiness: 'NOT READY'`
  - `code-review-report-critical.json` — `summary: { critical: 2, high: 0, medium: 0, low: 0 }`
  - `judge-llm-report-rejected.json` — `verdict: 'REJECTED'`
- **Tests**:
  - **TC-001**: Grill evaluator — all AC references pass
    - Given a criterion with `evaluator: 'sw:grill'`, `sourceACs: ['AC-US1-01']`
    - And grill-report.json has AC-US1-01 with `status: 'pass'`
    - When `evaluateRubric(rubric, reportsDir)` is called
    - Then that criterion's `result.status === 'pass'`
  - **TC-002**: Grill evaluator — any AC reference fails → criterion fails
    - Given criterion `sourceACs: ['AC-US1-01', 'AC-US1-02']` and AC-US1-02 has `status: 'fail'`
    - When evaluated
    - Then `result.status === 'fail'` and `result.evidence` mentions `AC-US1-02`
  - **TC-003**: Code-reviewer evaluator — zero critical+high+medium → pass
    - Given criterion with `evaluator: 'sw:code-reviewer'` and `summary: { critical: 0, high: 0, medium: 0 }`
    - When evaluated
    - Then `result.status === 'pass'`
  - **TC-004**: Code-reviewer evaluator — critical findings → fail
    - Given `summary: { critical: 2, high: 0, medium: 0 }`
    - When evaluated
    - Then `result.status === 'fail'` and `result.evidence` mentions `2 critical`
  - **TC-005**: Judge-LLM evaluator — APPROVED verdict → pass
    - Given `verdict: 'APPROVED'`
    - When evaluated
    - Then `result.status === 'pass'`
  - **TC-006**: Judge-LLM evaluator — REJECTED verdict → fail
    - Given `verdict: 'REJECTED'`
    - When evaluated
    - Then `result.status === 'fail'`
  - **TC-007**: Missing gate report → criterion result is skip
    - Given a criterion with `evaluator: 'sw:grill'` but `grill-report.json` does not exist
    - When evaluated
    - Then `result.status === 'skip'` and no error is thrown
  - **TC-008**: Malformed gate report → criterion result is skip (no crash)
    - Given `grill-report.json` contains invalid JSON
    - When evaluated
    - Then `result.status === 'skip'` (graceful degradation)
  - **TC-009**: summarizeResults returns correct counts
    - Given a RubricDocument with 3 blocking criteria (2 pass, 1 fail) and 2 advisory (1 pass, 1 fail)
    - When `summarizeResults(rubric)` is called
    - Then result is `{ total: 5, blocking: { total: 3, passed: 2, failed: 1 }, advisory: { total: 2, passed: 1, failed: 1 }, verdict: 'FAIL' }`
  - **TC-010**: FAIL verdict when any blocking criterion fails
    - Given at least 1 blocking criterion with `result.status === 'fail'`
    - When `summarizeResults` is called
    - Then `verdict === 'FAIL'`
  - **TC-011**: PASS verdict only when all blocking criteria pass
    - Given all blocking criteria have `result.status === 'pass'`
    - When `summarizeResults` is called
    - Then `verdict === 'PASS'`

**Dependencies**: T-001

---

### T-009: Implement RubricEvaluator (TDD GREEN)
**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
**Status**: [x] completed
**Model**: sonnet

**Description**: Implement `src/core/rubric/rubric-evaluator.ts` to make all T-008 tests pass.

**Implementation Details**:
- Evaluator dispatch table (keyed by `EvaluatorId`):
  - `'sw:grill'`: load `grill-report.json`, check `acCompliance.results[].acId` against `criterion.sourceACs` — all must have `status: 'pass'`. Also check `shipReadiness !== 'NOT READY'` for non-AC criteria.
  - `'sw:code-reviewer'`: load `code-review-report.json`, pass if `summary.critical === 0 && summary.high === 0 && summary.medium === 0`
  - `'sw:judge-llm'`: load `judge-llm-report.json`, pass if `verdict !== 'REJECTED'`
  - `'coverage'`: load coverage data (istanbul/c8 lcov); if absent, set skip
  - `'manual'`: always `skip`
- Report loading: wrap in try-catch; on any error set `status: 'skip'`, log warning
- `evaluatedAt`: `new Date().toISOString()`
- Evidence for failures: short human-readable string (e.g., `"AC-US1-02 failed in grill report"`)
- `evaluateRubric`: iterates all criteria, dispatches to evaluator, returns NEW RubricDocument (immutable)
- `summarizeResults`: counts by severity and status; `verdict: 'FAIL'` if any blocking criterion status is `'fail'`
- Do NOT write to rubric.md from this module — write-back is handled by the skill prompts (not code)

**Test Plan**:
- Run `npx vitest run src/core/rubric/__tests__/rubric-evaluator.test.ts` — all TC-001 through TC-011 must pass

**Dependencies**: T-001, T-008

---

### T-010: Create barrel export index.ts
**User Story**: US-001
**Satisfies ACs**: AC-US1-08
**Status**: [x] completed
**Model**: haiku

**Description**: Create `src/core/rubric/index.ts` re-exporting the public API of all rubric modules.

**Implementation Details**:
```typescript
export * from './types.js';
export * from './rubric-parser.js';
export * from './rubric-generator.js';
export * from './rubric-merger.js';
export * from './rubric-evaluator.js';
```
All imports use `.js` extensions (ESM with NodeNext resolution).

**Test Plan**:
- Verify no circular import errors: `node --input-type=module <<< "import './src/core/rubric/index.js'"`

**Dependencies**: T-003, T-005, T-007, T-009

---

## Phase 3: Integration — Completion Validator [AGENT-C]

> Targets `repositories/anton-abyzov/specweave/src/core/increment/completion-validator.ts`

---

### T-011: Write failing tests for completion-validator rubric integration (TDD RED)
**User Story**: US-005, US-010
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06, AC-US5-07, AC-US10-01
**Status**: [x] completed
**Model**: sonnet

**Description**: Extend existing `completion-validator` tests with rubric-specific test cases BEFORE modifying the validator. Must not break existing tests.

**Test Plan**:
- **File**: `src/core/increment/__tests__/completion-validator-rubric.test.ts` (new file alongside existing tests)
- **Tests**:
  - **TC-001**: All blocking criteria PASS → no rubric errors
    - Given a rubric.md with 3 blocking criteria all `[x] PASS`
    - When `validateCompletion(incrementId, incrementPath)` is called
    - Then result has zero errors referencing rubric
  - **TC-002**: 2 blocking criteria FAIL → error message lists them by ID+title
    - Given rubric with R-001 `[!] FAIL` and R-003 `[!] FAIL` (both blocking)
    - When validation runs
    - Then `errors` array contains a string matching `"Rubric: 2 blocking criteria failed"` with `R-001` and `R-003` mentioned
  - **TC-003**: 1 blocking criterion PENDING → error message
    - Given rubric with R-002 `[ ] PENDING` (blocking)
    - When validation runs
    - Then `errors` contains `"Rubric: 1 blocking criterion not yet evaluated: R-002"`
  - **TC-004**: Advisory failures → warnings, not errors
    - Given rubric with all blocking PASS, but 2 advisory FAIL
    - When validation runs
    - Then `errors` is empty and `warnings` contains a rubric advisory notice
  - **TC-005**: No rubric.md → existing hardcoded gates run unchanged
    - Given increment directory with no `rubric.md` at any tier
    - When validation runs
    - Then validation output is identical to pre-rubric behavior (no new errors/warnings mentioning rubric)
  - **TC-006**: Defense-in-depth — both rubric AND hardcoded gates contribute errors
    - Given rubric has 1 blocking FAIL and the existing code-review gate also has a finding
    - When validation runs
    - Then `errors` contains both a rubric error and the existing gate error
  - **TC-007**: `config.json` has `rubric.required: false` → rubric skipped
    - Given `config.json` with `{ "rubric": { "required": false } }`
    - When validation runs
    - Then no rubric evaluation occurs and no rubric errors appear
  - **TC-008**: Malformed rubric.md → warning added, no crash
    - Given a rubric.md with invalid markdown (missing frontmatter closer)
    - When validation runs
    - Then it does NOT throw; instead adds a warning about rubric validation failure

**Dependencies**: T-009, T-010

---

### T-012: Integrate rubric validation into completion-validator.ts (TDD GREEN)
**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06, AC-US5-07
**Status**: [x] completed
**Model**: sonnet

**Description**: Modify `src/core/increment/completion-validator.ts` to add rubric validation gate after line ~192 (after quality gate report validation, before test coverage validation).

**Implementation Details**:
- Insert lazy dynamic import block (see plan.md exact code snippet)
- Check `config.rubric?.required !== false` before running (opt-out mechanism)
- Call `mergeRubricLayers(resolveEffectiveRoot(), incrementId, incrementPath)`
- If `rubric !== null`, call `evaluateRubric(rubric, reportsDir)` and `summarizeResults(evaluated)`
- Blocking failures: push to `errors` array with format `"Rubric: N blocking criteria failed: R-001 (Title), ..."`
- Blocking PENDING: push to `errors` array with format `"Rubric: N blocking criteria not yet evaluated: R-002 (Title)"`
- Advisory failures: push to `warnings` array
- Wrap entire block in try-catch: on any error push a `warnings` entry and continue (never throw)
- Use `.js` import extensions: `'../rubric/rubric-merger.js'`, `'../rubric/rubric-evaluator.js'`

**Test Plan**:
- Run `npx vitest run src/core/increment/__tests__/completion-validator-rubric.test.ts` — all TC-001 through TC-008 must pass
- Run full existing test suite: `npx vitest run src/core/increment/` — zero regressions

**Dependencies**: T-010, T-011

---

## Phase 4: Template + Scaffold Integration [AGENT-D]

---

### T-013: Add rubric.md placeholder to template-creator.ts
**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [x] completed
**Model**: haiku

**Description**: Modify `src/core/increment/template-creator.ts` to create a `rubric.md` placeholder file when scaffolding a new increment directory.

**Implementation Details**:
- Find the section where `spec.md`, `plan.md`, `tasks.md` are written (likely a `writeFile` or template call block)
- Add a `rubric.md` write with placeholder content:
  ```markdown
  ---
  increment: {incrementId}
  title: {title}
  generated: ""
  source: auto-generated
  version: "1.0"
  status: template
  ---

  <!-- This file is auto-generated by sw-planner during planning.
       After planning, review and customize criteria before implementation.
       DO NOT edit manually until sw-planner has generated the full rubric. -->
  ```
- Template uses the same variable substitution mechanism as existing template files

**Test Plan**:
- **File**: Extend existing `template-creator` tests or add to `src/core/increment/__tests__/`
- **TC-001**: `createIncrementTemplates()` creates rubric.md
  - Given `createIncrementTemplates(incrementId, title, path)` is called
  - When directory is created
  - Then `rubric.md` exists with frontmatter `status: template` and placeholder comment
- **TC-002**: rubric.md placeholder has correct incrementId in frontmatter
  - Given `incrementId: '0999-test'`
  - When template is created
  - Then rubric.md frontmatter contains `increment: 0999-test`

**Dependencies**: T-001

---

### T-014: Create global rubric defaults file
**User Story**: US-009
**Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04, AC-US9-05
**Status**: [x] completed
**Model**: haiku

**Description**: Create `plugins/specweave/defaults/rubric-defaults.md` with the standard baseline criteria used for all increments.

**Implementation Details**:
- File must be valid rubric.md format (parseable by `parseRubric`)
- Frontmatter: `increment: defaults`, `title: Global Rubric Defaults`, `source: specweave-defaults`, `version: 1.0`, `status: defaults`
- `## Test Coverage` section:
  - `### R-D01: Unit test coverage meets project target [blocking]` — evaluator: `coverage`, threshold: `>= configured coverageTarget (default 90%) line coverage`
- `## Code Quality` section:
  - `### R-D02: No critical or high code review findings [blocking]` — evaluator: `sw:code-reviewer`, threshold: `critical === 0 AND high === 0`
- `## Independent Evaluation` section:
  - `### R-D03: Grill ship readiness verified [blocking]` — evaluator: `sw:grill`, threshold: `shipReadiness !== 'NOT READY'`
  - `### R-D04: LLM judge verdict acceptable [blocking]` — evaluator: `sw:judge-llm`, threshold: `verdict !== 'REJECTED'`
- All criteria use `R-D` prefix (e.g., `R-D01`) to distinguish from spec-derived criteria

**Test Plan**:
- **TC-001**: File is parseable without errors
  - Given `plugins/specweave/defaults/rubric-defaults.md` exists
  - When `parseRubricFile(path)` is called
  - Then it returns a `RubricDocument` with 4 criteria (R-D01 through R-D04) and no parse errors
- **TC-002**: All criteria have `R-D` prefixed IDs
  - Given the parsed document
  - Then every criterion ID matches `/^R-D\d+$/`

**Dependencies**: T-003

---

## Phase 5: Skill + Agent Prompt Updates [AGENT-E]

> All tasks in this phase modify markdown SKILL.md / agent prompt files only (no TypeScript).
> These are parallelizable with each other.

---

### T-015: [P] Update sw:done SKILL.md — rubric validation step
**User Story**: US-007
**Satisfies ACs**: AC-US7-01
**Status**: [x] completed
**Model**: haiku

**Description**: Edit `plugins/specweave/skills/done/SKILL.md` to include rubric validation as part of Gate 0 / closure checks.

**Implementation Details**:
- Locate the Gate 0 or Step 8 / closure section in SKILL.md
- Add instruction: "If `rubric.md` exists in the increment directory, rubric evaluation is automatic via `specweave complete`. The completion-validator reads, evaluates, and reports rubric results. Review any blocking failures before retrying closure."
- Keep the existing gate steps intact — rubric is additive (defense-in-depth)

**Test Plan**:
- **TC-001**: SKILL.md contains "rubric.md" reference
  - Given the updated SKILL.md
  - When searched for `rubric.md`
  - Then at least one match exists in the Gate 0 / closure section

**Dependencies**: None

---

### T-016: [P] Update sw:grill SKILL.md — rubric criterion evaluation
**User Story**: US-007
**Satisfies ACs**: AC-US7-02, AC-US7-05
**Status**: [x] completed
**Model**: haiku

**Description**: Edit `plugins/specweave/skills/grill/SKILL.md` to instruct grill to read and evaluate rubric criteria where `evaluator: sw:grill`.

**Implementation Details**:
- Locate Phase 0 (Spec Compliance) or the preamble instructions section
- Add instruction block:
  ```
  **Rubric Integration**: If `rubric.md` exists in the increment directory:
  1. Load the file and find all criteria where `Evaluator: sw:grill`
  2. For each criterion, use your AC compliance analysis to determine PASS or FAIL
  3. Update the criterion's `Result` field: `[x] PASS` or `[!] FAIL — <brief reason>`
  4. If rubric.md does not exist, proceed with existing behavior (no crash, no error)
  ```

**Test Plan**:
- **TC-001**: SKILL.md mentions rubric.md and evaluator field
  - Given the updated SKILL.md
  - When searched for `rubric.md`
  - Then at least one match exists with evaluator instruction

**Dependencies**: None

---

### T-017: [P] Update sw:code-reviewer SKILL.md — rubric criterion evaluation
**User Story**: US-007
**Satisfies ACs**: AC-US7-04, AC-US7-05
**Status**: [x] completed
**Model**: haiku

**Description**: Edit `plugins/specweave/skills/code-reviewer/SKILL.md` to instruct code-reviewer to read and evaluate rubric criteria where `evaluator: sw:code-reviewer`.

**Implementation Details**:
- Add instruction block similar to T-016 but for `sw:code-reviewer` evaluator
- Specify: if critical/high/medium findings remain, mark matching criteria FAIL with count in evidence
- If rubric.md absent: skip rubric operations entirely (no error)

**Test Plan**:
- **TC-001**: SKILL.md mentions rubric.md and `sw:code-reviewer` evaluator
  - Given the updated SKILL.md
  - When searched for `rubric.md`
  - Then at least one match exists

**Dependencies**: None

---

### T-018: [P] Update sw:judge-llm SKILL.md — rubric criterion evaluation
**User Story**: US-007
**Satisfies ACs**: AC-US7-03, AC-US7-05
**Status**: [x] completed
**Model**: haiku

**Description**: Edit `plugins/specweave/skills/judge-llm/SKILL.md` to instruct judge-llm to read and evaluate rubric criteria where `evaluator: sw:judge-llm`.

**Implementation Details**:
- Add instruction block: read criteria with `Evaluator: sw:judge-llm`, update Result to PASS if verdict != REJECTED, FAIL otherwise
- If rubric.md absent: proceed with existing behavior

**Test Plan**:
- **TC-001**: SKILL.md mentions rubric.md and `sw:judge-llm` evaluator
  - Given the updated SKILL.md
  - When searched for `rubric.md`
  - Then at least one match exists

**Dependencies**: None

---

### T-019: [P] Update sw-planner.md — generate rubric.md alongside tasks.md
**User Story**: US-008
**Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03
**Status**: [x] completed
**Model**: haiku

**Description**: Edit `plugins/specweave/agents/sw-planner.md` to add rubric generation as a final step after writing `tasks.md`.

**Implementation Details**:
- Locate the tasks.md generation step in sw-planner.md
- Add final step: "After writing tasks.md, generate `rubric.md` for this increment. Call `generateRubricFile(incrementId, incrementPath, { coverageTarget })` to produce `rubric.md` from spec.md ACs. Inform the user that rubric.md has been created and they can review/customize criteria before implementation begins."
- Mention that rubric criteria can be modified (severity changed, criteria added/removed) before work starts

**Test Plan**:
- **TC-001**: sw-planner.md mentions rubric.md generation
  - Given the updated sw-planner.md
  - When searched for `rubric.md`
  - Then at least one match exists in the tasks.md generation section

**Dependencies**: None

---

## Phase 6: Integration Test + Backward Compatibility [AGENT-F]

---

### T-020: Write full pipeline integration test (TDD RED)
**User Story**: US-005, US-010
**Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04, AC-US10-05
**Status**: [x] completed
**Model**: sonnet

**Description**: Write an end-to-end integration test that exercises the complete rubric pipeline: generate → parse → merge → evaluate → validate. All tests must fail before Phase 6 implementation.

**Test Plan**:
- **File**: `src/core/rubric/__tests__/rubric-pipeline.integration.test.ts`
- **Tests**:
  - **TC-001**: Full pipeline — generate from spec, evaluate against fixture reports, validate
    - Given a real spec.md content with 3 ACs and fixture gate reports (all passing)
    - When: `generateRubric` → `parseRubric` → `mergeRubricLayers` → `evaluateRubric` → `summarizeResults`
    - Then: `verdict === 'PASS'` and all blocking criteria have `result.status === 'pass'`
  - **TC-002**: Full pipeline — failing gate reports → FAIL verdict
    - Given fixture gate reports with code-review critical findings
    - When the full pipeline runs
    - Then `verdict === 'FAIL'` and the code-reviewer criterion has `result.status === 'fail'`
  - **TC-003**: Backward compat — increment with no rubric.md
    - Given an increment directory with only spec.md, tasks.md, plan.md (no rubric.md, no rubric-defaults.md)
    - When `mergeRubricLayers` is called
    - Then it returns `null` (no error)
    - And when `validateCompletion` is called on this increment
    - Then it completes without any rubric-related errors or warnings
  - **TC-004**: Parse-then-merge round trip preserves criterion count
    - Given a generated rubric.md string with 7 criteria
    - When parsed, then merge-layered with global defaults (4 criteria, no ID conflicts)
    - Then merged document has 11 criteria total

**Dependencies**: T-010, T-012

---

### T-021: Run full test suite and fix any regressions
**User Story**: US-010
**Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04, AC-US10-05
**Status**: [x] completed
**Model**: sonnet

**Description**: Run the complete specweave test suite and fix any regressions introduced by the rubric module or completion-validator changes.

**Implementation Details**:
- Run: `npx vitest run` from `repositories/anton-abyzov/specweave/`
- Fix any type errors or import issues that surfaced
- Verify the following specific backward-compat scenarios pass:
  1. Existing increment without rubric.md → no new errors in `validateCompletion`
  2. `config.json` without `rubric` section → rubric validation skipped (no crash)
  3. Gate tests (grill, code-reviewer, judge-llm) unaffected by rubric module import

**Test Plan**:
- All pre-existing tests pass (zero regressions)
- All new rubric tests pass (TC counts from T-002 through T-020)
- Coverage target: >= 90% for the new `src/core/rubric/` module

**Dependencies**: T-012, T-020

---

## Summary

| Phase | Agent | Tasks | Parallelizable |
|-------|-------|-------|----------------|
| 1: Core Types + Parser + Generator | A | T-001 to T-005 | T-004 after T-003 only |
| 2: Merger + Evaluator | B | T-006 to T-010 | T-006 and T-008 after T-001 |
| 3: Completion Validator | C | T-011, T-012 | After Phase 1+2 complete |
| 4: Template + Defaults | D | T-013, T-014 | After T-001; parallel with each other |
| 5: Skill Prompts | E | T-015 to T-019 | All fully parallel |
| 6: Integration + Regression | F | T-020, T-021 | T-020 after Phase 3; T-021 last |

**Dependency graph**:
```
T-001 ──→ T-002 ──→ T-003 ──→ T-004 ──→ T-005
T-001 ──→ T-006 ──→ T-007        (Phase 2, parallel with 1)
T-001 ──→ T-008 ──→ T-009
T-003,5,7,9 ──→ T-010 (index)
T-009,T-010 ──→ T-011 ──→ T-012
T-001 ──→ T-013 (template placeholder, any time after T-001)
T-003 ──→ T-014 (global defaults, any time after T-003)
T-015..T-019: independent of code tasks
T-010,T-012 ──→ T-020 ──→ T-021
```
