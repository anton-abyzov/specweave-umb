# Review round 3: GPT-6.2 Sol (Codex, high effort, on M4)

November 24, 2026. PR 847 at `0a585c074`.

Verdict: fix first. 3 should-fix, 1 nit. Sol confirmed the custom-base blocker is closed, videos use exact-file URLs again, and folder-to-link swaps change the signature.

| # | Severity | Finding | Response |
|---|---|---|---|
| 1 | Should-fix | Lowercasing `İ` changes string length, so a Windows HTML path was sliced at the wrong offset. | Fixed in `356942dec`: only ASCII A-Z is folded. Test with `İ` paths. |
| 2 | Should-fix | Report provenance could use a stale Board card. | Fixed: spec path and source come from the detail's card. Test with a stale card. |
| 3 | Should-fix | The 400-folder cap still dropped local reports. | Fixed: the cap is removed; folders are read 16 at a time and the 30-file limit applies after ranking. Test with 420 folders. |
| 4 | Nit | Two regression tests would pass on round 2's code. | Fixed: a hard link under a custom base, and a `reviews/` link swap in a selected worktree. |
