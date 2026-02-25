---
id: US-003
feature: FS-368
title: Cache detectBranch in KV
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1320
    url: https://github.com/anton-abyzov/specweave/issues/1320
---
# US-003: Cache detectBranch in KV

**Feature**: [FS-368](./FEATURE.md)

platform operator
**I want** GitHub branch detection results to be cached in KV
**So that** redundant GitHub API calls are eliminated for same-repo submissions

---

## Acceptance Criteria

- [x] **AC-US3-01**: `detectBranch` checks KV cache key `branch:{owner}/{repo}` before calling GitHub API
- [x] **AC-US3-02**: On cache miss, result is written to KV with 1-hour TTL
- [x] **AC-US3-03**: KV access uses `getWorkerEnv()` fallback to `getCloudflareContext()` (same as `getKV()`)
- [x] **AC-US3-04**: If KV read fails, falls through to GitHub API (graceful degradation)

---

## Implementation

**Increment**: [0368-queue-per-item-latency](../../../../../increments/0368-queue-per-item-latency/spec.md)

