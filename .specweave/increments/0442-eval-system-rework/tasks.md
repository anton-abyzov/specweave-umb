---
increment: 0442-eval-system-rework
generated_by: sw:test-aware-planner
tdd_mode: true
coverage_target: 90
by_user_story:
  US-007: [T-001, T-002]
  US-001: [T-003, T-004]
  US-002: [T-005, T-006]
  US-003: [T-007]
  US-005: [T-008, T-009]
  US-004: [T-010, T-011]
  US-006: [T-012, T-013, T-014]
---

# Tasks: 0442 — Rework Skill Evaluation System

## User Story: US-007 - Backward-Compatible Schema Extension

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Tasks**: 2 total, 0 completed

---

### T-001: Extend types.ts with V2 TypeScript types

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02
**Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/eval/types.ts` exists with V1 types
- **When** V2 types are added (Assertion, AssertionResult, RubricScore, VarianceEntry, VarianceData, EvalCaseResultV2, EvalRunResultV2)
- **Then** all new types compile without errors and existing V1 types remain unchanged

**Test Cases**:
1. **Unit**: `src/lib/eval/__tests__/types.test.ts`
   - `typesV2Assertion_hasIdTextTypeFields()`: Verify Assertion type shape compiles correctly with id, text, type="boolean"
   - `typesV2AssertionResult_hasAllFields()`: Verify AssertionResult contains assertionId, assertionText, pass, reasoning
   - `typesV2RubricScore_hasContentAndStructure()`: Verify RubricScore has contentScore and structureScore numbers
   - `typesV2VarianceData_hasPerAssertionAndTotalRuns()`: Verify VarianceData shape
   - `typesV2EvalRunResultV2_extendsEvalRunResult()`: Verify EvalRunResultV2 has methodologyVersion=2 and optional V2 fields
   - `isEvalRunResultV2_typeGuard_returnsTrueForV2()`: Verify type guard correctly discriminates V2 from V1
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/lib/eval/types.ts`
2. Add `Assertion`, `AssertionResult`, `RubricScore`, `VarianceEntry`, `VarianceData` types
3. Add `EvalCaseResultV2` extending `EvalCaseResult` with optional rubric + assertion fields
4. Add `EvalRunResultV2` extending `EvalRunResult` with `methodologyVersion: 2` and optional V2 aggregates
5. Export `isEvalRunResultV2(r: EvalRunResult | EvalRunResultV2): r is EvalRunResultV2` type guard checking `methodologyVersion === 2`
6. Run `npx tsc --noEmit` to verify no type errors

---

### T-002: Prisma schema extension and migration

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Status**: [x] completed

**Test Plan**:
- **Given** the current Prisma schema with EvalRun, EvalCase, and EvalTrigger enum
- **When** new nullable columns and REVERIFY enum value are added and migration is applied
- **Then** the DB schema is updated, existing V1 rows have nulls in new columns, and no data is lost

**Test Cases**:
1. **Integration**: `src/lib/eval/__tests__/eval-store-schema.test.ts`
   - `schema_evalRunV2Columns_areNullable()`: Create an EvalRun row with only V1 fields; verify new columns are null
   - `schema_evalCaseV2Columns_areNullable()`: Create an EvalCase with only V1 fields; verify rubric/assertion columns are null
   - `schema_evalTrigger_includesREVERIFY()`: Verify REVERIFY is a valid EvalTrigger value accepted by Prisma
   - **Coverage Target**: 85%

**Implementation**:
1. Open `prisma/schema.prisma`
2. Add to `EvalRun` model: `methodologyVersion Int?`, `assertionPassRate Float?`, `skillRubricAvg Float?`, `baselineRubricAvg Float?`, `varianceData Json?`, `runCountPerCase Int?`
3. Add to `EvalCase` model: `assertionResults Json?`, `skillContentScore Int?`, `skillStructureScore Int?`, `baselineContentScore Int?`, `baselineStructureScore Int?`
4. Add `REVERIFY` to `EvalTrigger` enum
5. Run `npx prisma migrate dev --name eval-v2-schema`
6. Run `npx prisma generate`
7. Verify existing unit tests still pass

---

