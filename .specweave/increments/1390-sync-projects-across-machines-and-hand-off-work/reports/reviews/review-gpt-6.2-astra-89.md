<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=069f4dad1c04428c74cb985164bcf41a650f43b1 at=2026-11-19T19:24:29.083Z -->
# Review: 1390 T-12, Hand off dialog selection
Verdict: fix first
Reviewer context: fresh session; Git objects at `069f4dad1c04428c74cb985164bcf41a650f43b1`. CI green per requester; no tests run.

## [high] Unticking one thread can add a different thread to the batch

`apps/web/src/components/handoff/handOffMachineRows.ts:148-151` recalculates the first 100 on every change and treats every missing override as true. With 101 eligible rows, row 101 opens unchecked. Untick row 1: row 101 becomes checked without the user choosing it, the limit notice disappears, and the next successful preflight admits it to the manual send at `apps/web/src/components/handoff/HandOffMachineDialog.tsx:663-676`. The submit path does not truncate visible ticks; the error is the substitution before submit. Initialize the checked IDs once and leave the slot empty until the user fills it.

## [high] A pending approval can arrive before a selected thread is interrupted

`apps/web/src/components/handoff/handOffMachineRows.ts:100-106` checks the window's current flags. After submit, the server handles the batch sequentially (`apps/server/src/handoff/HandoffMoves.ts:748-758`). If the second thread asks for approval while the first is moving, it must now stay. The runner reads the second thread again after taking the hold, but checks only automatic-start conditions before interrupting its active run (`apps/server/src/handoff/HandoffTransferRunner.ts:887-918`). Recheck stay conditions on the source before holding and immediately before interrupting; release without interrupting if the thread now needs an answer.

## [high] Preflight can send checkpoints for threads outside the selection

`apps/web/src/components/handoff/HandOffMachineDialog.tsx:542-555` joins selected IDs with commas, then splits that string for preflight. The thread ID contract is a trimmed nonempty string, not a comma-free identifier (`packages/contracts/src/baseSchemas.ts:314`). A comma inside a valid ID changes which threads are checked. Where the component IDs also identify real threads, the server prepares and replicates those threads' checkpoints, even if they are unchecked or outside the project scope (`apps/server/src/handoff/HandoffMoves.ts:819-825` and `:503-512`). This is a wrong-thread transfer during preflight, not a claim that the final submit splits IDs. Pass the original ID array unchanged.

## Follow-ups

With current, complete facts, the classifier filters by machine and project and excludes archived, subagent, coordinator, continued and fenced rows; idle settled rows are omitted. Missing handoff snapshot data is treated as an empty map rather than unknown (`apps/web/src/components/handoff/handOffMachineRows.ts:82-96`), so the window alone cannot guarantee a continued or fenced row never appears ticked. A regression test should cover snapshot loading as well as a row becoming ineligible after selection.
