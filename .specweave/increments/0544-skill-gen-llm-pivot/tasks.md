---
increment: 0544-skill-gen-llm-pivot
title: "Skill-Gen LLM Pivot: Replace Keyword Matching with LLM-Based Pattern Extraction"
status: completed
---

# Tasks

## US-004: Code Quality and Security — Shared Utils Extraction

### T-001: Create utils.ts with shared utilities, Zod schemas, and constants
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] Completed
**Test**: Given `repositories/anton-abyzov/specweave/tests/unit/skill-gen/utils.test.ts` is written RED with failing tests for every export → When `src/core/skill-gen/utils.ts` is created → Then all tests pass: `collectMarkdownFiles` finds `.md` files recursively and skips non-md files; `loadSignalStore` returns a Zod-validated store or an empty store on corrupt/missing file with a logged warning; `saveSignalStore` creates parent dirs and writes valid JSON; `sanitizeString` strips control characters and truncates to 200 chars; `estimateTokenCount` returns `Math.ceil(text.length / 4)`; `capEvidence` evicts the oldest entries FIFO when the array exceeds 20; `SignalStoreSchema` and `SignalEntrySchema` parse valid stores and reject malformed ones; `TOKEN_BUDGET` (50000), `MAX_EVIDENCE` (20), `MAX_STRING_LENGTH` (200) are exported constants

---

## US-002: Accurate Confidence Scoring / US-003: DriftDetector / US-004 — Type Changes

### T-002: Update types.ts — add uniqueSourceFiles, DriftResult, LLMPatternResponse; remove SignalCategory
**User Story**: US-002, US-003, US-004 | **Satisfies ACs**: AC-US2-01, AC-US3-02, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given the existing `src/core/skill-gen/types.ts` → When `uniqueSourceFiles?: string[]` is added to `SignalEntry`, `DriftResult` type is added with `{ skillFile: string; staleRefs: string[]; validRefs: string[] }`, `LLMPatternResponse` type is added with `{ patterns: Array<{ category: string; name: string; description: string; evidence: string[] }> }`, and the `SignalCategory` union + `| string` escape hatch are removed → Then TypeScript compilation succeeds with `tsc --noEmit`, `SignalEntry` accepts objects with and without `uniqueSourceFiles`, and a grep for `SignalCategory` across the whole module returns zero matches

---

## US-001: LLM-Based Pattern Extraction

### T-003: Rewrite signal-collector.ts — LLM-based detection and updated upsertSignal
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US4-01, AC-US4-02, AC-US4-04, AC-US4-05
**Status**: [x] Completed
**Test**: Given `signal-collector.test.ts` is rewritten with RED tests before any implementation → When `signal-collector.ts` is rewritten removing `PATTERN_CATEGORIES`, `MIN_KEYWORD_HITS`, and all private `loadStore`/`saveStore`/`collectMarkdownFiles`, and adding `detectPatternsLLM()` and updated `collect()` and `upsertSignal()` → Then: the mock `analyzeStructured` receives a prompt containing a `<documents>` block with file paths and contents; returned patterns are stored with sanitized strings (control chars stripped, length ≤ 200); `uniqueSourceFiles` is updated using Set semantics so duplicates are excluded; confidence equals `uniqueSourceFiles.length / minSignalCount` capped at 1.0; evidence arrays stop growing beyond 20 via `capEvidence`; when no LLM config is found `collect()` logs a warning and returns without throwing; when `analyzeStructured` rejects the error is caught, a warning is logged, and no exception propagates

### T-004: Implement batched LLM chunking for docs exceeding TOKEN_BUDGET
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] Completed
**Test**: Given `signal-collector.test.ts` has a RED test where three mock documents are each estimated at 20 000 tokens (60 000 total > 50 000 budget) → When `detectPatternsLLM()` processes them → Then `analyzeStructured` is called exactly twice (first batch within the 50K budget, second batch with the remaining doc); results from both calls are merged and deduplicated by `category + name`; when total tokens are ≤ TOKEN_BUDGET only a single `analyzeStructured` call is made