## User Story: US-001 - Assertion-Based Grading

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

---

### T-003: Implement assertion-grader.ts with batch LLM grading

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a skill output string and an array of N boolean assertions
- **When** `gradeAssertions(skillOutput, assertions, ai)` is called
- **Then** the LLM is called once (batch), and an `AssertionResult[]` is returned with pass/reasoning per assertion

**Test Cases**:
1. **Unit** (TDD — write tests first): `src/lib/eval/__tests__/assertion-grader.test.ts`
   - `gradeAssertions_batchesAllAssertions_inOneCall()`: Mock ai.run, verify called exactly once with all assertions in prompt; assert result length equals input assertions length
   - `gradeAssertions_twoPassOneFail_assertionPassRateIs0_67()`: 3 assertions where LLM returns pass=true,true,false; verify array has 2 pass and 1 fail; verify that 2/3 = 0.67 pass rate when caller computes it
   - `gradeAssertions_malformedJsonResponse_retriesOnce()`: First ai.run returns unparseable JSON; second returns valid; verify grader retries and succeeds
   - `gradeAssertions_twoFailedAttempts_allAssertionsMarkedFailed()`: Both batch calls fail; verify all assertions have pass=false and reasoning="Grading error"
   - `gradeAssertions_emptyAssertions_returnsEmptyArray()`: Input assertions=[]; verify output is []
   - **Coverage Target**: 95%

**Implementation**:
1. Write failing tests in `src/lib/eval/__tests__/assertion-grader.test.ts`
2. Create `src/lib/eval/assertion-grader.ts`
3. Implement `gradeAssertions(skillOutput: string, assertions: Assertion[], ai: Ai): Promise<AssertionResult[]>`
4. Build system prompt instructing LLM to return JSON array `[{ id, pass, reasoning }]`
5. Parse response; on failure retry once with same batch call
6. On second failure fall back: mark all assertions `pass: false, reasoning: "Grading error"`
7. Map results back to `AssertionResult[]` including `assertionText` from input
8. Run tests: `npx vitest run src/lib/eval/__tests__/assertion-grader.test.ts`

---

### T-004: Aggregate assertion results into EvalCase and EvalRun fields

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** an EvalRunResultV2 with multiple cases each having AssertionResult arrays
- **When** `storeEvalRun` persists the result
- **Then** each EvalCase row has `assertionResults` JSON and EvalRun has `assertionPassRate` = total passed / total assertions

**Test Cases**:
1. **Unit**: `src/lib/eval/__tests__/eval-engine-v2.test.ts` (aggregation logic)
   - `aggregateAssertionPassRate_twoPassOneFail_equals0_67()`: Directly test the aggregation helper; input has 3 assertions across 2 cases (2 pass, 1 fail); verify assertionPassRate = 0.67
   - `aggregateAssertionPassRate_allPassing_equals1_0()`: All assertions pass; verify assertionPassRate = 1.0
   - `aggregateAssertionPassRate_noCases_equals0()`: Empty cases array; verify assertionPassRate = 0
2. **Integration**: `src/lib/eval/__tests__/eval-store.test.ts`
   - `storeEvalRun_V2_persistsAssertionResultsOnEvalCase()`: Store a V2 result; query EvalCase from DB; verify assertionResults JSON matches input
   - `storeEvalRun_V2_persistsAssertionPassRateOnEvalRun()`: Verify EvalRun.assertionPassRate is persisted correctly
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests
2. Add `computeAssertionPassRate(cases: EvalCaseResultV2[]): number` helper in `eval-engine-v2.ts`
3. Extend `eval-store.ts` to write `assertionResults` on each `EvalCase` upsert when `methodologyVersion === 2`
4. Extend `eval-store.ts` to write `assertionPassRate` on `EvalRun` upsert when `methodologyVersion === 2`
5. Run tests

---

## User Story: US-002 - Rubric Scoring

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 0 completed

---

### T-005: Implement rubric-scorer.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** a skill output string, a baseline output string, and a prompt
- **When** `scoreRubric(output, prompt, ai)` is called for each output independently
- **Then** it returns `{ contentScore: 1-5, structureScore: 1-5 }` with scores clamped to the valid range

