# AC traceability with honest verification state

## Problem

An acceptance criterion shows as met on a thread's plan card once every task that cites it is done or skipped. Evidence and the verify report are ignored, a skipped task counts as proof, an AC no task cites looks merely "open", and nothing links an AC back to its user story. The CLI's verify report (`reports/verify.json`) carries only `acs: {total, done}`, so no reader can tell which AC passed, how, or through which tasks. Users read the checkmark as "tested" when it means "declared".

## Scope

In: per-AC detail in the CLI verify report (`src/core/tasks/verify-runner.ts`), the app reader (`apps/server/src/project/ThreadIncrementProgress.ts`, `apps/server/src/mods/SpecweaveProgress.ts`), the criterion contract, and the plan card. Out: changing the CLI close gate (an AC still counts done exactly as before), tracker sync.

## Acceptance Criteria

- [ ] AC-01: `specweave verify` writes `acs.items` with each AC's id, done flag, how it was decided (checkbox, ledger, none) and the tasks that cite it; `acs.total` and `acs.done` are unchanged
- [ ] AC-02: The app gives each AC one state: verified (citing tasks done with evidence and the latest verify passed after them), evidenced (done with evidence, verify missing, failed or older), declared (only ticked or a legacy status), skipped, open, uncovered (no task cites it); `met` stays for older clients
- [ ] AC-03: Each AC lists the tasks that cite it and its user story when the spec names one; each task lists its ACs (many-to-many)
- [ ] AC-04: The plan card shows the state, the covering tasks and the uncovered count, and never shows a checkmark for declared or skipped ACs
- [ ] AC-05: Increments without a verify report, without user stories, or with legacy `tasks.md` still render, with states derived only from what exists

## Approach

The CLI adds per-AC rows alongside its existing counts. The app derives state from the ledger evidence it already folds plus the verify report's `ok` and `ranAt`, comparing `ranAt` with the newest task completion. Story ids come from `AC-USn-NN` ids or the nearest `### US-NNN` heading above the AC.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Keep the CLI close gate unchanged; traceability is reported, not enforced (no existing increment stops closing)
- D-02 A skipped task never makes an AC verified; an AC whose only citing tasks are skipped shows as skipped
### Open
- none

## Tasks

### T-01 Per-AC items in verify.json
- AC: AC-01 | Files: src/core/tasks/verify-runner.ts, tests/unit/core/tasks/verify-ac-items.test.ts | Test: npx vitest run tests/unit/core/tasks/verify-ac-items.test.ts
### T-02 App criterion states, stories and covering tasks
- AC: AC-02, AC-03, AC-05 | Files: packages/contracts/src/threadIncrementProgress.ts, apps/server/src/mods/SpecweaveProgress.ts, apps/server/src/project/ThreadIncrementProgress.ts, apps/server/src/project/ThreadIncrementProgress.test.ts | Test: vp test run apps/server/src/project/ThreadIncrementProgress.test.ts
### T-03 Plan card shows traceability
- AC: AC-04 | Files: apps/web/src/components/chat/ThreadPlanCard.tsx | Test: headless plan card screenshot
### T-04 Verify and close 0962
