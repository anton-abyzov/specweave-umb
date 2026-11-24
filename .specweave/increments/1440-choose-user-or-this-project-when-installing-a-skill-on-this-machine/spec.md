# Choose User or This project when installing a skill on this machine

## Problem

On M5 (November 20, 2026) the owner opened the registry skill `rea` on the skill page and installed it on this machine. It landed in the project (`vskill.lock` entry `scope: "project"`, files under `.agents/skills/rea` with a `.claude/skills/rea` link) and the page offered no way to install it for the user instead.

The choice exists, but only for other machines. `SkillMachineInstall` (`apps/web/src/components/skills/SkillMachineInstall.tsx`) has "User, all projects" and "This project" radios, and `SkillAvailability.tsx:192` renders it only when `machineId` is set, which is never for this machine. "Install on several…" (`ProjectSkillFleetPush.tsx`) lists other machines only. The this-machine install in `SkillSearch.tsx` (`install()` at line 140) sends no scope: it follows whichever view is open, so it goes to the user folder only from Settings > Skills with no project picked (the `folder="~"`, `userLevel` view in `ProjectSkillsSettings.tsx:137`). Nothing on screen says that.

The server already supports both scopes for this machine: `SkillUpdate.ts:646` installs with `--global` from the home folder when `userLevel` is true.

Agents are a second gap. The "Install on several…" popover hard-codes Codex, Claude Code and Cursor (`ProjectSkillFleetPush.tsx:272`), but vskill 1.2.18 on M5 refuses Cursor: `Unknown agent(s): cursor. Available: claude-code, codex, copilot-cli`. `filterAgents` (`repositories/anton-abyzov/vskill/src/utils/agent-filter.ts:18`) checks a named `--agent` against detected agents only, and M5 has no `cursor` binary on PATH. SpecWithCode also runs Grok, OpenCode, Antigravity, Pi, Gemini CLI, Muse Code and Devin; none can be picked, Muse has no vskill entry at all, Devin is marked remote-only, and there is no way to add an agent vskill does not know.

Research, comparison and the per-provider folder table: [install-ux-research.md](reports/install-ux-research.md). Mockup: [install-mockup.html](reports/install-mockup.html).

## Scope

In: one install panel used for this machine and other machines, with "Who gets it" (Me, in every project / This project), machine rows with this machine first, agent chips and a one-line preview; every agent SpecWithCode runs; custom agents with a name and user and project skills folders; vskill changes to accept a named agent that is not detected and to read custom agents; tests and headless screenshots on synthetic data.

Out: moving or re-scoping an existing copy (no "promote to user"); automatic removal of copies; display-only work owned by 1361; a "local" third scope; installing vskill on another machine (1399).

## Acceptance Criteria

- [ ] AC-01: The skill page's install panel shows "Who gets it" as two choices, "Me, in every project" and "This project", each with the folder it writes under it, before any Install button. With no project open only the first is offered. The same panel serves this machine and other machines; "Install on several…" opens it.
- [ ] AC-02: Machine rows list this machine first, checked by default, then fleet machines. Each row states its current state for the chosen scope ("Already in this project, 1.0.1", "Not installed", "Offline", "Project not added there").
- [ ] AC-03: The skills search panel's Install buttons for this machine show the scope they will use and let the person switch it. The default follows D-01.
- [ ] AC-04: Choosing "Me, in every project" installs with `vskill install ... --global` from the home folder; "This project" installs in the project folder. A server test asserts the vskill arguments and working folder for both, and the agent ids passed with `--agent`.
- [ ] AC-05: The agent chips list the agents found on the checked machines first, then "Show all agents" with every provider SpecWithCode runs (Claude Code, Codex, GitHub Copilot, Cursor, Gemini CLI, Grok, OpenCode, Antigravity, Pi, Devin, Muse Code), each labelled "not detected" where vskill did not find it. Picking a not-detected agent installs into its registry folder and says so in the receipt; the hard-coded three-agent list is gone.
- [ ] AC-06: vskill accepts an explicitly named `--agent` from its full registry and custom agents, installs with a warning "<agent> not detected, installed anyway", and still refuses an unknown id with the list of valid ids. Devin installs to its local folder when the `devin` CLI is detected.
- [ ] AC-07: "Add a custom agent…" takes a name, a user skills folder and a project skills folder, saves it with vskill on the chosen machine, and offers "Also add on" for other machines. Folders are refused when they contain `..`, a project folder is absolute, a user folder is outside the home folder, or either points at a protected path or another agent's folder.
- [ ] AC-08: A custom agent installs, updates and removes like a built-in one: its id is in the vskill lock entry, Settings > Skills shows its copies with their scope, and `vskill remove` cleans its folder.
- [ ] AC-09: The preview line and the receipt state skill, version, scope in words, machines, agents and folders, matching what vskill wrote. When the skill already exists at the other scope on a machine, that row says so; nothing is removed.

