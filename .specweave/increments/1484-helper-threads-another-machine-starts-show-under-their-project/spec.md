# Helper threads another machine starts show under their project, not as loose No project chats

## Problem

On November 25, 2026 the 1482 push worker on M5 (a coordinator's `delegate_task` child in the specweave project) started "Git push credentials check on win" on win. win has no copy of specweave, so the worker passed `scratch: true, projectless: true`: `studio_thread_launch` refuses a scratch launch from a project thread without `projectless`, and that flag means "a chat outside any project". The thread landed in win's "No project" folder (`C:\Users\AntonAbyzov\.specwithcode\scratch\2026-11-25-goal-on-this-windows-machine-fad2d1d3`).

What the person then saw:

- Opened from the worker's link, the thread's header says "No project / Git push credentials check on win". Only the "From SpecWithCode · M5" chip hints where it came from. It does not name specweave or link the thread that asked for it.
- Its final report ends with `Blockers:`, so it shows Blocked and counts as needing the person, a stray card of its own. But its report went to the M5 worker that launched it (`reportBack`), and that worker relays it. A provider subagent or a worker's `delegate_task` child reporting to an agent never counts (`reportsToParentAgent`). A helper on another machine does.
- The origin it carries holds only the parent thread id (`originHint.parentThreadId`). The sidebar groups the chat with its requester's project (#388) only while the requester's thread shell is loaded. When it is not loaded (for example, the requester's machine is offline), nothing names the project.

The same worker's helpers on m4, m1 and linux-mini went into those machines' specweave copies and were fine.

## Scope

In:
- The sending machine passes the caller's project title in the origin hint, and the receiving machine keeps it on the thread's origin.
- A scratch launch from a project thread to a machine that has no copy of the project is allowed without `projectless`: it is that project's helper, listed under the project on the sending machine. The tool's text says so.
- The chat header of a helper chat names the requesting project and links the parent thread, instead of "No project".
- The chats list groups a helper chat under "From <project> on <machine>" when the requesting thread is not loaded.
- The parent thread shows the blockers of the helper chats it started on other machines, with a link to each. The helper keeps raising attention on its own as before: the worker that started it may have moved on (the 1482 worker's latest report no longer named the win sign-in), so dropping it from counts could lose a blocker.

Out: moving existing chats into projects; creating a project copy on the target; changing grants or project scope; the gh sign-in on win (owned by 1482 and the owner).

## Acceptance Criteria

- [x] AC-01: A remote launch by a thread sends `originHint.projectLabel` (the caller's project title, cleaned, at most 200 characters). The receiving machine stores it as `origin.parentProjectLabel`. An origin hint without it still decodes, and an older machine ignores it.
- [x] AC-02: `studio_thread_launch` with `scratch: true` and a named `machine` from a project thread succeeds without `projectless` when that machine has no copy of the project: not a member of its logical project, no saved worker project there, and a fresh probe of that machine alone reports no match from a complete list under a grant that says it shows every project. It is still refused when the machine has a copy, when no machine is named, and when the probe cannot confirm the absence (unreachable, list cut short or unreadable, repositories still being read, grant scope not "all" or not stated). The destination names its own "No project" folder (`scratchProjectId` in `studio_project_list`), so that folder is not taken for a repository still being read. The refusal and the tool description say which applies.
- [x] AC-03: For a chat in a machine's "No project" folder whose origin has a parent thread, the chat header shows the requesting project's name (from the loaded parent thread, else `parentProjectLabel`), followed by "· on <machine>", and links to the parent thread. A person's own chat still shows "No project".
- [x] AC-04: In the chats list, a helper chat whose requesting thread is loaded (including a subagent requester) opens from its project, not Chats. A helper whose requester is not loaded is grouped under "From <project> on <machine>" (or "From <machine>" from a machine that sent no project name), not under "No project".
- [x] AC-05: A launch whose origin hint carries a key the receiving build does not know still succeeds there (version skew with 1.0.431 and 1.0.432).
- [x] AC-06: A thread shows a note for each helper chat it started on another machine that is blocked: the helper's title, its machine and the blocker text, with an Open link. When the starting thread is a subagent, its root thread shows the note too. The note goes away once the helper is no longer blocked, archived or resolved.

## Approach

- Contracts: `packages/contracts/src/orchestratorMcp.ts` (`OrchestratorMcpOriginHint.projectLabel`), `packages/contracts/src/orchestrationV2.ts` (`OrchestrationV2ThreadOrigin.parentProjectLabel`). Both optional, so older machines ignore them (Effect Schema drops excess keys).
- Server: `apps/server/src/mcp/toolkits/project/remoteLaunch.ts` sends the label. `apps/server/src/mcp/threadOrigin.ts` cleans and stores it. `apps/server/src/mcp/toolkits/project/handlers.ts` allows a scratch launch to a machine with no copy. `tools.ts` changes the wording.
- Web: `apps/web/src/studio/standaloneChats.ts` gains `helperChatOrigin` (one resolver for header, list and parent note). `apps/web/src/components/chat/ChatHeader.tsx` gets the breadcrumb. `StudioSidebar.tsx` gets the label (it is at 1,490 lines, so the logic stays in `standaloneChats.ts`). A new `apps/web/src/components/chat/HelperChatBlockers.tsx` is rendered from `ChatView.tsx` beside the existing blocker note.
- Rejected: moving the thread into a real project on the target. That crosses the grant's project scope, and the target may not have the repository. Also rejected: reinterpreting `projectless` on the server. Grouping is display only.
- Risk: version skew. New fields are optional and display only, and the scratch allowance is checked on the sending machine.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: A helper's blocker keeps counting on its own; the starting thread (and its root) shows it too (reversible; rejected: dropping it from counts via `reportsToParentAgent`, which loses a blocker the worker no longer relays).
### Open
- none

## Tasks

### T-01 Origin carries the requester's project
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestratorMcp.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/threadOrigin.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunch.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/threadOrigin.test.ts | Test: vp test run apps/server/src/mcp/threadOrigin.test.ts

### T-02 Scratch helper on a machine without the project
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/scratchHelper.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/scratchHelper.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/RemoteWorkers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/workGrants.test.ts | Test: vp test run apps/server/src/mcp/toolkits/project/scratchHelper.test.ts

### T-03 Helper chats read as their project's
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/standaloneChats.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/standaloneChats.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ChatHeader.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/HelperChatBreadcrumb.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/HelperChatViews.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/StudioSidebar.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/sidebar-stable-order/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/sidebar-stable-order/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/sidebar-stable-order/reviewers.mjs, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/helperChats/, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/HelperChatViews.locale.test.tsx | Test: vp test run apps/web/src/studio/standaloneChats.test.ts apps/web/src/components/chat/HelperChatViews.test.tsx && node apps/web/tests/sidebar-stable-order/reviewers.mjs

### T-04 Blockers show in the starting thread; skew-safe origin hint
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/HelperChatBlockers.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunch.test.ts | Test: vp test run apps/web/src/components/chat/HelperChatViews.test.tsx apps/web/src/studio/standaloneChats.test.ts apps/server/src/mcp/toolkits/project/remoteLaunch.test.ts
