<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=6dd1443b8f480a175302ea20a5933a110dec7488 at=2026-11-19T20:38:57.554Z -->
# Review: 1390 Hand off plan RPC and dialog
Verdict: fix first
Reviewer context: fresh session; 38 changed files; Git objects at `6dd1443b8f480a175302ea20a5933a110dec7488`. No tests run, as requested. Citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

## [high] `apps/server/src/handoff/handoffPlanRead.ts:427-435` returns usage for a project outside the peer grant

For a linked but ungranted project, `apps/server/src/handoff/handoffPreflight.ts:98-99` records a grant failure naming the project. `apps/server/src/handoff/handoffPlan.ts:205-206,241-247,287-290` stops for a missing project or skips a denied account, but can return account evidence alongside the project denial when the account is otherwise allowed. `apps/server/src/handoff/handoffPlan.ts:365` preserves both. The new RPC copies the provider display name, account relationship and percentage into the view without checking the failure. No raw credentials are needed or returned. Short-circuit the project denial before inspecting tracks or sign-ins and return a non-identifying refusal with no evidence.

## [high] `apps/server/src/handoff/handoffPlanRead.ts:320-337` writes to the source repository while reading a plan

The dialog requests measurement for the selected destination at `apps/web/src/components/handoff/HandOffMachineDialog.tsx:603-606`. `apps/server/src/handoff/handoffPlan.ts:440-445` calls `writeCheckpoint` without a private store. `apps/server/src/handoff/checkpointGit.ts:147-152,347-365` writes a Git commit and ref to the actual repository. Removing the ref at `apps/server/src/handoff/handoffPlan.ts:487-491` does not remove the objects. No thread is held or moved, but opening the dialog is not read-only. Isolate measurement from the source object store and refs.

## Selection

`apps/web/src/components/handoff/handOffMachineRows.ts:146-149,185-190` excludes Stays and non-tickable rows from the loaded plan. That protection is not unconditional: `apps/web/src/components/handoff/HandOffMachineDialog.tsx:572-587,602-612,753-778` permits client fallback rows or a cached unmeasured plan while a measurement is pending; submission does not require the measured plan. A previously checked thread can be submitted before its over-limit Stays result arrives. This is a submission gap, not proof the server completes the move.

`apps/web/src/components/handoff/HandoffResults.tsx:180-185` selects the first reachable destination without usage evidence; the dialog uses that fallback at `apps/web/src/components/handoff/HandOffMachineDialog.tsx:572`. A same-account or unknown destination can therefore be preselected without a target click. A move still requires manual submission.

## RPC gate

Both sides require `orchestration:operate`: `apps/web/src/components/handoff/HandOffMachineDialog.tsx:564-565,600` and `packages/contracts/src/clientRpcPermissions.ts:141`. The refusal test at `apps/server/src/handoff/handoffPlanRead.test.ts:260-289` asserts that a read-only session gets `EnvironmentAuthorizationError` and the handler is never called. This scope check does not repair the peer's project-grant disclosure.
