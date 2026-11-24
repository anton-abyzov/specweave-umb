<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=8bcc581c239defdc778fc77635f42d5f6833c0d4 at=2026-11-20T01:51:51.683Z -->
# Review: 1427 Card indicator colour
Verdict: fix first

Reviewer context: fresh session, delta only.

## [high] `apps/web/tests/coordinator-menu/verify.mjs:144` reads text colour but not text fill

In the fixture's Chromium browser, `[data-action-machine] { -webkit-text-fill-color: #2f6fd6; }` paints the machine name blue without changing its computed `color`. The independent teal and blue probes still differ, and the equality at line 158 still passes in both themes at both widths. Check the indicator's resolved `-webkit-text-fill-color` against the independent teal reference as well.
