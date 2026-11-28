# Choose User or This project when installing a skill on this machine

## Problem

On M5 (November 20, 2026) the owner installed the registry skill `rea` on this machine. It landed in the project (`vskill.lock` entry `scope: "project"`) and nothing offered to install it for the user instead. On November 28, 2026 the owner hit the same wall in Settings > Skills for `firstproject`: the search showed `obsidian-brain` 1.0.12 from `anton-abyzov/vskill` with one Install button and nothing to choose where it goes. The owner asked for the choice at install time, a remembered default (for the user, for all projects, or for one project), and for the personal assistant to default to the user.

The this-machine installs (`SkillSearch.tsx` `install()` and `SkillUpdateRepos.tsx` `install()`) send no scope. The server follows the open view: `SkillUpdate.ts` `runInstall` installs with `--global` from the home folder only when the request carries `userLevel`, which only the machine view (no project) sends. Nothing on screen says which one it will be.

The Install button "kept spinning". The server trace for that click (November 28, 2026, 08:22:11 UTC, M5) shows the run did not hang: the `projects.skillsUpdate` call returned Success after 10.1 s (about 2.7 s of source checks, 2.3 s of `vskill install`, about 5 s of agent rescans). The client then rescanned the agents and searched again at 08:22:21. The lock entry was written at 08:22:16 into `firstproject/vskill.lock` with `scope: "project"`. The screenshot shows the pre-install state, so it was taken inside those 10 s. The real defects: 10 s with a spinner and no words, every Install button disabled meanwhile, and `install()` has no `finally`, so a thrown command would leave the buttons disabled for good.

Research and the per-provider folder table: [install-ux-research.md](reports/install-ux-research.md). Mockup: [install-mockup.html](reports/install-mockup.html).

## Scope

This slice (November 28, 2026): the scope choice for every this-machine install, the remembered default with its three levels, Percy's default, progress and receipt wording, and the spinner. Mac, Windows and Linux: the run is the same `vskill install <link> -y [--global]` argv the server already spawns through the Windows-aware process runner; vskill already has `--global`, so vskill needs no change or release for this slice.

