# Filter the project Threads panel by machine, agent and pull request

## Problem

The user could not find a way to focus the project Threads panel on one machine, though a machine filter has shipped since 1.0.143 (#1116). It sits inside the sliders icon, whose tooltip and accessible name both say "Sort threads", below the sort options. Nothing on the panel suggests that filtering exists. With 75 open threads on two machines, focusing on one is an everyday need.

## Scope

In: one quiet filter row in the project Threads panel with machine choices in view, and a filter menu for agent and open pull request.

Out: the sidebar Chats list (it keeps its own menu filter), server changes, and any change to grouping or sorting.

## Acceptance Criteria

- [x] AC-01: When a project's threads run on more than one machine, the panel shows All and each machine as one-click choices, with this machine first and the rest by name, each machine with its open thread count. The order does not change as counts change.
- [x] AC-02: Choosing a machine narrows every group to threads running there, is remembered per project under the existing storage key, and choosing All undoes it. A filter leaves Resolved folded and paging on. The filter lets go once one machine is left. The Machine section and "On X" pill are gone from the sort menu and header.
- [x] AC-03: A filter menu offers Agent when threads use more than one agent, and Open pull request when any thread has one. The filter button does not render when it has nothing to offer.
- [x] AC-04: An active agent or pull request filter shows as a removable chip in the row, is remembered per project, and machine counts reflect it.
- [x] AC-05: A machine with a thread waiting on the person that the filters keep off the list shows a waiting dot on its choice, except in unattended check projects. The summary line stays project-wide, so a filter cannot silently hide a request.
- [x] AC-06: When filters leave no thread, the panel says so and offers Clear filters.
- [x] AC-07: Stop all and Continue all say that they ignore filters and cover every machine while any filter is on.
- [x] AC-08: The row reads well in light, dark and a narrow pane, and every control has an accessible name and pressed state. Evidence is headless screenshots saved to files.

## Approach

`apps/web/src/studio/threadPaneFilters.ts` holds pure rules (choice order, agent options, faceted counts, match predicate). `ThreadsPane.tsx` renders them and `shell.css` styles them. The check at `apps/web/tests/project-workspace/thread-filter-check.mjs` captures the states headlessly.

Risk: a remembered filter hides threads on the next visit. The row is always visible while filtering, which is why these are chips in view and not menu state.

Rejected filters:

- Status: the groups already are the status filter, each one foldable.
- Model: a finer cut of agent that fragments into many one-thread options.
- Date: the list already sorts by activity and pages with Show more.
- Increment: "No increment" already has its own filter, and a bound increment is rarely a browse key.
- Waiting on you: already the first group.
- Saved views: too much machinery for three dimensions.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Machine choices stay in view instead of inside a menu, because the hidden menu is the reported problem. Agent and pull request sit behind one filter button, to keep the row to one line.
- D-02 "This machine" is the device's primary environment, the same meaning as the sidebar's Chats list.
- D-03 Bulk stop and continue keep acting on every thread. Scoping them to a filter would change a safety-relevant command; the menu says so instead.
### Open
- none

## Tasks

### T-01 Filter rules with unit tests
- AC: AC-01, AC-03, AC-04, AC-05 | Files: apps/web/src/studio/threadPaneFilters.ts, apps/web/src/studio/threadPaneFilters.test.ts | Test: pnpm exec vp test run apps/web/src/studio/threadPaneFilters.test.ts

### T-02 Filter row in the Threads panel
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: apps/web/src/components/studio/shell/ThreadsPane.tsx, apps/web/src/components/studio/shell/shell.css, apps/web/src/components/studio/ProjectWorkspace.test.tsx | Test: pnpm exec vp test run apps/web/src/components/studio/ProjectWorkspace.test.tsx

### T-03 Headless visual check
- AC: AC-08 | Files: apps/web/tests/project-workspace/thread-filter-check.mjs, apps/web/tests/project-workspace/machine-column-check.mjs | Test: node apps/web/tests/project-workspace/thread-filter-check.mjs

### T-04 Verify and close 1320
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: specweave verify 1320
