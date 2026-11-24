# Shared project tooltip and cross-machine link suggestion

## Problem

Two gaps in the SpecWithCode Projects sidebar (repo `anton-abyzov/specwithcode`):

1. The shared (`Share2Icon`, coordinator) and handed-off (`ArrowRightLeftIcon`, workers) icons in `apps/web/src/components/studio/shell/SidebarProjectList.tsx` carry their meaning ("Shared from M4 Max with Ministorm") only as an `aria-label`. Hovering shows nothing.
2. EasyChamp (`github.com/anton-abyzov/sw-easychamp`) is open on M4 (project `5848bdc2-3ac2-4ecb-b66e-c10840260324`, `logicalProject` null, workspace root is the repository root) and on M1 (project `58004cd4-5d17-4ad7-9f40-216d98da3bd2`, plus three `machine-handoff:*` staging copies). No "Same repository as X on <machine>. Link them?" suggestion shows. Linking is only reachable through Project settings > Machines.

Root cause of 2: the sidebar groups projects with `buildProjectGroups` in the default `repository` grouping mode, which keys an unlinked project by its repository's canonical key. Two unlinked copies of one repository on two machines therefore become one row whose members span both machines. `duplicateLinkSuggestions` (`apps/web/src/studio/duplicateProjectLink.ts`) only pairs two separate rows (`same.length !== 2`) and drops any row with a non-plain member (such as a `machine-handoff:*` copy), so the merged row never gets a suggestion. Its unit tests built two separate groups by hand, a shape the default grouping does not produce for two unlinked copies.

## Scope

In: a visible hover tooltip on the shared/handed-off icon; a link suggestion on one sidebar row that merges unlinked copies of one repository from two machines; unit tests for both. Out: changes to the link dialog, server-side matching, or grouping modes.

## Acceptance Criteria

- [ ] AC-01: Hovering the shared or handed-off icon on a sidebar project row shows its label (the same text as its `aria-label`) as a native tooltip; the `aria-label` stays.
- [ ] AC-02: A sidebar row that holds exactly two plain, unlinked copies of the same repository (same remote and same place inside it) on two different machines gets the "Same repository as X on <machine>. Link them?" suggestion, anchored on this machine's copy, with the other machine's copy as the candidate.
- [ ] AC-03: The existing safety conditions still hold for the merged row: no suggestion when copies differ by repository or folder inside it, share a machine, are linked, are three or more plain copies, or were dismissed. Non-project staging copies (`machine-handoff:*`, handoff folders) in the row are ignored rather than blocking it.

## Approach

`SidebarProjectList.tsx`: wrap each shared icon in a `span` carrying `title`, `role="img"`, `aria-label` and the `data-shared-project` attribute, matching the link-suggestion span next to it (rows already use native `title`; no Tooltip component there). The icon becomes `aria-hidden`.

`duplicateProjectLink.ts`: after the two-row pass, a merged-row pass: for each group not already suggested, take its plain eligible members; when there are exactly two, on two machines, both unlinked, with one repository key, suggest the copy elsewhere joining the copy on this machine (only when one of them is on this machine, so the anchor is unambiguous). Rejected: changing the grouping so unlinked copies split into two rows, since that changes every sidebar user's layout.

## Decisions

### Asked
- D-01 Where to edit, given the hook that blocks manual worktrees → pending (user)
### Defaulted (change any before sw-do)
- D-02 Native `title` tooltip, matching the row's other hints → default
- D-03 The merged row is suggested only when one copy is on this machine → default
### Open
- none

## Tasks

### T-01 Shared icon hover tooltip
- AC: AC-01 | Files: apps/web/src/components/studio/shell/SidebarProjectList.tsx, apps/web/src/components/studio/shell/SidebarProjectList.test.tsx | Test: npx vitest run apps/web/src/components/studio/shell

### T-02 Link suggestion for a row merged across machines
- AC: AC-02, AC-03 | Files: apps/web/src/studio/duplicateProjectLink.ts, apps/web/src/studio/duplicateProjectLink.test.ts | Test: npx vitest run apps/web/src/studio/duplicateProjectLink.test.ts

### T-03 Verify and close 1253
- AC: AC-01, AC-02, AC-03 | Files: none | Test: specweave verify 1253

## Follow-up

Anton's November 7, 2026 scope addition (Use worktrees default for new projects and one-click enable) outgrew this increment and is tracked as [1256](../1256-use-worktrees-new-project-default-and-one-click-enable/spec.md), shipped in the same release.
