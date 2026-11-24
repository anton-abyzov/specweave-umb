# Handoff copies the project folder, reconciles and can undo

## Problem

A handoff moves only committed code, by pushing each repository's HEAD to its origin and fetching it on the destination (October 19, 2026). Uncommitted work, untracked and ignored files, local branches and stashes never arrive; a dirty source or destination is refused; a missing repository is never cloned; there is no rollback and no unfence of the source after a failure. The user's real folder, the M4's EasyChamp (`/Users/antonabyzov/Projects/sw-easychamp`: 54.8 GB, 36 nested repositories plus 17 linked worktrees, 8 dirty repositories, directory symlinks, about 16 GB of ignored increment evidence), cannot be handed off at all. The user wants a safe copy of the folder's local files so the project is runnable on another machine, including into a folder that already exists and is out of sync. Design: `~/Projects/github/studio-research-notes/project-join-handoff-pairing-2026-10-19.md` section 6.

## Scope

In: SpecWithCode server folder transfer (manifest, content-addressed chunks, resumable pull, staging), transfer grant, reconcile planner, apply with backups and journal, Undo, unfence on failure, handoff dialog modes and preview, "copy files only" vs "copy and move the coordinator", docs. Out: secret files and sign-ins (0950; this increment excludes secret-like files and shows them as "handled in the secrets step"), per-project grants (0951). The existing push-and-fetch handoff stays for small clean projects.

## Acceptance Criteria

