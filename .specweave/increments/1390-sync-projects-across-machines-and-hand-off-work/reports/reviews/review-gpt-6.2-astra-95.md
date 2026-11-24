<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=2622d4c90fe094d5664883ca775cff0de9931073 at=2026-11-19T19:32:52.293Z -->
# Review: 1390 T-14 stays assertion
Verdict: ship
Reviewer context: fresh session, Git-object delta only.

At `apps/web/tests/handoff-mode/verify.mjs:179-189`, each name from the literal list must match exactly one rendered row. A missing or renamed title yields zero matches. No other assertion is broken by this delta.
