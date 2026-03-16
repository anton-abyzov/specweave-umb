---
increment: 0442-eval-system-rework
title: Rework Skill Evaluation System
type: feature
priority: P1
status: completed
created: 2026-03-06T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Rework Skill Evaluation System

## Problem Statement

The current vskill-platform eval system uses blind A/B comparison (with-skill vs without-skill) judged by a single LLM call that returns a holistic 0-100 score and a verdict. This approach has three critical weaknesses:

1. **No assertion granularity** -- there is no way to know WHICH claims a skill fails to deliver on. The judge produces a single score with free-text reasoning, making it impossible to pinpoint specific quality gaps.
2. **No run-to-run stability signal** -- each eval runs once, so flaky LLM outputs or non-discriminating test cases are invisible. A skill that passes 60% of the time looks identical to one that passes 100%.
3. **No structured quality dimensions** -- the judge prompt mentions Relevance, Depth, Structure, Specificity, and Correctness but the model returns a single score, collapsing all dimensions into one opaque number.

Anthropic's skill-creator patterns demonstrate a superior methodology: assertion-based grading with structured rubrics and multi-run variance analysis. This increment brings that methodology to the platform's automated eval pipeline.

## Goals

- Replace holistic judging with per-assertion PASS/FAIL grading with evidence
- Add rubric scoring (Content 1-5, Structure 1-5) for both skill and baseline outputs
- Run each test case N times to detect flaky tests and compute confidence intervals
- Support the existing `evals.json` assertion format and auto-generate assertions from SKILL.md
- Provide a re-verification queue to batch re-evaluate all published skills under the new methodology
- Maintain full backward compatibility with V1 eval data (nullable new columns, V1 verdict logic preserved)

## User Stories

### US-001: Assertion-Based Grading (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** each test case graded against specific verifiable assertions (PASS/FAIL with evidence)
**So that** I can pinpoint exactly which claims a skill fails to deliver on

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a test case with N assertions, when the eval runs, then the LLM judge returns `{ pass: boolean, reasoning: string }` for each assertion individually
- [x] **AC-US1-02**: Given a test case with 3 assertions where 2 pass and 1 fails, when the assertion results are aggregated, then the case `assertionPassRate` equals 0.67
- [x] **AC-US1-03**: Given an assertion result, when stored in the DB, then the `EvalCase.assertionResults` JSON column contains an array of `{ assertionId, assertionText, pass, reasoning }` objects
- [x] **AC-US1-04**: Given an eval run with multiple cases, when the run completes, then the `EvalRun` record includes an `assertionPassRate` field computed as total passed / total assertions across all cases

---

### US-002: Rubric Scoring (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** each output (skill and baseline) scored on Content (1-5) and Structure (1-5) rubric dimensions
**So that** I have structured quality signals beyond a single opaque score

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a skill output and a baseline output, when the rubric scorer runs, then it returns `{ contentScore: 1-5, structureScore: 1-5 }` for each output independently
- [x] **AC-US2-02**: Given rubric scores, when stored, then `EvalCase` has nullable columns `skillContentScore`, `skillStructureScore`, `baselineContentScore`, `baselineStructureScore` (all Int, 1-5)
- [x] **AC-US2-03**: Given an eval run, when aggregating rubric scores, then `EvalRun` stores `skillRubricAvg` and `baselineRubricAvg` as the mean of (contentScore + structureScore) / 2 across all cases
- [x] **AC-US2-04**: The existing `qualityScore` (0-100) and `baselineScore` (0-100) columns remain populated for backward compatibility with V1 eval runs

---