- [ ] AC-01: The handoff destination step offers: use the folder as it is (today's behaviour), copy from the source machine (default), or clone from origin per repository.
- [ ] AC-02: The source builds a manifest only while its project is idle: every file's path, type, mode, size, mtime and SHA-256; symlinks recorded as links and never followed; per-repository HEAD, branches, stash count, worktrees and origin. Files are classified as repository data (`.git`), tracked and untracked work, ignored rebuildable (`node_modules`, `.next`, `dist`, `build`, `DerivedData`, `Pods`, `.gradle`, coverage, caches), ignored project data (everything else ignored), and secret-like (the `WorkspaceSensitivePaths` list plus `.env*`).
- [ ] AC-03: The selection screen shows sizes per class before anything moves. Defaults: repository data, tracked and untracked work and ignored project data on; rebuildable off; secret-like off and deferred to 0950. "Exact copy of everything" turns all non-secret classes on.
- [ ] AC-04: Content moves server to server: the source mints a transfer grant scoped to this operation and folder (read-only, expires with the operation) and returns its private reachable URL; the destination pulls the manifest and chunks with it. Nothing passes through the browser except the grant and the URL. A source without a private URL the destination can reach is refused with a reason.
- [ ] AC-05: Chunks are content-addressed and verified by SHA-256, deduplicated against what the destination already has, and compressed in transit. A destination restart or a network drop resumes without re-sending verified chunks. Progress shows bytes and files done and remaining.
- [ ] AC-06: Files are assembled in a staging folder under the destination state directory, never written into the target folder before Apply. A final pass re-checks size and mtime on the source and re-sends or flags anything that changed.
- [ ] AC-07: Into a new empty folder, Apply produces a copy where each repository's `git fsck --connectivity-only` succeeds, HEAD, branches and stashes match the source, `git status` matches, linked worktrees work (`git worktree repair` when the home path differs), symlinks arrive as symlinks, and file modes match.
- [ ] AC-08: Into an existing folder, the preview classifies each repository and the non-repository files per the matrix in section 6.3 (same, fast-forward, ahead, diverged, dirty, conflict, new, only here) and shows files and bytes to move. Apply stays disabled until every row that needs a decision has one. Defaults never destroy anything on the destination; a diverged repository never loses a commit on either side; source branches arrive as `swc/from-<machine>/<branch>` when they cannot fast-forward.
- [ ] AC-09: Before Apply, every file it overwrites or removes is copied to `<stateDir>/machine-handoffs/backups/<op>/` and every ref it changes is recorded. An apply journal records each step. Undo restores files and refs byte-for-byte until the backup is discarded (default 14 days).
- [ ] AC-10: Operation state persists across restarts: planned, scanning, previewed, approved, transferring, verifying, applying, applied, undone, failed (with the step to resume). A failure before Apply leaves the target folder unchanged and returns the source coordinator binding to active with a recorded reason.
- [ ] AC-11: The dialog separates "Copy files only" (the destination becomes a linked copy that runs workers, using 0948's link when available; the coordinator stays) from "Copy and move the coordinator here" (today's handoff semantics, run only after files are applied and verified).
- [ ] AC-12: The source folder is unchanged by a copy, and the source project is not fenced in "Copy files only" mode.
- [ ] AC-13: User docs explain the three destination modes, what is copied by default, conflicts and Undo.

## Approach

New `apps/server/src/fleet/folderTransfer/`: `manifest.ts` (walk and classify; reuse `handoffGit` discovery and `WorkspaceSensitivePaths`), `chunkStore.ts`, `transferGrant.ts` (operation-scoped bearer with a path root and expiry, verified on every request), `sourceRoutes.ts` (HTTP: manifest and chunk endpoints behind the grant), `pullWorker.ts` (resumable destination pull with persisted progress), `reconcile.ts` (pure planner over source and destination repo states and file hashes), `apply.ts` (backups, journal, git operations, worktree repair), `undo.ts`. Extend `MachineHandoff.ts` and `MachineHandoffStore.ts` with the copy mode, state machine and unfence. Contracts in `packages/contracts/src/machineHandoff.ts`. Web: `MachineHandoffDialog.tsx`, `ProjectMachineHandoff.tsx`, new `HandoffCopyPreview.tsx` and progress view. Tests: pure planner matrix, chunk resume, end-to-end two isolated servers on loopback with a synthetic umbrella (nested repos, linked worktrees, dirty files, ignored data, symlinks, diverged history), headless dialog screenshots. A live check copies a real mid-size project into a scratch folder on the M3 from the installed release.

## Decisions

### Asked
- none (the user asked to implement all recommendations, October 19, 2026)
### Defaulted
- D-01: Copy is the default destination mode; clone from origin is per repository; the push-and-fetch handoff remains for small clean projects.
- D-02: Ignored project data (for EasyChamp, `.specweave/increments` evidence and `work/`) is copied by default; rebuildable folders are not.
- D-03: The destination pulls from the source over its private Tailscale Serve URL with an operation-scoped grant; no SSH, no browser relay of content.
- D-04: Undo keeps backups for 14 days, then they can be discarded from the operation's page.

## Tasks

### T-01 Manifest, classification and transfer grant
- AC: AC-02, AC-03, AC-04 | Files: apps/server/src/fleet/folderTransfer/manifest.ts, apps/server/src/fleet/folderTransfer/transferGrant.ts, tests beside them | Test: vp test run apps/server/src/fleet/folderTransfer

### T-02 Chunk store, source routes and resumable pull into staging
- AC: AC-04, AC-05, AC-06 | Files: apps/server/src/fleet/folderTransfer/chunkStore.ts, sourceRoutes.ts, pullWorker.ts, tests | Test: vp test run apps/server/src/fleet/folderTransfer

### T-03 Reconcile planner (pure) for new and existing folders
- AC: AC-07, AC-08 | Files: apps/server/src/fleet/folderTransfer/reconcile.ts, reconcile.test.ts | Test: vp test run apps/server/src/fleet/folderTransfer/reconcile.test.ts

### T-04 Apply, backups, journal, Undo and worktree repair
- AC: AC-07, AC-09 | Files: apps/server/src/fleet/folderTransfer/apply.ts, undo.ts, tests | Test: vp test run apps/server/src/fleet/folderTransfer

### T-05 Handoff integration: copy mode, state machine, unfence, coordinator choice
- AC: AC-01, AC-10, AC-11, AC-12 | Files: apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/MachineHandoffStore.ts, packages/contracts/src/machineHandoff.ts, tests | Test: vp test run apps/server/src/fleet/MachineHandoff.test.ts

### T-06 Dialog, selection, preview and progress UI
- AC: AC-01, AC-03, AC-05, AC-08, AC-09, AC-11 | Files: apps/web/src/components/studio/MachineHandoffDialog.tsx, ProjectMachineHandoff.tsx, HandoffCopyPreview.tsx | Test: web tests; headless screenshots

### T-07 Two-server end-to-end verification and docs
- AC: AC-05, AC-07, AC-08, AC-09, AC-10, AC-13 | Files: scripts/studio-folder-transfer/verify.mjs, docs/user/moving-a-project.md | Test: node scripts/studio-folder-transfer/verify.mjs <owned report dir>

### T-08 PR, merge, release and live copy into a scratch folder on the M3
- AC: all | Files: none | Test: PR Gate green; installed build copies a real project into a scratch folder on the M3, fsck and status match, Undo restores

### T-09 Verify and close 0949
