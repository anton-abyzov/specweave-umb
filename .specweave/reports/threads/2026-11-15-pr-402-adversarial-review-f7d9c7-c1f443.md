---
title: "PR 402 adversarial review"
thread: "thread:delegated-task:command%3Amcp%3A79ba565a-e4a0-4284-89ef-42356ac24527%3Adelegate-task%3Apr402-review-round1-enterprise"
threadTitle: "Review folder copy origin leftovers"
savedAt: "2026-11-15T00:43:41.124Z"
---

# PR 402 adversarial review
Verdict: fix first

Reviewed commit: `5ddfceb5fa606901bcc5bfa12abc2d91467ec9f3`

Reviewer: `gpt-6.1-sol`. Author model: Claude Opus 5.5. Scope: `git diff origin/main...HEAD`, read-only. The requested `sw-review` skill was not installed; the installed adversarial-review skill was loaded instead. No reviewed source files were edited, and nothing was pushed or posted to GitHub.

Findings: 1 high, 2 medium.

## [high] Clearing an occupied clone folder drops identical untracked source files

Where: `apps/server/src/fleet/folderTransfer/apply.ts:428-434`

Why: Choose clone and take-theirs for a non-root repository whose destination folder holds an untracked file identical to the source's untracked file. The planner still compares against the pre-clear destination: only replace steps invalidate those entries (`reconcile.ts:544-549`), and identical content gets no write action (`reconcile.ts:666-668`). The new clear moves the whole folder away, while Git restores only tracked content. Apply completes successfully with the untracked file absent from the destination, despite it being present on both sides in the preview.

Evidence: A local bare-origin reproduction generated `actions: []`, `git: ["clone"]`, then returned `checks: []`. `svc/scratch.txt` existed before Apply and did not exist afterwards; its original bytes were in `backups/files/svc/scratch.txt`. This is introduced by the new whole-folder clear; the old clone path left the identical file in place.

Fix: Make planning account for occupied clone folders being cleared, so source files omitted only because they were present are actually staged and restored. Keep the preview's per-file decisions consistent with that whole-folder replacement behavior.

## [medium] Undo crash replay moves the restored original away again

Where: `apps/server/src/fleet/folderTransfer/apply.ts:434-436`; downstream `apps/server/src/fleet/folderTransfer/undo.ts:615-625`

Why: The new backup precedes the clone marker, creating a journal with both entries for the same folder. A failed clone can leave the created clone folder empty. Undo moves that empty folder into `undone-clones`, then restores the original backup. If the process crashes after restoring the original but before its completion mark, `undoProgress` correctly recognizes the restored original. However, the replay skip excludes `cloned` (`undo.ts:441-445`), so the clone handler moves the restored original into the empty `undone-clones` folder. The already-completed backup restoration is skipped. Retry reports no problems but leaves the original missing from its destination.

Evidence: Reproduced using an unreachable local origin. First Undo restored `svc/original.txt` with `problems: []`. Removing only the final `undo-file-done` journal line modeled a crash between restoration and its completion mark. Second Undo again returned `problems: []`, but `svc/original.txt` was absent; its original bytes had moved to `backups/undone-clones/svc/original.txt`.

Fix: Do not replay the clone-removal step for a path whose original restoration is completed or digest-reconciled. Add durable clone-removal progress if necessary to distinguish the intermediate states.

## [medium] Existing clone previews are refused solely for missing new metadata

Where: `apps/server/src/fleet/folderTransfer/destinationService.ts:1173`; comparison at `apps/server/src/fleet/folderTransfer/destinationService.ts:598-605`

Why: Plans persisted before this change lack `cloneOrigins`. Approve passes undefined, causing another origin lookup and producing a current plan with the new field. Even when the origin answer and every existing plan field are unchanged, JSON equality fails. Approve rewrites the plan and incorrectly reports `The destination changed. Review the updated comparison before copying.` Every old preview with a selected origin-bearing clone hits this once; a second approval can proceed after the rewritten plan is reviewed.

Evidence: Reproduced the old plan shape by removing only `cloneOrigins` from a generated plan, matching the base branch's serialization. Replanning with identical cached origin answers yielded `plansEqual: false`, `onlyAddedKey: ["cloneOrigins"]`, and `sameOtherFields: true`.

Fix: Normalize or migrate old previews before strict comparison, without treating newly attached origin metadata alone as a destination change. Where possible, reconstruct the reviewed origin decisions from the old plan rather than re-probing.

## Checked and ruled out

- New-format preview and approval use the same origin-answer map and property insertion order; the network-drift regression passes. Sorted origin answers prevent completion-order differences in serialization.
- The origin-probe worker processes each repository once, with four workers per invocation. The concurrency test passes.
- Aborted probes are converted to null internally, but the added `signal.throwIfAborted()` prevents the completed answer map from being used to publish a preview after cancellation.
- Root `.` clones do not enter the new clear branch. The pre-existing temporary-clone behavior remains unchanged; no new root-clone defect was identified in this diff.
- The backup intent is synced before moving the original, and the clone intent is synced before cloning. Apply replay handles the ordinary before/after-backup windows through the existing backup map. Undo's later restoration replay is the separate defect above.
- Standard SSH origins retain HTTPS fallback; explicit non-22 ports no longer invent an HTTPS endpoint. Both origin-candidate tests pass.
- The new occupied-folder test verifies first-pass restoration but does not exercise identical source/destination untracked content or Undo interrupted after original restoration.

## Validation and limits

The authorized verification copy was confirmed at the reviewed SHA. With Node `22.20.0`, the following focused command passed: 3 files, 30 tests.

`cd /Users/antonabyzov/.specwithcode/m4/verify/specwithcode && specweave-studio checks run -- node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/folderTransfer/apply.test.ts apps/server/src/fleet/folderTransfer/destinationService.test.ts apps/server/src/fleet/folderTransfer/originCandidates.test.ts`

The independent reproduction script ran through `specweave-studio checks run -- node --experimental-strip-types` against that same copy and reproduced all three findings. Fixtures used local disposable Git repositories and synthetic state, with no live account access. Finding lines were reread against the unchanged reviewed head before reporting. No full suites, builds, or typechecks were run.

Review recording is unavailable in the installed CLI: SpecWeave `3.1.21` rejects `--record` with `error: unknown option '--record'`. The alternate installed version, `3.1.4`, also exposes no recording option. No shared toolchain was modified.
