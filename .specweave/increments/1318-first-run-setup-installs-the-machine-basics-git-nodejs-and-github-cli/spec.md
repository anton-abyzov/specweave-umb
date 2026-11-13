# First-run setup installs the machine basics: Git, Node.js and GitHub CLI

## Problem

On a brand-new Mac, Windows or Linux machine, SpecWithCode's first-run setup only notices a missing Git (and only offers a button on a Mac). Node.js, which SpecWeave setup needs, and the GitHub CLI, which publishing needs, are not checked at all. People find out later, from a failed "Set up SpecWeave" or a failed new project, with a text that tells them to go install something by hand.

## Scope

In: a quiet "Machine basics" block in the onboarding Agents step that checks Git, Node.js and GitHub CLI on the machine being set up; one-click installs where one is safe without an admin password (Mac Git through Apple's developer tools, Windows Git through winget, Node.js 22 and gh from pinned SHA-256 checked downloads into the app's own folder); a copyable package-manager command for Git on Linux; install buttons where SpecWeave setup fails for a missing Node.js and where a new project fails for a missing Git; translations in every language.
Out: Python, Homebrew, Docker; replacing a Node.js from Homebrew, nvm, fnm or volta; editing shell profiles; signing gh in (that stays the person's step); a Settings > Machines column (see D-03).

## Acceptance Criteria

- [ ] AC-01: A machine's server answers which of Git, Node.js and GitHub CLI it has, which package manager it has (winget, apt, dnf, pacman, zypper), and which of them it can install itself.
- [ ] AC-02: Installing Node.js or gh downloads the pinned build, refuses a checksum mismatch, unpacks into the app's folder without admin rights, streams its log, and never replaces a Node.js the machine already has.
- [ ] AC-03: After a Node.js install, SpecWeave setup and the agents' PATH find it without a restart and without shell-profile edits.
- [ ] AC-04: The Agents step shows one quiet line when everything is present, a row only for each missing tool, gh under a collapsed optional line, a visible log for every install, and never blocks Continue.
- [ ] AC-05: Git installs in one click on a Mac (developer tools) and on Windows with winget; elsewhere on Windows a git-scm.com link; on Linux a copyable distro command and Check again.
- [ ] AC-06: A SpecWeave setup that fails for a missing Node.js, and a new project that fails for a missing Git, offer the install there.
- [ ] AC-07: Every new phrase is translated in all 8 phrase catalogs.

## Approach

Server: `apps/server/src/machineTools/` (check + install, pins added to `provision/manifest.ts` for darwin-x64 and Windows), a `machineTools.check` / `machineTools.install` RPC group shaped like provisioning (`machineTools.install` streams log lines), managed tool folders added to the process PATH at start and after an install, and to `nodeToolDirs` for SpecWeave setup. Web: `MachineBasics.tsx` in the onboarding Agents step replacing the single Git row (falls back to the old Git row for a server that does not answer the new call), a shared install-with-log component reused by the JIT spots and a small global install dialog. Rejected: running Node/gh installs as a terminal command string (no pinned checksum check on Windows, shell differences); reusing the whole provision runner (Linux/Mac-arm only, needs a lock and plan).

## Decisions

### Asked
- D-01 Plan approved by the owner (artifact 5mVKJwWfcCj3W6Y6t4TZhm): check first, install only what is missing, visible button and log, no admin password, skipping always fine.
### Defaulted (change any before sw-do)
- D-02 Node.js and gh land where provisioning already puts them (`<home>/runtime/node/<stem>`, `<home>/tools/gh/<version>`), so provisioning and install.sh recognise them.
- D-03 Settings > Machines: skipped if it does not fit cleanly; reported in the PR.
### Open
- none

## Tasks

### T-01 Machine tools check and install on the server
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/machineTools.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/rpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/machineTools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/rpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/machineTools.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provision/manifest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/nodeToolDirs.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/os-jank.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/machineTools src/project/nodeToolDirs.test.ts src/project/SpecweaveSetup.test.ts

### T-02 Machine basics block in the Agents step
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/MachineBasics.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AgentsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineTools.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/MachineBasics.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/onboarding

### T-03 Install where SpecWeave setup or a new project fails
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectSpecweaveSetting.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/hooks/useNewProject.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/machineTools/MachineToolInstallDialog.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/machineTools src/components/studio

### T-04 Translations
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/i18n/i18n.test.ts

### T-05 Verify and close 1318
- AC: AC-01, AC-04 | Files: none | Test: specweave verify 1318
