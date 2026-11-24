# Review round 2: GPT-6.2 Sol (Codex, high effort, on M4)

November 24, 2026. PR 847 at `2edcaf8ff`.

Verdict: fix first. 1 blocker, 5 should-fix. Sol agreed the two copier issues from round 1 (#2, #6) can stay deferred.

| # | Severity | Finding | Response |
|---|---|---|---|
| 1 | Blocker | Hard-link protection missed custom app bases: a sibling cache's `board-copies` was readable but not link-checked. | Fixed in `0a585c074`: the link check matches by shape (any `userdata`/`dev` segment followed by `board-copies`), plus the configured state folder. |
| 2 | Should-fix | Videos got a relative asset request, which the server rejects. | Fixed: only HTML is re-rooted. Test added. |
| 3 | Should-fix | A `reviews/` folder replaced by a link to the same folder kept the cache signature. | Fixed: entries stamp `f`, `d` or `o`. Test added. |
| 4 | Should-fix | The 64-folder cap dropped reports before ranking. | Raised to 400 (removed in round 3). |
| 5 | Should-fix | Copy labels were wrong on Windows paths and umbrella planning roots. | Fixed: a per-path function names the card's copy for files in its spec folder, else the project folder. |
| 6 | Should-fix | Windows Library HTML missed the prefix check. | Fixed: forward slashes, case-insensitive on drive and UNC paths. Test added. |
