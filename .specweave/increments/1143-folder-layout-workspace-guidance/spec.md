# Folder layout workspace guidance

## Problem

SpecWithCode gives no advice on worktrees versus the current checkout when a project is added or edited, and its Automatic workspace default asks only "is this folder a Git repository?". An umbrella folder (EasyChamp: a root repository whose `.gitignore` excludes `repositories/`, with separate clones under `repositories/<owner>/<repo>`) reads as one repository, so every new chat gets a thin worktree cut from the umbrella's main branch that holds none of the services' code. The owner prefers no worktrees as the default advice for multi-repo work.

## Scope

In: the layout reports whether its checkouts are separate clones; Automatic resolves to Current checkout for such folders; guidance on project add (toast), on Project settings > Use worktrees, and in the Project folder change check. Out: EasyChamp worktree cleanup (separate thread), mobile composer (its Automatic is already Current checkout), any forced setting change.

## Acceptance Criteria

- [ ] AC-01: FolderLayout reports `separateClones` (a found checkout with its own `.git` folder), and the server's launch rule uses it.
- [ ] AC-02: With no workspace configured, a new web chat in a Git folder holding separate clones (umbrella or microservices layout) starts in the current checkout; a single repository still gets a worktree.
- [ ] AC-03: Adding a project shows which workspace is recommended for its layout (current checkout for umbrella/nested clones, worktrees for one repository), and Project settings > Use worktrees and the Project folder check show the same recommendation without changing the setting.

## Approach

Server: `readFolderLayout` notes a `.git` directory per checkout as `separateClones`; `holdsSeparateClones` reads it; contracts add an optional `layout.separateClones`. Web: one `folderLayoutGuidance.ts` holds the recommendation rule and copy; `useProjectFolderHealth` caches the whole folder check so the composer default, the add-project toast and settings share one walk per project; `resolveNewThreadWorkspaceDefault` asks for separate clones only when the folder is a Git repository. Rejected: a new layout RPC (the folder check already returns it) and walking the folder in the VCS status stream (it refreshes too often).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Automatic picks Current checkout for any Git folder holding separate clones, not only a gitignored `repositories/`: a worktree leaves separate clones out either way, and this matches the server's launch rule from #1007.
- D-02: Guidance only recommends; it never writes the Use worktrees setting.
### Open
- none

## Tasks

### T-01 Layout reports separate clones
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/project/FolderLayout.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/project/launchWorkspace.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/project.ts | Test: cd repositories/anton-abyzov/specweave-studio/apps/server && npx vitest run src/project/FolderLayout.test.ts src/mcp/toolkits/project/launchWorkspace.test.ts

### T-02 Automatic uses current checkout for multi-repo folders, and guidance
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/lib/folderLayoutGuidance.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/lib/newThreadWorkspaceDefault.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/studio/useProjectFolderHealth.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/hooks/useHandleNewThread.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProjectDefaultsSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectFolderChange.tsx | Test: cd repositories/anton-abyzov/specweave-studio/apps/web && npx vitest run src/lib/folderLayoutGuidance.test.ts src/lib/newThreadWorkspaceDefault.test.ts src/components/settings src/components/studio/ProjectFolderChange.test.tsx

### T-03 Verify and close 1143
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/CHANGELOG.md | Test: PR CI green and merged
