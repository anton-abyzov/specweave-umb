# Late delegated results reach the parent: reproduce first, then fix

## Problem

A worker's result is the product of a delegated task. The upstream triage of November 14, 2026 (`.specweave/increments/1346-t3-code-changes-since-november-2/reports/2026-11-15-t3-code-triage-november-2-to-november-14-2026-bb97f4-af68df.md`, row R16) found four upstream fixes for results that never reach the parent, and our completion-delivery path has the same shape:

- A result that arrives after the parent went idle does not wake it. `apps/server/src/mcp/OrchestratorMcpService.ts:2356` picks `observedByRunId` from the latest active run of any provider.
- A sibling's wake is lost when the parent is steered or interrupted, or when its queue row is removed (`apps/server/src/orchestration-v2/Orchestrator.ts:13070`).

The reviewer moved this out of "measure first" because lost worker results are the costliest failure in a fleet. `Orchestrator.ts` is 13,932 lines and has diverged, so nothing here ports line for line.

Upstream commits: `36d0dcbf55`, `8d54c8b1a7`, `4dff7de3f9`, `6b96956c30`.

## Scope

In: one reproducing test per loss case against our orchestrator, then the smallest fix that makes each pass. Out: any redesign of completion delivery, the queue-order change (R5), and the delegate wait timeout (1348 AC-04).

## Acceptance Criteria

- [ ] AC-01: `reports/cases.md` lists each loss case from the four upstream commits, says whether it reproduces in our tree, and names its test. A case that does not reproduce keeps its test as a regression guard.
- [ ] AC-02: A delegated result that completes after the parent's run ended wakes the idle parent with that result.
- [ ] AC-03: When two children finish and the parent is steered between them, both results are delivered.
- [ ] AC-04: When the parent is interrupted while a child's wake is queued, the wake is delivered on the next run and is not dropped.
- [ ] AC-05: When a queued wake's row is removed, the result stays readable through `task_status` and is delivered once, never twice.
- [ ] AC-06: Each test in AC-02 to AC-05 fails on the pre-fix code (recorded in `reports/red-green.md`), and the existing orchestration suites stay green.
- [ ] AC-07: The PR has green CI and a ship verdict from another model family at its merged head; the public repository gains no mention of the upstream project.

## Approach

Test first, in this order: write the four reproducing tests with the existing orchestrator test fixtures, run them red, commit them as the first commit of the branch, then fix. The fix follows our delivery design (receipts and `observedByRunId`), not upstream's structure.

Runs after 1348's delegate PR, which touches `OrchestratorMcpService.ts` too. Merges and releases with 1348 if ready; it is not a permission change.

Risk: high. A wrong fix delivers a result twice or wakes the wrong run. The double-delivery assertion in AC-05 is the guard.

## Review
- Reviewer: meta
- Depth: deep
- Required: yes

## Decisions

### Asked
- D-01 Own increment, tests first → yes (user, November 14, 2026).
### Defaulted (change any before sw-do)
- D-02 A case that needs more than a local change to `Orchestrator.ts` is recorded in `reports/cases.md` with its failing test marked skipped and a reason, and reported, instead of a broad rewrite.
### Open
- none

- D-90 Added from 1474 (November 25, 2026): the upstream review found two more late-result losses for this increment to cover when it starts: settling a thread cancels automatic queued wakes, so delegated results are lost (`2c3d3b4501`, our `apps/server/src/orchestration-v2/Orchestrator.ts:3604`), and its companion at `:13879` (`d4d54658f9`). Lane notes: 1474 `reports/lanes/a3-server.md`.

## Tasks

### T-01 Reproduce each loss case
- AC: AC-01, AC-06 | Files: .specweave/increments/1349-late-delegated-results-reach-the-parent/reports/cases.md, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.lateDelegatedResults.test.ts | Test: test -s .specweave/increments/1349-late-delegated-results-reach-the-parent/reports/cases.md

### T-02 Fix delivery for late results and surviving wakes
- AC: AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/orchestration-v2/Orchestrator.lateDelegatedResults

### T-03 Review, merge, verify and close 1349
- AC: AC-07 | Files: .specweave/increments/1349-late-delegated-results-reach-the-parent/ | Test: specweave verify 1349
