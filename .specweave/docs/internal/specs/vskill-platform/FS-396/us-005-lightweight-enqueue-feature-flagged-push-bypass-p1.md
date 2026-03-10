---
id: US-005
feature: FS-396
title: "Lightweight Enqueue (Feature-Flagged Push Bypass) (P1)"
status: completed
priority: P1
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** platform developer."
project: vskill-platform
---

# US-005: Lightweight Enqueue (Feature-Flagged Push Bypass) (P1)

**Feature**: [FS-396](./FEATURE.md)

**As a** platform developer
**I want** `dispatchExternalScans()` to only write PENDING status to DB+KV without HTTP dispatch when `SAST_PULL_MODE` is enabled
**So that** the platform enqueues work for the pull-based source instead of pushing to workers

---

## Acceptance Criteria

- [x] **AC-US5-01**: When `SAST_PULL_MODE` env var is truthy, `dispatchExternalScans()` writes PENDING status to KV and creates/upserts the ExternalScanResult DB row with status=PENDING, then returns without making HTTP calls to scanner workers
- [x] **AC-US5-02**: When `SAST_PULL_MODE` is falsy or absent, the existing push dispatch behavior is preserved unchanged (round-robin POST to SCANNER_WORKERS)
- [x] **AC-US5-03**: The DB upsert uses `@@unique([skillName, provider])` constraint -- if a row already exists with PENDING or RUNNING status, the enqueue is skipped (dedup, same as current KV dedup logic)
- [x] **AC-US5-04**: The GitHub Actions fallback code path is left in place (removal deferred to follow-up increment)
- [x] **AC-US5-05**: All three call sites (process-submission, finalize-scan, admin/scan-external) use the updated `dispatchExternalScans()` with no call-site changes needed

---

## Implementation

**Increment**: [0396-pull-based-sast-scanner](../../../../../increments/0396-pull-based-sast-scanner/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
