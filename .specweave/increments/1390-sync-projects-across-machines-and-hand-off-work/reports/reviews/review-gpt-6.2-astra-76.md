<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=4f75c508670dca16cca1346e1accc2d247da2f2b at=2026-11-19T17:43:19.263Z -->
SHIP
Verdict: ship

Reviewed `anton-abyzov/specwithcode#717` at `4f75c508670dca16cca1346e1accc2d247da2f2b` against `8720e49f` and the approved series ending at `9f4f13151`. Fresh session, Git objects only; no build or test run.

Commits 1, 2, 3 and 5 preserve the approved behavior. A missing capability or failed probe keeps a sent transfer fenced before either a takeover or a status request. A batch cannot fall through to legacy settlement; release still requires a definite no (`apps/server/src/handoff/HandoffTransferRunner.ts:394,553,590-636`). Folder replay probes the peer before sending fresh extras and never resends an interrupted journal entry (`apps/server/src/handoff/HandoffBatch.ts:458-471,1087-1125`). The receiver resolves the caller's granted project and eligible repository before applying folder work (`apps/server/src/handoff/HandoffBatch.ts:343-379`). The merged plan receiver is unchanged and still returns the target's confirmed evidence (`apps/server/src/handoff/handoffPlanReceiver.ts:204`).

Commit 10 extracts the same arrival calculation with the same checkpoint and `shouldResume` input; the revision rejection still precedes file placement (`apps/server/src/handoff/HandoffBatch.ts:168-173`, `apps/server/src/handoff/HandoffReceiver.ts:947-951`). Its only test change supplies the new receiver dependency to the retired-route fixture (`apps/server/src/handoff/handoffRoute.retired.test.ts:90`). No assertion was removed or weakened.

Nit: `apps/server/src/handoff/HandoffReceiver.ts:948` grows from 1,488 to 1,497 lines; `packages/contracts/src/rpc.ts:2496` from 2,570 to 2,577; `apps/server/src/server.ts:785` from 1,684 to 1,694. These are call-site, RPC registration and dependency-wiring additions, not new policy in the oversized files.
