# Review round 4: GPT-6.2 Sol (Codex, high effort, on M4)

November 24, 2026. PR 847 at `356942dec` (amended to `88cf45b2f`, same tree, to drop a commit trailer the repository's CI refuses).

Verdict: fix first. 2 should-fix, 1 nit. Sol confirmed the `İ` offsets, the provenance from the detail, the folder cap and the worktree link-swap coverage are fixed.

| # | Severity | Finding | Response |
|---|---|---|---|
| 1 | Should-fix | A remote spec-only update moves the copy without changing the card's time, so an idle panel kept an old spec path. | Fixed in `8117580c9`: the refresh key includes the card's spec path and source. Test added. |
| 2 | Should-fix | A Windows path differing only in non-ASCII case (`Équipe`) missed the workspace match. | Fixed: `boardPaths.ts` compares whole segments without case and cuts results from the original path. Tests added. |
| 3 | Nit | The custom-base fixture sat outside the configured base. | Fixed: it sits in a sibling identity under the base, where the state rule and the Board exception both apply. |
