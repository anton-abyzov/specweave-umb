# Hand off the coordinator of a large project

## Problem

"Hand off coordinator now" refuses for the specweave umbrella (1,629 threads) with "The retained context exceeds the handoff limit. Select a smaller source chat." A coordinator handoff retains the full message history of every thread in the project, capped at 100 threads and 2 MB (MachineHandoff.ts context(), contextWithinLimits). Seen live on 1.0.126, 2026-10-30, after the files were copied to ministorm. Workers keep running on the source, so carrying their transcripts is not needed.

## Scope

In: the coordinator keeps its own history (trimmed to fit, newest first, with a note that older messages stay on the source); worker threads travel as a summary (id, title, branch, status, last activity, short last message), capped with a total count; the dialog explains what moved. Out: moving worker threads or their transcripts; chunked multi-bundle transfer.

## Acceptance Criteria

- [ ] AC-01: A coordinator handoff of a project with more than 100 threads and more than 2 MB of history succeeds; the bundle stays within MACHINE_HANDOFF_MAX_BYTES.
- [ ] AC-02: The destination coordinator receives its own recent history and a summary list of the workers, and says how many older messages and threads stayed on the source.
- [ ] AC-03: A small project still carries full transcripts as before; older peers still accept the bundle.
- [ ] AC-04: The user docs describe what a coordinator handoff carries.

## Approach

Change context() in apps/server/src/fleet/MachineHandoff.ts (extract to a helper module to stay under 1500 lines) and handoffBundle.ts limits; contracts stay backward compatible (optional summary fields). Budget: coordinator messages newest-first up to a byte budget, then worker summaries; full transcripts only when everything fits.

## Decisions

### Defaulted (change any before sw-do)
- D-01 Worker transcripts stay on the source; only summaries travel (reversible).

## Tasks

### T-01 Fit a large project's coordinator context into the handoff
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/handoffBundle.ts, apps/server/src/fleet/coordinatorContext.ts, packages/contracts/src/machineHandoff.ts | Test: cd apps/server && npx vp test run src/fleet

### T-02 Document what a coordinator handoff carries
- AC: AC-04 | Files: docs/user/moving-a-project.md | Test: grep -q "summary" docs/user/moving-a-project.md

### T-03 Verify and close 1145
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specweave verify 1145-hand-off-the-coordinator-of-a-large-project
