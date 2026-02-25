---
id: US-002
feature: FS-368
title: Merge setContentHash into storeScanResult
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1319
    url: https://github.com/anton-abyzov/specweave/issues/1319
---
# US-002: Merge setContentHash into storeScanResult

**Feature**: [FS-368](./FEATURE.md)

platform operator
**I want** content hash to be stored in the same KV write as the scan result
**So that** 2 redundant KV round-trips are eliminated per submission

---

## Acceptance Criteria

- [x] **AC-US2-01**: `storeScanResult` accepts optional `contentHash` parameter
- [x] **AC-US2-02**: When `contentHash` is provided, `storeScanResult` sets `contentHashAtScan` on the submission record during its existing read-modify-write
- [x] **AC-US2-03**: Standalone `setContentHash` call is removed from `processSubmission`
- [x] **AC-US2-04**: Exported `setContentHash` function retained for backward compatibility

---

## Implementation

**Increment**: [0368-queue-per-item-latency](../../../../../increments/0368-queue-per-item-latency/spec.md)

