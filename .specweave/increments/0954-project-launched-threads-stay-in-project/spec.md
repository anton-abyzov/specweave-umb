# Project-launched threads stay in their project

## Problem

On October 19, 2026 five agent-launched worker threads appeared in the user's global Chats as "No project": "Prepare-update session: lapse, don't revoke" and "Release retry must not hide unhandled errors" (from "Clean completed app worktrees", 13:28), and 0948, 0949+0950 and 0951 (from the project-joining lead, 23:13). All were started from threads in project specweave with `studio_thread_launch scratch:true`, because project specweave lists no app repository and `existing_worktree` refuses worktrees of other repositories. The user expects a request sent in a project to create threads in that project. Only a request the user explicitly makes without a project should go to global Chats. No supported API can re-home a live thread without restarting it.

## Scope

In: SpecWithCode (`anton-abyzov/specwithcode-dev`):
- the `studio_thread_launch` scratch branch (handlers.ts, tools.ts; coordinate with 0945),
- ThreadMoveService and its dialog, for an in-place adoption of a "No project" thread,
- the move dialog copy.

Out: adding repositories to a project, which is the user's access decision; sidebar ordering, owned by 0952.

## Acceptance Criteria

- [ ] AC-01: `studio_thread_launch scratch:true` from a thread whose project is not the Scratch project is refused. The reason names that project and how to stay in it. The launch goes through only with `projectless:true`, documented as "only when the user asked for a chat outside any project". Callers outside a thread and threads in the Scratch project keep today's behavior.
- [ ] AC-02: Moving a "No project" thread to a project keeps it in place, with nothing restarted, stopped, archived or copied. The conversation, its folder binding, runs, queue and owner stay. Only its project changes. The thread's event history keeps where it started.
- [ ] AC-03: The dialog explains this for a "No project" thread: "it keeps its conversation and folder". It offers no "Start it there now".
- [ ] AC-04: Adoption is user-only and refuses archived, paused or missing targets. Repeating it after it landed is refused as "already in that project", and nothing changes.

## Decisions

### Asked
- none
### Defaulted
- D-01: Refuse rather than silently re-route scratch launches from project threads. Agents get a reason they can act on, and the projectless path stays available with explicit intent.
- D-02: Adoption is safe without a restart only for the Scratch project, because it has no project folder or memory the thread would leave behind.

## Tasks

### T-01 Scratch guard for project callers
- AC: AC-01 | Files: apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/tools.ts | Test: vp test run apps/server/src/mcp/toolkits/project/handlers.test.ts

### T-02 In-place adoption of No-project threads
- AC: AC-02, AC-03, AC-04 | Files: apps/server/src/orchestration-v2/ThreadMoveService.ts, apps/server/src/orchestration-v2/Orchestrator.ts, apps/web/src/components/ThreadMoveDialog.tsx | Test: vp test run apps/server/src/orchestration-v2/ThreadMoveService.test.ts

### T-03 PR, merge, and repair of the five threads
- AC: AC-01, AC-02 | Files: none | Test: after the release, the user moves the five chats to specweave; db query shows project_id 1332065e-... with runs unchanged

### T-04 Verify and close 0954
