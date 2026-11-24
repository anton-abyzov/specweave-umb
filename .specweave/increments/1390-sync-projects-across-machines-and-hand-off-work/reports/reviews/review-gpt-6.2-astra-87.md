<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=a60449a5e18f53eb8a4bfbc5c66b4bfbf4c88c78 at=2026-11-19T19:19:39.917Z -->
# Review: 1390 T-14 Hand off fixtures
Verdict: fix first
Reviewer context: fresh session; six changed files; Git objects only. No build or test run.

## [high] `apps/web/tests/handoff-mode/verify.mjs:197` cannot detect a wrong state returned by the row logic

The fixture mounts the shipped dialog and progress view and calls the real `progressRow` (`apps/web/tests/handoff-mode/progressCases.ts:113`). But the expected state and action are serialized from that very output (`apps/web/tests/handoff-mode/main.tsx:491-496`). If a held record loses its Resume here action, the view removes the button and the verifier now expects zero buttons (lines 206-210). A wrong mapped state likewise changes both sides. Specify expected states and actions independently by input record, and locate actionable buttons by role and accessible name, not merely row text. Replacing a button with plain text currently passes the positive check.

The reason comparison at lines 200-205 does catch a missing or incorrect rendered reason on a stayed or failed row with detail. Both verifiers launch headless, but external evidence requires an explicit output directory; their defaults are repository-relative (`apps/web/tests/handoff-mode/verify.mjs:14`, `apps/web/tests/away-mode/verify.mjs:15`). No personal path, private hostname or secret found in the diff.

Nonblocking follow-ups: preflight checks count failure types without matching messages to rows (lines 251-264); the eight pending scenarios are enumerated at lines 43-69, including coordinator refusal, window-close recovery, folder fallback, routine retry, coordinator stays, conditional source continuation, idle threads and provider usage.
