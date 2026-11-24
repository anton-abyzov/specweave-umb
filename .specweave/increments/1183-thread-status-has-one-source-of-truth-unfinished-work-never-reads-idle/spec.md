# Thread status has one source of truth; unfinished work never reads Idle

## Problem

On November 2, 2026 the EasyChamp Threads panel listed "Tournament chat video for players" under Idle while the worker had two live background commands watching a deploy, and it was going to resume when they ended. The coordinator chip said Done and the panel said Idle for the same thread. Status is derived separately in `projectThreadGroup`, `threadTone`, `threadCardStatus`, `resolveSidebarThreadStatus`, `resolveThreadStatusPill` and the mobile list, and they disagree.

Evidence: run 10 ended at 22:27:58 UTC, the screenshot file was created at 22:36:04 UTC, and the projection held `pendingBackgroundTasks` `bpx7qsqav` and `bfqtwav7c`, both `kind: command`, with their processes alive.

Causes:

- `backgroundWorkHoldsCompletion` excludes commands, correct for alerts but reused as "is work unfinished".
- `threadDependencyWait` never reads the roster, and returns early for a `delegate_task` child whose run ended.
- `threadTone` calls the Waiting group idle, so the dot disagrees with the section.
- A host that cannot be reached gets an idle dot.
- "Attention unavailable" appears when only a remote worker read is missing, above confident zero counts.
- A finished remote worker (`wake_pending`) on an unread machine keeps coverage incomplete indefinitely.

## Scope

In: one shared wait rule, panel, dot, chip, pill, sidebar, overview and mobile list agreeing, an explicit unknown state, honest partial coverage copy. Out: speeding up the slow fleet endpoints, changing when completion alerts fire, stopping background work, changing server roster derivation.

## Acceptance Criteria

- [x] AC-01: A thread with any live background task, including a `delegate_task` child whose run completed, reads Waiting in the panel, not Idle.
- [x] AC-02: The panel section, dot, chip label, status word, thread pill, sidebar status and mobile list status agree for that thread; none says Idle, Done, Ready or Completed.
- [x] AC-03: A real blocker, held queue, failed run or settled mark still outranks the background wait.
- [x] AC-04: Completion alerts for a run that left only commands running fire as before.
- [x] AC-05: A thread on an unreachable host shows an unknown tone and label, never idle.
- [x] AC-06: When local threads are live and only remote coverage is missing, the summary and empty sections say what was not read rather than "Attention unavailable" above confident zeros.
- [x] AC-07: A remote worker whose run finished (`wake_pending`) does not keep coverage incomplete; a `stopped` worker does, because it may still be running on the other machine.
- [x] AC-08: Traces identify the slow reads, and a failed remote read cannot make local threads read as unknown.
- [x] AC-09: Before and after headless screenshots are saved to files.

## Approach

`threadDependencyWait` in `packages/client-runtime/src/state/projectAttention.ts` becomes the one rule, reading the roster first. `threadTone` gains `background` and `unknown` tones; `threadCardStatus` and rows follow it. `resolveSidebarThreadStatus` and the mobile equivalent read the roster; `ThreadNotificationCoordinator` keeps its old input through a new `resolveThreadAlertStatus`, so alerts are unchanged. Rejected: making commands hold completion, which would bring back the alert suppression #14872 fixed.

Risk: a dev server left running keeps its thread in Waiting with "Background command running". That is true, and sends no alert.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 long-lived commands read Waiting, labelled "Background command running" (reversible).
### Open
- none

## Tasks

### T-01 One wait rule and tones
- AC: AC-01, AC-02, AC-03, AC-05 | Files: packages/client-runtime/src/state/projectAttention.ts, apps/web/src/studio/shellModel.ts, apps/web/src/studio/projectWorkspaceModel.ts, apps/web/src/components/studio/shell/shell.css | Test: npx vitest run packages/client-runtime/src/state/projectAttention.test.ts apps/web/src/studio

### T-02 Sidebar, pill, mobile, alerts
- AC: AC-02, AC-04 | Files: apps/web/src/components/Sidebar.logic.ts, apps/web/src/components/ThreadNotificationCoordinator.tsx, apps/mobile/src/features/threads/threadListV2.ts | Test: npx vitest run apps/web/src/components/Sidebar.logic.test.ts apps/mobile/src/features/threads

### T-03 Honest coverage and the slow request
- AC: AC-06, AC-07, AC-08 | Files: packages/client-runtime/src/state/projectAttention.ts, apps/web/src/studio/shellModel.ts, apps/web/src/components/studio/shell/ThreadsPane.tsx | Test: npx vitest run packages/client-runtime/src/state/projectAttention.test.ts apps/web/src/studio

### T-04 Before and after screenshots
- AC: AC-09 | Files: scratch fixture only | Test: headless Playwright capture saved to files

### T-05 Verify and close 1183
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: none | Test: specweave verify 1183-thread-status-has-one-source-of-truth-unfinished-work-never-reads-idle
