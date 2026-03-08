---
id: US-008
feature: FS-431
title: "Settings Generator and Migration Config"
status: completed
priority: P0
created: 2026-03-05T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-008: Settings Generator and Migration Config

**Feature**: [FS-431](./FEATURE.md)

**As a** developer
**I want** documentation and tooling updated to reflect the HTTP hook architecture
**So that** I can enable, configure, and troubleshoot the new hook system

---

## Acceptance Criteria

- [x] **AC-US8-01**: Given `hooks.httpMode: true` in config.json, when `specweave hooks generate-settings` runs, then it writes a valid `.claude/settings.json` hooks block with HTTP URLs for the 8 supported events and command paths for the 9 command-only events
- [x] **AC-US8-02**: Given `hooks.httpMode: false` (or absent), when hooks are evaluated, then the existing bash hook system operates unchanged with no behavioral difference
- [x] **AC-US8-03**: Given a developer upgrades specweave, when config.json does not contain `hooks.httpMode`, then the default is `false` (opt-in for existing installs)
- [x] **AC-US8-04**: Given `hooks.httpMode: true`, when `specweave hooks status` runs, then it reports whether the dashboard server is running, the hook endpoint URL, and the count of events received in the current session

---

## Implementation

**Increment**: [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-018**: Implement hooks status command and config default enforcement
- [x] **T-019**: End-to-end integration test for full hook event flow
