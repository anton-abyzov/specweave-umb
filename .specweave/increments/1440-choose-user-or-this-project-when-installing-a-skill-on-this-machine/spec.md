# Choose User or This project when installing a skill on this machine

## Problem

On M5 (November 20, 2026) the owner opened the registry skill `rea` on the skill page and installed it on this machine. It landed in the project (`vskill.lock` entry `scope: "project"`, files under `.agents/skills/rea` with a `.claude/skills/rea` link) and the page offered no way to install it for the user instead.

The choice exists, but only for other machines. `SkillMachineInstall` (`apps/web/src/components/skills/SkillMachineInstall.tsx`) has "User, all projects" and "This project" radios, and `SkillAvailability.tsx:192` renders it only when `machineId` is set, which is never for this machine. "Install on several…" (`ProjectSkillFleetPush.tsx`) lists other machines only. The this-machine install in `SkillSearch.tsx` (`install()` at line 140) sends no scope: it follows whichever view is open, so it goes to the user folder only from Settings > Skills with no project picked (the `folder="~"`, `userLevel` view in `ProjectSkillsSettings.tsx:137`). Nothing on screen says that.

The server already supports both scopes for this machine: `SkillUpdate.ts:646` installs with `--global` from the home folder when `userLevel` is true.

## Scope

In: a visible User / This project choice for every install on this machine (skill page "Available on" card for this machine, and the Install buttons in the skills search panel); the chosen scope sent as `userLevel`; the receipt naming the scope; a hint when the same skill already exists at the other scope; tests and headless screenshots on synthetic data.

Out: moving or re-scoping an existing copy (no "promote to user"); removing copies; changes to vskill; display-only work owned by 1361; other machines' install flow, which already has the choice.

## Acceptance Criteria

- [ ] AC-01: On the skill page, this machine's "Available on" card offers the same install control as other machines' cards: "User, all projects" and "This project" radios, a preview, then a confirmed install. With no project open, only User is offered.
- [ ] AC-02: Every Install button for this machine in the skills search panel shows the scope it will use and lets the person switch it before installing. The default follows the open view (user view: User; project view: This project), so no current flow changes silently.
- [ ] AC-03: Choosing User installs with `vskill install ... --global` from the home folder (server `userLevel: true`); choosing This project installs in the project folder. A test asserts the exact vskill arguments and working folder for both.
- [ ] AC-04: The receipt reads "Installed vX on <machine> for user, all projects" or "... for this project", matching what vskill wrote.
- [ ] AC-05: When the skill is already installed at the other scope on this machine, the control says so ("Also in this project" / "Also installed for the user") before install; nothing is removed or moved.

## Approach

1. Web logic first: reuse `machineInstallPlan` and `scopeLabel` from `SkillMachineInstall.tsx` for this machine; let `SkillMachineInstall` run without a fleet `machineId` by calling the local skill run (`useSkillUpdateRun`) with `userLevel` from the chosen scope.
2. `SkillAvailability.tsx`: render the install control for this machine too.
3. `SkillSearch.tsx`: a small scope toggle beside the install button, passed into the install request through `skillFolderInput`.
4. No server change expected; if the local install path ignores `userLevel` for registry links, add it in `SkillUpdate.ts` with a test.

Risk: `SkillSearch.tsx` and `SkillUpdatePanel` are out of scope for 1361 and partly listed by 1360 (`SkillUpdate*`); check `project_checkout_queue` and 1360's Files before claiming tasks.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The default scope follows the open view, so existing flows keep their behaviour (reversible).
- D-02: No automatic removal of the copy at the other scope; the person removes it with `vskill remove --local` (reversible).
### Open
- none

## Tasks

### T-01 Scope choice for this machine on the skill page
- AC: AC-01, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineInstall.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillAvailability.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineInstall.test.tsx | Test: npx vitest run src/components/skills/SkillMachineInstall.test.tsx (from apps/web)

### T-02 Scope toggle in the skills search panel
- AC: AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillSearch.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillSearch.test.tsx | Test: npx vitest run src/components/skills/SkillSearch.test.tsx (from apps/web)

### T-03 vskill arguments per scope
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdate.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdate.test.ts | Test: npx vitest run src/project/SkillUpdate.test.ts (from apps/server)

### T-04 Headless screenshots on synthetic data
- AC: AC-01, AC-02 | Files: .specweave/increments/1440-choose-user-or-this-project-when-installing-a-skill-on-this-machine/reports/ | Test: test -s .specweave/increments/1440-choose-user-or-this-project-when-installing-a-skill-on-this-machine/reports/screenshots.md
