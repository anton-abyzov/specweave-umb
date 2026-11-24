# 1312 review (PR 269)

Reviewer: claude-sonnet-5-5, fresh context, two rounds. Reviewed diff: `origin/main..25aac4167a` (27 files, apps/web), then the fix `25aac4167a..3ba2eae0d3`. Merged head `4bf42dfd70` differs from `3ba2eae0d3` only by main and the CHANGELOG line.

## Round 1: FIX

Must-fix: `apps/web/src/components/ServerUpdateAction.tsx` remote Wait until quiet installed the pinned `targetVersion` once the machine was quiet, even when the machine had already updated itself (its own install also waits for quiet) or moved past it, causing an extra restart or a downgrade. Fixed in `3ba2eae0d3`: `serverReachedVersion` reads the machine's `serverVersion` each round and again just before installing, and the wait ends with its notice closed.

Nice-to-have, fixed: the loop now looks once before its first 15 s sleep; a two-way question with a list focuses Later, not the first row.

Nice-to-have, not taken: a second Update press during a wait gives no feedback (the notice has Cancel).

Checked fine: the 3 s poll is cleared on unmount and drops late answers; dialogs resolve once; toast close and Cancel end the wait; the hold window still forces only on the desktop path; every `askRestartForWork` settles.

## Round 2: SHIP

`configValueAtom` exposes the remote `serverVersion` and refreshes on reconnect after the restart; versions share one scheme; Base UI merges the Cancel ref so initial focus works; test mocks are isolated. Nice-to-haves left: the config atom may read null when nothing displays that machine (falls back to the old behaviour); no message when the wait ends because the machine is already on the version.

## Rebase note

The original head `03a09c6ac9` was built on a tree from before #271 and would have reverted it (112 files). It was replaced by a 27-file replay onto main (`25aac4167a`).
