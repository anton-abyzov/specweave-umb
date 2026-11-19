<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=5cb3dba4680824c17171d482761f51fe2c4abe53 at=2026-11-19T15:54:26.802Z -->
SHIP
Verdict: ship

Reviewed `anton-abyzov/specwithcode#702` at `5cb3dba4680824c17171d482761f51fe2c4abe53`, limited to the round 2 AC-38 blocker.

Finding 2 closed. At `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.ts:744`, both starts reject an ambiguous track before target evidence can qualify the row. It stays unticked and unselectable, with a reason. A genuinely untracked thread bypasses that guard and retains the model-only fallback at line 208.

`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPlan.test.ts:726` replaces the manual Resume expectation with Stays for running, waiting and settled-with-unsaved-work cases, and keeps a separate ticked Resume assertion for an untracked thread.

Pre-fix CI run `44559489461` on `fcdba7194` was queued. Assertion failure not yet confirmed.
