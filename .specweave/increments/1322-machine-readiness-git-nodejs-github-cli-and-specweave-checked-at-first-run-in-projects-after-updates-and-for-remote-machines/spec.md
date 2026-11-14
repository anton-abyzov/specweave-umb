# Machine readiness: Git, Node.js, GitHub CLI and SpecWeave checked at first run, in projects, after updates and for remote machines

## Problem

On November 13, 2026, Anton created a project on his Windows PC (SpecWithCode 1.0.281) and was told SpecWeave and Node.js were not installed. When he tried to add GitHub Copilot (which he uses through his enterprise account in VS Code), the Sign in step failed with "Device sign-in requires a compatible Copilot CLI 1.x (1.0.95 or newer), device-code support and a working local Node.js runtime". That one message covers four different causes, including the real one on that PC: no Node.js, so Copilot CLI (an npm package) cannot run.

Machine basics (1318, PR #321) checks Git, Node.js and gh only in first-run setup, and only from the release after 1.0.281. Nothing checks again after an app update, SpecWeave CLI is not part of it, remote machines cannot be set up from the coordinator's machine, and providers that already have an install or a sign-in on the machine (Copilot in VS Code, gh) are not detected.

## Scope

In: one machine-readiness model per machine covering Git, Node.js, GitHub CLI and SpecWeave CLI, plus provider readiness for agents (installed? signed in?), shown in three places: first-run setup, project creation or SpecWeave setup, and after each app update, where a quiet sweep installs what is missing and replaces app-installed pins that are too old, only while the machine is idle. Settings > Machines shows the same rows for every machine, local or remote over Connect, with Install. Copilot sign-in failures name their real cause, offer Install Node.js when Node.js is the cause, and the sign-in step tells the person when it finds Copilot in VS Code or gh signed in, including an enterprise host. Windows: portable, no-admin installs (Node.js zip, gh zip, SpecWeave into the app's folder), Git through winget. A live install job on GitHub Actions windows-latest, ubuntu and macOS.
Out: reading, copying or passing any existing token (VS Code's, gh's) to another tool; replacing a Node.js, gh or SpecWeave the person installed; installing Git without the person pressing Install (it needs an installer and admin rights on Windows); Python, Docker, Homebrew.

## Acceptance Criteria

- [x] AC-01: A machine's server reports Git, Node.js, GitHub CLI and SpecWeave CLI, each with presence, version when known, whether the app installed it, whether it is too old, and whether the app can install or update it, and an older client still reads the answer.
- [ ] AC-02: Installing SpecWeave puts the pinned 3.x release in the app's own folder with the app's or the machine's Node.js, no admin rights and no shell-profile edits, and agents and SpecWeave setup find it without a restart.
- [x] AC-03: After the app starts on a new version, a sweep waits until no thread is running, then installs any missing Node.js, gh and SpecWeave the app can install and replaces app-installed ones older than the pins; it never installs Git, never touches the person's own tools, never runs while work is running, and records what it did.
- [ ] AC-04: First-run setup, Settings > Machines (each machine, local or remote over Connect) and the SpecWeave setup or new-project failure show the same rows with Install, Update and Install everything missing, and a read-only viewer sees the rows without the buttons.
- [ ] AC-05: Copilot sign-in failures say which of these it is: Node.js missing (with Install Node.js), Copilot CLI too old or not installed (with Install or Update), or the CLI not answering; the old catch-all text is gone.
- [ ] AC-06: The Copilot sign-in step says when it finds Copilot in VS Code or a gh sign-in on that machine, names the account and host (github.com or an enterprise host) without reading any token, and starts device sign-in against that host.
- [ ] AC-07: The live install of Node.js, gh and SpecWeave into a new home passes on GitHub Actions windows-latest, ubuntu-latest and macos-latest.
- [ ] AC-08: Every new phrase is translated in all 8 phrase catalogs.
- [ ] AC-09: Add to another machine checks the destination's Git, Node.js and SpecWeave while the copy is prepared and, when one is missing there, shows that machine's rows with Install; tools and provider sign-ins are never copied.

## Approach

Server: extend `apps/server/src/machineTools/` with a `specweave` tool (npm `install --prefix <home>/tools/specweave` with the found Node.js, pinned `SPECWEAVE_VERSION` in `provision/manifest.ts`, minimum 3.1.21), versions and `managed`/`outdated` per tool. Wire compatibility: `MachineToolsCheck` keeps its fields; the richer answer is a new optional `tools` array, so an old client ignores it and `installable` never carries the new id. A new `machineTools/readinessSweep.ts` started from `server.ts` compares the running version with `<home>/provision/readiness.json`, polls the runs projection until idle, installs through the same lock as the RPC, and writes the result. Copilot: `CopilotDeviceAuthentication.ts` splits the catch-all into causes with a `needs` hint; a read-only probe lists gh hosts and accounts (`gh auth status` text, never `--show-token`) and whether VS Code has the GitHub Copilot extension (its folder exists), then the sign-in step shows it and passes `--host` for an enterprise host. Web: `MachineBasics.tsx` grows the SpecWeave row, Update and Install all; `MachineReadinessChecklist.tsx` mounts it per machine; the Copilot sign-in step renders the cause and the found sign-ins. CI: `.github/workflows/machine-tools-live.yml` runs the live test on three OSes when `apps/server/src/machineTools/**` or `provision/manifest.ts` change.

Rejected: reusing VS Code's or gh's token for Copilot (reads secrets; the person signs in once with device code instead); installing Git silently (admin prompt on a busy machine); a new Settings toggle for the sweep (it only adds files to the app's folder while idle; it can be added later).

## Decisions

### Asked
- D-01 Anton (November 13, 2026): one machine-readiness model with the tools a project needs plus providers, shown at first run, project creation and after updates; remote machines set up from the coordinator over Connect; never force anything on a busy machine.
### Defaulted (change any before sw-do)
- D-02 New increment instead of extending 1318: 1318's PR has merged and it closes on its own release check.
- D-03 The after-update sweep is on by default with no setting; it installs only into the app's folder and only while idle.
- D-04 Existing sign-ins are detected and named, never reused: Copilot still needs one device sign-in in SpecWithCode.
- D-05 Anton (November 13, 2026): copying a project to another machine should check that machine's tools; tools and sign-ins stay per machine.
### Open
- none

## Tasks

### T-01 SpecWeave CLI and versions in the machine check
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/machineTools.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/machineTools/machineTools.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/machineTools/specweaveTool.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/machineTools/rpc.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provision/manifest.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/SpecweaveSetup.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/machineTools/machineTools.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/machineTools src/project/SpecweaveSetup.test.ts

### T-02 Readiness sweep after an app update
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/machineTools/readinessSweep.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/machineTools/readinessSweep.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/server.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/machineTools/readinessSweep.test.ts

### T-03 Copilot sign-in names its cause and finds existing sign-ins
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/acp/CopilotDeviceAuthentication.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/acp/AcpRegistryAuth.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/acp/copilotExistingSignIns.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/acp/CopilotDeviceAuthentication.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/acp/ProviderAuthFlow.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/providerSetup.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/acp/AcpRegistryAuth.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/provider/acp/CopilotDeviceAuthentication.test.ts src/provider/acp/copilotExistingSignIns.test.ts

### T-04 Readiness rows at first run, in Settings > Machines and where setup fails
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/MachineBasics.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachineReadinessChecklist.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/machineTools/MachineToolInstallDialog.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/machineTools.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/MachineBasics.test.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/onboarding src/components/machineTools src/components/settings/MachineReadinessChecklist.test.tsx

### T-05 Live installs on Windows, Linux and macOS in CI
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/.github/workflows/machine-tools-live.yml, repositories/anton-abyzov/specwithcode-dev/apps/server/src/machineTools/machineTools.test.ts | Test: gh run list -R anton-abyzov/specwithcode --workflow machine-tools-live.yml -L 1 --json conclusion -q '.[0].conclusion' | grep -qx success

### T-06 Translations
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases/ru.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/i18n/i18n.test.ts

### T-08 Add to another machine checks the destination's tools
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/machineTools/DestinationReadiness.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/machineTools/DestinationReadiness.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/AddToMachineDialog.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/AddToMachineDialog.test.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/machineTools/DestinationReadiness.test.tsx src/components/chat/AddToMachineDialog.test.tsx

### T-07 Verify and close 1322
- AC: AC-01, AC-03 | Files: none | Test: specweave verify 1322
