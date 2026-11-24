# Add approved folders while project work runs

## Problem

On October 23, 2026, the user approved adding `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio` to the specweave project, and it still could not be added. There were two failures:

- **The agent path refuses.** `studio_project_update` rejects any change to approved folders (`apps/server/src/mcp/toolkits/project/handlers.ts:665-686`), and no `studio_project_request` action exists that lets the agent ask while the user approves in an app card (`apps/server/src/project/ProjectActionRequests.ts:43`).
- **The settings path refuses.** Settings > Environment > Save changes fails with "Stop active project work before changing folder access." `ProjectService.update` denies every environment change while any thread in the project is active (`apps/server/src/project/ProjectService.ts:721-747`), including a purely additive one. A project with a running coordinator, routine or worker, including the thread that asked, can therefore never gain a folder.

Adding a folder does not affect turns in flight: the environment is read at each turn start (`ProjectEnvironmentRuntime.ts:31-98`). Removing a folder or changing the root or a repository path does affect them, which is why the guard exists.

## Scope

In:

- Additive folder approvals, and repository registrations whose path is inside an approved root, succeed while threads run.
- Removals, path changes and root changes stay blocked while threads run.
- A user-approved `add_folder` action on `studio_project_request`. The agent asks, the user approves in the app, and agents still cannot self-grant.
- Clearer refusal text that points to the supported path.
- One leftover "Studio" UI string becomes SpecWithCode (`apps/server/src/orchestration-v2/OrphanedRuns.ts:50`).

Out:

- Renaming the local `specweave-studio` folder. 103 worktrees, the umbrella release manifest, the Codex trust entry and the verify scripts depend on it (`docs/studio/naming.md` policy).
- Renaming internal identifiers (CLI, npm, MCP `studio-code`, environment variables, launchd labels).
- Removing folders while threads run.

## Acceptance Criteria

- [ ] AC-01: While another thread in the project is running, saving Settings > Environment with one added folder succeeds and persists. Removing a folder, changing a repository `localPath` or changing the root while a thread runs is still denied.
- [ ] AC-02: An agent can call `studio_project_request` with `action: "add_folder"` and `folder`. The user sees an approval card naming the canonical path, and approving it adds the folder even while other threads run. Declining changes nothing.
- [ ] AC-03: Agents still cannot self-grant: `studio_project_update` folder widening is refused with a message naming `add_folder`, and `studio_pending_request_respond` cannot answer an `add_folder` card.
- [ ] AC-04: Home, `~/.ssh`-style protected locations, already-approved folders, folders beyond the 16-folder limit, and a folder whose real path changed between request and approval are refused, and nothing changes.
- [ ] AC-05: The refusal text for blocked environment changes says removals and changes need stopped work and that adding works while threads run. The orphaned-run notice says SpecWithCode, not Studio.
- [ ] AC-06: The installed app on this Mac lets the specweave project approve the app checkout folder, and the 1009 successor launches bound to it.

## Approach

1. `ProjectService.ts`: add `isAdditiveEnvironmentChange(prior, next)` over the normalized environment. Every prior folder is kept, and every prior repository is kept with an identical id, url and localPath. Skip the active-work denial only when the root is unchanged and the change is additive.
2. `ProjectActionRequests.ts`: add the `add_folder` action with `folder` and `canonicalFolder` params. `describe()` resolves through `resolveProjectEnvironment`, which applies the realpath, protected-location, dedupe and limit checks. `apply()` re-resolves and compares canonical paths (time-of-check to time-of-use), then calls `projects.update` with `approvalRequestId` and `expectedRevision`.
3. `handlers.ts` and `tools.ts`: pass `folder` through and point the refusals at `add_folder`.
4. `contracts/environmentHttp.ts`, `ProjectService.ts`, `OrphanedRuns.ts`: update the text.
5. Tests: `ProjectService.test.ts`, `ProjectActionRequests.test.ts`, `route.integration.test.ts`, the thread handler test, `http.test.ts`, `environmentHttp.test.ts`.

Rejected alternative: letting `studio_project_update` widen folders. That would let an agent grant itself access, and personal projects route on approved folders (`projectRouting.ts:36-41`).

Risks:

- A Claude thread with background work gets a clear "background work blocks query replacement" error on its next turn until that work ends.
- Adding the first folder to an empty environment stops threads on providers other than Codex, Claude or full-access ACP. This is unchanged behavior, and the card states it.

## Decisions

### Asked
- D-01: may an agent add the folder itself → the user approved this folder on October 23, 2026 ("Yes, I approve it. Go ahead and edit yourself") and asked to fix SpecWithCode so it works.
### Defaulted (change any before sw-do)
- D-02: agents still cannot self-grant; the agent requests and the user approves in a card (reversible, keeps the #539 security rule).
- D-03: keep the local folder name `specweave-studio` (rename audit: compatible, renaming breaks 103 worktrees).
### Open
- none

## Tasks

### T-01 Allow additive environment saves while threads run
- AC: AC-01, AC-05 | Files: apps/server/src/project/ProjectService.ts, apps/server/src/project/ProjectService.test.ts, packages/contracts/src/environmentHttp.ts, packages/contracts/src/environmentHttp.test.ts, apps/server/src/project/http.test.ts, apps/server/src/orchestration-v2/OrphanedRuns.ts | Test: cd <worktree> && bun run --cwd apps/server vitest run src/project/ProjectService.test.ts src/project/http.test.ts

### T-02 User-approved add_folder request
- AC: AC-02, AC-03, AC-04 | Files: apps/server/src/project/ProjectActionRequests.ts, apps/server/src/project/ProjectActionRequests.test.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/tools.ts | Test: cd <worktree> && bun run --cwd apps/server vitest run src/project/ProjectActionRequests.test.ts

### T-03 Ship and accept on the installed app
- AC: AC-06 | Files: none (release via the 1015 owner) | Test: installed app approves the folder; studio_project_read shows it; 1009 successor launches

### T-04 Verify and close 1023
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1023-add-approved-folders-while-project-work-runs
