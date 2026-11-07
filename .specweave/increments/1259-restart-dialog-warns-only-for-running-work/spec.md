# Restart dialog warns only for running work

## Problem

Pressing Restart to update opens "Restart to install SpecWithCode 1.0.207?" even when the only things open are questions and approvals waiting on the user (Anton, November 7, 2026, screenshot of "1 running, 2 questions waiting in 2 threads"). A turn paused on a question also counts as "1 running", because its run stays active while it waits. Those requests are closed and asked again after the restart (0991), so nothing is lost, yet they open the dialog and keep "Restart when idle" waiting until the hold window ends.

## Scope

In: the server marks the work of a thread that only waits on a person; the app restart dialog, its "Restart when idle" wait and the Update now confirm ignore that work. Out: the update agent's unattended quiet install (its 2-minute stale-wait release stays), tool calls and sign-ins (still count as work), wording elsewhere in Settings.

## Acceptance Criteria

- [x] AC-01: The prepare result marks each blocker of a thread whose blockers are only runs, sessions and requests, with every request an approval or question that is asked again, as `waitsOnPerson: true`; a thread with a sign-in, tool-call request, effect, queued message, live subagent node or pending background task is not marked.
- [x] AC-02: Restart to update restarts at once, without a dialog, when the only open work waits on the person (questions and approvals are closed and asked again after the restart).
- [x] AC-03: When real work runs, the dialog shows one summary line, lists only the running threads (rows open the thread) with counts in one aligned column, and notes under the list how many questions and approvals are asked again after the restart and how long Restart when idle waits.
- [x] AC-04: "Restart when idle" restarts as soon as only person waits remain.
- [x] AC-05: Update now asks no stop question when only person waits remain.
- [x] AC-06: A service that omits `waitsOnPerson` keeps the current behavior.

## Approach

Server `ServiceUpdateBlockers.summarizeBlockers` computes `waitsOnPerson` per thread from the rows (kinds and request kinds), reusing the stale-wait request kinds, moved there from `ServiceUpdatePreparation.ts`. Contract adds optional `waitsOnPerson`. Web: `describeAppRestartWarning`, `describeServiceUpdateStop` and `groupRunningWork` drop person-wait blockers from the work; the question line counts all requests. No staleness check: a person pressed the button and the requests are asked again.

Rejected: dropping all `request` blockers on the client alone. A paused turn's `run` blocker would still read as running, which is the case in the screenshot.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Nothing runs → no dialog at all, the restart starts at once (asked by the task; reversible).
- D-02 Sign-ins (`auth_refresh`) still count as work, as they do for the stale-wait release.
### Open
- none

## Tasks

### T-01 Server marks person waits
- AC: AC-01 | Files: packages/contracts/src/serviceUpdatePreparation.ts, apps/server/src/serviceUpdate/ServiceUpdateBlockers.ts, apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts | Test: cd ../specwithcode-dev/apps/server && npx vitest run src/serviceUpdate/ServiceUpdateBlockers.test.ts

### T-02 Restart dialog, idle wait and Update now ignore person waits
- AC: AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, apps/web/src/components/sidebar/restartRunningWork.logic.ts, docs/studio/updates.md | Test: cd ../specwithcode-dev/apps/web && npx vitest run src/components/sidebar/SidebarRestartToUpdate.logic.test.ts

### T-03 Verify and close 1259
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1259
