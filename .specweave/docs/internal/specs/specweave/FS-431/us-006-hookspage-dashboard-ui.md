---
id: US-006
feature: FS-431
title: "HooksPage Dashboard UI"
status: completed
priority: P0
created: "2026-03-05T00:00:00.000Z"
tldr: "**As a** developer."
project: specweave
---

# US-006: HooksPage Dashboard UI

**Feature**: [FS-431](./FEATURE.md)

**As a** developer
**I want** a HooksPage in the dashboard showing a real-time event stream
**So that** I have visibility into Claude Code's behavior during a session

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given the dashboard is open, when hook events arrive, then the HooksPage displays them in a scrollable reverse-chronological timeline updated in real-time via SSE
- [x] **AC-US6-02**: Given the HooksPage is displayed, when the user selects a filter (event type, session ID, or time range), then only matching events are shown
- [x] **AC-US6-03**: Given consecutive events of the same type occur (e.g., repeated PostToolUse on Edit), when displayed in the timeline, then they are collapsed into a summary row showing count and expandable on click
- [x] **AC-US6-04**: Given an event resulted in a block/deny decision, when displayed in the timeline, then it is visually highlighted with a distinct style (red/warning)

---

## Implementation

**Increment**: [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-014**: Implement HooksPage with real-time SSE event stream
- [x] **T-015**: Implement HooksPage filter bar
