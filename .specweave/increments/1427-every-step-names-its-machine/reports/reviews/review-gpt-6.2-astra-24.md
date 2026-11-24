<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=d3fce9338d636b9702d301354bb24b77258b3793 at=2026-11-20T01:46:43.240Z -->
# Review: 1427 coordinator question card
Verdict: fix first

Reviewer context: fresh session, static review of `d3fce9338d636b9702d301354bb24b77258b3793`. No build or test run.

## [high] `apps/web/tests/coordinator-menu/verify.mjs:134` checks the colour attribute, not the rendered colour

A CSS override can paint the indicator M5 blue while `data-machine-color` remains `teal`. All four cases would pass: the assertion reads the attribute, and the screenshots have no comparison. Check the indicator's computed colour against the expected teal for each theme.

The fixture mounts the production question card. Exact, scoped text checks reject wrong or missing machine labels on both the card and the thread chip. The PR diff changes five fixture files, uses generic names and changes no production file.
