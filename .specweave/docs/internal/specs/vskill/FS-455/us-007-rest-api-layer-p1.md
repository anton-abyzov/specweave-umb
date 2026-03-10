---
id: US-007
feature: FS-455
title: "REST API Layer (P1)"
status: completed
priority: P1
created: 2026-03-08T00:00:00.000Z
tldr: "**As a** the frontend SPA."
project: vskill
external:
  github:
    issue: 23
    url: https://github.com/anton-abyzov/vskill/issues/23
---

# US-007: REST API Layer (P1)

**Feature**: [FS-455](./FEATURE.md)

**As a** the frontend SPA
**I want** a REST API served by the eval server
**So that** all UI operations have a backend contract to call

---

## Acceptance Criteria

- [x] **AC-US7-01**: Given the server is running, when the SPA calls `GET /api/skills`, then it receives a JSON array of all discovered skills with plugin name, skill name, eval count, and benchmark status
- [x] **AC-US7-02**: Given a valid skill path, when the SPA calls `GET /api/skills/:plugin/:skill/evals`, then it receives the full `evals.json` content for that skill
- [x] **AC-US7-03**: Given valid eval case data, when the SPA calls `PUT /api/skills/:plugin/:skill/evals`, then the server validates and writes the updated `evals.json` to disk, returning the saved content
- [x] **AC-US7-04**: Given a benchmark or comparison request, when the SPA calls `POST /api/skills/:plugin/:skill/benchmark` or `POST /api/skills/:plugin/:skill/compare`, then the server streams progress via Server-Sent Events (SSE) and writes results to history on completion
- [x] **AC-US7-05**: Given a skill with history, when the SPA calls `GET /api/skills/:plugin/:skill/history`, then it receives a list of all timestamped benchmark/comparison runs with summary metadata

---

## Implementation

**Increment**: [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-013**: Validate complete REST API contract against spec
- [x] **T-014**: Wire complete build pipeline (tsconfig, package.json, prepublish)
