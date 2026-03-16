# Architecture Plan: 0442 — Rework Skill Evaluation System

## 1. Executive Summary

Replace the vskill-platform's holistic A/B eval pipeline with assertion-based grading, rubric scoring, and multi-run variance analysis. V2 coexists with V1 via a `methodologyVersion` field and nullable columns. Six implementation phases: schema, grader, prompts, engine, wiring, docs.

---

## 2. Architecture Context

### 2.1 Current System (V1)

```
prompt-generator  ─►  comparator  ─►  judge  ─►  eval-engine  ─►  eval-store
     │                    │              │            │                 │
     │  TestPrompt[]      │  Comp-       │  Judge-    │  EvalRun-      │  DB +
     │  (auto/author)     │  Result      │  Result    │  Result        │  KV
     │                    │              │  (0-100)   │  (verdict)     │
```

V1 uses a single LLM call in `judge.ts` that returns one 0-100 score and a verdict. No assertion granularity, no rubric dimensions, single execution per test case.

### 2.2 Target System (V2)

```
prompt-generator-v2        comparator (KEPT)          NEW MODULES
     │                          │                          │
     │  TestPrompt[] +          │  ComparatorResult        │
     │  Assertion[]             │  (unchanged)             │
     │                          │                          │
     ▼                          ▼                          ▼
┌────────────────────────────────────────────────────────────────────┐
│                     eval-engine-v2.ts                              │
│                                                                    │
│  for each test case × N runs:                                     │
│    1. comparator.runComparator()          (reused, unchanged)     │
│    2. assertion-grader.gradeAssertions()  (NEW)                   │
│    3. rubric-scorer.scoreRubric()         (NEW)                   │
│                                                                    │
│  After all runs:                                                   │
│    4. variance-analyzer.analyze()         (NEW)                   │
│    5. verdict-v2.computeV2Verdict()       (NEW)                   │
│                                                                    │
│  Aggregate into EvalRunResultV2                                    │
└────────────────────────────────────────────────────────────────────┘
         │
         ▼
    eval-store.ts (EXTENDED)
         │
    DB (nullable V2 columns) + KV
```

### 2.3 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| V1 coexistence | `methodologyVersion` field (null = V1, 2 = V2) | Zero breaking changes; V1 data untouched |
| Assertion storage | Flat JSON column on `EvalCase` | Avoids JOIN overhead on hot read path |
| Variance storage | Flat JSON column on `EvalRun` | Per-run aggregate, not per-case |
| Assertion type | `boolean` only (LLM-judged) | No regex/keyword matching per spec |
| Baseline comparison | KEPT (comparator unchanged) | Rubric delta is secondary verdict signal |
| Multi-run count | Trigger-based: SUBMISSION=1, REGRESSION=3, REVERIFY=5 | Progressive confidence by context |
| New queue | None (reuse EVAL_QUEUE) | Existing infra sufficient |
| AI interface | `Ai.run(model, { messages })` unchanged | Both CF AI and Claude adapter already implement it |

---

## 3. Component Design

### 3.1 New Modules

All new modules live in `src/lib/eval/` and accept the same `Ai` interface.

#### 3.1.1 assertion-grader.ts

**Purpose**: Grade each boolean assertion against the skill output via LLM.

```
INPUT:  skillOutput: string, assertions: Assertion[], ai: Ai
OUTPUT: AssertionResult[]

Where:
  Assertion       = { id: string, text: string, type: "boolean" }
  AssertionResult = { assertionId: string, assertionText: string, pass: boolean, reasoning: string }
```

**LLM strategy**: One LLM call per test case with ALL assertions in the prompt. The model returns a JSON array of `{ id, pass, reasoning }` for each assertion. This batches assertions to minimize LLM calls (N assertions = 1 call, not N calls).

**System prompt**: Instruct the model to evaluate each assertion independently against the provided output. Return structured JSON. If the model returns malformed JSON, fall back to per-assertion individual calls.

**Error handling**: If the batch call fails or returns unparseable output, retry once. If still failed, mark all assertions as `pass: false` with reasoning `"Grading error"`.

#### 3.1.2 rubric-scorer.ts

**Purpose**: Score an output on Content (1-5) and Structure (1-5).

```
INPUT:  output: string, prompt: string, ai: Ai
OUTPUT: RubricScore = { contentScore: number, structureScore: number }
```