### US-003: V2 Verdict Logic (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the verdict computed from assertion pass rate (primary) and rubric delta (secondary)
**So that** eval verdicts reflect both "meets its own claims" and "better than no skill"

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `assertionPassRate >= 0.80` AND skill rubric overall > baseline rubric overall + 1, when computing verdict, then the result is `EFFECTIVE`
- [x] **AC-US3-02**: Given `assertionPassRate >= 0.60` AND skill rubric > baseline rubric, when computing verdict, then the result is `MARGINAL`
- [x] **AC-US3-03**: Given `assertionPassRate >= 0.40` (but not meeting EFFECTIVE or MARGINAL thresholds), when computing verdict, then the result is `INEFFECTIVE`
- [x] **AC-US3-04**: Given `assertionPassRate < 0.40`, when computing verdict, then the result is `DEGRADING`
- [x] **AC-US3-05**: Given an eval run with `methodologyVersion` null (V1), when displaying results, then the V1 verdict logic (deltaScore thresholds) is used unchanged
- [x] **AC-US3-06**: Given an eval run, when stored, then `EvalRun.methodologyVersion` is set to `2` for all new V2 runs

---

### US-004: Multi-Run Variance Analysis (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** each test case run N times with mean/stddev computed per assertion
**So that** I can detect flaky tests and non-discriminating assertions

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given trigger `SUBMISSION`, when eval runs, then each test case executes 1 time (N=1, fast path)
- [x] **AC-US4-02**: Given trigger `REGRESSION`, when eval runs, then each test case executes 3 times (N=3)
- [x] **AC-US4-03**: Given trigger `REVERIFY`, when eval runs, then each test case executes 5 times (N=5)
- [x] **AC-US4-04**: Given N runs of a test case, when aggregating, then the system computes mean and stddev of each assertion's pass rate (1=pass, 0=fail across runs)
- [x] **AC-US4-05**: Given an assertion with pass rate stddev > 0.3 across runs, when the eval completes, then the assertion is flagged as `flaky: true` in the variance data
- [x] **AC-US4-06**: Given an assertion that passes in ALL runs across ALL test cases, when the eval completes, then the assertion is flagged as `nonDiscriminating: true`
- [x] **AC-US4-07**: Given multi-run data, when stored, then `EvalRun.varianceData` JSON column contains `{ perAssertion: [{ assertionId, mean, stddev, flaky, nonDiscriminating }], totalRuns }`

---

### US-005: Enhanced Prompt and Assertion Generation (P2)
**Project**: vskill-platform

**As a** platform operator
**I want** the eval pipeline to support structured assertions from `evals.json` format and auto-generate assertions when none exist
**So that** every skill can be evaluated with assertion-based grading regardless of author-provided test cases

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a SKILL.md with an `## Evaluations` section containing evals.json-format data, when generating test cases, then the system parses and uses the structured assertions directly
- [x] **AC-US5-02**: Given a SKILL.md with a `## Test Cases` section containing `Prompt:` / `Expected:` pairs, when generating test cases, then the system converts each `Expected` value into assertions via an LLM call that produces `{ id, text, type: "boolean" }[]`
- [x] **AC-US5-03**: Given a SKILL.md with neither `## Evaluations` nor `## Test Cases`, when generating test cases, then the system fully auto-generates prompts AND assertions via LLM from the skill description and content
- [x] **AC-US5-04**: All generated assertions use `type: "boolean"` exclusively -- no regex or keyword matching types
- [x] **AC-US5-05**: Auto-generated assertions are NOT written back to the skill repository -- they exist only in the eval run data

---

### US-006: Re-Verification Queue (P2)
**Project**: vskill-platform

**As a** platform admin
**I want** a `/api/v1/admin/eval/reverify` endpoint that enqueues all published skills for re-evaluation with V2 methodology
**So that** I can batch-validate the entire skill catalog under the new grading system

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given a POST to `/api/v1/admin/eval/reverify`, when authenticated as SUPER_ADMIN or internal, then all non-deprecated published skills are enqueued to `EVAL_QUEUE` with `trigger: "REVERIFY"` and `methodologyVersion: 2`
- [x] **AC-US6-02**: The existing `EVAL_QUEUE` is reused -- no new queue is created
- [x] **AC-US6-03**: The `EvalTrigger` Prisma enum is extended with a `REVERIFY` value
- [x] **AC-US6-04**: Given a reverify run, when processing, then the eval consumer uses N=5 runs per test case
- [x] **AC-US6-05**: No auto-deprecation occurs -- skills with DEGRADING verdicts are flagged but remain published; admins decide next steps
- [x] **AC-US6-06**: The endpoint returns `{ queued: number, totalSkills: number }` response confirming enqueue count

