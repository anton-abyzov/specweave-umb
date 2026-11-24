# Workers honor the project worker model before lanes, Auto and parent model

## Problem

The Aide project's model is Claude Opus 5.5. Even so, Aide workers that delegate_task started without a named model ran on `muse-wonder-full-1.0`, Copilot `claude-opus-5.5` and Codex `gpt-6.1-sol` between November 2 and November 4, 2026. Code on main at `4de211381b` shows three ways this happens:

1. **Parent model:** delegate_task applies the project's worker model only when the caller is the project coordinator (`projectDelegationTarget`, `apps/server/src/project/ProjectDelegation.ts`). Any other caller's worker inherits the caller's current model, including a model the caller fell back to. studio_thread_launch and create_threads behave the same way (`apps/server/src/mcp/toolkits/project/handlers.ts`).
2. **Lanes and Auto:** after the worker model is picked, `routeResolvedTarget` and `routeWorkerTask` still let model lanes, learned preferences or Auto move the worker, even when the project set its model.
3. **Room check:** `workerLaunchWithRoom` moves a worker off the project model when that provider is at its switch threshold. This is the configured limit fallback. It records `launchFallbackFrom`, so the thread is marked.

There are also two sources for the project's model: the aggregate `project.defaultModelSelection` and the `defaultModelSelection` key in project overrides. The worker path reads only the aggregate.

## Scope

In:
- The project's model is the worker model for every worker started in the project without a named model: delegate_task, studio_thread_launch and create_threads, whatever the caller.
- Lanes and Auto apply only when the project has no model of its own.
- The limit fallback stays, and it is marked on the thread.
- The Project settings row is labeled "Thread and worker model".

Out: changing the limit-fallback policy itself. Workers whose caller names a model are unchanged.

## Acceptance Criteria

- [ ] AC-01: With a project model set, a worker that delegate_task starts without a named model, from any caller in the project, starts on that model. An override key wins over the aggregate field.
- [ ] AC-02: With a project model set, model lanes, learned preferences and Auto do not move such a worker. With none set, they behave as before.
- [ ] AC-03: studio_thread_launch and create_threads follow the same rule for any caller.
- [ ] AC-04: When the room check moves a worker off the project model, the thread records it as a fallback for the project model.
- [ ] AC-05: The project-scope Model row reads "Thread and worker model" and explains that lanes and Auto apply only when it is unset.

## Approach

- `apps/server/src/project/ProjectDelegation.ts`: add `projectWorkerModel(settings, project)`, which returns the override key first, then the aggregate field. `projectDelegationTarget` applies it for any caller in the project.
- `apps/server/src/mcp/OrchestratorMcpService.ts`: run the room check for any caller whose worker takes the project model, and skip routing for it.
- `apps/server/src/mcp/toolkits/project/handlers.ts`: apply the same rule for thread launches.
- `apps/web/src/components/settings/ProjectDefaultsSettings.tsx`: new project-scope label and description.
- Rejected: a separate `workerModelSelection` key. The project's Model already is the worker model in the coordinator path, and a second key would let the two disagree.

## Decisions

### Asked
- D-01: the checkout slot. Asked; waiting for the answer.
### Defaulted (change any before sw-do)
- D-02: the project's Model setting is the worker model, and no new key is added.
- D-03: the limit fallback at the switch threshold stays, marked on the thread.
### Open
- none

## Tasks

### T-01 Project worker model for every unnamed worker, no lanes or Auto over it
- AC: AC-01, AC-02, AC-03, AC-04 | Files: [apps/server/src/project/ProjectDelegation.ts, apps/server/src/mcp/OrchestratorMcpService.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/project/ProjectDelegation.test.ts] | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && ../../node_modules/.bin/vp test run src/project/ProjectDelegation.test.ts

### T-02 Label the setting
- AC: AC-05 | Files: [apps/web/src/components/settings/ProjectDefaultsSettings.tsx, apps/web/src/components/settings/ProjectDefaultsSettings.test.tsx] | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && ../../node_modules/.bin/vp test run src/components/settings/ProjectDefaultsSettings.test.tsx