**LLM strategy**: One call per output. Two calls total per test case (skill output + baseline output). The prompt includes the rubric definitions:

- **Content (1-5)**: 1=irrelevant/wrong, 2=partially relevant, 3=adequate, 4=thorough+accurate, 5=exceptional depth+correctness
- **Structure (1-5)**: 1=unreadable, 2=poor organization, 3=adequate, 4=well-structured, 5=exemplary formatting+flow

**Clamping**: Scores outside 1-5 are clamped. Non-numeric responses default to 3.

#### 3.1.3 variance-analyzer.ts

**Purpose**: Compute per-assertion mean/stddev across N runs, flag flaky and non-discriminating assertions.

```
INPUT:  multiRunResults: AssertionResult[][] (N runs, each with same assertions)
OUTPUT: VarianceData = {
  perAssertion: VarianceEntry[],
  totalRuns: number
}

Where:
  VarianceEntry = {
    assertionId: string,
    mean: number,       // 0.0-1.0 (mean pass rate)
    stddev: number,     // standard deviation
    flaky: boolean,     // stddev > 0.3
    nonDiscriminating: boolean  // mean === 1.0 across ALL test cases
  }
```

**nonDiscriminating detection**: An assertion is non-discriminating if it passes in ALL runs across ALL test cases. This requires the analyzer to receive data for all test cases, not just one. The engine collects all per-case results first, then calls the analyzer with the full dataset.

#### 3.1.4 verdict-v2.ts

**Purpose**: Compute V2 verdict from assertion pass rate and rubric delta.

```
INPUT:  assertionPassRate: number, skillRubricAvg: number, baselineRubricAvg: number
OUTPUT: EvalVerdict

Logic:
  assertionPassRate >= 0.80 AND skillRubricAvg > baselineRubricAvg + 1  => EFFECTIVE
  assertionPassRate >= 0.60 AND skillRubricAvg > baselineRubricAvg      => MARGINAL
  assertionPassRate >= 0.40                                              => INEFFECTIVE
  assertionPassRate <  0.40                                              => DEGRADING
```

This is a pure function with no LLM calls.

### 3.2 Modified Modules

#### 3.2.1 types.ts — Extended Types

New types added (V1 types preserved):

```
Assertion           { id, text, type: "boolean" }
AssertionResult     { assertionId, assertionText, pass, reasoning }
RubricScore         { contentScore, structureScore }
VarianceEntry       { assertionId, mean, stddev, flaky, nonDiscriminating }
VarianceData        { perAssertion: VarianceEntry[], totalRuns }

EvalCaseResultV2 extends EvalCaseResult {
  assertionResults?: AssertionResult[]
  skillContentScore?: number
  skillStructureScore?: number
  baselineContentScore?: number
  baselineStructureScore?: number
}

EvalRunResultV2 extends EvalRunResult {
  methodologyVersion: 2
  assertionPassRate?: number
  skillRubricAvg?: number
  baselineRubricAvg?: number
  varianceData?: VarianceData
  runCountPerCase?: number
  cases: EvalCaseResultV2[]
}
```

The `EvalRunResult` union: `EvalRunResult | EvalRunResultV2` -- detected via `methodologyVersion`.

#### 3.2.2 prompt-generator.ts — Enhanced (V2)

New capability: parse `## Evaluations` section (evals.json format) in addition to existing `## Test Cases`.

**Priority order**:
1. `## Evaluations` section (structured assertions inline) -- parse directly
2. `## Test Cases` with `Prompt:` / `Expected:` pairs -- convert `Expected` to assertions via LLM
3. Full auto-generation from skill description -- generate both prompts AND assertions

**Output change**: `TestPrompt` gains an optional `assertions?: Assertion[]` field. When assertions are present, the V2 engine uses them. When absent, the engine falls back to V1 holistic judging.

#### 3.2.3 eval-engine.ts — KEPT (V1 path)

The existing `runQualityEval` function is KEPT UNCHANGED. It becomes the V1 code path.

#### 3.2.4 eval-engine-v2.ts — New Orchestrator

A new `runQualityEvalV2` function that:
1. Calls the enhanced prompt generator (with assertions)
2. For each test case, loops N times (trigger-based):
   - Runs comparator (reused)
   - Runs assertion grader
   - Runs rubric scorer on both outputs
