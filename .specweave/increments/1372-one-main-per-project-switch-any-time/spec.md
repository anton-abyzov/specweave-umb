# 1372 One main per project, switch any time

## Problem

Anton, November 16, 2026, setting up M5: the "Copy to another machine" dialog asks "Copy or move" (Copy: "Keep working here"; Move: "Work continues there, and this copy stops starting work"). Neither deletes anything. The only difference is which machine runs the coordinator ("Main"), and after a plain copy the copy machine's coordinator box is locked ("Open m4's coordinator" only), which he called impractical. He asked for no choice at copy time, every copy able to run the coordinator, and "Make X main" as a separate switch flipped any time.

Design and review: `.specweave/reports/main-switch/options.png` (three options, A picked) and `.specweave/reports/main-switch/review-muse-wonder-1.0.md` (muse-wonder-1.0, xhigh: A with changes). Decision: project memory `decision_copy_to_another_machine_flow.md` ("One main, switch any time").

Facts checked on origin/main (`repositories/anton-abyzov/specwithcode`):
- A copy linked as workers is `transferred` with `successor` = the kept main (`apps/server/src/project/ProjectLink.ts` accept, about line 667), which is what `takeover` requires (about line 1110). `takeover` names the old main as predecessor, so it gives way on reconnect through `supersede` (`apps/web/src/components/studio/CoordinatorSync.tsx`). `startCoordinator` names none and yields two mains ("also main").
- The 10-minute unreachable guard is web policy only: `TAKEOVER_UNREACHABLE_MS` and `takeoverAvailability` in `apps/web/src/studio/projectLink.ts`.
- Manual takeover claims no epoch on worker machines. Only the automatic paths call `studio_coordinator_claim_epoch` (`apps/server/src/project/CoordinatorStandbyRearm.ts`, `apps/server/src/fleet/RemoteWorkerAdoption.ts`), so reachable workers keep obeying the old main.
- Starting the move on the old main needs `orchestration:operate`, `filesystem:write` and `source-control:write` there (`packages/contracts/src/clientRpcPermissions.ts` machineHandoffPrepare), not `access:write`.
- On an unlinked copy, "Move coordinator to X…" also links the projects and overwrites X's goal and instructions (project memory `reference_unlinked_projects_and_remote_sends.md`). The sidebar link offer is limited to two copies (`apps/web/src/components/studio/projectRepositoryRows.logic.ts` about line 157). Settings > Machines says "Not shared" for a copy the menu calls "not linked".

## Scope

In:
- "Make {machine} main" in the machine menu and in a copy's message box.
- The offline switch through `takeover` with epoch claims.
- The copy's message box.
- "Link X to this project…" replacing Move on unlinked copies.
- The link offer for two or more copies.
- The Settings label.
- Translations and headless captures.

Out:
- Sending from the copy without leaving its page.
- Fencing an offline old main's local work.
- Merging conversations.
- Removing `copy-and-move` from the contract.
- Cleaning up m1's `machine-handoff:` projects.
- Linking EasyChamp's copies. That is a live action, run once the new link flow ships.

## Acceptance Criteria

- [x] AC-01: On any linked copy that only runs workers (not main, not also running its own coordinator), the machine menu offers one item, "Make {machine} main". With the old main reachable it runs the existing coordinator move: the conversation moves and the old main becomes a copy. A machine that is already main gets no item. When this app never loaded main, the item shows disabled with "Connect {machine} first".
- [x] AC-02: With the old main unreachable for 10 minutes or more, "Make {machine} main" runs `takeover`, never `startCoordinator`. The project then has one main: the old one reads as superseded, not "also main". Before 10 minutes the item is disabled and says when it unlocks.
- [x] AC-03: After a manual takeover, the new main claims its epoch on every reachable member machine, so steering from the old main to a reachable worker machine is refused (`thread_fenced`). A machine that cannot be reached is reported, not retried forever.
- [x] AC-04: A copy's message box no longer dead-ends. It reads "Main for {project} is {machine}" and offers "Write to {machine}'s coordinator" (opens that page) and "Make {this} main", under the same rules as AC-01 and AC-02. After an offline switch it says the old conversation stays on the old machine as history.
- [x] AC-05: An unlinked copy (same repository, registered on its own) gets no "Move coordinator to X…". It gets "Link {machine} to this project…". The confirmation names what that machine loses (its own coordinator stops; its goal and instructions are no longer used, and are replaced only if it later becomes main), and linking does not change main.
- [x] AC-06: The sidebar link offer appears for two or more unlinked copies of one repository (EasyChamp: m1, m3, m4), not only exactly two.
- [x] AC-07: Settings > Machines labels an unlinked copy that exists elsewhere "Not linked · also on {machines}", never "Not shared" or "No other machine has a copy of this project".
- [x] AC-08: Headless captures, light and dark: the menu on a copy with "Make M5 main", the copy's message box, an unlinked trio with "Link…", and the Settings label. They are saved in `reports/screens/`.
- [ ] AC-09: The "Copy to another machine" dialog has no "Copy or move" radio for the folder method. A copy is always copy-only and Main stays where it was (Git only still moves Main). The header names the real current Main: "From {source}. Main stays on {main}." When {source} is not linked to the project the destination belongs to, the dialog says so and never moves Main or relinks the destination silently. Copying into a machine that already holds a linked copy offers "Make {machine} main" on the done screen (`makeMain`).

