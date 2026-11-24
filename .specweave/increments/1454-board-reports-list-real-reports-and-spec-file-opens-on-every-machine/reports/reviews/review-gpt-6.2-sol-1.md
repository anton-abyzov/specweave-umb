# Review round 1: GPT-6.2 Sol (Codex, high effort, on M4)

November 24, 2026. PR 847 at `0ff9dd284`. Gemini 4 Neon could not run: both Copilot instances were out of monthly quota until December 1, 2026.

Verdict: fix first. 1 blocker, 7 should-fix.

| # | Severity | Finding | Response |
|---|---|---|---|
| 1 | Blocker | A hard link planted in `board-copies` to nested app state, such as a composer draft, passed both readers. | Fixed in `2edcaf8ff`. Reads are allowed only for increment files, and a file with more than one link is refused. |
| 2 | Should-fix | Copy staging can follow a pre-existing link (`IncrementCopies.ts:668`). | Deferred. The code is from 1421 and unchanged here; exploiting it needs write access to the state folder. |
| 3 | Should-fix | A `reviews/` path relative to `reports/` was grouped as a report, so reviews could push a real report out. | Fixed. Test added. |
| 4 | Should-fix | A linked `reports/reviews` folder was listed. | Fixed: only a real folder is listed. Test added. |
| 5 | Should-fix | The 12-folder cap hid reports before ranking. | Cap raised to 64; the file limit applies after ranking. |
| 6 | Should-fix | A report name that is invalid on Windows discards the copy (`IncrementCopies.ts:403`). | Deferred. The code is from 1421 and unchanged here. |
| 7 | Should-fix | HTML reports lost their sibling stylesheets. | Fixed: the asset is rooted at the workspace or the copy root. Server test added. |
| 8 | Should-fix | The viewer named the card's copy for reports from the project folder. | Fixed: files under the project folder say so. |

Version skew: the response shape works in both upgrade directions (reviewer).
