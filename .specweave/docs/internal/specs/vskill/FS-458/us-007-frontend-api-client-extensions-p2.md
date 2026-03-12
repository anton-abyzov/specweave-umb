---
id: US-007
feature: FS-458
title: "Frontend API Client Extensions (P2)"
status: completed
priority: P1
created: "2026-03-09T00:00:00.000Z"
tldr: "**As a** developer."
project: vskill
external:
  github:
    issue: 34
    url: "https://github.com/anton-abyzov/vskill/issues/34"
---

# US-007: Frontend API Client Extensions (P2)

**Feature**: [FS-458](./FEATURE.md)

**As a** developer
**I want** the frontend API client to support all new endpoints (baseline, filtered history, history-compare)
**So that** the UI components can consume the new backend capabilities

---

## Acceptance Criteria

- [x] **AC-US7-01**: Given the api client, when `api.runBaseline(plugin, skill)` is called, then it initiates an SSE connection to `POST /api/skills/:plugin/:skill/baseline`
- [x] **AC-US7-02**: Given the api client, when `api.getHistory(plugin, skill, filters)` is called with optional filter params, then query parameters are appended to the history GET request
- [x] **AC-US7-03**: Given the api client, when `api.compareRuns(plugin, skill, timestampA, timestampB)` is called, then it fetches from `GET /api/skills/:plugin/:skill/history-compare`
- [x] **AC-US7-04**: Given the frontend types, when `HistorySummary` type is updated, then it includes the `"baseline"` option in the `type` union and optional enriched fields

---

## Implementation

**Increment**: [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-011**: Update api.ts with getHistory filters and compareRuns, update types.ts
