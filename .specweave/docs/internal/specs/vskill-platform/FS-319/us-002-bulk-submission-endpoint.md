---
id: US-002
feature: FS-319
title: Bulk Submission Endpoint
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1265
    url: https://github.com/anton-abyzov/specweave/issues/1265
---
# US-002: Bulk Submission Endpoint

**Feature**: [FS-319](./FEATURE.md)

crawl worker
**I want** to submit discovered repos in batches of up to 100
**So that** HTTP overhead is reduced by 100x compared to 1-by-1 POSTs

---

## Acceptance Criteria

- [x] **AC-US2-01**: `POST /api/v1/submissions/bulk` accepts `{ repos: [{repoUrl, skillName, skillPath}] }` (max 100 per batch)
- [x] **AC-US2-02**: Internally fans out to existing submission + queue logic per repo
- [x] **AC-US2-03**: Returns summary: `{ submitted: N, skipped: N, errors: N }`
- [x] **AC-US2-04**: Auth via `X-Internal-Key` header (same as existing internal submissions)

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)

