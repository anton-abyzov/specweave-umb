# One Copy to another machine flow: secrets included by default, one coordinator question

## Problem

Anton, November 13, 2026, before recording the M4 to M5 move: the project's machine menu offers "Add to another machine…", "Move to another machine…", "Move to m5…", "Sync to m5…" and an "Add or move to another machine" button. They open one dialog whose first screen shows a Workspace locations table (source folder, selected repository, checkout, mode, branch, destination folder, checkout, worktree storage), three paragraphs about worktrees and private data, a "Where › Copy › Done" line, a "Hand off and continue there" / "Copy local files" toggle, a machine list, a folder and More options with three file methods. Secrets are left out unless the person finds "Include secrets" on the review screen and then ticks a second confirmation. The Git handoff adds an "18 uncommitted files stay on m4" warning and "7 repositories keep work on m4 that Git won't carry". He cannot tell what each choice copies or how they differ.

The code confirms his reading: every path is the same copy engine (`HandoffFolderCopy`, modes `copy-only` and `copy-and-move`). "Copy local files" copies and links the copy as workers; "Hand off and continue there" copies the same files and then moves the coordinator (its context up to 2 MB, the 200 most recent threads summarized). The only real difference is where the coordinator runs. The Git-only handoff (no file copy) and the clone-from-Git method are rarer variants of the same thing.

## Scope

In: one "Copy to another machine…" entry for the project (menu and button); one dialog with the machine, the folder, a short "What comes along" list, one "Where should the coordinator run?" question and a Details disclosure for the technical rows and methods; secrets copied by default, shown as an explicit included line that expands to the file list; the Git-only path cleaned the same way; headless screenshots; review, merge and a release request.

Out: server or wire changes; the composer's Run on "Add to another machine…" (it starts a thread on a machine without the project and keeps its own dialog); Settings > Machines role labels (PR 350 owns them; this dialog's wording matches "Coordinator here" / "Workers only"); the machine readiness check (PR 337, not merged, so the dialog does not claim it).

## Acceptance Criteria

- [ ] AC-01: The project's machine menu has one "Copy to another machine…" item in place of "Add to another machine…", "Move to another machine…" and "Sync to {machine}…"; the dialog trigger button reads "Copy to another machine". A machine that already has a linked copy keeps the coordinator-only move, renamed "Move coordinator to {machine}…". "Start a coordinator on {machine}" and "Leave this machine…" are unchanged.
- [ ] AC-02: The copy dialog opens on one screen: title "Copy {project} to {machine}" (or "to another machine" before one is picked), one line "From {source}. Nothing on {machine} is replaced without asking.", the machine list, "Folder on {machine}", "What comes along", "Where should the coordinator run?" and a closed "Details" disclosure. No Hand off / Copy local files toggle, no Workspace locations table and no step line on this screen.
- [ ] AC-03: "Where should the coordinator run?" offers "Keep on {source}" (default; "{machine} runs workers.") and "Move to {machine}" ("Its conversation and threads continue on {machine}; {source} runs workers."). Keep runs `copy-only`, Move runs `copy-and-move`. The primary button reads "Copy to {machine}" or "Copy and move to {machine}", and the review's approve button says the same.
- [ ] AC-04: Secret files are included by default. Setup shows a checked "Secrets (.env, keys): included" line; the review shows "Secrets (.env, keys): N files, included" with Show to list each file with its own checkbox, and no second confirmation. Unticking the line leaves them on the source and says so. Sign-ins to Claude, Codex and GitHub are never copied, and the list says so.
- [ ] AC-05: Details holds the Workspace locations rows, the worktree notes, "How files travel" (Copy everything / Clone clean repositories from Git / Git only, no file copy) and "Let me choose file types first". Choosing Git only shows the Git screen with the coordinator question fixed to Move (Git only always moves it) and no toggle.
- [ ] AC-06: On the Git-only screen, uncommitted files and repositories with unpushed work show as one short line in What comes along ("18 uncommitted files stay on m4: Git carries commits only.") with Commit for me, not as a warning box; the Workspace locations table and the left-behind list sit under Details.
- [ ] AC-07: Headless screenshots of the setup screen (light and dark), the review with secrets expanded and the Git-only screen are saved in this increment's reports/ folder.
- [ ] AC-08: An adversarial review by GPT-6.1 Sol (Codex, xhigh, on linux-mini) finds no unresolved correctness issue, required CI is green, the PR is merged and a release is requested with `request-release.sh`.

