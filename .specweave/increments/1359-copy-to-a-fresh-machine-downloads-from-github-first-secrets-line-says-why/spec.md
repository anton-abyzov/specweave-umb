# Copy to a fresh machine downloads from GitHub first; secrets line says why

## Problem

Anton, November 15, 2026, setting up the M5 from scratch: "cloning the repository should be the most advised way. Maybe the second one is to copy all those files ... the secrets could be useful if you could run it locally ... even without those keys, AI agents could understand the whole code and find the gaps ... It's more about the verification phase." Today "Copy to another machine…" defaults to "Copy everything" (7.5 GB, 122k files for specweave-umb over Connect), the clone choice hides under Details as "Clone clean repositories from Git", and the secrets line says where secrets go but not what they are for. Recorded in project memory `decision_copy_to_another_machine_flow.md`, "Clone first on a fresh machine".

## Scope

In: a repository with unpushed commits or stashes is always copied, never cloned (review round 1, P1); the copy dialog's default way files travel becomes "Download from GitHub" (clone repositories the destination does not have yet; local changes, untracked files and ticked secrets still come from the source); "Copy everything" stays as the second choice for unpushed commits, local branches and stashes; the secrets line in the copy dialog and the secrets step says agents can read and fix code without keys, and secrets are for running the app or services, live tests, and MCP or Chrome sessions. Secrets stay ticked by default. Out: Add to another machine's older chat flow beyond the shared secrets wording, grouping secrets by kind.

## Acceptance Criteria

- [x] AC-01: Opening "Copy to another machine…" starts with "Download from GitHub (recommended)" chosen and listed first under How files travel; "Copy everything" is second and says it also brings unpushed commits, local branches and stashes; Details stays closed for the default; reopening or "Copy files only" returns to the clone default, and a resumed copy keeps the method it started with.
- [x] AC-02: The repository explanation in the preview names Download from GitHub as the default and Copy from {source} as the way to bring unpushed commits, local branches and stashes.
- [x] AC-04: A repository with commits not on any remote-tracking branch, or with stashes, is never cloned: it is copied whole with its history, and its row says why; a clone never leaves unpushed work behind or lands on another commit.
- [x] AC-03: The secrets line, in the copy setup and in the secrets step, adds: agents can read and fix the code without them; they are needed to run the app or services, live tests, or MCP and Chrome sessions on {target}. Secrets stay included by default.

## Approach

`ProjectMoveOptions.tsx` reorders and relabels METHODS and exports `DEFAULT_COPY_METHOD = "clone"`; `ProjectMachineHandoff.tsx` uses it wherever it reset to "copy"; `HandoffCopySetup.tsx` opens Details only for Git only and adds the secrets reason; `HandoffSecretsStep.tsx` adds the same reason; `HandoffCopyPreview.tsx` swaps which choice is the default. The server already copies a repository whole when it is on the destination or its remote is unreadable there, so the clone default never fails where copy worked.

## Decisions

### Asked
- D-01 Clone first on a fresh machine, copy second, secrets line says why → yes (Anton, November 15, 2026)
### Defaulted (change any before sw-do)
- D-02 Secrets stay ticked by default (the November 13 default stands) → default
- D-03 The clone default applies to every copy, not only an empty destination: the server only clones repositories the destination lacks, so an existing copy behaves as before → default
### Open
- none

## Tasks

### T-01 Clone-first default and secrets reason
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/manifest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/reconcile.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceDrift.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/git.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMoveOptions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopySetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffSecretsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyPreview.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.test.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/studio/HandoffFolderCopy.test.tsx src/components/studio/MachineHandoffDialog.test.tsx src/components/studio/ProjectMachineHandoff.test.tsx && cd ../server && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/manifest.test.ts src/fleet/folderTransfer/reconcile.test.ts src/fleet/folderTransfer/sourceDrift.test.ts
