# Aide routes requests to the projects that own them

## Problem

The user wants to tell the personal assistant (Aide, a `kind: personal` project) anything and have it start work in the project that owns it (October 19, 2026). Today Aide can only `delegate_task` inside its own folder, or call `studio_thread_launch` with another project's ID: that thread runs on Aide's coordinator model, bypasses the target project's coordinator (its owners, memory and active work), carries no attachments and has no retry key. An EasyChamp audit was started in the SpecWeave project by mistake and had to be cancelled.

## Scope

In: SpecWithCode (`anton-abyzov/specwithcode-dev`) server MCP tools, personal-assistant coordinator instructions, a routed-message label in the coordinator conversation, docs. Out: projects on other machines (the existing machine routing stays), moving threads between projects (owned by the "Move threads between projects" increment), granting folders.

## Acceptance Criteria

- [ ] AC-01: `studio_route_targets`, called by a personal assistant's coordinator, lists the projects it may route to: active projects in this environment whose folder is the assistant's own folder or inside one of its approved folders. Each row carries the folder that grants it, the goal, the coordinator link and the latest threads' titles and statuses, never the other project's memory.
- [ ] AC-02: `studio_project_route` delivers one user message from the assistant's conversation to the target project's coordinator, starting that coordinator when the project has none. The user's words arrive unchanged, marked as theirs, with a one-line provenance header (assistant, thread, message, optional assistant note) and their screenshots and files.
- [ ] AC-03: A target outside the approved folders, or archived, paused, deleted or the assistant itself, is refused with a reason that names the fix; routing never adds folders, grants or credentials. A non-personal or non-coordinator caller is refused.
- [ ] AC-04: Retrying a route of the same message to the same project delivers it once (stable command identity), also after the source upload staging expired; routing the same message to two projects delivers one copy to each.
- [ ] AC-05: The target coordinator cannot run in broader runtime or interaction modes than the assistant's own thread.
- [ ] AC-06: Personal-assistant coordinators are told to route owned work with these tools, to pick the target from words, memory and the target list, to ask one concise project choice only when two or more targets remain plausible, to route a multi-project request once per project with a note naming that project's part, and never to start another project's work in their own folder. Every coordinator is told how to treat a routed message, and never to revive cancelled work because of one.
- [ ] AC-07: The coordinator conversation shows a routed message as the user's words with a "Routed by <assistant>" line instead of the raw header.

## Approach

`apps/server/src/project/projectRouting.ts` (pure): approved-folder containment on real paths, refusal reasons, the provenance header and its parser. `ProjectCoordinatorService.route`: the existing durable coordinator send with a cross-project sender, attachments re-staged from the source message to deterministic pending uploads. `apps/server/src/mcp/toolkits/project/route.ts` holds both handlers; `tools.ts` declares them. `ProjectWorkspaceService.projectContextText` adds the instructions. Web: `projectCoordinatorMessageDisplay.ts` strips the header and `CoordinatorConversation.tsx` labels it. Integration test drives the real tool handlers against an in-memory server runtime.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Access evidence is the assistant's own folder plus its approved additional folders (real paths), the same approval that already lets its agents read and write there. No new grant model.
- D-02: Routed work goes to the target project's coordinator, which then starts or reuses its workers, so ownership, memory and duplicate checks stay with that project. The assistant does not launch workers in other projects directly.
- D-03: Projects on other machines are out of scope; the assistant says so and offers the local project if one matches.

## Tasks

### T-01 Routing core: access, header, coordinator route with attachments
- AC: AC-02, AC-03, AC-04, AC-05 | Files: apps/server/src/project/projectRouting.ts, apps/server/src/project/projectRouting.test.ts, apps/server/src/project/ProjectCoordinatorService.ts | Test: vp test run apps/server/src/project/projectRouting.test.ts

### T-02 MCP tools studio_route_targets and studio_project_route
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: apps/server/src/mcp/toolkits/project/route.ts, apps/server/src/mcp/toolkits/project/tools.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/route.integration.test.ts | Test: vp test run apps/server/src/mcp/toolkits/project/route.integration.test.ts

### T-03 Assistant and coordinator instructions, routed-message display, docs
- AC: AC-06, AC-07 | Files: apps/server/src/project/ProjectWorkspaceService.ts, apps/web/src/studio/projectCoordinatorMessageDisplay.ts, apps/web/src/components/studio/CoordinatorConversation.tsx, docs/studio/project-orchestration.md | Test: vp test run apps/web/src/studio/projectCoordinatorMessageDisplay.test.ts apps/server/src/project/ProjectWorkspaceService.test.ts

### T-04 PR, release and installed runtime check
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: specweave-studio --version on the installed service; studio_route_targets from Aide

### T-05 Verify and close 0945
