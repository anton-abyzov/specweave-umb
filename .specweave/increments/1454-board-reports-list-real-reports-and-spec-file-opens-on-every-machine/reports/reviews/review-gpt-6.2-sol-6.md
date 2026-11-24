# Review round 6: GPT-6.2 Sol (Codex, high effort, on M4)

November 24, 2026. PR 847 at `5311dd6b8`.

Verdict: fix first. 1 should-fix. Sol confirmed `Straße` and `Strasse` stay separate.

| # | Severity | Finding | Response |
|---|---|---|---|
| 1 | Should-fix | JavaScript folds Greek `ς` and `σ` together where NTFS keeps them apart, so a worktree page could still be re-rooted to the project. | Fixed in `34b9910d5` by changing the approach: on Windows only ASCII letters match without case. A missed match serves the page by its exact path (right file, no sibling CSS); a false match can no longer happen. Increment reports are rooted at their own copy from their own path. |