---

### US-007: Backward-Compatible Schema Extension (P1)
**Project**: vskill-platform

**As a** developer
**I want** the DB schema extended with new nullable columns on EvalRun and EvalCase
**So that** existing V1 data is preserved and new V2 fields coexist without breaking queries

**Acceptance Criteria**:
- [x] **AC-US7-01**: `EvalRun` gains nullable columns: `methodologyVersion` (Int, default null), `assertionPassRate` (Float, nullable), `skillRubricAvg` (Float, nullable), `baselineRubricAvg` (Float, nullable), `varianceData` (Json, nullable), `runCountPerCase` (Int, nullable)
- [x] **AC-US7-02**: `EvalCase` gains nullable columns: `assertionResults` (Json, nullable), `skillContentScore` (Int, nullable), `skillStructureScore` (Int, nullable), `baselineContentScore` (Int, nullable), `baselineStructureScore` (Int, nullable)
- [x] **AC-US7-03**: `EvalTrigger` enum gains the `REVERIFY` value
- [x] **AC-US7-04**: All existing V1 eval data is preserved unchanged after migration -- new columns are null for V1 rows
- [x] **AC-US7-05**: A Prisma migration is created and applied without data loss

## Functional Requirements

### FR-001: LLM-Based Assertion Grading
The assertion grader sends each assertion to the CF AI model (same `Ai` binding used by comparator/judge) with the skill output as context. The model returns `{ pass: boolean, reasoning: string }` per assertion. All assertions use `type: "boolean"` -- no regex/keyword matching.

### FR-002: Rubric Scorer
A new module (`rubric-scorer.ts`) evaluates both skill and baseline outputs on two dimensions: Content (1-5) and Structure (1-5). The scorer makes one LLM call per output, requesting JSON `{ contentScore: number, structureScore: number }`. Scores are integers clamped to 1-5.

### FR-003: Multi-Run Orchestration
The eval engine wraps each test case execution in a loop of N iterations (determined by trigger type). After all runs, it aggregates assertion pass rates per assertion, computes mean and stddev, and flags flaky/non-discriminating assertions.

### FR-004: Assertion Source Priority
1. `## Evaluations` section in SKILL.md (evals.json inline format) -- highest priority
2. `## Test Cases` section with Prompt/Expected pairs -- convert Expected to assertions via LLM
3. Fully auto-generated from skill description/content -- lowest priority

## Success Metrics

- All published skills can be re-evaluated with V2 methodology without errors
- Assertion-based verdicts produce more actionable feedback than V1 holistic scores (qualitative, validated by admin review)
- Flaky assertion detection identifies at least 1 non-discriminating assertion per 10 skills on average (validates the variance analysis is working)

## Out of Scope

- Admin UI changes for displaying V2 eval results (future increment)
- Auto-deprecation of DEGRADING skills
- Writing auto-generated assertions back to skill repositories
- Regex or keyword-based assertion matching (LLM-only for now)
- Changes to the public skill detail API response format
- Updating the eval editor admin page for V2 assertions

## Dependencies

- Existing `EVAL_QUEUE` Cloudflare Queue binding
- CF AI model (`@cf/meta/llama-4-scout-17b-16e-instruct`) via `Ai` binding
- Anthropic Claude API adapter (optional, used when `ANTHROPIC_API_KEY` is set)
- Prisma schema and migration tooling
- Existing eval admin endpoints (bulk, trigger, direct)

## Technical Notes

- The `Ai` interface (`ai.run(model, { messages })`) is the abstraction boundary -- both CF AI and the Claude adapter implement it. All new modules (assertion grader, rubric scorer) use this same interface.
- `assertionResults` and `varianceData` are stored as JSON columns rather than normalized tables to keep the schema flat and avoid join overhead on the hot eval read path.
- The V1 comparator (`comparator.ts`) is KEPT -- baseline comparison still runs. Rubric scoring is applied to BOTH outputs. Assertions are checked against skill output only.
- The eval engine detects methodology version at runtime: if assertions are available, run V2 pipeline; otherwise fall back to V1 holistic scoring.
