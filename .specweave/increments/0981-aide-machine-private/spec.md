# One private personal assistant per machine

## Problem

On October 20, 2026 the user set this rule:
- there is exactly one personal assistant (Aide) per machine;
- connecting to Anna's notebook shows Anna's machine's own assistant, with a completely different context;
- personal assistant context is never shared, so personal assistants have no handoff.

This rule overrides the earlier one-assistant-per-fleet design. Per-project thread handoff stays.

What the code does today, on `anton-abyzov/specwithcode-dev` main at d6dc8ec68e:

- **Clients aim for one assistant per fleet.** The web (`apps/web/src/studio/personalAssistant.ts`) opens another machine's assistant before creating one, creates on the lowest environment id, and offers "Create a separate assistant". iOS (`ShellSummaries.swift`) keeps one assistant across all linked machines.
- **The server singleton is incomplete.** `ManagedProjectFolders.ts` keeps one personal project per server for `projectsCreateNew`. But `studio_project_create` with a `workspaceRoot` passes `kind` straight to `ProjectService.create` and can make a second one. The decider also accepts a workspace patch that changes `kind`, and nothing serialises two concurrent creates.
- **Machine-to-machine access reaches the assistant.** Work grants of kind `all` (the default for legacy coordinators) make a personal project and its threads listable, readable, sendable and interruptible by another machine's coordinator (`workGrantPolicy.projectInGrant`, `workGrantAccess.assertThreadWritable`). Linked memory and plan export also have no kind check.
- **No kind check on these paths:** remote launch into a personal project (`machineProjectId`), a personal coordinator launching on another machine, `studio_thread_migrate`, limit handoff and thread handoff mode.
- **Already safe:** `MachineHandoff` (project handoff, folder copy) and the `ProjectLink` link steps refuse non-code projects. `studio_project_route` sends one user message, not history.

## Scope

**In** (all in `anton-abyzov/specwithcode-dev`):
- server enforcement of one assistant per machine;
- server isolation of the assistant from every machine-to-machine path;
- web selection and labelling of each machine's assistant;
- hiding handoff, Run on and copy controls for the assistant;
- tests and headless evidence with fictional machines;
- an audit of existing duplicates on the M4 through the approved CLI.

**Out:**
- iOS Swift (`apps/ios`). The iOS owner `mcp:2c7d2701-3df2-4e93-b3b9-41460a03eaa4` owns voice and call support, the Aide scroll hang and broken links, and iOS assistant selection. I coordinate the shared contract with them.
- `apps/server/src/handoff/HandoffMode.ts`, which the 0967 owner is editing. I give them a guard to call.
- Any deletion, merge, archive or kind change of existing projects.
- Paid call or TTS services.
- Copying credentials.

## Access model

