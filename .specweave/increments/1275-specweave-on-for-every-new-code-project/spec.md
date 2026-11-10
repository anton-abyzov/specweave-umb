# SpecWeave on for every new code project

## Problem

Anton, November 10, 2026: "how to consider it for all new projects", meaning every SpecWithCode code project should plan its work as SpecWeave increments.

Today `specweave init` runs from one place only: the New project dialog for a brand-new folder with "Use SpecWeave" checked (1262; `CommandPalette.tsx:3280` → `createNamedProject` → `scaffoldRepository`, `apps/server/src/project/ManagedProjectFolders.ts:521`). The coordinator only gets the "plan in SpecWeave" guidance when `.specweave/config.json` exists (`ProjectWorkspaceService.ts:193`). Every other route registers a code project without it (all lines on `origin/main` of `anton-abyzov/specwithcode`):

- Agent-created projects: `studio_project_create`, `apps/server/src/mcp/toolkits/project/handlers.ts:921` calls `createNamedProject` with no `specweave`; the `workspaceRoot` branch (`:954`) calls `projects.create` and never sets up.
- A New project name that matches an existing folder: `bindExistingFolder` (`ManagedProjectFolders.ts:622`, reached at `:665-667`) ignores `specweave`.
- Clone (tracked, `ws.ts:2759-2770` creates the project before the clone finishes; legacy, `CommandPalette.tsx:3444`), Add existing folder (`CommandPalette.tsx:3128`), and the mobile Add project screen (`apps/mobile/src/features/projects/AddProjectScreen.tsx:742,1065,1236,1338,1385`).
- Add to another machine: `addToMachine.ts:232` proxies `studio_project_create` to the target without `specweave`.
- Projects made before November 8, 2026 or where init failed: only Project settings > General > "Set up SpecWeave" (`ProjectSpecweaveSetting.tsx`) turns it on, and nothing points the person there.

## Scope

In: a visible SpecWeave choice (on by default) on every route that creates or adds a code project (web/desktop, mobile, MCP, add to machine); setup after clone completes; a one-time, dismissable prompt for existing code projects without SpecWeave; copy and tool descriptions.

Out: personal projects (never set up); fleet handoff project creation (`fleet/MachineHandoff.ts:1362`); the generic `project.create` RPC and CLI `project create` (low-level registration stays as is); auto-committing init files in existing or cloned repos; changing what `specweave init` writes; the folder picker itself (1272).

## Acceptance Criteria

- [ ] AC-01: `studio_project_create` takes an optional `specweave` boolean, default true for code projects. Title-only create passes it to `createNamedProject`; the `workspaceRoot` branch runs `ProjectWorkspaceService.setUpSpecweave` after registering. The reply carries `specweaveSetUp: true` when the server ran the step and `specweaveError` when it failed; the project is kept either way. `specweave: true` with `kind: "personal"` is refused before anything is created; `specweave: false` skips setup.
- [ ] AC-02: When New project (dialog or MCP) binds an existing folder and SpecWeave is on, setup runs if the folder has no `.specweave/config.json` and is not already planned by an umbrella (`isSpecweaveProject`). It never commits in that folder. The dialog no longer says SpecWeave was "not added to an existing folder"; it reports the real outcome.
- [ ] AC-03: Web/desktop Clone (destination step) and Add existing folder show a "Use SpecWeave" option, checked by default, with the same files disclosure as New project (`SpecweaveSetupDetails`). It is hidden when the server lacks `serverConfig.specweaveSetUp`, the connection lacks `AuthFilesystemWriteScope`, the folder is already a SpecWeave project, or the add came through the folder-copy link prompt.
- [ ] AC-04: A tracked clone with SpecWeave on runs setup on the server after the clone finishes successfully, never on an empty or partial folder (`ProjectCloneStartInput.specweave`, advertised by a new capability flag). A legacy clone runs it after the add. A failed clone never runs it.
- [ ] AC-05: Mobile New project, Add local folder and Clone (tracked and legacy) show a "Use SpecWeave" switch, on by default, under the same conditions as AC-03; New passes `specweave` to `createNew`, Add and legacy Clone call `projects.specweaveSetUp` after the project is visible (`waitForProject`), tracked Clone passes `specweave` to `startProjectClone`. A setup failure is a non-fatal alert; the project stays.
- [ ] AC-06: `studio_project_add_to_machine` takes the same optional `specweave` (default true), forwards it to the target's `studio_project_create`, raises that call's timeout to cover `specweave init` (at least 4 minutes when on), and reports `specweaveError`, or "not supported on <machine>" when the target's reply lacks `specweaveSetUp`. The existing-copy early return reports that setup was not attempted. The web Add to machine dialog passes the flag through.
- [ ] AC-07: Setup never fails the create or add. Every failure (CLI missing, not a Git repository top, timeout, permission) is shown once with `specweave init`'s reason and a pointer to Project settings > Set up SpecWeave.
- [ ] AC-08: An existing code project whose workspace read returns `specweave: false` shows a one-time "Set up SpecWeave" prompt in the project view, with the files list and a confirm step. "Not now" dismisses it for that project on that device for good; it never runs setup without the click. It does not appear for personal projects, umbrella children (`specweave: true`), old servers (`specweave` undefined) or connections without `AuthFilesystemWriteScope`. Project settings and the prompt share one setup hook.
- [ ] AC-09: The `SpecweaveSetup.ts` header, the `ProjectCreateNewInput.specweave` doc and the MCP tool descriptions state the rule: SpecWeave is on by default on every route, always visible and switchable, and never run without a create/add action or a click.
- [ ] AC-10: New project behaviour from 1262 and 1272 holds: existing `ManagedProjectFolders`, `ProjectCreation`, `useNewProject` and `NewProjectFolderPicker` tests pass unchanged or with copy-only edits. A headless end-to-end run creates a project through each web route against a temp Git repo and screenshots each option and outcome.