**Test Cases**:
1. **Unit** (TDD — write tests first): `src/lib/eval/__tests__/rubric-scorer.test.ts`
   - `scoreRubric_validLLMResponse_returnsContentAndStructure()`: Mock ai.run returning `{"contentScore":4,"structureScore":3}`; verify output matches
   - `scoreRubric_scoresAbove5_clampsTo5()`: LLM returns `{"contentScore":7,"structureScore":6}`; verify output is {5, 5}
   - `scoreRubric_scoresBelow1_clampsTo1()`: LLM returns `{"contentScore":0,"structureScore":-1}`; verify output is {1, 1}
   - `scoreRubric_nonNumericResponse_defaultsTo3()`: LLM returns invalid JSON; verify {contentScore:3, structureScore:3}
   - `scoreRubric_makesOneCallPerOutput()`: Verify ai.run called exactly once per scoreRubric invocation
   - **Coverage Target**: 95%

**Implementation**:
1. Write failing tests in `src/lib/eval/__tests__/rubric-scorer.test.ts`
2. Create `src/lib/eval/rubric-scorer.ts`
3. Implement `scoreRubric(output: string, prompt: string, ai: Ai): Promise<RubricScore>`
4. Build LLM prompt with rubric definitions (Content 1-5, Structure 1-5)
5. Parse JSON response; clamp scores to [1, 5]; default to 3 on parse failure
6. Run tests

---

### T-006: Persist rubric scores and aggregate averages

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** an EvalRunResultV2 with per-case rubric scores for skill and baseline
- **When** `storeEvalRun` persists the V2 result
- **Then** each EvalCase has the four rubric score columns populated, EvalRun has skillRubricAvg and baselineRubricAvg, and qualityScore/baselineScore remain populated for V1 compat

**Test Cases**:
1. **Unit**: `src/lib/eval/__tests__/eval-engine-v2.test.ts`
   - `computeRubricAvg_twoScores_returnsCorrectMean()`: Two cases with content=4,structure=3 and content=5,structure=5; verify skillRubricAvg = (3.5+5)/2 = 4.25
   - `computeRubricAvg_noCases_returnsNull()`: Empty case array; verify rubricAvg is null/undefined
2. **Integration**: `src/lib/eval/__tests__/eval-store.test.ts`
   - `storeEvalRun_V2_persistsRubricScoresOnEvalCase()`: Verify skillContentScore, skillStructureScore, baselineContentScore, baselineStructureScore are all stored
   - `storeEvalRun_V2_persistsRubricAvgsOnEvalRun()`: Verify skillRubricAvg and baselineRubricAvg on EvalRun
   - `storeEvalRun_V2_qualityScoreStillPopulated()`: Verify qualityScore and baselineScore (V1 compat) are still present in V2 result
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests
2. Add `computeRubricAvg(cases: EvalCaseResultV2[], target: "skill" | "baseline"): number | null` helper in `eval-engine-v2.ts`
3. Extend `eval-store.ts` to write the four rubric columns on each `EvalCase` upsert
4. Extend `eval-store.ts` to write `skillRubricAvg` and `baselineRubricAvg` on `EvalRun` upsert
5. Verify `qualityScore` and `baselineScore` write path is not disturbed
6. Run tests

---

## User Story: US-003 - V2 Verdict Logic

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06
**Tasks**: 1 total, 0 completed

---

### T-007: Implement verdict-v2.ts with four-tier verdict logic

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06
**Status**: [x] completed

**Test Plan**:
- **Given** an assertionPassRate (0-1) and skill/baseline rubric averages
- **When** `computeV2Verdict(assertionPassRate, skillRubricAvg, baselineRubricAvg)` is called
- **Then** it returns EFFECTIVE, MARGINAL, INEFFECTIVE, or DEGRADING per the defined thresholds; V1 runs with null methodologyVersion use V1 verdict logic unchanged

