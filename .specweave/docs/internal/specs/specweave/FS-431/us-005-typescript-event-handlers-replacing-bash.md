---
id: US-005
feature: FS-431
title: "TypeScript Event Handlers Replacing Bash"
status: completed
priority: P0
created: "2026-03-05T00:00:00.000Z"
tldr: "**As a** developer."
project: specweave
---

# US-005: TypeScript Event Handlers Replacing Bash

**Feature**: [FS-431](./FEATURE.md)

**As a** developer
**I want** TypeScript handler functions for all event types replacing the existing bash handler scripts
**So that** event processing is type-safe, testable, and works on all platforms

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given an increment lifecycle event (created/done/archived/reopened) arrives via hook, when the handler processes it, then it executes the equivalent logic of living-specs-handler.sh, status-line-handler.sh, project-bridge-handler.sh, and github-sync-handler.sh
- [x] **AC-US5-02**: Given a spec.updated event arrives, when the handler processes it, then it executes the equivalent logic of living-docs-handler.sh, ac-validation-handler.sh, and github-sync-handler.sh
- [x] **AC-US5-03**: Given a SubagentStart or SubagentStop event arrives, when the handler processes it, then it updates the in-memory agent tracking store with agent_id, agent_type, session_id, started_at/stopped_at, and duration_ms
- [x] **AC-US5-04**: Given a TaskCompleted event arrives, when the handler processes it, then it records the completion in the in-memory store and appends to `.specweave/state/hooks/events.jsonl`
- [x] **AC-US5-05**: Given any handler throws an error, when the error occurs during event processing, then the error is logged to `.specweave/logs/hooks.log` and the HTTP response is still returned (never blocks CC)

---

## Implementation

**Increment**: [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-011**: Implement PreToolUse handler with blocking rules
- [x] **T-012**: Implement subagent lifecycle and task-completed handlers
- [x] **T-013**: Implement passthrough and session-lifecycle handlers
