# Folder copy wizard: step bar, Back, remembered step

## Problem

"Continue on another machine" (folder copy) has no navigation. The stage is a plain state that async runners and the server overwrite. Nothing records where the person was, and there is no Back. The owner, on 2026-10-26: "this process is kind of a wizard, so we must remember where we are because I think it was just putting me directly to the last step. There is no navigation between steps, so rethink this whole process."

Three things cause the jump:
1. The one-click default goes from setup straight to Done. The step line shows only Measure, Copy, Done.
2. Every reopen calls resume(), which maps the server state straight to a stage.
3. A finished copy-only copy keeps its pointer for Undo, so every later reopen lands on Done.

The only way back from any step is Cancel or Copy again, and both discard work. Evidence: reports/design-plan.md (code map with path:line).

## Scope

In:
- a fixed step bar per mode: Where, What, Review, Copy, Transfer (moves only), Done;
- clickable completed steps and a footer Back that only look (review mode, live actions hidden);
- labelled change actions before Apply ("Change where (cancels this copy)", "Change what to copy (measures again)", "Save folder" while choosing);
- the remembered step (seen/viewed) and restore on reopen, with a "Checking…" body and a resume note;
- a finished copy archived as "last copy", so reopen starts at Where with a View/Undo strip;
- a draft of the setup choices;
- extracting panels and footer to keep files under 1500 lines.

Out:
- making step-by-step the default (one-click stays);
- MachineHandoffDialog.tsx and HandoffCopyActions.tsx, which belong to the dialog-close thread;
- the method chooser unmounting a live flow (follow-up);
- server changes.

## Acceptance Criteria

- [ ] AC-01: Extracting the step panels and footer from HandoffFolderCopy.tsx changes no behaviour; every existing folder-copy test still passes.
- [ ] AC-02: The steps are fixed per mode (Where, What, Review, Copy, [Transfer], Done). A pure model maps all 10 stages, revisit rules, edit actions, restore and resume notes. The pointer gains validated seen, viewed, doneSeen and linked; last-copy and draft keys round-trip and survive a throwing localStorage; an old pointer parses unchanged.
- [ ] AC-03: Completed steps are buttons that open a read-only review with a banner and "Go to <live>"; future steps and every step while close-locked are disabled. A one-click copy shows What and Review as done and auto, and both are reviewable. Reviewing never calls the server.
- [ ] AC-04: Back appears on every live step after Where and in review, never calls the server, and is disabled while close-locked or checking. Change actions appear only before Apply, say what they cost, and work as labelled. After Apply, reviews are read-only and offer "Start a new copy with these settings".
- [ ] AC-05: Reopening shows "Checking the copy…" until the destination answers, then restores the viewed step when the copy is where it was. Otherwise it shows the live step with a note of what happened while closed. A finished copy-only copy is archived after Done was seen: the next reopen shows Where with a last-copy strip whose View leads to Done with Undo. An unreachable destination keeps the saved step with Check again. linkCopyAsWorkers is not re-run when linked.
- [ ] AC-06: A headless walk of both flows at 375x812 and 1280x800 in light and dark has no horizontal scroll and exactly one enabled primary per live step. Screenshots are saved to reports/.

## Approach

reports/design-plan.md is the full plan (judge of three designs; winner C with A and B grafts). The order is:
- T-01: extraction, with no behaviour change;
- T-02: pure model handoffCopyWizard.ts and the pointer, last-copy and draft keys in handoffFolderCopyPending.ts;
- T-03: clickable CopyStepLine and HandoffCopyReview.tsx;
- T-04: Back and change actions (cancelBeforeApply, rechoose, saveFolderOnly);
- T-05: useCopyStepView.ts with checking, restore and resume note, plus archive and draft;
- T-06: headless fixture walk.

Back is the first child of HandoffCopyActions with data-slot copy-back and mr-auto, so it sits far left; under the dialog-close thread's flex-row-reverse, #848 adds order-last to keep it there. Restore fires when the stage first leaves setup, not after the run. Risk: an approval the watcher already has in flight can land while reviewing; the banner shows it.

Branch: claude/folder-copy-wizard, stacked on claude/fix-folder-measure-hang (#807); rebase onto main once #807 merges.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: One-click stays the default; skipped steps are shown as done and auto, and are reviewable → keep (reversible one-line flip).
- D-02: Changing what to copy after the compare starts measures again, because the server ignores a new selection and refuses a new folder for an existing operation → labels say so.
### Open
- none

## Tasks

### T-01 Extract step panels and footer, no behaviour change
- AC: AC-01 | Files: apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffCopyStepPanels.tsx, apps/web/src/components/studio/HandoffCopyFooter.tsx | Test: cd repositories/anton-abyzov/specweave-studio/.worktrees/folder-copy-wizard && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/HandoffFolderCopy apps/web/src/components/studio/ProjectMachineHandoff.test.tsx apps/web/src/components/studio/MachineHandoffDialog.test.tsx

### T-02 Step model and pointer, last-copy and draft keys
- AC: AC-02 | Files: apps/web/src/components/studio/handoffCopyWizard.ts, apps/web/src/components/studio/handoffCopyWizard.test.ts, apps/web/src/components/studio/handoffFolderCopyPending.ts, apps/web/src/components/studio/handoffFolderCopyPending.test.ts, apps/web/src/components/studio/handoffCopySteps.ts, apps/web/src/components/studio/handoffCopyAuto.test.ts | Test: cd repositories/anton-abyzov/specweave-studio/.worktrees/folder-copy-wizard && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/handoffCopyWizard.test.ts apps/web/src/components/studio/handoffFolderCopyPending.test.ts apps/web/src/components/studio/handoffCopyAuto.test.ts

### T-03 Clickable step bar and read-only review
- AC: AC-03 | Files: apps/web/src/components/studio/HandoffCopyGuide.tsx, apps/web/src/components/studio/HandoffCopyReview.tsx, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffCopyStepPanels.tsx, apps/web/src/components/studio/HandoffFolderCopy.test.tsx, apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx | Test: cd repositories/anton-abyzov/specweave-studio/.worktrees/folder-copy-wizard && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/HandoffFolderCopy

### T-04 Back and change actions
- AC: AC-04 | Files: apps/web/src/components/studio/HandoffCopyFooter.tsx, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffCopyReview.tsx, apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx, apps/web/src/components/studio/HandoffFolderCopy.cancel.test.tsx | Test: cd repositories/anton-abyzov/specweave-studio/.worktrees/folder-copy-wizard && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/HandoffFolderCopy

### T-05 Checking, restore, resume note, archive and draft
- AC: AC-05 | Files: apps/web/src/components/studio/useCopyStepView.ts, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/HandoffCopyStepPanels.tsx, apps/web/src/components/studio/HandoffCopyGuide.tsx, apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx, apps/web/src/components/studio/HandoffFolderCopy.test.tsx, apps/web/src/components/studio/HandoffFolderCopyWatcher.test.tsx | Test: cd repositories/anton-abyzov/specweave-studio/.worktrees/folder-copy-wizard && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/HandoffFolderCopy apps/web/src/components/studio/HandoffFolderCopyWatcher.test.tsx apps/web/src/components/studio/ProjectMachineHandoff.test.tsx

### T-06 Headless walk of both flows
- AC: AC-06 | Files: apps/web/tests/folder-copy/verify.mjs, apps/web/tests/folder-copy/* | Test: cd repositories/anton-abyzov/specweave-studio/.worktrees/folder-copy-wizard && node node_modules/vite-plus/bin/vp build --config apps/web/tests/folder-copy/vite.config.ts && node apps/web/tests/folder-copy/verify.mjs /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1087-folder-copy-wizard-step-bar-back-remembered-step/reports/headless
