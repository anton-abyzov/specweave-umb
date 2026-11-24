<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=3774f92984493de50fdba65338e2179f6ddddfe2 at=2026-11-20T00:46:32.405Z -->
# Review: 1427 ordered machine names in the grant step
Verdict: ship
Reviewer context: fresh session; static review of both commits, no tests run.

At `apps/server/src/fleet/RemoteWorkers.test.ts:808-823`, the fixture names the responding machine `Machine A` and the launch target `Machine B`. The literal expectation requires `On Machine A (not on Machine B)`, so swapping the labels fails. The test retains the rejection of `this machine`; the error-code checks remain intact. No other assertion weakened and no production file changed.
