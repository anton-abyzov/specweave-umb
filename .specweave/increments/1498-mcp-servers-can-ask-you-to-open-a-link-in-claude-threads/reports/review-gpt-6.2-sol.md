<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=claude depth=standard repo=. base=03cdc099cef4b4371abec2084feaf64740d9710f head=cb9ec6724 at=2026-11-28T12:43:50.000Z -->
Verdict: ship

Round 4 of the GPT-6.2 Sol review at `cb9ec6724` said ship; recorded again after the closing verify of November 28, 2026. Its two should-fixes (raw bidirectional controls, longest wildcard suffix) were fixed after that round in `696b653fb` (T-09), which no review round saw. No new review was run.

# 1498 adversarial review

November 28, 2026. Reviewer: GPT-6.2 Sol (Codex) on m4, thread "1498 adversarial review: MCP link cards (Sol on m4)". Gemini 4 Neon was out of its monthly quota and Sol on M5 was at capacity, so the review ran on m4's Codex. The implementing session's own `reports/review.md` stays on M5, where the work ran; this copy is rebuilt from the review thread for the close on m4.

| Round | Head | Verdict | Findings |
|---|---|---|---|
| 1 | `16cbd35b7` | fix first | 2 blockers (one "I'm done" accepted another link in the same call; `https:example.test` resolved against the app's origin), should-fixes on the static done marker and the answer gate |
| 2 | `98a57b594` | fix first | 2 blockers (two asks with one URL shared an answer; a fleet coordinator session could answer), 1 should-fix (`https:///@example.test/` passed) |
| 3 | `488a20795` | fix first | 2 blockers (identical link and message replayed; remote owner window and coordinator share a principal), 1 should-fix (dot segments rewritten by the bridges) |
| 4 | `cb9ec6724` | ship | both consent findings downgraded; 2 should-fix (longest wildcard suffix for `*.run.app`, raw bidirectional controls in the URL) |

Round 4 accepted the reasoning that an identical replay inside one tool call is a `-32042` retry (AC-05), and that URL-mode `accept` carries no data and opens nothing. Remote press provenance through the fleet management credential is an owner follow-up outside 1498.

The two round 4 should-fixes were fixed after the review in `696b653fb` (T-09): raw bidirectional controls are refused and the longest wildcard suffix is matched. No review round ran on `696b653fb`. App PR #1021 merged as `45650362d` with 28 checks green on `696b653fb`.
