# Review: 1454 Board Reports list real reports, Spec file opens on every machine
Verdict: ship · risk: medium · 0 remaining findings (0 critical, 0 high, 0 medium, 0 low)
Reviewer context: new session on M4 · GPT-6.2 Sol (Codex, high effort) reviewing Claude Opus 5.5 · PR anton-abyzov/specwithcode#847 (`board-reports-and-spec-file`, ship at `34b9910d5`, merged as `a34dc2ca6`) and follow-up PR #900 (ship at `cafc0f45e`, merged as `110aa4417`)

Gemini 4 Neon could not run: both Copilot Enterprise instances were out of monthly quota until December 1, 2026, so the review fell back to GPT-6.2 Sol per the reviewer order.

## Rounds

Seven rounds on #847 and two on #900. Each round's findings and responses are in `reports/reviews/`:

- `review-gpt-6.2-sol-1.md` to `review-gpt-6.2-sol-7.md`: #847, from fix first (1 blocker, 7 should-fix) to ship.
- `review-followup-900.md`: a second, independent review (Claude Opus 5.5 with refuters) of an early commit, its remaining viewer findings fixed in #900, and Sol's two rounds on #900.

## What was checked

- The read exception for the Board's remote copies (`userdata/board-copies`): increment files only, never written, hard links refused under the configured state folder, sibling installs and custom bases.
- Report listing: groups ranked before the 30-file limit, every subfolder read, linked folders skipped, signature changes on folder-to-link swaps.
- Viewer: HTML rooted at its workspace or its own copy, Windows paths compared without ASCII case only (no false matches), provenance from the detail's card, refresh when the card changes copy, videos and arrow keys.

## Deferred (pre-existing, agreed with the reviewer)

- `apps/server/src/project/IncrementCopies.ts`: copy staging can follow a pre-existing link in the state folder; a Windows-invalid or case-colliding optional report name can stop a remote copy from being written. Both predate this increment (1421).
