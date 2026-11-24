<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=fe2998686f3770f9de67444f579721bdddec8ba4 at=2026-11-19T20:26:23.363Z -->
# Review: 1390 T-17, round 5
Verdict: ship
Reviewer context: fresh session; Git objects only.

BOM: `apps/server/src/fleet/folderTransfer/git.ts:35-41,124-129` preserves leading U+FEFF on Git stdout and flags invalid UTF-8. Buffer path conversions preserve the BOM too (`apps/server/src/fleet/folderTransfer/portableGit.ts:418,432`); the default TextDecoders parse JSON envelopes, not raw paths.

Rebase: against `6d50697e` and `d38774aa1`, no confinement check or LAN route was dropped. `apps/server/src/fleet/folderTransfer/destinationService.ts:711-720` reads current LAN state under the operation lock and captures the approved target in the same record; line 1374 forwards that approval, and lines 435-445 retain the per-operation LAN client.

No fail-open findings in scope. The previously accepted backup race was not reassessed.
