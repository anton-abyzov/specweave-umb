---
id: US-001
feature: FS-509
title: "Persist LLM Model in Scan Results"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-001: Persist LLM Model in Scan Results

**Feature**: [FS-509](./FEATURE.md)

**As a** platform operator
**I want** the LLM model name to be stored with each Tier 2 scan result
**So that** I can track which model processed each scan and identify OpenAI-incurring scans

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given the Prisma schema `ScanResult` model, when the migration runs, then a nullable `llmModel String?` column exists in the `ScanResult` table
- [ ] **AC-US1-02**: Given the `Tier2Payload` interface in `finalize-scan/route.ts`, when a Tier 2 scan payload is received, then the `model` field is accepted as an optional string property
- [ ] **AC-US1-03**: Given the `StoredScanResult` interface in `submission-store.ts`, when a Tier 2 result is constructed, then the `llmModel` optional string property is available for storage
- [ ] **AC-US1-04**: Given `persistScanResultToDb` in `submission-store.ts`, when a scan result with a non-null `llmModel` is persisted, then the `llmModel` value is written to the database `ScanResult` row
- [ ] **AC-US1-05**: Given `finalize-scan/route.ts` destructures the request body and calls `storeScanResult`, when a Tier 2 payload includes `model`, then the value is passed through to `storeScanResult` as `llmModel`

---

## Implementation

**Increment**: [0509-track-tier2-llm-model](../../../../../increments/0509-track-tier2-llm-model/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
