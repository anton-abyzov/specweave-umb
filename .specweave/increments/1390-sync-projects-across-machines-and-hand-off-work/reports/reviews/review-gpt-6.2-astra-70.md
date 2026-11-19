<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=a05964d657475623fd2fea7c239a83043a3bf1f9 at=2026-11-19T16:49:29.593Z -->
SHIP
Verdict: ship

Independent round 8 delta review of `a05964d657475623fd2fea7c239a83043a3bf1f9`. Both round 7 findings are closed. Git-object inspection only; tests were not run.

`apps/server/src/handoff/handoffMove.compat.test.ts:159-181` passes the receiver's actual heartbeat answer to the extracted v1.0.378 handler. The previously active source then names the continuation, is fenced at epoch 2, refuses a turn and interrupts the active run. The handler executes the tagged continuation loop, not an assertion-side state assignment (`apps/server/src/handoff/previousRelease.handoffMoves.test.fixture.ts:924-948`).

`apps/server/src/handoff/handoffMove.drain.test.ts:85-125` drops the authorized request before delivery, checks that the operation survives sleep, matches its ID to the receipt-bearing record, and checks both epoch-2 leases and exactly one launch after a second tick. The incapable-peer case still expects zero launches after two ticks (`apps/server/src/handoff/handoffMove.compat.test.ts:335-350`).

No existing test lost an assertion or acquired a permissive default. The shared sleep helper preserves both the no-post and refusal checks (`apps/server/src/handoff/handoffMove.test.fixture.ts:596-626`).
