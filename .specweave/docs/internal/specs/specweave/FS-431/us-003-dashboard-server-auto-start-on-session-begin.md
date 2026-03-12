---
id: US-003
feature: FS-431
title: "Dashboard Server Auto-Start on Session Begin"
status: completed
priority: P0
created: "2026-03-05T00:00:00.000Z"
tldr: "**As a** developer."
project: specweave
---

# US-003: Dashboard Server Auto-Start on Session Begin

**Feature**: [FS-431](./FEATURE.md)

**As a** developer
**I want** the dashboard server to auto-start when a Claude Code session begins
**So that** the HTTP hook endpoint is available before the first hook event fires

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `hooks.httpMode: true` in `.specweave/config.json`, when a Claude Code SessionStart command hook fires, then a Node.js command-bridge script starts the dashboard server in the background if not already running
- [x] **AC-US3-02**: Given the dashboard server is already running on the configured port, when the SessionStart hook fires, then the command-bridge detects the existing instance (via port check) and does not start a duplicate
- [x] **AC-US3-03**: Given `hooks.httpMode: true`, when the developer runs `specweave dashboard --hooks`, then the server starts with hook routes enabled on the same port as the dashboard
- [x] **AC-US3-04**: Given the server auto-starts, when it is ready to accept connections, then it writes the port and PID to `.specweave/state/hooks/server.pid` for discovery by the command-bridge

---

## Implementation

**Increment**: [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: Write PID file on server start and add --hooks CLI flag
- [x] **T-008**: Implement command-bridge auto-start with duplicate detection
