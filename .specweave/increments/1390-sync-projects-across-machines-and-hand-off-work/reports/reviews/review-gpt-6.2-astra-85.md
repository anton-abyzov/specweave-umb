<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=677c6774fd5afa621a46c41651b40a7c228c4401 at=2026-11-19T19:02:49.208Z -->
# Review: 1390 T-17 LAN grant expiry, round 4
Verdict: ship
Reviewer context: fresh session; Git object inspection only.

At `apps/server/src/fleet/folderTransfer/sourceService.ts:388-391`, authorization rereads the current grant and samples the clock after the authority await. At or past expiry it returns revoked before refreshing idle time or permitting the read.

The regression test at `apps/server/src/fleet/folderTransfer/twoServer.lanSwitch.test.ts:255-281` holds the manifest decision, advances the service clock eight days, then releases it. It expects refusal, cancellation for revocation, and HTTP 401 on token reuse. No other regression found in the delta. Tests were not run.
