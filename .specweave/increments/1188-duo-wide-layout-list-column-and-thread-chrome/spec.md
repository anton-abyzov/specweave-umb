# Duo wide layout: list column and thread chrome

## Problem

On an unfolded iPhone Duo at 951x669, the owner wants the layout in `/Users/antonabyzov/Downloads/Open Codex.png`: a list column with a project picker and machine filters beside a quiet thread. PR #1232 adds the two columns and the coordinator column, but the list still shows the wordmark, a tree with three-line rows and New chat at the bottom, it closes on every thread change, and the status rail stays empty.

## Scope

In: the wide list's header, machine chips, single-project list, a list that stays open, the plain thread title, controls in the rail, the machine named in the composer, the working agents pill. Out: compact phone layouts, a microphone or voice mode, message feedback buttons, the neutral colour scheme, changes to PR #1232 itself.

## Acceptance Criteria

- [ ] AC-01: From 760 points, the list header holds the sidebar toggle, a way to change list level and one capsule with search and New chat.
- [ ] AC-02: With two or more machines, chips under the header show All and each machine with its status, and a chip filters the threads.
- [ ] AC-03: With a project in scope, the list holds its coordinator and its threads on single lines; All projects shows the existing tree.
- [ ] AC-04: A list opened with Show projects stays open while threads change, until Show coordinator.
- [ ] AC-05: Beside the list, a thread's title is plain text, its controls sit in the status rail when the scene reports one, and its composer names the machine.
- [ ] AC-06: A pill above the composer counts a coordinator's working threads or a thread's working subagents, and opens or scrolls to them.
- [ ] AC-07: With a one-sided status rail, headers start below the top edge's touch zone, so the top-left control answers along its whole height, and a hidden column can come back from a pushed thread.
- [ ] AC-08: Rail controls share the clock and Wi-Fi centre and start below them.
- [ ] AC-09: Projects do not unfold in the wide list: a project row goes down a level in the same column, a header back button returns, and this replaces the project picker menu.
- [ ] AC-10: Left and right are always about the same project: going into a project opens its coordinator unless one of its chats is open, and opening a chat ends the all-projects level.
- [ ] AC-11: With a thread open, the column header switches between Coordinator and Threads, the choice persists, and Threads counts what needs you.
- [ ] AC-12: Every thread row leads with a status mark in the desktop's language (needs you, failed, working, done, idle), and finished threads are distinct from idle ones.
- [ ] AC-13: Thread rows keep their order when status or updates change, sorted by `activityAt`; All, Needs you and Working chips filter without moving rows; a project spanning machines names the machine on each row.
- [ ] AC-14: Status words match desktop #1250: groups Needs you, Working, Offline (only when present), Idle, Resolved; dependency waits count as Working with "Waiting" only as a row's reason; counts read "1 needs you" and "2 need you"; a last-message ask reads "Reply needed" and clears on reply; "Waiting on you" is gone from thread status.

## Approach

`SidebarView` holds the header, chips and scoped sections; `AppRouter` holds the scope and chip state, so it is testable. `ChatView` holds the rail, pill and placeholder. `TitleCapsule` gains a plain style. The list's resting width grows from 32% to 42% of the scene, capped at 420 points, to match the reference. The branch stacks on `feat/duo-coordinator-beside-thread` and can only merge after #1232.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 The left column still defaults to the coordinator when a thread is open; the list is one tap away and the existing setting turns it off (reversible).
- D-02 The column follows the open chat until the person goes back to all projects; going into a project opens it on the right, so the columns never disagree (reversible).
### Open
- none

## Tasks

### T-01 List column
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/SidebarView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift | Test: make test-core

### T-02 Thread chrome
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/Weave/Components/TitleCapsule.swift | Test: DuoWideLayoutTests on an iPhone Duo simulator

### T-04 Top edge, rail and project level
- AC: AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/SidebarView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/Weave/Tokens/WeaveMetrics.swift | Test: AdaptiveLayoutUITests on an unfolded iPhone Duo simulator

### T-05 One project, status on every row
- AC: AC-10, AC-11, AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/ColumnHeader.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/ThreadStatusMark.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/SidebarView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift | Test: make test-core and AdaptiveLayoutUITests on an unfolded iPhone Duo simulator

### T-06 Status words from #1250
- AC: AC-14 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/ThreadAttention.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Support/Logic.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Overview/ProjectOverviewView.swift | Test: make test-core

### T-03 Verify and close 1188
- AC: all | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/docs/IPHONE-DUO.md | Test: specweave verify