**Test Cases**:
1. **Unit** (TDD — write tests first): `src/lib/eval/__tests__/verdict-v2.test.ts`
   - `computeV2Verdict_highPassRateAndRubricDelta_returnsEFFECTIVE()`: passRate=0.85, skillAvg=4.5, baselineAvg=3.0; verify EFFECTIVE
   - `computeV2Verdict_highPassRateButNoRubricDelta_returnsMARGINAL()`: passRate=0.85, skillAvg=3.5, baselineAvg=3.0 (delta=0.5, not >1); verify MARGINAL
   - `computeV2Verdict_marginalPassRateAndRubricAdvantage_returnsMARGINAL()`: passRate=0.65, skillAvg=3.5, baselineAvg=3.0; verify MARGINAL
   - `computeV2Verdict_lowPassRate_returnsINEFFECTIVE()`: passRate=0.50, skillAvg=2.0, baselineAvg=3.0; verify INEFFECTIVE
   - `computeV2Verdict_veryLowPassRate_returnsDEGRADING()`: passRate=0.30; verify DEGRADING regardless of rubric scores
   - `computeV2Verdict_exactBoundary0_80_withDeltaOver1_returnsEFFECTIVE()`: passRate=0.80, skillAvg=4.2, baselineAvg=3.1; verify EFFECTIVE (boundary inclusive)
   - `computeV2Verdict_exactBoundary0_40_returnsINEFFECTIVE()`: passRate=0.40; verify INEFFECTIVE (not DEGRADING)
   - `computeV2Verdict_exactBoundary0_39_returnsDEGRADING()`: passRate=0.39; verify DEGRADING
   - `v1VerdictLogic_judgeTs_remainsUnchanged()`: Verify judge.ts is not imported or called by verdict-v2.ts
   - `storeEvalRun_V2_methodologyVersionIs2()`: Verify EvalRun.methodologyVersion is stored as 2 for new V2 runs
   - **Coverage Target**: 95%

**Implementation**:
1. Write all failing tests first
2. Create `src/lib/eval/verdict-v2.ts`
3. Implement `computeV2Verdict(assertionPassRate: number, skillRubricAvg: number, baselineRubricAvg: number): EvalVerdict`
4. Logic: EFFECTIVE (passRate>=0.80 AND skillAvg > baselineAvg+1), MARGINAL (passRate>=0.60 AND skillAvg > baselineAvg), INEFFECTIVE (passRate>=0.40), DEGRADING (passRate<0.40)
5. Confirm V1 `judge.ts` is NOT modified
6. Extend `eval-store.ts` to write `methodologyVersion: 2` on EvalRun when storing V2 results
7. Run tests

---

## User Story: US-005 - Enhanced Prompt and Assertion Generation

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 2 total, 0 completed

---

### T-008: Parse Evaluations section and convert Expected to assertions

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** a SKILL.md with an `## Evaluations` section (evals.json format) or a `## Test Cases` section with Prompt/Expected pairs
- **When** `generateTestPrompts(skillMd, ai)` is called
- **Then** for the Evaluations path, assertions are parsed directly without an LLM call; for the Test Cases path, Expected values are converted to `{ id, text, type: "boolean" }[]` via LLM; generated assertions are NOT written back to the repo

**Test Cases**:
1. **Unit** (TDD): `src/lib/eval/__tests__/prompt-generator.test.ts`
   - `generateTestPrompts_withEvaluationsSection_parsesAssertionsDirectly()`: SKILL.md with `## Evaluations` JSON block; verify TestPrompt.assertions populated and ai.run NOT called for assertion generation
   - `generateTestPrompts_withTestCasesSection_convertsExpectedToAssertions()`: SKILL.md with `## Test Cases` Prompt/Expected pairs; verify ai.run called once per test case to convert Expected; output assertions have type="boolean"
   - `generateTestPrompts_assertionType_alwaysBoolean()`: All generated or parsed assertions have type="boolean"
   - `generateTestPrompts_noAssertionsWrittenBack()`: Verify no file write operations occur during prompt generation
   - `generateTestPrompts_evaluationsPriority_overTestCases()`: SKILL.md with both sections; verify Evaluations section wins and Test Cases section is ignored
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests
2. Open `src/lib/eval/prompt-generator.ts`
3. Add `parseEvaluationsSection(skillMd: string): Assertion[] | null` — parse `## Evaluations` JSON block
4. Add `convertExpectedToAssertions(expected: string, ai: Ai): Promise<Assertion[]>` — LLM call producing `{ id, text, type: "boolean" }[]`
5. Update `generateTestPrompts` to check for `## Evaluations` first, then `## Test Cases`
6. Attach `assertions?: Assertion[]` to the `TestPrompt` type and each returned prompt
7. Run tests

