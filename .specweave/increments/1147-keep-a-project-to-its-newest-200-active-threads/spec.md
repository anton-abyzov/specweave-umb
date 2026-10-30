# Keep a project to its newest 200 active threads

## Problem

The specweave project on the M4 has 1,629 threads, and 1,623 of them are live (checked 2026-10-30 with `specweave-studio db query`). The 30-day inactive archive (`archiveInactiveThreadsAfterDays`, InactiveThreadArchiveGuard.ts) only accepts threads with `createdBy: "user"`, a web or mobile `creationSource`, and no parent thread. In this project 1,622 of the live threads were created by agents: 1,082 by a provider and 540 through MCP, mostly coordinator-delegated workers. Because of that, nothing ever archives them. The project list grows without bound, coordinator handoffs hit their context limits (increment 1145), and the owner asked for a cap of 100 to 200 live threads per project.

## Scope

In:
- A project setting "Keep active chats per project", default 200, range 20 to 5000, or "No limit".
- A server sweep that archives the oldest finished threads beyond the cap. It covers agent-created and child threads, with every protection the inactive archive already has.
- A settings row next to "Archive inactive chats".

Out:
- Deleting threads. Archiving is soft and reversible with Unarchive.
- Recreating projects.
- Changing the 30-day rule.

## Acceptance Criteria

- [ ] AC-01: When a project has more live threads than its cap, the server archives the oldest finished threads until the count is at the cap, about 50 per minute. This applies to agent-created and child threads too.
- [ ] AC-02: The sweep never archives:
  - the coordinator;
  - a running, queued, waiting, pinned, snoozed, stopped-but-unanswered or blocked thread;
  - a thread with a pending request, open terminal, saved draft or watched PR;
  - a thread owned by or executing on another machine;
  - a thread active within the last hour;
  - a thread that a routine targets.
- [ ] AC-03: The setting is in Settings > Storage, defaults to 200, accepts a custom value from 20 to 5000 or "No limit", and can be overridden per project.
- [ ] AC-04: An archived thread keeps its history and comes back with Unarchive.

## Approach

Contracts (`workspaceLifecycleSettings.ts`, `settings.ts`, `orchestrationV2.ts`):
- Add `keepActiveThreadsPerProject`, a nullable integer from 20 to 5000 with a default of 200, plus its patch key.
- Extend the `thread.archive` sweep marker with an optional `reason: "overflow"`. A sweep archive still skips cleanup and runs under the guard.

`InactiveThreadArchiveGuard.ts`:
- Split the protections into `isSweepArchiveProtected(thread, { allowAgent })`.
- Add `isOverflowArchiveCandidate`, which allows agent and child threads but needs one idle hour.
- For overflow, the guard re-counts live threads in the project and refuses when the project is at or under its cap. It refuses a thread that a routine targets by `thread_id`, rather than every thread in a project that has a routine.

`InactiveThreadArchive.ts`:
- After the inactive page, take projects with more than 20 live threads.
- Resolve each project's cap, then select the oldest `count - cap` threads by `updated_at`, excluding coordinator ids, up to 50 per sweep.
- Dispatch them.

Web:
- Add `ActiveThreadCapSetting.tsx` in StorageSettings, modelled on InactiveThreadArchiveSetting.

Rejected alternatives:
- Deleting old threads, because it loses history.
- Capping at create time, because that blocks new work.
- Widening the 30-day rule to agent threads, because that would not bound a project that creates hundreds of threads a week.

Risks:
- A worker's parent coordinator may refer to an archived child. Archived threads still resolve by id, so links keep working.

## Decisions

### Asked
- D-01: Should projects be capped at a live thread count? → Yes, 100 to 200 (owner, 2026-10-30). I took 200.
### Defaulted (change any before sw-do)
- D-02: On by default at 200 for every project, overridable per project (reversible).
- D-03: Overflow candidates must be idle for 1 hour (reversible).
### Open
- none

## Tasks

### T-01 Overflow archive setting, guard and sweep
- AC: AC-01, AC-02, AC-04 | Files: packages/contracts/src/workspaceLifecycleSettings.ts, packages/contracts/src/settings.ts, packages/contracts/src/orchestrationV2.ts, apps/server/src/orchestration-v2/InactiveThreadArchiveGuard.ts, apps/server/src/orchestration-v2/InactiveThreadArchive.ts, apps/server/src/orchestration-v2/InactiveThreadArchive.test.ts | Test: cd repositories/anton-abyzov/specweave-studio && npx vitest run apps/server/src/orchestration-v2/InactiveThreadArchive.test.ts apps/server/src/orchestration-v2/Orchestrator.inactiveArchive.test.ts

### T-02 Settings row
- AC: AC-03 | Files: apps/web/src/components/settings/ActiveThreadCapSetting.tsx, apps/web/src/components/settings/ActiveThreadCapSetting.test.tsx, apps/web/src/components/settings/StorageSettings.tsx | Test: cd repositories/anton-abyzov/specweave-studio && npx vitest run apps/web/src/components/settings/ActiveThreadCapSetting.test.tsx

### T-03 Verify and close 1147
- AC: AC-01, AC-02, AC-03, AC-04 | Files: .specweave/increments/1147-keep-a-project-to-its-newest-200-active-threads/reports/ | Test: specweave verify 1147-keep-a-project-to-its-newest-200-active-threads
