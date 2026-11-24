<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=be6738cf5b7ed697dc9847dff2dd09a203824b4a at=2026-11-20T01:56:51.890Z -->
# Review: 1427 machine name paint
Verdict: fix first
Reviewer context: fresh session, one-file delta at `be6738cf5b7ed697dc9847dff2dd09a203824b4a`.

## [high] `apps/web/tests/coordinator-menu/verify.mjs:154` counts decoration as lettering

A positioned `::after` covering the name with an opaque background and an inset `8px` by `8px` square of `currentColor` hides every letter without changing the DOM text, box, computed color or fill. On a contrasting solid background, the square supplies 64 teal pixels to both `ink` and `core`, above the thresholds of 40 and 8. Their mean is teal, so the assertion passes with only a square on screen.

Compare against a glyph mask for `linux-mini` drawn independently at the fixture's font and size, checking both the coverage and color of the expected strokes. Add the covering-square case as a negative control.
