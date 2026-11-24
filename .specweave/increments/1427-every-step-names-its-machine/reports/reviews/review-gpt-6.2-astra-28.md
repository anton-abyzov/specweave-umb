<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=877dbe0c35088f640c0c8f0edccbe28bea5a1916 at=2026-11-20T02:03:12.033Z -->
# Review: 1427 coordinator question card
Verdict: fix first

Reviewer context: fresh session, static review of `877dbe0c35088f640c0c8f0edccbe28bea5a1916`.

## [high] `apps/web/tests/coordinator-menu/verify.mjs:142` rejects equivalent painted colours

A theme can replace the mixed machine-text token with its precomputed six-digit hex value for that theme. Chromium serializes that token as `rgb(...)` and the fixture's independent sRGB mix as `color(srgb ...)`. Even when both resolve to the same screenshot RGB bytes, the string equality fails before the screenshot is checked. Line 143 has the same issue for text fill alone. Resolve both computed values to RGBA bytes, as the fixture already does for the reference, and compare those. A precomputed teal token should pass; M5 blue should still fail.

The worker log reports eight successful shots with the existing stylesheet, not with an equivalent literal token. The docstring and PR body disclose the overlay limit accurately; that is not the finding.
