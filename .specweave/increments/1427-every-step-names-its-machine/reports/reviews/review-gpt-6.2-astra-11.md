<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=c73f6ec2f73de3c55c19e5bcee079142a65bfa46 at=2026-11-20T00:13:17.547Z -->
# Review: 1427 window labels rebase
Verdict: ship
Reviewer context: fresh session, Git objects only.

Three of four patches are unchanged. The second differs only in context: all eight catalogs retain the `iphone` import and spread from main. The rebase changes no PR lines and drops no main entry.

In each locale, none of the 17 `machineLabels` keys overlaps the 17 `iphone` keys, the main catalog's explicit keys, or the `sync` and `handoff` keys. No translation changes through spread order. No findings.
