# Review round 5: GPT-6.2 Sol (Codex, high effort, on M4)

November 24, 2026. PR 847 at `8117580c9`.

Verdict: fix first. 1 should-fix. Sol confirmed the stale-copy refresh and the custom-base fixture are fixed.

| # | Severity | Finding | Response |
|---|---|---|---|
| 1 | Should-fix | JavaScript uppercases `Straße` and `Strasse` alike, but Windows treats them as different folders, so a worktree's page could be re-rooted to the project. | Fixed in `5311dd6b8`: names are compared unit by unit with one-for-one case mappings only, as Windows does. Tests for both directions and for `straße`/`STRAßE`. |
