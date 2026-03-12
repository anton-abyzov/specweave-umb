---
id: US-002
feature: FS-509
title: "Heuristic Backfill of Historical Scan Data"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-002: Heuristic Backfill of Historical Scan Data

**Feature**: [FS-509](./FEATURE.md)

**As a** platform operator
**I want** existing Tier 2 scan results to have inferred `llmModel` values based on scan duration
**So that** historical cost analysis is possible without rescanning all submissions

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given existing Tier 2 scan results with `durationMs > 30000`, when the backfill migration runs, then `llmModel` is set to `"gpt-4o-mini (inferred)"`
- [x] **AC-US2-02**: Given existing Tier 2 scan results with `durationMs` between 20000 and 30000 inclusive, when the backfill migration runs, then `llmModel` is set to `"unknown (ambiguous)"`
- [x] **AC-US2-03**: Given existing Tier 2 scan results with `durationMs < 20000`, when the backfill migration runs, then `llmModel` is set to `"cloudflare (inferred)"`
- [x] **AC-US2-04**: Given the backfill targets only `tier = 2` rows, when the migration runs, then Tier 1 and Tier 3 scan results are not modified

---

## Implementation

**Increment**: [0509-track-tier2-llm-model](../../../../../increments/0509-track-tier2-llm-model/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add Backfill SQL to Migration — Duration-Based llmModel Attribution