---

### T-009: Auto-generate prompts and assertions from skill description

**User Story**: US-005
**Satisfies ACs**: AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** a SKILL.md with neither `## Evaluations` nor `## Test Cases`
- **When** `generateTestPrompts(skillMd, ai)` is called
- **Then** the system fully auto-generates both prompts AND assertions via LLM; all assertions have type="boolean" and nothing is written to the repo

**Test Cases**:
1. **Unit** (TDD): `src/lib/eval/__tests__/prompt-generator.test.ts`
   - `generateTestPrompts_noSections_autoGeneratesPromptsAndAssertions()`: SKILL.md with only a description; verify ai.run called for full auto-generation; output has TestPrompt[] with non-empty assertions arrays
   - `generateTestPrompts_autoGenerated_assertionsAreBooleanType()`: All assertions in auto-gen output have type="boolean"
   - `generateTestPrompts_autoGenerated_notWrittenToRepo()`: Verify no file I/O side effects
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests
2. Add `autoGeneratePromptsAndAssertions(skillMd: string, ai: Ai): Promise<TestPrompt[]>` — LLM call that returns both prompts and assertions from skill description
3. Update `generateTestPrompts` to call this as the final fallback (lowest priority)
4. Enforce type="boolean" on all outputs (sanitize after LLM call regardless of LLM response)
5. Run tests

---

## User Story: US-004 - Multi-Run Variance Analysis

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
**Tasks**: 2 total, 0 completed

---

### T-010: Implement variance-analyzer.ts

**User Story**: US-004
**Satisfies ACs**: AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
**Status**: [x] completed

**Test Plan**:
- **Given** N arrays of AssertionResult (one per run, each covering the same assertions)
- **When** `analyzeVariance(multiRunResults, totalRuns)` is called
- **Then** it returns VarianceData with per-assertion mean, stddev, flaky flag (stddev > 0.3), and nonDiscriminating flag (mean === 1.0 across ALL cases)

**Test Cases**:
1. **Unit** (TDD): `src/lib/eval/__tests__/variance-analyzer.test.ts`
   - `analyzeVariance_threeDeterministicPassingRuns_mean1_stddev0()`: 3 runs all passing; verify mean=1.0, stddev=0.0, flaky=false
   - `analyzeVariance_mixedResults_computesMeanAndStddev()`: 3 runs where assertion passes 2/3; verify mean approx 0.67, stddev computed correctly
   - `analyzeVariance_highVariance_flaggedAsFlaky()`: Alternating pass/fail (stddev > 0.3); verify flaky=true
   - `analyzeVariance_lowVariance_notFlaky()`: All passing (stddev=0); verify flaky=false
   - `analyzeVariance_assertionPassesAllRunsAllCases_nonDiscriminating()`: Assertion always passes in every run across every test case input; verify nonDiscriminating=true
   - `analyzeVariance_assertionFailsSometimes_notNonDiscriminating()`: At least one run has a failure; verify nonDiscriminating=false
   - `analyzeVariance_totalRuns_correctInOutput()`: Input totalRuns=5; verify varianceData.totalRuns=5
   - **Coverage Target**: 95%

**Implementation**:
1. Write failing tests first
2. Create `src/lib/eval/variance-analyzer.ts`
3. Implement `analyzeVariance(multiRunResults: AssertionResult[][], totalRuns: number): VarianceData`
4. Per assertion: collect pass values (1/0) across runs; compute mean = sum/N; compute stddev = sqrt(mean of squared deviations)
5. Flag `flaky: stddev > 0.3`; flag `nonDiscriminating: mean === 1.0` (assertion passed in ALL runs)
6. Return `{ perAssertion: VarianceEntry[], totalRuns }`
7. Run tests

---

### T-011: Implement eval-engine-v2.ts with multi-run orchestration

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
**Status**: [x] completed