## Approach

1. vskill first, since the app relies on it: `filterAgents` takes the full registry for named ids; a custom agent store (`~/.vskill/agents.json`, `{ id, displayName, userSkillsDir, projectSkillsDir }`) merged into `AGENTS_REGISTRY` at load; `vskill agents add|list|remove [--json]`; folder guards; lock entries keep the custom id. Release vskill before the app work that calls it.
2. Server: one install request for this machine and the fleet push with `scope` and `agents[]`; read the agent list from `vskill agents list --json` per machine instead of a hard-coded list; `vskill agents add` behind the existing skill-change permission.
3. Web: one `SkillInstallPanel` replaces the this-machine button, `SkillMachineInstall` scope radios and the fleet popover's agent checkboxes; logic in a tested `.logic.ts`; the search panel gets a scope toggle.
4. Muse Code: find which folder Muse reads (T-01); if it reads none, show it as "does not load skill files" rather than offer a folder.

Risks: vskill version skew across machines (an older vskill refuses custom ids; the panel must say "update vskill on <machine>"); `SkillSearch.tsx` and `SkillUpdate*` overlap 1360's Files, so check `project_checkout_queue` and 1360 before claiming T-05 and T-06.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The scope default follows the open view (user view: Me; project view: This project), and the last choice is remembered per machine (reversible).
- D-02: No automatic removal of the copy at the other scope; the row's menu offers Remove (reversible).
- D-03: Pattern: Claude Code's install-time scope question in two choices, worded by who gets the skill, plus VS Code's visible per-machine rows (research report).
- D-04: Custom agents are per machine, rolled out with the existing explicit "Also add on" step, as 1399 does for skills (reversible).
### Open
- D-05 (user): where custom agents are stored. Recommended: in vskill (`~/.vskill/agents.json` plus `vskill agents add`), with the app only as a form over it, so CLI installs and the app agree and the 1399 rule "install with vskill, one lock per machine" holds. Alternative: app-only, which works sooner but leaves CLI installs unaware of custom agents.
- D-06 (user): whether "Me, in every project" should be the default for a skill installed from the registry, even in a project view. Recommended: keep D-01 (follow the view, remember the last choice), since every choice is now visible before Install.

## Tasks

### T-01 Muse Code and Devin skill folders
- AC: AC-05 | Files: .specweave/increments/1440-choose-user-or-this-project-when-installing-a-skill-on-this-machine/reports/ | Test: test -s .specweave/increments/1440-choose-user-or-this-project-when-installing-a-skill-on-this-machine/reports/agent-folders.md

### T-02 vskill: named agents from the full registry
- AC: AC-06 | Files: repositories/anton-abyzov/vskill/src/utils/agent-filter.ts, repositories/anton-abyzov/vskill/src/commands/add.ts, repositories/anton-abyzov/vskill/src/agents/agents-registry.ts, repositories/anton-abyzov/vskill/src/utils/agent-filter.test.ts | Test: npx vitest run src/utils/agent-filter.test.ts (from repositories/anton-abyzov/vskill)

### T-03 vskill: custom agents
- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/vskill/src/agents/custom-agents.ts, repositories/anton-abyzov/vskill/src/commands/agents.ts, repositories/anton-abyzov/vskill/src/index.ts, repositories/anton-abyzov/vskill/src/agents/custom-agents.test.ts | Test: npx vitest run src/agents/custom-agents.test.ts (from repositories/anton-abyzov/vskill)

### T-04 Server: scope and agents for every install, agent list from vskill
- AC: AC-04, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdate.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdate.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/vskillTool.ts | Test: npx vitest run src/project/SkillUpdate.test.ts (from apps/server)

### T-05 Web: one install panel
- AC: AC-01, AC-02, AC-05, AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillInstallPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillInstallPanel.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillInstallPanel.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillMachineInstall.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillAvailability.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillFleetPush.tsx | Test: npx vitest run src/components/skills/SkillInstallPanel.logic.test.ts (from apps/web)

### T-06 Web: scope toggle in the skills search panel
- AC: AC-03, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillSearch.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/skills/SkillSearch.test.tsx | Test: npx vitest run src/components/skills/SkillSearch.test.tsx (from apps/web)

### T-07 Headless screenshots on synthetic data
- AC: AC-01, AC-02, AC-05, AC-07 | Files: .specweave/increments/1440-choose-user-or-this-project-when-installing-a-skill-on-this-machine/reports/ | Test: test -s .specweave/increments/1440-choose-user-or-this-project-when-installing-a-skill-on-this-machine/reports/screenshots.md