3. Aggregates multi-run data via variance analyzer
4. Computes V2 verdict
5. Returns `EvalRunResultV2`

The consumer decides V1 vs V2 based on whether assertions are available.

#### 3.2.5 eval-store.ts — Extended

`storeEvalRun` gains logic to persist V2 fields when `methodologyVersion === 2`:
- On `EvalRun`: `methodologyVersion`, `assertionPassRate`, `skillRubricAvg`, `baselineRubricAvg`, `varianceData`, `runCountPerCase`
- On `EvalCase`: `assertionResults`, `skillContentScore`, `skillStructureScore`, `baselineContentScore`, `baselineStructureScore`

KV payload also gains V2 summary fields.

#### 3.2.6 eval-consumer.ts — Extended

After resolving skill metadata and choosing the AI adapter, the consumer:
1. Calls the enhanced prompt generator
2. If assertions are available: `runQualityEvalV2()`
3. Else: `runQualityEval()` (V1 fallback)
4. Passes `trigger` through to determine N (run count)

New: handles `REVERIFY` trigger type.

#### 3.2.7 eval-types.ts — Extended

`EvalQueueMessage` gains optional `methodologyVersion?: number` field. The consumer reads it to force V2 when set.

### 3.3 New API Endpoint

#### POST /api/v1/admin/eval/reverify

```
Auth: SUPER_ADMIN or internal key
Body: {} (no params needed)
Response: { queued: number, totalSkills: number }
```

Implementation:
1. Query all non-deprecated published skills
2. Enqueue each to `EVAL_QUEUE` with `{ trigger: "REVERIFY", methodologyVersion: 2 }`
3. Batch in groups of 25 (CF queue limit)
4. Return count

---

## 4. Schema Changes

### 4.1 EvalRun — New Nullable Columns

```
EvalRun (existing columns unchanged)
────────────────────────────────────────────────────
NEW COLUMNS:
methodologyVersion  Int?     /// null = V1, 2 = V2
assertionPassRate   Float?   /// 0.0-1.0, V2 only
skillRubricAvg      Float?   /// mean of (content+structure)/2 across cases
baselineRubricAvg   Float?   /// same for baseline
varianceData        Json?    /// { perAssertion: [...], totalRuns }
runCountPerCase     Int?     /// N runs per test case (1, 3, or 5)
```

### 4.2 EvalCase — New Nullable Columns

```
EvalCase (existing columns unchanged)
────────────────────────────────────────────────────
NEW COLUMNS:
assertionResults       Json?   /// [{ assertionId, assertionText, pass, reasoning }]
skillContentScore      Int?    /// 1-5 rubric
skillStructureScore    Int?    /// 1-5 rubric
baselineContentScore   Int?    /// 1-5 rubric
baselineStructureScore Int?    /// 1-5 rubric
```

### 4.3 EvalTrigger Enum — Extended

```
enum EvalTrigger {
  SUBMISSION
  REGRESSION
  MANUAL
  REVERIFY     /// NEW — batch re-eval with V2 methodology
}
```

### 4.4 Migration Strategy

- Single Prisma migration: `ALTER TABLE` with `ADD COLUMN ... NULL` for each new column
- `ALTER TYPE "EvalTrigger" ADD VALUE 'REVERIFY'`
- No data backfill required -- V1 rows keep nulls in new columns
- Zero downtime: nullable columns with no defaults do not lock the table

---

## 5. Data Flow

### 5.1 V2 Eval Pipeline (Single Test Case, Single Run)

```
TestPrompt + Assertion[]
        │
        ▼
   comparator.runComparator(prompt, skillContent, ai)
        │
        ├─► skillOutput
        └─► baselineOutput
                │
      ┌─────────┼──────────────────────────┐
      │         │                          │
      ▼         ▼                          ▼
 assertion    rubric-scorer            rubric-scorer
 -grader      .scoreRubric             .scoreRubric
 .grade()     (skillOutput)            (baselineOutput)
      │         │                          │
      ▼         ▼                          ▼
 Assertion   RubricScore              RubricScore
 Result[]    {content,structure}       {content,structure}
```

### 5.2 Multi-Run Aggregation (N > 1)