**Test Plan**:
- **Given** a skill, trigger type (SUBMISSION/REGRESSION/REVERIFY), and enhanced test prompts with assertions
- **When** `runQualityEvalV2(skill, trigger, ai)` is called
- **Then** each test case runs N times (1/3/5 based on trigger), variance is analyzed, V2 verdict is computed, and EvalRunResultV2 is returned with methodologyVersion=2

**Test Cases**:
1. **Unit** (TDD): `src/lib/eval/__tests__/eval-engine-v2.test.ts`
   - `runQualityEvalV2_SUBMISSION_runsEachCaseOnce()`: Mock all sub-modules; verify gradeAssertions called (testCaseCount * 1) times
   - `runQualityEvalV2_REGRESSION_runsEachCaseThreeTimes()`: Verify calls = (testCaseCount * 3)
   - `runQualityEvalV2_REVERIFY_runsEachCaseFiveTimes()`: Verify calls = (testCaseCount * 5)
   - `runQualityEvalV2_aggregatesMultiRunIntoVarianceData()`: 3-run REGRESSION; verify result.varianceData.totalRuns=3
   - `runQualityEvalV2_computesV2Verdict()`: Mock computeV2Verdict; verify it is called with assertionPassRate, skillRubricAvg, baselineRubricAvg
   - `runQualityEvalV2_returnsMethodologyVersion2()`: Verify result.methodologyVersion === 2
   - `runQualityEvalV2_runCountPerCase_storedInResult()`: Verify result.runCountPerCase matches N for given trigger
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests
2. Create `src/lib/eval/eval-engine-v2.ts`
3. Implement trigger-to-N mapping: `{ SUBMISSION: 1, REGRESSION: 3, REVERIFY: 5 }`
4. For each TestPrompt, run N iterations: `comparator.runComparator()`, `gradeAssertions()`, `scoreRubric()` for skill output, `scoreRubric()` for baseline output
5. Collect all run results per test case; after all cases call `analyzeVariance()` with aggregated data
6. Compute `assertionPassRate`, `skillRubricAvg`, `baselineRubricAvg` across all cases and runs
7. Call `computeV2Verdict` and assemble `EvalRunResultV2` with `methodologyVersion: 2` and `runCountPerCase: N`
8. Wire into `eval-consumer.ts`: if assertions present in TestPrompts OR `message.methodologyVersion === 2` then call `runQualityEvalV2`, else call `runQualityEval` (V1 fallback)
9. Run tests

---

## User Story: US-006 - Re-Verification Queue

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06
**Tasks**: 3 total, 0 completed

---

### T-012: Extend eval-consumer.ts and eval-types.ts for REVERIFY trigger

**User Story**: US-006
**Satisfies ACs**: AC-US6-03, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** an eval queue message with `trigger: "REVERIFY"` and `methodologyVersion: 2`
- **When** the eval consumer processes the message
- **Then** it routes to `runQualityEvalV2` with N=5 runs per test case, and no auto-deprecation occurs for DEGRADING verdicts

**Test Cases**:
1. **Unit**: `src/lib/queue/__tests__/eval-consumer.test.ts`
   - `evalConsumer_REVERIFY_routesToV2Engine()`: Mock queue message with trigger=REVERIFY; verify runQualityEvalV2 is called (not runQualityEval)
   - `evalConsumer_REVERIFY_N5runs()`: Verify REVERIFY trigger propagates to eval-engine-v2 which uses N=5
   - `evalConsumer_REVERIFY_neverAutoDeprecates()`: After storing DEGRADING verdict from reverify, verify no skill status is updated to deprecated
   - `evalConsumer_SUBMISSION_noAssertions_routesToV1()`: No assertions in TestPrompts and no methodologyVersion; verify V1 runQualityEval is called
   - `evalTypes_EvalQueueMessage_hasMethodologyVersionField()`: Verify EvalQueueMessage type compiles with optional `methodologyVersion?: number` field
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests
2. Add `methodologyVersion?: number` to `EvalQueueMessage` in `src/lib/queue/eval-types.ts`
3. Update `eval-consumer.ts` to handle `REVERIFY` trigger without throwing on unknown value
4. Implement V1/V2 routing: if `message.methodologyVersion === 2` OR assertions exist in TestPrompts then call `runQualityEvalV2`; otherwise call `runQualityEval`
5. Confirm no auto-deprecation logic is added
6. Run tests

