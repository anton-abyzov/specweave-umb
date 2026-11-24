# Terminal commands switch, on by default, with a stable commands folder

## Problem

Anton, November 15, 2026, looking at `~/.zprofile` on the M5: the SpecWithCode commands block (PR 470) names versioned folders, so it changes on every Node.js, SpecWeave or Codex update, and the only way to stop it is deleting the block by hand. He asked whether apps like Codex and Claude have an uninstaller, and said: "Maybe we should ask during installation about it. I would suggest having it on by default." Today there is no switch, `specwithcode uninstall` leaves the block behind, and a deleted block can never come back.

## Scope

In: a per-machine server setting `terminalCommands` (on by default); one stable folder `<app home>/commands` of links to the current versioned tools, so the block lists only fixed folders; off removes this home's folders from the block, on adds them back; a block the person deletes turns the setting off; Settings > General "Use these commands in Terminal" with a search entry; a ticked line in the existing first-run Agents step (no new wizard step); `specwithcode uninstall` removes the block from every startup file and the commands folder. Out: Windows (no block there), fish and other shells, a new wizard step.

## Acceptance Criteria

- [x] AC-01: The block lists `~/.local/bin`, `~/.local/share/specweave/providers/bin` (when they hold a command) and `<app home>/commands`, never a versioned folder; an update of Node.js, gh, SpecWeave or Codex moves a link in the commands folder and leaves the startup file as it is; a block written by an older build is rewritten to the commands folder.
- [x] AC-02: Links in the commands folder point at the current tools, links to removed tools go, and a file in that folder that is not a link is never touched.
- [x] AC-03: The `terminalCommands` setting defaults to on. Off removes this home's folders from the block (and the block when nothing else is listed) and forgets the file; on adds the block again. Another app home's folders stay while they hold a command.
- [x] AC-04: A block the person deletes turns the setting off instead of coming back; turning it back on adds the block again. The change applies at start, every two minutes, and as soon as the setting changes.
- [x] AC-05: Settings > General shows "Use these commands in Terminal" for each machine, found by searching for terminal, PATH or zprofile; the first-run Agents step shows a ticked "Use claude, codex and specweave in Terminal too" line on macOS and Linux for people who may maintain the machine.
- [x] AC-06: `specwithcode uninstall` on macOS and Linux removes the block from `.zprofile`, `.zshrc`, `.bash_profile` and `.bashrc`, clears the record, deletes the commands folder, and names any file it could not change.

## Approach

`terminalPath.ts` gains `terminalCommandsDir`, `syncTerminalCommandLinks` (links in the commands folder, atomic via a temp link and rename), an `enabled` input to `syncTerminalPath`, and `removeTerminalPathBlocks`. `terminalPathRuntime.ts` reads the setting, runs the links then the block, flips the setting off on "opted-out", and reruns on setting changes. Contracts add `terminalCommands` to `ServerSettings` and its patch. The web adds a `ScopedSwitch` row and search entry and a checkbox under `MachineBasics` in `AgentsStep.tsx`. `uninstall.ts` calls `removeTerminalPathBlocks` and removes the folder.

## Decisions

### Asked
- D-01 On by default, asked as a ticked line during first run, switchable in Settings → yes (Anton, November 15, 2026)
### Defaulted (change any before sw-do)
- D-02 A deleted block turns the switch off rather than staying deleted forever, so the switch is the one source of truth → default
- D-03 The line goes inside the existing Agents step, since a new wizard step breaks the release walkers → default
### Open
- none

## Tasks

### T-01 Terminal commands switch
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/terminalPath.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/terminalPath.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/terminalPathRuntime.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serverRuntimeStartup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/uninstall.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AgentsStep.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/server && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/machineTools/terminalPath.test.ts src/cli/uninstall.test.ts && cd ../web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/onboarding src/components/settings/settingsEntryScope.test.ts
