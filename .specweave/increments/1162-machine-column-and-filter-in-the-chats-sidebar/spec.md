# Machine column and filter in the Chats sidebar

## Problem

The sidebar's Chats rows show a small unnamed laptop icon only on chats from another machine, so the one chat local to this machine looks like it lost its icon, and no row says which machine it runs on. The icon also shifts when a status dot appears. Evidence: the November 1, 2026 screenshot on the M4, and `StudioSidebar.tsx` rendering `LaptopIcon` only for `machine || location.moved`, with `machine` null on the primary environment.

## Scope

In: a named, aligned machine column on every chat row when the list spans machines; a Machine filter in the Chats filter menu with an "On <machine>" pill above the list; a Machine option under Group by. Out: the Projects list; the Threads pane, which already has its column and filter; server or contract changes.

## Acceptance Criteria

- [ ] AC-01: When chats run on more than one machine, on a machine other than this one, or moved, every row shows its machine name in one right-aligned column, including this machine's chats; a list on this machine alone shows no column.
- [ ] AC-02: The status dot and plan chip sit before the column, so the column does not shift when a dot appears; a moved chat shows `→ <machine>` and an unreachable machine shows the offline mark beside its name.
- [ ] AC-03: A Chats list narrower than 224 px keeps the first letters of the name; the tooltip and screen reader text name the machine on every row.
- [ ] AC-04: With more than one machine, the filter menu offers Machine with each machine's open chat count; choosing one narrows the list, is remembered, shows an "On <machine>" pill above the list, and Show all or Reset to defaults undoes it.
- [ ] AC-05: A saved machine filter survives remote hosts loading and is dropped once every host has answered and that machine has no chats; a filtered empty list says so by machine.
- [ ] AC-06: Group by offers Machine, with one heading per machine; the column hides there because the headings name the machine, and the offline mark stays.

## Approach

`threadMachineFilter.ts` gains `chatsShowMachineColumn`, the pure rule for whether the column shows. `shellModel.ts` gains the `machine` grouping and a machine-aware empty message. `StudioSidebar.tsx` computes options from the chats the current "Agent threads" choice lists, regardless of status and activity, so the column does not come and go as those filters change. A saved filter is only dropped against live snapshots from every host and across all chats, so a machine hidden by "Agent threads" keeps its filter. The filter is stored apart from `ChatListOptions` under `studio:chats-machine:v1`, because its value is a machine id rather than a fixed choice. Rejected: a filter-only design with no row label (the user still could not read a row's machine) and keeping the icon on every row (an icon does not say which machine).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A named text column replaces the unnamed laptop icon, matching the Threads pane (reversible).
- D-02 The column follows the execution machine, the same machine the filter uses (reversible).
### Open
- none

## Tasks

### T-01 Machine column and offline mark on chat rows
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/threadMachineFilter.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/StudioSidebar.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/shell.css | Test: npx vp test run --project unit src/studio/threadMachineFilter.test.ts src/components/studio/shell/StudioSidebar.test.tsx

### T-02 Machine filter, pill and Group by Machine
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/StudioSidebar.tsx | Test: npx vp test run --project unit src/studio/shellModel.test.ts src/components/studio/shell/StudioSidebar.test.tsx

### T-03 Headless evidence, release and installed check on the M4
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/sidebar-stable-order/chat-machines.mjs | Test: headless chat-machines.mjs at wide and narrow widths

### T-04 Verify and close 1162
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify
