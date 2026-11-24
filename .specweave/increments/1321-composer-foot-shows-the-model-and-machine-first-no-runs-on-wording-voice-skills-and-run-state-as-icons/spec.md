# Composer foot keeps the machine and model readable first; voice, skills and run state as icons

## Problem

Anton, November 13, 2026, on two screenshots of the desktop app at phone and half-screen width: the composer's bottom line spends its room on the wrong things. The machine chip says "Runs on linux-mini", Voice is a labelled menu, Skills prints "Skills 50" and the coordinator prints "Waiting for background work", while the model is cut to "Op". His priority: the model and the machine the work runs on; voice, skills and idle or waiting matter less.

Same session, second report: he is on the M4 (red) with its coordinator open, a linux-mini thread open on the right, and a blue line across the top of the whole window. He could not tell what that line refers to. In code (`apps/web/src/studio/windowMachine.ts`) a thread's claim outranks its project's, so the window-wide bar follows the right-hand thread (linux-mini, blue) while the coordinator in the middle runs on the M4 (red). The right-hand thread's composer also loses its machine border whenever a banner sits above it ("Resume with less context", "11 subagents"): `ComposerSurface` hides the host outline that carries the color.

Evidence: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-74d44936-f7a2-46e4-ac46-7192657a7ff1.png`, `...-5326f41a-10b2-4326-b96e-dc38a923abde.png`, `...-e9f007f6-f088-40b4-9680-2acf4149a7a4.png`, `...-8af2e0e5-425a-411a-a06b-d2f8be89689e.png`.

## Scope

In: the web app's thread composer foot (ChatComposer), the coordinator composer foot (CoordinatorComposer, OrchestratorSwitcher, ProjectWorkspaceSurface), the draft "Run on" picker, the Voice and Skills triggers, the window machine bar and per-pane machine edges, the thread composer's machine border under a banner. Desktop, narrow windows and phone widths in the web app.

Out: the native iOS and Android composer (it has no machine chip or Voice menu, so nothing to change there); the machine menus' contents (view, move, add, leave stay as they are); the model chip's own fit steps (1284); routine and scheduled-task forms, whose "Runs on" is a form label, not a chip.

## Acceptance Criteria

- [ ] AC-01: Two or three designs are mocked up at desktop, half and phone width, one is picked with the reason, and the mockup page is saved in this increment's reports.
- [ ] AC-02: The machine chip keeps "Runs on <machine>" and sits first, with the model right beside it on the same row: the thread chip and the coordinator chip read in full (not cut, not shortened) at 1100, 600 and 390 px.
- [ ] AC-03: In the thread composer the model's name stays readable at 390 px and up: below 560 px the foot wraps, machine and model on the first row and voice, attach, skills and Send on the second; Send shows the machine's short label instead of "Send to <machine>" below 720 px. The machine chip counts at its full width in the fit, so other controls fold before its name is cut; only when even that does not fit does it shrink to its short label, never hiding the machine and model.
- [ ] AC-04: Voice and Skills are icon buttons at every width (no "Voice" or "Skills 50" words); their tooltip and accessible name keep the full wording and count, and their menus work as before.
- [ ] AC-05: The coordinator foot shows the machine and the model together on its first row when they fit; its run state is a dot with a tooltip, and it shows words only when it needs the person ("Needs you", "Run failed").
- [ ] AC-06: No window-wide machine bar. Each pane says which machine runs it by its own colored leading edge: the coordinator pane in its machine's color, the thread pane in its thread's machine color.
- [ ] AC-07: A thread composer keeps its machine-colored border while a banner (resume, subagents) sits above it, as the coordinator composer does.
- [ ] AC-08: A headless browser check renders the real composer controls at 1100, 600 and 390 px in light and dark, asserts the above, and saves before and after screenshots.

## Approach

Picked design (mockups in `reports/composer-foot-mockups.html`): machine and model side by side as the first two controls; everything else on the line is an icon. Revised the same day (D-05): "Runs on <machine>" stays, both it and the model read in full at every width, and a narrow foot wraps to a second row for the icons and Send instead of cutting either. Rejected: one split chip holding machine and model (two menus behind one pill, hard to hit on a phone, and the model picker's fit logic measures its own trigger); moving the machine onto the composer's top border (it would sit far from the model and collide with banners).

Machine color per pane: each pane's leading edge (2px, inset) wears the machine that runs that pane; the composer border and Send keep it too. The window-wide bar and its claim store go, since two panes on two machines cannot share one bar.

Files, in order:

1. `apps/web/src/components/chat/ThreadMachineComposerChip.tsx`, `apps/web/src/components/chat/restingComposerControlsMeasurement.ts`: the chip loses its narrow-width cap and counts at its full width; `ComposerPrimaryActions.tsx`: Send's short label below 720 px.
2. `apps/web/src/components/studio/ComposerVoiceMenu.tsx`, `apps/web/src/components/chat/ComposerSkillsPopover.tsx`: icon triggers with tooltips.
3. `apps/web/src/components/chat/ChatComposer.tsx`: below 560 px the foot wraps, the controls take the first row and the actions the second.
4. `apps/web/src/components/studio/ProjectWorkspaceSurface.tsx`, `apps/web/src/components/studio/shell/shell.css`: coordinator foot order and state dot.
5. `apps/web/src/components/MachineWindowTint.tsx`, `apps/web/src/studio/windowMachine.ts`, `apps/web/src/routes/__root.tsx`, `apps/web/src/components/ChatView.tsx`, `apps/web/src/components/chat/ComposerSurface.tsx`: per-pane edge, border under a banner.

Risks: ChatComposer's footer fit is measured from the DOM; changing chip widths moves fit thresholds, so `composerFooterLayout` and `restingComposerControlsMeasurement` tests and the composer-controls fixture are rerun. PR #327 (open) touches OrchestratorSwitcher's menu, not its trigger; rebase on whichever merges first.

## Decisions

### Asked
- D-01 Priority on the composer line → model and machine first; voice, skills, attach and idle or waiting become icons (Anton, November 13, 2026).
- D-02 Machine color cue → per pane instead of one window-wide top line; the thread composer gets a machine border like the coordinator's (Anton and the coordinator, November 13, 2026).
### Defaulted (change any before sw-do)
- D-03 The coordinator's run state keeps words for "Needs you" and "Run failed" only: those ask the person to act; every other state is a dot with a tooltip.
- D-04 Skills shows its icon only; the count moves to the tooltip and accessible name.
- D-05 "Runs on" stays (Anton, November 13, 2026, revising D-01's first pass): the machine chip first, the model next to it, both readable at every width; the less important controls give way.
### Open
- none

## Tasks

The composer-foot Test runs in this machine's verification copy (`specweave-studio checks copy`), moved to the PR's head; the shared checkout is not touched.

### T-01 Mock up two or three designs and pick one
- AC: AC-01 | Files: .specweave/increments/1321-composer-foot-shows-the-model-and-machine-first-no-runs-on-wording-voice-skills-and-run-state-as-icons/reports/composer-foot-mockups.html | Test: test -s .specweave/increments/1321-composer-foot-shows-the-model-and-machine-first-no-runs-on-wording-voice-skills-and-run-state-as-icons/reports/composer-foot-mockups.html

### T-02 Machine chip keeps Runs on and its full width
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ThreadMachineComposerChip.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/restingComposerControlsMeasurement.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/restingComposerControlsMeasurement.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/thread-machine/verify.mjs | Test: specweave-studio checks run --label 1321 -- bash -c 'cd ~/.specwithcode/m4/verify/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/composer-foot/vite.config.ts > /dev/null && node apps/web/tests/composer-foot/verify.mjs ~/.specwithcode/m4/evidence/composer-foot-1321'

### T-03 Model keeps its name; voice and skills as icons
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ChatComposer.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ComposerPrimaryActions.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ComposerVoiceMenu.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ComposerSkillsPopover.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/index.css | Test: specweave-studio checks run --label 1321 -- bash -c 'cd ~/.specwithcode/m4/verify/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/composer-foot/vite.config.ts > /dev/null && node apps/web/tests/composer-foot/verify.mjs ~/.specwithcode/m4/evidence/composer-foot-1321'

### T-04 Coordinator foot: machine and model first, state as a dot
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/shell.css | Test: specweave-studio checks run --label 1321 -- bash -c 'cd ~/.specwithcode/m4/verify/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/composer-foot/vite.config.ts > /dev/null && node apps/web/tests/composer-foot/verify.mjs ~/.specwithcode/m4/evidence/composer-foot-1321'

### T-05 Per-pane machine edge; thread composer border under a banner
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/MachineWindowTint.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/windowMachine.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/routes/__root.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/index.css, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/picker-calm/fixture.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/picker-calm/verify.mjs | Test: specweave-studio checks run --label 1321 -- bash -c 'cd ~/.specwithcode/m4/verify/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/composer-foot/vite.config.ts > /dev/null && node apps/web/tests/composer-foot/verify.mjs ~/.specwithcode/m4/evidence/composer-foot-1321'

### T-06 Headless check at three widths, light and dark, before and after
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/composer-foot/verify.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/composer-foot/main.tsx | Test: specweave-studio checks run --label 1321 -- bash -c 'cd ~/.specwithcode/m4/verify/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/composer-foot/vite.config.ts > /dev/null && node apps/web/tests/composer-foot/verify.mjs ~/.specwithcode/m4/evidence/composer-foot-1321'

### T-07 Verify and close 1321
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: .specweave/increments/1321-composer-foot-shows-the-model-and-machine-first-no-runs-on-wording-voice-skills-and-run-state-as-icons/spec.md | Test: specweave verify 1321-composer-foot-shows-the-model-and-machine-first-no-runs-on-wording-voice-skills-and-run-state-as-icons
