# Live thread activity and tool groups

## Problem

A working thread shows "Working for 12m 50s" and a ticking counter, but nothing says what the agent is doing right now, when it last did anything, or which machine runs it. The user watched one for 13 minutes and could not tell quiet work from a stuck turn (October 19, 2026). The ticking timer is client-side and proves nothing about liveness.

The live tool row ("Running · curl …") opens the turn's recent tool calls, but it has no chevron, count or boundary. Expanded, the earlier Read/Ran/Searched calls look like children of the running command, and the clickable target is not visible.

## Scope

In: the chat timeline's Working header, live activity row (tool or thinking) and expanded tool-group rendering in SpecWithCode (`anton-abyzov/specwithcode-dev`). Out: sidebar pills, server watchdog thresholds, thread panel redesign.

## Acceptance Criteria

- [ ] AC-01: The live activity row names the current step from real turn items (the running tool's label, "Thinking" while the latest item is reasoning or a tool just finished) and shows how long that step has run, timed from the item's own start.
- [ ] AC-02: When no turn item has changed for 60 seconds or more, the activity row says "No new events for N" instead of "Thinking"; the time comes from the newest turn item's update, never from the client timer.
- [ ] AC-03: The Working header shows a compact machine label for the thread's host and a live dot that animates only while events are fresh; when the host is not connected it says the status may be stale instead of implying progress.
- [ ] AC-04: A tool-group header (live or settled) shows a chevron and the count of tool calls it opens, and its accessible name says it shows or hides those calls.
- [ ] AC-05: Expanded tool calls sit inside an indented, left-bordered group so they read as a sibling list of the turn, not as subtasks of the running command; each call keeps its own disclosure.

## Approach

`apps/web/src/components/chat/liveActivity.ts` (new, pure): last-activity time from the active run's turn items, quiet threshold, step start time. `MessagesTimeline.tsx`: Working header machine label and dot, live row elapsed and quiet label, group header chevron and count. `WorkLog.tsx`: group-content boundary. `ChatView.tsx` passes the run's last activity time and machine label/connection. Headless fixture under `apps/web/tests/live-activity/` renders the real rows for screenshots.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Quiet threshold 60 s for the activity row; the existing 10-minute stall chip with Stop/Continue stays as is.
- D-02: Machine label shows on the Working header only, not as a new thread-panel element.

## Tasks

### T-01 Truthful live activity: step elapsed, quiet state, machine label
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/chat/liveActivity.ts, apps/web/src/components/chat/liveActivity.test.ts, apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/ChatView.tsx | Test: vp test run apps/web/src/components/chat/liveActivity.test.ts

### T-02 Tool groups read as groups
- AC: AC-04, AC-05 | Files: apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/chat/WorkLog.tsx | Test: vp test run apps/web/src/components/chat/MessagesTimeline.test.tsx

### T-03 Headless visual evidence, PR, release and installed check
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: apps/web/tests/live-activity/, scripts/studio-verify/live-activity.mjs | Test: node scripts/studio-verify/live-activity.mjs <report-dir>

### T-04 Verify and close 0942