## Approach

1. Server core (`ManagedProjectFolders.ts`): in the existing-folder branch, when `specweave` is on and the folder is not a SpecWeave project, call the local `setUpSpecweave(cwd)` (`:512`) without committing; return `specweaveError`. Reuse `hasSpecweaveConfig` / `isSpecweaveProject` from `ThreadIncrementProgress.ts`.
2. MCP (`mcp/toolkits/project/tools.ts:90-102,168`, `handlers.ts:867,954`, `addToMachine.ts:31,43,232,255`): add `specweave` to the MCP input schemas only, not to the shared `ProjectCreatePayload`; strip it before `projects.create`. Add `ProjectWorkspaceService` to the create tool's dependencies. Under a partial remote work grant, `specweave` is allowed only where the grant already allows create (it runs `npx specweave@3` on that machine); `workGrants.test.ts` covers it.
3. Clone (`packages/contracts/src/projectClone.ts:60`, `ws.ts:2759`, `contracts/src/server.ts`): optional `specweave` on `ProjectCloneStartInput`; the server calls `setUpSpecweave` on the clone's `done` transition and records the outcome on the clone job so the UI can show it. New capability `serverConfig.cloneSpecweave`.
4. Shared web hook `apps/web/src/hooks/useSpecweaveSetUp.ts` extracted from `ProjectSpecweaveSetting.tsx` (`run()`), used by settings, the add-folder path and the prompt.
5. Web routes (`CommandPalette.tsx` add-folder `:3128-3154` and clone destination `:4225-4238`, `CloneProjectDestination.tsx`): a `specweave: { checked, toggle } | null` option; state lives next to `newProjectUsesSpecweave` (`:1044`).
6. Prompt: `apps/web/src/components/studio/SpecweaveSetupPrompt.tsx` mounted in `ProjectWorkspaceSurface.tsx` (which already reads `specweave`, `:299`); dismissal in `useLocalStorage` key `studio:specweave-prompt-dismissed:<environmentId>:<projectId>`. Per device by choice: no contract change, and a dismissed prompt on one device is cheap to see once more elsewhere.
7. Mobile: `apps/mobile/src/state/projectWorkspace.ts` (`createProjectWorkspaceAtoms`), a `SpecweaveSwitchRow` component (keeps `AddProjectScreen.tsx`, 1,441 lines, under 1,500), `supportsSpecweave` on `EnvironmentOption` (`:84`, `:401-432`); `useCreateProject` (`:692`) returns the `projectId`.
8. Copy and docs last (AC-09).

Rejected: running setup silently for every existing project (writes `.specweave/`, `AGENTS.md`, `CLAUDE.md`, `.gitignore` into repos the person owns; `SpecweaveSetup.ts:2-4`); a server-side "SpecWeave by default" setting (one more knob; the visible checkbox already is the choice); auto-committing init files in existing repos.

Risks: `npx specweave@3` can take minutes on first run, so setup after register stays async where the RPC is already async (clone, add to machine) and is bounded by the existing 3-minute `INIT_TIMEOUT`; older target machines drop the unknown field silently, covered by `specweaveSetUp` in the reply and the capability flags; `setUpSpecweave` can race the project projection (`not_found`), so mobile and web await the project first.

### Coordination with 1272 (folder picker) and the shared checkout