- **Explicit access:** a client session issued by a machine itself (that machine's desktop app, or a device the owner paired to that machine). It sees that machine's assistant. Connecting to Anna's notebook therefore shows Anna's assistant, labelled with her machine's nickname, never merged with yours.
- **Machine-to-machine access** (work grants, remote MCP calls, threads started by another machine's work, linked memory or plan sync, link preview, handoff, migrate, limit handoff, remote launch): never reaches a personal project, whatever the grant kind, including `all` and `listed`.
- **Routing:** `studio_project_route` keeps sending only the one user-authored message to a local project's coordinator. It never sends assistant history or memory.

## Acceptance Criteria

- [ ] AC-01: A machine has at most one personal project that is not deleted. Archived ones still count.
  - A create of kind `personal` from any path (`projectsCreateNew`, `studio_project_create` with or without `workspaceRoot`, CLI, HTTP) returns the existing one or is refused with a typed reason when one exists.
  - Two concurrent creates produce one assistant.
  - A project's kind cannot be changed after creation.
- [ ] AC-02: Machine-to-machine callers never see or reach a personal project:
  - `studio_project_list` omits it, and `studio_project_read`, thread list, read, send, interrupt and wait refuse it, for every grant kind;
  - the refusal says the assistant is private to its machine;
  - remote launch with a personal `machineProjectId` is refused.
- [ ] AC-03: A personal assistant cannot leave its machine:
  - its coordinator cannot launch workers on another machine, and routing stays local;
  - linked memory export, linked plan export and link preview refuse it with no content;
  - `studio_thread_migrate` and limit-handoff candidates exclude its threads;
  - a shared guard (`assertNotMachinePrivate`) is given to 0967 for `HandoffMode`.
- [ ] AC-04: The web shows one assistant per machine:
  - Set up opens or creates the assistant on the chosen machine only, with no "Create a separate assistant" and no opening of another machine's assistant;
  - with more than one machine, each assistant is labelled with its machine nickname, for example "Aide · Anna's MacBook";
  - a duplicate from before this rule stays visible with its history, is marked "extra" after its machine name, and is listed after every machine's own assistant.
- [ ] AC-05: Handoff controls (project handoff, Run on, Add to machine, consolidate) are not offered for a personal project.
- [ ] AC-06: Existing data is preserved. No migration deletes, merges, archives or rewrites a project. Duplicates found by the audit are reported with counts only. Any destructive cleanup is a separate decision asked with `ask_user`.
- [ ] AC-07: Tests cover pairing, switching machine, reconnect, an offline machine, remote calls, a guest (grant-bearing) caller and concurrent singleton creation. Headless evidence with two fictional machines is saved in `evidence/`.

## Decisions

- D-01: The assistant of a machine is its earliest-created non-deleted personal project. This needs no new id, no schema change and no migration. Later duplicates keep `kind: personal` and their data.
- D-02: The singleton is enforced in the project decider, under a dedicated lock, so every create path is covered.
- D-03: Isolation is enforced on the receiving machine's server (`projectInGrant` and the export and launch entry points). Client filtering is presentation only.
- D-04: Kind is immutable after creation. Converting the assistant to a code project would make private history linkable.
- D-05 (open gate, not in this increment): a hub-brokered phone code (`/api/studio/fleet/phone/mint`, `apps/server/src/fleet/phoneLinks.ts`) gives a phone standard client scopes on every fleet machine, Anna's notebook included, so that phone can read Anna's assistant without her machine's owner pairing the phone directly. Closing this needs sessions to carry how they were issued, plus filtering of personal projects and their threads in client reads for brokered sessions. That reaches the snapshot pipeline and phone linking (0970). It is raised with the iOS and phone owner as a follow-up and is not claimed as fixed.

## Tasks

### T-01 Singleton assistant per machine in the decider
- AC: AC-01, AC-07 | Files: apps/server/src/orchestration-v2/ProjectCommands.ts, apps/server/src/project/ProjectService.ts, apps/server/src/project/ManagedProjectFolders.ts, packages/shared/src/personalAssistant.ts | Test: vp test run apps/server/src/orchestration-v2/ProjectCommands.test.ts apps/server/src/project/ProjectService.personalAssistant.test.ts

### T-02 Machine-to-machine isolation of the assistant
- AC: AC-02, AC-03, AC-07 | Files: apps/server/src/fleet/workGrantPolicy.ts, apps/server/src/mcp/workGrantAccess.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/remoteLaunch.ts, apps/server/src/project/LinkedMemorySync.ts, apps/server/src/project/ProjectPlanService.ts, apps/server/src/project/ProjectLink.ts, apps/server/src/mcp/toolkits/orchestrator/migrate.ts, apps/server/src/orchestration-v2/MachineLimitHandoff.ts | Test: vp test run apps/server/src/fleet apps/server/src/mcp apps/server/src/project

### T-03 Web: one assistant per machine, labelled; no handoff controls
- AC: AC-04, AC-05 | Files: apps/web/src/studio/personalAssistant.ts, apps/web/src/components/CommandPalette.tsx, apps/web/src/components/studio/shell/StudioSidebar.tsx, apps/web/src/studio/addToMachine.ts, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: vp test run apps/web/src/studio apps/web/src/components/studio

### T-04 Audit existing assistants and coordinate shared scope
- AC: AC-06 | Files: none | Test: `specweave-studio db query` counts of personal projects on the M4; messages to the 0967, 0969 and iOS owners

### T-05 Headless evidence with two fictional machines
- AC: AC-04, AC-05, AC-07 | Files: apps/web/tests/aide-per-machine/ | Test: headless Playwright; evidence in .specweave/increments/0981-aide-machine-private/evidence/

### T-06 PR, release coordination and installed check
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: installed version on the M4, singleton create refused twice, headless

### T-08 Preserve personal kind in title-only MCP creation
- AC: AC-01, AC-02 | Files: apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/handlers.test.ts, apps/server/src/mcp/toolkits/project/workGrants.test.ts | Test: vp test run apps/server/src/mcp/toolkits/project
- Follow-up from installed 1.0.68 acceptance: pass the requested kind to ManagedProjectFolders so repeated personal creation returns the existing assistant.

### T-07 Verify and close 0981