---

### T-013: Implement POST /api/v1/admin/eval/reverify endpoint

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-05, AC-US6-06
**Status**: [x] completed

**Test Plan**:
- **Given** a POST request to `/api/v1/admin/eval/reverify` with a valid SUPER_ADMIN or internal auth token
- **When** the endpoint processes the request
- **Then** all non-deprecated published skills are enqueued to the existing EVAL_QUEUE with trigger=REVERIFY and methodologyVersion=2, and the response contains `{ queued: number, totalSkills: number }`

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/eval/reverify/__tests__/route.test.ts`
   - `reverify_SUPER_ADMIN_authPasses()`: Request with valid SUPER_ADMIN session; verify 200 response
   - `reverify_internalKey_authPasses()`: Request with X-Internal-Key header; verify 200 response
   - `reverify_noAuth_returns403()`: Unauthenticated request; verify 403
   - `reverify_enqueuesToExistingEvalQueue_notNewQueue()`: Verify only existing EVAL_QUEUE binding is used
   - `reverify_batchesIn25Groups()`: 30 published skills; verify queue.sendBatch called with at most 25 messages per batch
   - `reverify_returnsQueuedAndTotalCount()`: 5 published non-deprecated skills; verify response body is `{ queued: 5, totalSkills: 5 }`
   - `reverify_excludesDeprecatedSkills()`: Mix of deprecated and published; verify deprecated are excluded from enqueue
   - `reverify_neverAutoDeprecates()`: Verify endpoint contains no skill status mutation calls
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests
2. Create `src/app/api/v1/admin/eval/reverify/route.ts`
3. Implement auth check (SUPER_ADMIN session OR internal key header — match pattern from existing admin routes)
4. Query Prisma for all skills where status is published and not deprecated
5. Build queue messages: `{ trigger: "REVERIFY", skillId, methodologyVersion: 2 }` per skill
6. Batch-enqueue in groups of 25 using existing EVAL_QUEUE binding from Cloudflare env
7. Return `{ queued: enqueued, totalSkills: total }`
8. Run tests

---

### T-014: Update eval-regression.ts cron for V2 support

**User Story**: US-006
**Satisfies ACs**: AC-US4-02 (REGRESSION trigger with N=3)
**Status**: [x] completed

**Test Plan**:
- **Given** the regression cron job that enqueues skills for periodic re-evaluation with trigger=REGRESSION
- **When** the cron runs
- **Then** skills whose SKILL.md contains assertions (Evaluations or Test Cases section) are enqueued with `methodologyVersion: 2`; skills without assertions are enqueued without methodologyVersion (V1 fallback)

**Test Cases**:
1. **Unit**: `src/lib/cron/__tests__/eval-regression.test.ts`
   - `evalRegression_skillWithEvaluationsSection_enqueuedWithMethodologyV2()`: Mock skill SKILL.md containing `## Evaluations`; verify queue message has methodologyVersion=2
   - `evalRegression_skillWithTestCasesSection_enqueuedWithMethodologyV2()`: Mock skill SKILL.md with `## Test Cases`; verify methodologyVersion=2
   - `evalRegression_skillWithoutAssertionSections_enqueuedWithoutMethodologyVersion()`: Mock skill with no relevant sections; verify methodologyVersion is absent from queue message
   - `evalRegression_trigger_alwaysREGRESSION()`: Verify trigger field is "REGRESSION" for all cron-dispatched messages
   - **Coverage Target**: 85%

**Implementation**:
1. Write failing tests
2. Open `src/lib/cron/eval-regression.ts`
3. For each skill being enqueued, fetch or inspect its SKILL.md content
4. Check for presence of `## Evaluations` or `## Test Cases` heading in the content
5. If found: add `methodologyVersion: 2` to the queue message; otherwise omit it
6. Keep trigger as "REGRESSION" (no change to existing trigger logic)
7. Run tests
8. Run full test suite: `npx vitest run`