1272 edits `CommandPalette.tsx` (machine default, Add project → New project path), `ManagedProjectFolders.ts` (suggested projects root), `ProjectCreation.tsx`, `projectCreation.ts`, `NewProjectFolderPicker.tsx`, `RemoteFolderBrowser.tsx` and possibly the clone destination's picker. 1275 branches from `main` only after 1272 merges (the checkout queue already orders it: 1258 → PR #120 fix → 1267 → 1272 → 1273 → 1275), and starts no app edits before the coordinator's "specweave-default may branch". Inside the shared files 1275 limits itself to: the existing-folder branch of `createNamedProject` and nothing near the projects root; the add-folder submit and the `CloneProjectDestination` props in `CommandPalette.tsx`, not the picker, machine default or New project steps; no edits to `projectCreation.ts`, `NewProjectFolderPicker.tsx` or `RemoteFolderBrowser.tsx`. 1273 is mobile but touches the composer and side menu, not `AddProjectScreen.tsx`.

## Decisions

### Asked
- D-01 SpecWeave on for all new code projects → yes, on by default everywhere, never silent for existing projects (Anton via the coordinator, November 10, 2026).
### Defaulted (change any before sw-do)
- D-02 Clone and Add existing default to checked, with the files disclosure visible; init files are left uncommitted in those repos.
- D-03 MCP `specweave` defaults to true for code projects; agents pass `false` to skip.
- D-04 The existing-project prompt is dismissed per device (localStorage), not synced.
- D-05 Folder-copy links (`onFolderCopies`) and fleet handoff never set up, so copies of one project do not diverge.
- D-06 Under a partial remote work grant, `specweave` follows the create permission; no separate grant.
### Open
- none

## Tasks

### T-01 Server: set up SpecWeave when New project binds an existing folder
- AC: AC-02, AC-07 | Files: apps/server/src/project/ManagedProjectFolders.ts, apps/server/src/project/ManagedProjectFolders.test.ts, apps/server/src/project/SpecweaveSetup.ts, packages/contracts/src/project.ts | Test: bun run --cwd apps/server test ManagedProjectFolders SpecweaveSetup

### T-02 MCP: specweave on studio_project_create and add_to_machine
- AC: AC-01, AC-06, AC-07, AC-09 | Files: apps/server/src/mcp/toolkits/project/tools.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/handlers.test.ts, apps/server/src/mcp/toolkits/project/addToMachine.ts, apps/server/src/mcp/toolkits/project/addToMachine.test.ts, apps/server/src/mcp/toolkits/project/workGrants.test.ts | Test: bun run --cwd apps/server test handlers addToMachine workGrants

### T-03 Clone: run setup after a tracked clone finishes
- AC: AC-04, AC-07 | Files: packages/contracts/src/projectClone.ts, packages/contracts/src/projectClone.test.ts, packages/contracts/src/server.ts, apps/server/src/ws.ts, apps/server/src/project/ProjectCloneTracker.ts, apps/server/src/project/ProjectCloneTracker.test.ts | Test: bun run --cwd apps/server test ProjectCloneTracker && bun run --cwd packages/contracts test projectClone

### T-04 Web: shared setup hook, Use SpecWeave on Clone and Add existing, Add to machine flag
- AC: AC-03, AC-04, AC-06, AC-07, AC-10 | Files: apps/web/src/hooks/useSpecweaveSetUp.ts, apps/web/src/hooks/useSpecweaveSetUp.test.tsx, apps/web/src/components/studio/ProjectSpecweaveSetting.tsx, apps/web/src/components/CommandPalette.tsx, apps/web/src/components/studio/CloneProjectDestination.tsx, apps/web/src/components/studio/ProjectCreation.tsx, apps/web/src/components/studio/ProjectCreation.test.tsx, apps/web/src/hooks/useNewProject.ts, apps/web/src/hooks/useNewProject.test.tsx, apps/web/src/components/chat/AddToMachineDialog.tsx, apps/web/src/components/AddToMachineJobRunner.tsx | Test: bun run --cwd apps/web test useSpecweaveSetUp ProjectCreation useNewProject AddToMachine ProjectWorkspaceSettings

### T-05 Web: one-time Set up SpecWeave prompt for existing projects
- AC: AC-08 | Files: apps/web/src/components/studio/SpecweaveSetupPrompt.tsx, apps/web/src/components/studio/SpecweaveSetupPrompt.test.tsx, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: bun run --cwd apps/web test SpecweaveSetupPrompt

### T-06 Mobile: Use SpecWeave switch on New, Add folder and Clone
- AC: AC-05, AC-07 | Files: apps/mobile/src/state/projectWorkspace.ts, apps/mobile/src/features/projects/SpecweaveSwitchRow.tsx, apps/mobile/src/features/projects/AddProjectScreen.tsx, apps/mobile/src/features/projects/AddProjectScreen.test.ts | Test: bun run --cwd apps/mobile test AddProjectScreen && bun run --cwd apps/mobile typecheck

### T-07 Copy, docs and headless end-to-end check
- AC: AC-09, AC-10 | Files: apps/server/src/project/SpecweaveSetup.ts, packages/contracts/src/project.ts, apps/web/tests/specweave-default/verify.mjs | Test: node apps/web/tests/specweave-default/verify.mjs
