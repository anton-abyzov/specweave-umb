---
id: US-007
feature: FS-431
title: "AgentsPage Dashboard UI"
status: completed
priority: P0
created: "2026-03-05T00:00:00.000Z"
tldr: "**As a** developer."
project: specweave
---

# US-007: AgentsPage Dashboard UI

**Feature**: [FS-431](./FEATURE.md)

**As a** developer
**I want** an AgentsPage in the dashboard showing subagent lifecycle
**So that** I can track agent activity and performance across sessions

---

## Acceptance Criteria

- [x] **AC-US7-01**: Given agents have been tracked via SubagentStart/SubagentStop events, when the AgentsPage loads, then it displays a table with columns: agent_id, agent_type, session_id, started_at, stopped_at, duration_ms
- [x] **AC-US7-02**: Given an agent is currently running (SubagentStart received, no SubagentStop yet), when the AgentsPage displays it, then the status shows "running" with a live duration counter
- [x] **AC-US7-03**: Given multiple sessions have agent data, when the user filters by session ID, then only agents from that session are displayed
- [x] **AC-US7-04**: Given new SubagentStart/SubagentStop events arrive, when the AgentsPage is open, then the table updates in real-time via SSE without page reload

---

## Implementation

**Increment**: [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-016**: Implement AgentsPage with agent table and live duration counter
- [x] **T-017**: Implement AgentsPage session filter
