---
id: US-001
feature: FS-431
title: "HTTP Hook Event Receiver"
status: completed
priority: P0
created: 2026-03-05T00:00:00.000Z
tldr: "**As a** developer using SpecWeave."
project: specweave
external:
  github:
    issue: 1514
    url: https://github.com/anton-abyzov/specweave/issues/1514
---

# US-001: HTTP Hook Event Receiver

**Feature**: [FS-431](./FEATURE.md)

**As a** developer using SpecWeave
**I want** Claude Code hook events received by an HTTP endpoint on the dashboard server
**So that** event processing is reliable, cross-platform, and does not depend on bash

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the dashboard server is running with hooks enabled, when Claude Code sends a POST to `POST /api/hooks/:eventName`, then the server accepts the request and returns 200 within 500ms
- [x] **AC-US1-02**: Given a PreToolUse event is received, when the handler evaluates blocking rules, then the response includes `hookSpecificOutput` with `permissionDecision: "allow"` or `"deny"` and a `permissionDecisionReason`
- [x] **AC-US1-03**: Given a PostToolUse, Stop, SubagentStop, TaskCompleted, UserPromptSubmit, PostToolUseFailure, or PermissionRequest event is received, when no blocking rule applies, then the server returns 200 with empty body
- [x] **AC-US1-04**: Given a malformed or unknown event type is POSTed, when the server processes the request, then it returns 400 with a JSON error message and does not crash
- [x] **AC-US1-05**: Given the server receives an event, when processing completes, then a TypeScript handler function (not a bash script) executes the event-specific logic

---

## Implementation

**Increment**: [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add HookEvent and AgentRecord types to types.ts
- [x] **T-002**: Implement HookEventRouter with handler registration and error isolation
- [x] **T-003**: Register hook routes on DashboardServer and wire SSE broadcast
