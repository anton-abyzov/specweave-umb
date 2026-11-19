<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=387393db1856487141569c391a66b82f04a6cd39 at=2026-11-19T17:14:55.672Z -->
SHIP
Verdict: ship
Reviewer context: fresh session; Git-object delta only, 0 findings.

`apps/server/src/handoff/HandoffReceiver.ts:637-649` wires the same dependencies; line 1478 exposes the resulting check. No caller or scope gate moved. `apps/server/src/handoff/handoffPlanReceiver.ts:112-157` still checks source identity before compatibility, then reads providers, settings and the document in order. Settings failures still map to HTTP 500. Lines 158-206 preserve grant checks, lease inspection and results without taking a lock or lease. The Effect signature at lines 42-45 adds no service requirement. The import back to the receiver at line 28 is type-only, so it creates no runtime cycle.
