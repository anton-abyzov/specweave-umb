<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=c127be2861a008d77173d6a6015222cde0be369e at=2026-11-19T17:41:53.953Z -->
SHIP
Verdict: ship

Reviewer context: fresh cross-model review of `c127be2861a008d77173d6a6015222cde0be369e`, based on `8720e49f`. Git objects only; tests not run.

Five patches are identical to the approved series. The only resolution in the second patch places the same capability gate after the plan gate in `apps/server/src/handoff/handoffPlanReceiver.ts:130-141`. No test assertion was removed or weakened by the rebase. Target confirmation still precedes the new reset-time ranking, which applies only when no sign-in qualifies (`apps/server/src/handoff/handoffPlan.ts:288-310`).

The adapter passes run and disposition (`apps/server/src/orchestration-v2/LimitHandoffAdapter.ts:241-244`). The runner checks both before holding, reads Off inside the lease update, and refuses a changed run before stopping it (`apps/server/src/handoff/HandoffTransferRunner.ts:793-802,847-869,891-908`). Admission rereads the destination list and recomputes local track eligibility with current provider data and unexpired holds (`apps/server/src/orchestration-v2/MachineLimitHandoff.ts:765-779`; `apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:2098-2124`).

The new refusals release only unsent holds. Once sent, the existing dispatch, fence and replay paths still keep an uncertain transfer held rather than treating a failed retry as a definite no (`apps/server/src/handoff/HandoffTransferRunner.ts:334-361,511-557,1174-1190`).

Nit (low): `apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:1827-1832,2108-2124` adds more than a call site: hold expiry and the fresh-trigger comparison are admission logic. Keep the reads in the worker and extract the comparison when next touched. The file grew from 2,384 to 2,415 lines, but is identical to the approved head.