```
Run 1:  [AssertionResult[], RubricScore, RubricScore]
Run 2:  [AssertionResult[], RubricScore, RubricScore]
...
Run N:  [AssertionResult[], RubricScore, RubricScore]
        │
        ▼
   variance-analyzer.analyze(allRuns)
        │
        ▼
   VarianceData { perAssertion: [...], totalRuns: N }
        │
        ▼
   Aggregate: mean assertionPassRate, mean rubric scores
        │
        ▼
   verdict-v2.computeV2Verdict(assertionPassRate, skillRubricAvg, baselineRubricAvg)
        │
        ▼
   EvalRunResultV2
```

### 5.3 V1/V2 Routing in Consumer

```
eval-consumer
    │
    ├─ resolve skill + fetch SKILL.md
    │
    ├─ call prompt-generator (enhanced)
    │    │
    │    ├─ assertions found?  ─► YES ─► runQualityEvalV2()  (V2 path)
    │    │                                  │
    │    └─ no assertions      ─► NO  ─► runQualityEval()    (V1 path, unchanged)
    │
    ├─ OR: message.methodologyVersion === 2?  ─► force V2 (auto-generate assertions)
    │
    └─ storeEvalRun() (handles both V1 and V2 shapes)
```

---

## 6. LLM Call Budget

Each eval involves multiple LLM calls. Budget analysis per test case per run:

| Call | Count | Purpose |
|------|-------|---------|
| Comparator: skill output | 1 | Generate with-skill response |
| Comparator: baseline output | 1 | Generate without-skill response |
| Assertion grader | 1 | Grade all assertions (batched) |
| Rubric scorer: skill | 1 | Score skill output |
| Rubric scorer: baseline | 1 | Score baseline output |
| **Total per case per run** | **5** | |

For a REVERIFY run with 5 test cases and N=5 runs:
- 5 cases x 5 runs x 5 calls = **125 LLM calls**
- Plus prompt generation: ~1-3 calls
- Estimated wall time at ~3s/call (CF AI): ~6-7 minutes per skill

For SUBMISSION with 5 test cases and N=1:
- 5 cases x 1 run x 5 calls = **25 LLM calls**
- Estimated wall time: ~75 seconds per skill

This fits within CF Queue's 15-minute per-message timeout.

---

## 7. Phased Implementation Plan

### Phase 1: Type Foundation + DB Schema

**Files touched**: `types.ts`, `prisma/schema.prisma`

1. Add all new TypeScript types to `types.ts` (Assertion, AssertionResult, RubricScore, VarianceData, V2 result types)
2. Add `REVERIFY` to EvalTrigger enum in Prisma schema
3. Add nullable columns to EvalRun and EvalCase in Prisma schema
4. Create and apply Prisma migration
5. Verify existing V1 tests still pass (no breaking changes)

### Phase 2: Assertion Grader + Rubric Scorer

**New files**: `assertion-grader.ts`, `rubric-scorer.ts`, `verdict-v2.ts`

1. Implement `assertion-grader.ts` with batch LLM grading
2. Implement `rubric-scorer.ts` with Content/Structure scoring
3. Implement `verdict-v2.ts` with the four-tier logic
4. Unit tests for all three modules (mock `Ai` interface)

### Phase 3: Enhanced Prompt Generator

**Files touched**: `prompt-generator.ts`

1. Add `## Evaluations` section parser (evals.json format)
2. Add LLM-based assertion conversion from `Expected:` values
3. Add full auto-generation path (prompts + assertions from skill description)
4. Return `Assertion[]` on `TestPrompt` type
5. Unit tests for all three source priority paths

### Phase 4: V2 Eval Engine + Variance Analyzer

**New files**: `eval-engine-v2.ts`, `variance-analyzer.ts`

1. Implement `variance-analyzer.ts` (mean, stddev, flaky, nonDiscriminating flags)
2. Implement `eval-engine-v2.ts` orchestrator:
   - Multi-run loop (N from trigger)
   - Calls comparator, assertion grader, rubric scorer per run
   - Aggregates via variance analyzer
   - Computes V2 verdict
   - Returns `EvalRunResultV2`
3. Unit tests with mocked AI for deterministic multi-run scenarios

### Phase 5: Queue/Consumer/Cron/API Wiring