Later slice (not in this increment's closure): agent chips for every agent SpecWithCode runs, custom agents, and vskill accepting a named agent that is not detected (the former AC-05 to AC-08, kept below under "Later slice" for the follow-up increment). Also later: "Also add on" for a project-scope copy (the target machine already supports `scope: "project"`; the web rollout sends User only).

Out: moving or re-scoping an existing copy; automatic removal of the copy at the other scope; a third "local" scope; installing vskill on another machine (1399).

## Acceptance Criteria

- [ ] AC-01: Every this-machine install (the search's "Available in a connected repo" rows and the connected repo list) shows "Install for" with two choices, "You, in every project" and "This project", each naming where it writes (the home folder, or the project folder). With no project open (the machine view) only the first applies and is stated. The choice is visible before Install is pressed.
- [ ] AC-02: The request carries the chosen scope explicitly (`install.scope`). The server installs with `vskill install <link> -y --global` from the home folder for "user" and without `--global` from the project folder for "project", whatever view is open. A server test asserts argv and working folder for both, and the lock path read back. An older server that does not report the `skillInstallScope` capability gets no chooser; the panel says the install follows the view there.
- [ ] AC-03: A remembered default with three levels, resolved in this order: the project's own setting ("Follow machine default", "You, in every project", "This project"); then the personal assistant (Percy's project) installs for you; then the machine's default; then the built-in default (D-06). The chooser starts on the resolved value and says where that value comes from.
- [ ] AC-04: The default can be set from the chooser ("Make this the default for this project" or "for every project on <machine>") and from Settings > Skills in the machine view (the machine default). Both write the machine's settings; a project's choice goes in that project's settings overrides. Changing it needs the settings-write permission and is refused by the server without it.
- [ ] AC-05: While an install runs, a status line says "Installing <skill> for <scope words> on <machine>…" and every Install button waits until it ends. The receipt states skill, version and the scope read back from the lock ("for you, in every project" or "for this project"). A failed or thrown run always re-enables the buttons.
- [ ] AC-06: After a "You, in every project" install, from the search or the connected repo list, the existing "Also add on" step is offered for other machines (1399). After a "This project" install the receipt says that adding it on other machines works for skills installed for you in every project.

## Approach

1. Contracts: `SkillInstallScope = "user" | "project"`; `install.scope` on `ProjectSkillsUpdateInput`; `skillInstallScope` in `ServerSettings` (machine default) and in `ProjectSettingsOverrides`; capability `skillInstallScope`; `scope` on each install outcome, taken from the lock that was read back.
2. Server: `runInstall` uses `install.scope` when present, else the view as before. Report the capability.
3. Web: one tested `skillInstallScope.logic.ts` resolves the default and words; a `SkillInstallScopeChoice` control in `SkillUpdateCenter` drives both install callers; machine default control in the machine view; progress, receipt and `finally`.

Where the setting lives, and why: in each machine's server settings, with a per-project override in that machine's `projectSettingsOverrides`. Skills are per machine (decision 1399: one vskill lock per machine, Skills page shows one machine), every install runs on the machine that owns the folders, and the server already resolves per-project overrides the same way for other settings, so the default sits next to the lock it affects and works from any window viewing that machine. Percy's default is a rule, not a stored value, so it follows Percy to any machine and a project setting still wins.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 (replaced November 28, 2026): the owner asked for a remembered default, which replaces "follow the open view" and the research report's rejection of a default setting. One source of truth: the explicit default; no silent "last choice" memory.
- D-02: No automatic removal of the copy at the other scope (reversible).
- D-03: Pattern: Claude Code's install-time scope question in two choices, worded by who gets the skill (research report).
- D-06 (owner decision, defaulted): the built-in default for a project is "This project", which matches vskill's own default and keeps a project's skills in its repository for collaborators; Percy and the machine view install for you. The owner can flip the machine default to "You, in every project" in one click.
- D-07: The default lives in the machine's server settings with a per-project override (see Approach).
### Open
- D-05 (user, later slice): where custom agents are stored. Recommended: in vskill (`~/.vskill/agents.json` plus `vskill agents add`).

## Tasks

### T-01 Contracts and server: explicit install scope, settings keys, capability
- AC: AC-02, AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSkillRepos.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdate.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settingsScopes.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdate.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/projectSkillsInventory.ts, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/settings_continuity.py | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/project/SkillUpdate.test.ts packages/contracts/src/settingsScopes.test.ts (from repositories/anton-abyzov/specwithcode)

### T-02 Web: scope logic, chooser, default, progress and receipt
- AC: AC-01, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/skillInstallScope.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/skillInstallScope.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillInstallScopeChoice.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillUpdateCenter.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillSearch.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillSearch.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillUpdateRepos.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillUpdateOutcome.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillRollout.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/projectOverrideRows.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: node ../../node_modules/vite-plus/bin/vp test run src/components/skills/skillInstallScope.logic.test.ts src/components/skills/SkillSearch.test.tsx (from repositories/anton-abyzov/specwithcode/apps/web)

### T-03 Headless screenshot of the chooser on synthetic data
- AC: AC-01, AC-05 | Files: .specweave/increments/1440-choose-user-or-this-project-when-installing-a-skill-on-this-machine/reports/, repositories/anton-abyzov/specwithcode/apps/web/tests/skill-install-scope/, repositories/anton-abyzov/specwithcode/docs/operations/checks.md | Test: test -s .specweave/increments/1440-choose-user-or-this-project-when-installing-a-skill-on-this-machine/reports/screenshots.md

## Later slice (follow-up increment)

Kept from the November 20 plan, not part of this increment's closure: agent chips listing every agent SpecWithCode runs with "not detected" labels; vskill accepting an explicitly named `--agent` from its full registry with a warning; custom agents with user and project folders stored by vskill and rolled out with "Also add on"; custom agents in lock entries, Settings > Skills and `vskill remove`; Muse Code and Devin skill folders; "Also add on" for project-scope copies.
