---
id: US-002
feature: FS-431
title: "In-Memory Event Store with JSONL Persistence"
status: completed
priority: P0
created: 2026-03-05T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-002: In-Memory Event Store with JSONL Persistence

**Feature**: [FS-431](./FEATURE.md)

**As a** developer
**I want** hook events persisted in-memory and flushed to JSONL files
**So that** I can query recent analytics, agent activity, and task completions without adding native npm dependencies

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a hook event is received, when the handler processes it, then the event is stored in an in-memory Map/array keyed by session ID and also appended to `.specweave/state/hooks/events.jsonl`
- [x] **AC-US2-02**: Given the dashboard server starts, when it initializes, then it reads existing JSONL files from `.specweave/state/hooks/` to hydrate the in-memory store (events.jsonl, agents.jsonl)
- [x] **AC-US2-03**: Given events.jsonl exceeds 10MB, when a new event is appended, then the file is rotated (renamed with timestamp suffix) and a new file is created
- [x] **AC-US2-04**: Given the server starts, when it scans JSONL files, then files older than 30 days are deleted
- [x] **AC-US2-05**: Given the dashboard server shuts down gracefully, when the shutdown signal is received, then all in-memory events not yet flushed are written to JSONL before exit

---

## Implementation

**Increment**: [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Implement HookEventStore with in-memory Map and JSONL append
- [x] **T-005**: Implement JSONL hydration on server start and 30-day cleanup
- [x] **T-006**: Wire HookEventStore into DashboardServer lifecycle