**Files touched**: `eval-consumer.ts`, `eval-store.ts`, `eval-types.ts`, `eval-regression.ts`
**New files**: `src/app/api/v1/admin/eval/reverify/route.ts`

1. Extend `eval-store.ts` to persist V2 fields (conditional on methodologyVersion)
2. Extend `eval-consumer.ts` with V1/V2 routing logic
3. Extend `eval-types.ts` with `methodologyVersion` on queue message
4. Update `eval-regression.ts` cron to use V2 when assertions available
5. Create `/api/v1/admin/eval/reverify` endpoint
6. Integration tests for the full pipeline (consumer + store + V2 engine)

### Phase 6: Documentation

1. Update eval pipeline living docs in `.specweave/docs/internal/specs/`
2. Document V2 methodology, verdict thresholds, and LLM call budget
3. Document reverify admin workflow

---

## 8. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM returns malformed JSON from assertion grader | Assertions all marked failed | Batch fallback: retry once, then individual calls, then default to fail |
| Rubric scores outside 1-5 | Invalid data in DB | Clamp to 1-5 in rubric-scorer; DB accepts Int (no constraint needed) |
| REVERIFY overwhelms queue | Queue backpressure | Batch enqueue in groups of 25; CF Queue has built-in backpressure |
| Multi-run wall time exceeds queue timeout | Message retried infinitely | REVERIFY N=5 with 5 cases = ~7 min, well under 15-min CF limit |
| V1 to V2 migration breaks existing queries | Admin UI/API returns null fields | All new columns nullable; no API response format changes (out of scope) |
| nonDiscriminating detection requires cross-case data | Incorrect flagging if done per-case | Variance analyzer receives all test case data at once (engine aggregates before calling) |

---

## 9. Testing Strategy

### Unit Tests (per module)

- `assertion-grader.test.ts` -- mock AI, verify pass/fail/reasoning, malformed JSON fallback
- `rubric-scorer.test.ts` -- mock AI, verify score clamping, default behavior
- `verdict-v2.test.ts` -- pure function, all four verdict thresholds plus boundary cases
- `variance-analyzer.test.ts` -- deterministic runs, verify mean/stddev/flaky/nonDiscriminating
- `eval-engine-v2.test.ts` -- mock all sub-modules, verify orchestration and N-run loop
- `prompt-generator.test.ts` -- evals.json parsing, Expected-to-assertion conversion, auto-gen

### Integration Tests

- `eval-consumer.test.ts` -- V1/V2 routing, REVERIFY trigger handling
- `eval-store.test.ts` -- V2 field persistence, V1 backward compat

---

## 10. File Inventory

### New Files

| File | Module | Phase |
|------|--------|-------|
| `src/lib/eval/assertion-grader.ts` | Assertion grading | 2 |
| `src/lib/eval/rubric-scorer.ts` | Rubric scoring | 2 |
| `src/lib/eval/verdict-v2.ts` | V2 verdict logic | 2 |
| `src/lib/eval/variance-analyzer.ts` | Multi-run analysis | 4 |
| `src/lib/eval/eval-engine-v2.ts` | V2 orchestrator | 4 |
| `src/app/api/v1/admin/eval/reverify/route.ts` | Reverify endpoint | 5 |

### Modified Files

| File | Change | Phase |
|------|--------|-------|
| `src/lib/eval/types.ts` | Add V2 types | 1 |
| `prisma/schema.prisma` | Nullable columns, REVERIFY enum | 1 |
| `src/lib/eval/prompt-generator.ts` | evals.json support, assertion gen | 3 |
| `src/lib/eval/eval-store.ts` | V2 field persistence | 5 |
| `src/lib/queue/eval-consumer.ts` | V1/V2 routing | 5 |
| `src/lib/queue/eval-types.ts` | methodologyVersion field | 5 |
| `src/lib/cron/eval-regression.ts` | V2 support | 5 |

### Unchanged Files

| File | Reason |
|------|--------|
| `src/lib/eval/comparator.ts` | Reused as-is by both V1 and V2 |
| `src/lib/eval/judge.ts` | V1-only; still used by V1 fallback path |
| `src/lib/eval/claude-adapter.ts` | Implements Ai interface; no changes needed |
| `src/lib/eval/usefulness.ts` | V1 metric; out of scope for V2 |
| `src/lib/eval/eval-engine.ts` | V1 engine preserved for fallback |
