# Agent project creation matches the dialog: machine, parent folder and GitHub

## Problem

From the New project review of November 10, 2026 (`.specweave/reviews/new-project-2026-11-10/report.html`), in the SpecWithCode app (`specwithcode-dev`). The New project dialog lets a person pick the machine, the parent folder and a private GitHub repository. The agent tool `studio_project_create` (`apps/server/src/mcp/toolkits/project/tools.ts:90-100`, handler `handlers.ts:867-935`) can do none of that:

1. No machine. It creates on the machine hosting the MCP session. The only remote route is `studio_project_add_to_machine`, which needs an existing project with a remote, so an agent cannot start an empty project on M1 or the Minisforum.
2. No parent folder. A title-only call runs `createNamedProject({ name, kind })` with no `parentPath` (`handlers.ts:922-931`), so the project lands in the app's managed storage, not `~/Projects`. With `workspaceRoot` it only registers a folder: no `git init`, README or first commit.
3. No GitHub. No MCP tool calls `publishRepository`.
4. It rejects a folder that is already a registered project, where the dialog returns that project with `existing: true`.

SpecWeave on the MCP route is covered by increment 1275 and is not repeated here.

## Scope

In: `machine`, `parentPath` and `github` inputs on `studio_project_create`; the same scaffold as the dialog (git init, README, first commit) in the chosen parent; publishing a private repository; returning an existing project instead of failing; the result naming machine, path and what happened.

Out: SpecWeave setup on this route (1275); public repositories; creating on a machine whose grant covers only some projects (stays refused, with the existing message); the dialog itself; cloning (`studio_project_clone` is unchanged).

## Acceptance Criteria

- [ ] AC-01: `studio_project_create {title, parentPath}` creates `<parentPath>/<slug>` with git init, README and a first commit, exactly as the dialog does, and returns the final path including any `-2` suffix. Without `parentPath` it uses the machine's suggested projects folder (`suggestedProjectsRoot`), not managed storage.
- [ ] AC-02: `studio_project_create {machine}` creates the project on that fleet machine through the existing remote MCP client, subject to the same grant checks as `studio_project_add_to_machine`. The result names the machine and the project id there.
- [ ] AC-03: A project created on another machine is usable at once from the caller: the tool result includes the call that starts a thread there, and that call works without a further add or link step.
- [ ] AC-04: `github: true` (or `{account}`) publishes a private repository after the first commit using that machine's GitHub sign-in. The result reports `published`, `remote_added` or the failure reason; a publish failure does not fail the create.
- [ ] AC-05: Calling it for a folder that is already a registered project returns that project with `existing: true` and creates nothing.
- [ ] AC-06: Refusals name the fix: unknown or offline machine, grant missing or limited to some projects, parent folder missing or denied, older SpecWithCode on the target ("update SpecWithCode on <machine>").
- [ ] AC-07: Calls with only `title` or `workspaceRoot` that work today keep working, except the default location in AC-01; `handlers.test.ts` cases for create pass with that one change.

## Approach

1. Contracts (`packages/contracts/src/project.ts`, `orchestratorMcp.ts`): optional `machine`, `parentPath`, `github` on the tool input; `existing`, `published` and `publishError` on the result.
2. `handlers.ts`: pass `parentPath` to `createNamedProject`; default it to the suggested projects root; map the existing-project case to a result.
3. Remote: when `machine` is another machine, proxy `studio_project_create` there with `RemoteStudioMcpClient`, as add-to-machine does for clone and create. The remote project gets its own logical project and coordinator on that machine; the result carries its id.
4. Publish: call `SourceControlRepositoryService.publishRepository` on the creating machine after the commit; read its status.
5. Tool description in `tools.ts`: say what each input does and that a remote project lives on that machine.

Ordering: after 1275 (same handler and payload) and 1286 (create error reasons), so this reuses their typed results.

Rejected: a separate `studio_project_create_remote` tool (one tool with `machine` matches `studio_thread_launch`).

Open design point settled by default: a project created remotely is not linked to anything here, because there is no local copy. It appears in the caller's sidebar under that machine through the normal connection.

Risks: changing the default location for title-only calls moves where agents' projects land; older servers ignore `parentPath`, so the remote call must check the target's capability first.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Title-only creates go to the suggested projects folder, as in the dialog.
- D-02 GitHub repositories are private only.
- D-03 A remote create does not make a local copy or a link.
### Open
- none

## Tasks

### T-01 Contracts: machine, parentPath, github inputs and result fields
- AC: AC-01, AC-02, AC-04, AC-05 | Files: packages/contracts/src/project.ts, packages/contracts/src/orchestratorMcp.ts | Test: bun run --cwd packages/contracts test project orchestratorMcp

### T-02 Local create: parent folder, scaffold, existing project
- AC: AC-01, AC-05, AC-07 | Files: apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/handlers.test.ts, apps/server/src/mcp/toolkits/project/tools.ts | Test: bun run --cwd apps/server test handlers

### T-03 Remote create through the fleet client
- AC: AC-02, AC-03, AC-06 | Files: apps/server/src/mcp/toolkits/project/createOnMachine.ts, apps/server/src/mcp/toolkits/project/createOnMachine.test.ts, apps/server/src/mcp/toolkits/project/handlers.ts | Test: bun run --cwd apps/server test createOnMachine

### T-04 Publish to GitHub from the tool
- AC: AC-04 | Files: apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/handlers.test.ts | Test: bun run --cwd apps/server test handlers
