<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=89b85562f1eba83a5f7a9ef2ed04c415c124ce75 at=2026-11-19T19:28:52.570Z -->
# Review: 1390 T-14 headless fixtures
Verdict: fix first
Reviewer context: fresh session, four-file Git delta at `89b85562f1eba83a5f7a9ef2ed04c415c124ce75`.

## [high] `apps/web/tests/handoff-mode/verify.mjs:178-182` compares the Stays reason list to itself

`apps/web/tests/handoff-mode/progressCases.ts:212-214` constructs one record from each `STAYS_REASONS` entry, and lines 144-151 copy its input detail into the expectation. `apps/web/tests/handoff-mode/main.tsx:491-494` exports those expectations and the same reason list. Omitting a reason from that list drops it from both sides; no change in rendered output can fail this assertion. Remove it or compare rendered reasons against an independent inventory.

The actual DOM checks are independent: states and controls are literal per input state (`apps/web/tests/handoff-mode/progressCases.ts:92-102`); reasons use the record detail, not `progressRow` output, though most Stays inputs come from server constants (lines 44-55). The verifier checks the rendered reason, locates buttons by role and exact accessible name, and checks Wait as text without a button (`apps/web/tests/handoff-mode/verify.mjs:195-225`). Both evidence defaults use the OS temporary directory (`apps/web/tests/handoff-mode/verify.mjs:16-18`, `apps/web/tests/away-mode/verify.mjs:17-19`).
