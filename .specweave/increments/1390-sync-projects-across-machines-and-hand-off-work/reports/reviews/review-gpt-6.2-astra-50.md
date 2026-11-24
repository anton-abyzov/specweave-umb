<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=960d52a11537556d25fdea18eb7ef9503cdc8fb6 at=2026-11-19T15:40:25.024Z -->
SHIP
Verdict: ship

Finding 4 (AC-47) is closed at `960d52a11537556d25fdea18eb7ef9503cdc8fb6`.

When two automatic groups arrive in one poll, only the one opened is marked seen. An arrival before Done also stays unseen. Closing the dialog triggers selection again, so the waiting group opens once without replacing the current dialog (`apps/web/src/components/handoff/handOffProgress.logic.ts:267-279`; `apps/web/src/components/handoff/HandOffProgress.tsx:510-516`).

The red log names test blob `54773edcf8c54ca4a512e5584eb0209170386522` from `47617f2ca`. It shows assertion failures for both required cases and for two active groups on first read. The tests are unchanged at the reviewed head; the log reports 462 passing tests after the fix. No suite was rerun for this review.
