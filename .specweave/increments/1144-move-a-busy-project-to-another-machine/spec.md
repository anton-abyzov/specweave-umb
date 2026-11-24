# Move a busy project to another machine

## Problem

"Hand off and continue there" (copy-and-move) can never finish for the specweave umbrella moving from the M4 to ministorm. Threads keep writing ledger and metadata files, and copy-and-move checks the live tree instead of a captured copy. approve() refuses ("The copy was refused. The source changed…") once the destination has content, and the coordinator move needs the whole tree byte-identical (sourceService.assertCurrentSnapshot), so it fails with a bare source_changed. Seen live on 1.0.123, 2026-10-29.

## Scope

In: capture copy-and-move like copy-only (with keep-last bytes for files that never settle); replace whole-tree equality at the handover with a path-level drift list; let the person copy again, move without the listed paths, or keep the coordinator on the source; show paths left on the source on the done screen; update docs. Out: automatic delta copy of post-capture changes (follow-up), legacy records and non-capturable volumes (keep strict checks, now with a list).

## Acceptance Criteria

- [x] AC-01: A copy-and-move into a destination that already holds the project succeeds while ledger files change on the source; Apply writes the captured bytes.
- [x] AC-02: When files changed after the copy, the move is refused with the exact list of changed paths and repositories, not a bare error.
- [x] AC-03: "Move without these N paths" completes the move; the accepted paths are recorded and a new path forces a fresh review.
- [x] AC-04: The done screen names the paths that stayed on the source.
- [x] AC-05: The user docs describe the capture, the list and the three choices.

## Approach

Design from workflow wf_794fbd85-fb0 ("Captured move with a path-level drift review at the fence"), saved in the session scratchpad as move-design.json. Files: sourceSnapshot.ts (keep-last), sourceService.ts (capture both modes, drift-basis.json), new sourceDrift.ts (computeDrift with size+ctime+ino+dev shortcut), folderCopyPreparation.ts (driftSince + acceptedSourceChanges), MachineHandoff.ts (extract bundle helper, pass acceptance, copyDrift RPC), FolderCopyHandoff.ts, contracts, useCoordinatorTransfer.ts, handoffCopySteps.ts, new HandoffSourceChanges.tsx and useCoordinatorMove.ts, HandoffCopyDone.tsx, docs/user/moving-a-project.md. Acceptance is by path, by a digest the server produced, so a ledger that keeps changing cannot bounce an accepted move. Rejected: a fenced delta with a new "sealed" publication state (holds the fence for minutes, large contract churn).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Paths changed after the copy stay on the source when the person picks "Move without these" → recorded and listed on the done screen (reversible: copy again later).
- D-02 Legacy records and network or coarse-timestamp volumes → strict refusal with the list, no acceptance.
### Open
- none

## Tasks

### T-01 Capture copy-and-move and review drift at the handover
- AC: AC-01, AC-02, AC-03 | Files: apps/server/src/fleet/folderTransfer/sourceSnapshot.ts, apps/server/src/fleet/folderTransfer/sourceService.ts, apps/server/src/fleet/folderTransfer/sourceDrift.ts, apps/server/src/fleet/folderCopyPreparation.ts, apps/server/src/fleet/MachineHandoff.ts, apps/server/src/fleet/machineHandoffBundle.ts, apps/server/src/fleet/FolderCopyHandoff.ts, packages/contracts/src/machineHandoff.ts, packages/contracts/src/folderCopy.ts | Test: cd apps/server && npx vp test run src/fleet/folderTransfer src/fleet/MachineHandoffFolderCopy.test.ts src/fleet/MachineHandoff.test.ts

### T-02 Show the change list and the three choices
- AC: AC-02, AC-03, AC-04 | Files: apps/web/src/components/studio/useCoordinatorTransfer.ts, apps/web/src/components/studio/handoffCopySteps.ts, apps/web/src/components/studio/useCoordinatorMove.ts, apps/web/src/components/studio/HandoffSourceChanges.tsx, apps/web/src/components/studio/HandoffFolderCopy.tsx, apps/web/src/components/studio/handoffFolderCopyPending.ts, apps/web/src/components/studio/HandoffCopyDone.tsx | Test: cd apps/web && npx vp test run src/components/studio

### T-03 Document moving a busy project
- AC: AC-05 | Files: docs/user/moving-a-project.md | Test: grep -q "Files that change while moving" docs/user/moving-a-project.md

### T-04 Verify and close 1144
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1144-move-a-busy-project-to-another-machine