---

## US-003: DriftDetector Improvement

### T-005: Update drift-detector.ts — PASCAL_CASE_EXCLUSIONS, DriftResult[] return, remove console.warn
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01
**Status**: [x] Completed
**Test**: Given `drift-detector.test.ts` is updated with RED tests before implementation → When `drift-detector.ts` is updated with a `PASCAL_CASE_EXCLUSIONS` constant (~30 words: TypeScript, JavaScript, SpecWeave, ReactComponent, NextJs, NodeModule, ErrorBoundary, PascalCase, CamelCase, etc.), `check()` return type changed from `Promise<void>` to `Promise<DriftResult[]>`, all `console.warn` calls removed, and private `collectMarkdownFiles` replaced by the shared import from `utils.ts` → Then: `check()` returns an array of `DriftResult` objects each containing `skillFile`, `staleRefs`, and `validRefs`; none of the 30 excluded PascalCase words appear in any `staleRefs` array; a `vi.spyOn(console, 'warn')` receives zero calls throughout the test run; TypeScript compilation succeeds with the updated signature

---

## US-001 / US-004: SuggestionEngine Update

### T-006: Update suggestion-engine.ts — use shared utils, file-based confidence qualifying filter
**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US2-03, AC-US4-01, AC-US4-02
**Status**: [x] Completed
**Test**: Given `suggestion-engine.test.ts` is updated with RED tests → When `suggestion-engine.ts` replaces its private `loadStore`/`saveStore` with shared imports from `utils.ts` and changes the qualifying filter to `(entry.uniqueSourceFiles?.length ?? entry.incrementIds.length) >= minCount` → Then: a signal with 3 distinct source files qualifies when `minCount` is 3; a signal without `uniqueSourceFiles` but with 3 `incrementIds` also qualifies (backward compat fallback); private `loadStore`/`saveStore` are no longer defined in this file; both `loadSignalStore` and `saveSignalStore` from `utils.ts` are called during the test (verified via vi.mock or spy)

---

## US-005: Instant Seed Mode

### T-007: Add collectSeed() to signal-collector.ts and wire --seed CLI flag
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] Completed
**Test**: Given `signal-collector.test.ts` has RED tests for `collectSeed()` and the CLI skill command handler is located → When `collectSeed()` is implemented (scans all living docs, single batched LLM call reusing the same path as `collect()`, deduplicates by `category + name` against existing store entries, sets `firstSeen` to current ISO timestamp) and the `--seed` flag in the skill handler is wired to call `collectSeed()` → Then: a store containing `{ category: 'auth', name: 'jwt-pattern' }` does not gain a duplicate when seed returns the same pattern; a new pattern from seed is stored with `firstSeen` matching the mocked `Date.now()` value; `collectSeed()` on an empty docs directory makes zero `analyzeStructured` calls; invoking the CLI with `--seed` calls `collectSeed()` and not `collect()`

---

## US-006: Real-World Validation Tests

### T-008: Write integration tests — TypeScript fixture, Python ML fixture, empty project fixture
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [x] Completed
**Test**: Given fixture directories exist under `tests/unit/skill-gen/fixtures/` with realistic markdown docs (TypeScript project: docs mentioning error handling, testing patterns, and architecture decisions; Python ML project: docs mentioning data pipelines and model training; empty project: zero markdown files) and mocked `analyzeStructured` returns project-appropriate patterns → When `integration.test.ts` runs the full pipeline (signal detection → suggestion engine → store persistence) for each fixture → Then: the TypeScript fixture produces signals whose categories include `error-handling`, `testing`, and `architecture`; the Python ML fixture produces signals whose categories include `data-pipeline` and `model-training`; the empty project fixture completes without error, returns zero signals, and `analyzeStructured` is never called; every test scenario persists a `skill-signals.json` that passes `SignalStoreSchema.parse()` without throwing