## Approach

Option A of `reports/mockups.html` (screenshot `reports/mockups.png`): one dialog, one coordinator question. Option B (separate Copy to / Move to verbs) keeps two entry points and makes a change of mind mean reopening. Option C (three-step wizard) needs a full measure before its counts and takes three screens for one choice.

Web only, in `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio`:
1. `OrchestratorSwitcher.tsx`, `ProjectWorkspaceSurface.tsx`: one Copy item calling `requestHandoff("copy")`; Move to {machine} becomes Move coordinator to {machine}. `MachineHandoffDialog.tsx` button label.
2. `ProjectMachineHandoff.tsx`: the dialog opens on the copy flow (`intent` copy, method copy) for every request except a resumed Git handoff; the share view and the "existing folder means Git" default go.
3. `HandoffCopySetup.tsx`: drop `MoveIntentToggle`; add `CopyAlong` (What comes along) and `CoordinatorChoice`; More options becomes Details and also holds `HandoffWorkspaceSummary`. `HandoffFolderCopy.tsx` stays under 1500 lines: the summary moves into setup, the step line hides on setup.
4. `HandoffSecretsStep.tsx` and the secret state in `HandoffFolderCopy.tsx`: `includeSecrets` (default true) ticks every receivable secret file when the measure lists them, and counts as the confirmation.
5. `MachineHandoffDialog.tsx` GitWhere: no toggle, coordinator fixed to Move, summary and left-behind under Details.
6. Tests: the existing component suites and `apps/web/tests/folder-copy` fixture move to the new wording.

Risk: secrets on by default changes 1164 AC-06 (opt-in). Anton asked for it; the line is visible and one click turns it off, the files still go only to the chosen machine with owner-only permissions.

## Decisions

### Asked
- D-01 Secrets default → included by default, shown as an explicit line (Anton, November 13, 2026, via the coordinator brief).
### Defaulted (change any before sw-do)
- D-02 Name of the one action → "Copy to another machine…": the word Anton uses, and true for files in both coordinator choices.
- D-03 Coordinator default → Keep on the source; moving is one click and is the less reversible choice.
- D-04 Coordinator-only move to a machine that already has a linked copy stays, as "Move coordinator to {machine}…": it copies nothing and is the cheap path for the umbrella.
### Open
- none

## Tasks

### T-01 Mockups of three options and the pick
- AC: AC-02 | Files: .specweave/increments/1325-one-copy-to-another-machine-flow-secrets-included-by-default-one-coordinator-question/reports/mockups.html | Test: test -s .specweave/increments/1325-one-copy-to-another-machine-flow-secrets-included-by-default-one-coordinator-question/reports/mockups.png

### T-02 One Copy to another machine entry
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/OrchestratorSwitcher.test.tsx

### T-03 One-screen copy dialog with the coordinator question
- AC: AC-02, AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopySetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMoveOptions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/HandoffFolderCopy.wizard.test.tsx src/components/studio/ProjectMachineHandoff.test.tsx

### T-04 Secrets included by default
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffSecretsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/HandoffFolderCopy.test.tsx

### T-05 Git-only screen cleaned the same way
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/MachineHandoffDialog.test.tsx

### T-06 Headless screenshots
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/verify.mjs, .specweave/increments/1325-one-copy-to-another-machine-flow-secrets-included-by-default-one-coordinator-question/reports/ | Test: ls .specweave/increments/1325-one-copy-to-another-machine-flow-secrets-included-by-default-one-coordinator-question/reports/after-setup-light.png

### T-07 Review, CI, merge and release request
- AC: AC-08 | Files: .specweave/increments/1325-one-copy-to-another-machine-flow-secrets-included-by-default-one-coordinator-question/reports/review.md | Test: test -s .specweave/increments/1325-one-copy-to-another-machine-flow-secrets-included-by-default-one-coordinator-question/reports/review.md

### T-08 Verify and close 1325
- AC: AC-08 | Files: .specweave/increments/1325-one-copy-to-another-machine-flow-secrets-included-by-default-one-coordinator-question/spec.md | Test: specweave verify 1325
