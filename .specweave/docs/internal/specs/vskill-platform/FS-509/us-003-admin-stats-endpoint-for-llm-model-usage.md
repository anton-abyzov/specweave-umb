---
id: US-003
feature: FS-509
title: "Admin Stats Endpoint for LLM Model Usage"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** platform administrator."
project: vskill-platform
---

# US-003: Admin Stats Endpoint for LLM Model Usage

**Feature**: [FS-509](./FEATURE.md)

**As a** platform administrator
**I want** a stats endpoint showing LLM model distribution over time
**So that** I can monitor OpenAI cost exposure and track fallback frequency

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given the endpoint `GET /api/v1/admin/scan-model-stats`, when an unauthenticated request is made, then a 401 response is returned
- [x] **AC-US3-02**: Given the endpoint `GET /api/v1/admin/scan-model-stats`, when an admin-authenticated request is made with `from` and `to` ISO date query params, then a JSON response is returned containing model distribution counts grouped by `llmModel` value
- [x] **AC-US3-03**: Given the `granularity` query param is set to `day`, when the stats endpoint is called with a date range, then results are grouped by calendar day
- [x] **AC-US3-04**: Given the `granularity` query param is set to `month`, when the stats endpoint is called with a date range, then results are grouped by calendar month
- [x] **AC-US3-05**: Given the response includes an `estimatedCost` field for each model group, when the model is `gpt-4o-mini` or `gpt-4o-mini (inferred)`, then cost is calculated using gpt-4o-mini per-token pricing

---

## Implementation

**Increment**: [0509-track-tier2-llm-model](../../../../../increments/0509-track-tier2-llm-model/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Create Stats Route — Auth, Param Validation, and Query
- [x] **T-005**: Implement Granularity Grouping — Day and Month Bucketing
- [x] **T-006**: Implement Cost Estimation and Summary Totals