## Approach

Order: the switch (T-01 to T-03) ships first, and the dialog thread drops the radio only after it merges. Otherwise copying would lose its only way to move main. The Settings label (T-05) waits for PR #499, which has that file open.

- **Server:** after `takeover` succeeds, the server claims the new epoch on each linked member's fleet machine through the existing `studio_coordinator_claim_epoch` client call, as the standby path does. No new RPC, scope or grant.
- **Web:** a `makeMain(copy)` helper picks the path. If the old main is connected, it uses the existing coordinator move (`useCoordinatorMove`/`useCoordinatorTransfer`, the same confirm). If the old main is past the guard, it calls `projectLink.takeover`. If neither, it is disabled with the time left.
- **Rejected:**
  - Every copy coordinating at once: duplicate planning and claims.
  - Typing from anywhere to one coordinator: it is dead when main sleeps.
  - Dropping the 10-minute guard: a briefly closed laptop would lose main.
- **Risks:**
  - The online move needs write scopes on the old main. A window holding only a Connect read session there gets a refusal that says so. The test covers the message.
  - An offline old main can start local work until it reconnects. This is accepted and stated in the decision.

## Decisions

### Asked
- D-01 Remove Copy or move; one main with a switch you can flip any time → yes (Anton, November 16, 2026).
- D-02 An offline switch starts without the old conversation, which stays on the old machine → yes (Anton).
- D-03 Link EasyChamp's three unlinked copies → yes (Anton). Main stays m4 (default, below).

### Defaulted (change any before sw-do)
- D-04 Keep the 10-minute guard for offline switches → default (Muse recommended).
- D-05 EasyChamp main stays m4 when linked → default; Anton can switch it.
- D-06 "Write to {machine}'s coordinator" opens that page rather than sending in place → default for the first build.

- D-07 "Run {machine}'s coordinator again" leaves the copy's message box and stays only in Settings → accepted after the PR 516 review.

### Open
- none

## Tasks

### T-01 Manual takeover claims its epoch on reachable members
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectLink.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectLinkRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/takeoverEpochClaims.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/takeoverEpochClaims.test.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/server && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/project/takeoverEpochClaims.test.ts src/project/ProjectLink.test.ts

### T-02 Make X main in the machine menu; Link instead of Move for unlinked copies
- AC: AC-01, AC-02, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectLink.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/makeMain.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/makeMain.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/studio/OrchestratorSwitcher.test.tsx src/studio/makeMain.test.ts

### T-03 A copy's message box offers Write to main and Make this main
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorBlockedNotice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CoordinatorBlockedNotice.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/workersOnlyCopy.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/studio/CoordinatorBlockedNotice.test.tsx src/components/studio/ProjectWorkspace.threads.test.tsx

### T-04 Link offer for two or more unlinked copies
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/duplicateProjectLink.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/duplicateProjectLink.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectRepositoryRows.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectRepositoryRows.logic.test.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/studio/projectRepositoryRows.logic.test.ts

### T-05 Settings says Not linked, also on (after PR #499)
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/machinesSettings.logic.test.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/settings/machinesSettings.logic.test.ts

### T-06 Translations and headless captures
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/verify.mjs | Test: cd ~/.specwithcode/m4/verify/specwithcode && node node_modules/vite-plus/bin/vp build --config apps/web/tests/coordinator-menu/vite.config.ts && node apps/web/tests/coordinator-menu/verify.mjs /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1372-one-main-per-project-switch-any-time/reports/screens

### T-08 Copy dialog: no Copy or move, header names the real Main
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMoveOptions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopySetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineHandoffDialog.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/sendToMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyDone.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyFooter.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyStepPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.busy.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.cancel.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.retention.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.sourceChanges.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.testkit.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.mainSwitch.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMachineHandoff.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/handoffFolderCopyRules.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useCopyDraft.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useCopyLink.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/sendToMachine.test.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/done-reopen.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/screens.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/send-screens.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/stubs.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/machine-folders/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/machine-folders/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/machine-handoff/verify.mjs | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/studio/MachineHandoffDialog.test.tsx src/components/studio/HandoffFolderCopy.test.tsx

### T-07 Verify and close 1372
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: .specweave/increments/1372-one-main-per-project-switch-any-time/spec.md | Test: specweave verify 1372-one-main-per-project-switch-any-time
