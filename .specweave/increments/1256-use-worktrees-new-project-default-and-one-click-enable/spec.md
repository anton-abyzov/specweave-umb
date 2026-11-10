# Use worktrees default for new projects and one-click enable

## Problem

Use worktrees is a per-project switch (the project's General tab and Settings > Projects). The global Settings > General page only says "Set per project" with an Open Projects button, so there is no way to choose what new projects start with, and nothing shows which projects have it on.

When the switch is off, an agent in the project checkout that runs `git worktree add` gets the `MANUAL_WORKTREE_REFUSAL` text from the `git` shim (`apps/server/src/provider/ManualWorktreeGuard.ts`), and nothing reaches the UI. Agents read it as a dead end and stop; the person has to find the project setting by hand.

Requested by Anton on November 7, 2026, as a scope addition shipped in the same release as 1253.

## Scope

In: an environment-wide default for NEW projects' Use worktrees, applied once when a project is created; the global page showing that default, a link to Projects and, when projects differ, which projects have it on; a one-click "Turn on Use worktrees for this project" action in the thread when an agent hits the refusal; refusal text that tells the agent to keep working. Out: any global switch overriding existing projects, worktree storage settings, the launch-time notices in `launchWorkspace.ts`.

## Acceptance Criteria

- [ ] AC-01: Settings > General shows "Use worktrees for new projects" (a switch for an environment setting, off by default) with an Open Projects link. Changing it never changes an existing project's switch.
- [ ] AC-02: A project created while the default is on starts with its own Use worktrees switch on (a project-scoped `defaultThreadEnvMode: "worktree"` override); with it off, a new project gets no override. A project whose override already exists is never changed.
- [ ] AC-03: When the listed projects differ (some on, some off), the global row lists the projects that have Use worktrees on; when they all agree it says so instead of listing.
- [ ] AC-04: A thread whose command output contains the Use worktrees refusal shows a card with a one-click "Turn on Use worktrees for this project" button. Clicking it turns on that project's own switch (the same setting as its General tab); once the switch is on, the card says so, and that the agent's next turn can create its worktree, instead of offering the button.
- [ ] AC-05: The refusal text tells the agent to keep working in its checkout and that the person can turn Use worktrees on from the card, instead of ending its turn.

## Approach

Contracts: add `newProjectThreadEnvMode` ("local" | "worktree", default "local") to the environment `ServerSettings` and its patch, environment-only (not project-scoped, never in project overrides).

Server: `ProjectService.create` already seeds `threadFinishAction` with `seedNewProjectFinishAction`. Seed `defaultThreadEnvMode: "worktree"` the same way when the environment default is "worktree" and the project has no override.

Web: in `ProjectDefaultsSettings.tsx`, replace `environmentWorkspaceRow` with the new-projects switch, the Open Projects button and the list of projects with Use worktrees on (effective values through `resolveProjectSettings`, only when they differ). The thread card follows `ChromeConnectCard`: detect the refusal text in a work entry (`packages/client-runtime/src/work-log/presentation.ts`), render under the work row in `MessagesTimeline.tsx`, update the project override the way `CoordinatorAccessPicker` does (per-key `projectSettingsOverrideChanges`).

Rejected: a global switch that overrides every project (Anton asked for per-project control); having the shim read live state (the policy is recomputed each turn, so the next turn already runs with the new setting); sending an automatic follow-up turn from the card (it would start a provider turn the person did not ask for).

## Decisions

### Asked
- D-01 Global switch vs default for new projects → default for new projects only (Anton, November 7, 2026)
### Defaulted
- D-02 The card does not send a message itself: the agent was told to keep working, the runtime policy is read each turn, so the next turn (any message) can create the worktree → default
### Open
- none

## Tasks

### T-01 New-project default setting and creation seed
- AC: AC-01, AC-02 | Files: packages/contracts/src/settings.ts, apps/server/src/project/ProjectService.ts, apps/server/src/project/ProjectService.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectService.test.ts

### T-02 Global Settings row: default, Projects link, projects with it on
- AC: AC-01, AC-03 | Files: apps/web/src/components/settings/ProjectDefaultsSettings.tsx, apps/web/src/components/settings/ProjectDefaultsSettings.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/ProjectDefaultsSettings.test.tsx

### T-03 One-click enable card and refusal text
- AC: AC-04, AC-05 | Files: apps/server/src/provider/ManualWorktreeGuard.ts, packages/client-runtime/src/work-log/presentation.ts, apps/web/src/components/chat/UseWorktreesCard.tsx, apps/web/src/components/chat/MessagesTimeline.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/UseWorktreesCard.test.tsx

### T-04 Verify and close 1256
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1256
