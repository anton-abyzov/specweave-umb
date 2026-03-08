---
id: US-004
feature: FS-431
title: "Command-Bridge for Command-Only Events"
status: completed
priority: P0
created: 2026-03-05T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-004: Command-Bridge for Command-Only Events

**Feature**: [FS-431](./FEATURE.md)

**As a** developer
**I want** the 9 command-only hook events (SessionStart, SessionEnd, Notification, SubagentStart, ConfigChange, PreCompact, TeammateIdle) forwarded to the HTTP server
**So that** all events flow through a unified TypeScript handler pipeline

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given a command-only event fires (SessionStart, SessionEnd, Notification, SubagentStart, ConfigChange, PreCompact, TeammateIdle), when the command-bridge script runs, then it reads the event payload from stdin and POSTs it to `http://localhost:{port}/api/hooks/{eventName}`
- [x] **AC-US4-02**: Given the dashboard server is not running, when the command-bridge attempts to POST, then it fails silently (exit 0) without blocking Claude Code
- [x] **AC-US4-03**: Given `hooks.httpMode: true`, when `specweave hooks generate-settings` runs, then it produces a valid `.claude/settings.json` hooks section with HTTP transport for the 8 supported events and command transport (pointing to the command-bridge script) for the remaining 9

---

## Implementation

**Increment**: [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Implement command-bridge.mjs stdin-to-HTTP forwarding
- [x] **T-010**: Implement settings generator command
