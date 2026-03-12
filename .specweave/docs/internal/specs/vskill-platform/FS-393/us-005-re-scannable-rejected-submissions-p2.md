---
id: US-005
feature: FS-393
title: "Re-Scannable Rejected Submissions (P2)"
status: completed
priority: P1
created: "2026-03-01T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-005: Re-Scannable Rejected Submissions (P2)

**Feature**: [FS-393](./FEATURE.md)

**As a** platform operator
**I want** rejected submissions to be eligible for re-scanning after a configurable cooldown period
**So that** submissions rejected due to transient issues (rate limits, temporary scan failures) can be automatically retried without manual intervention

---

## Acceptance Criteria

- [x] **AC-US5-01**: `submission-dedup.ts` treats `kind: "rejected"` as `kind: "new"` when the submission's `updatedAt` exceeds the configured staleness window for rejected state
- [x] **AC-US5-02**: BLOCKED submissions remain permanently blocked (never re-scannable via dedup staleness)
- [x] **AC-US5-03**: The `checkSubmissionDedupBatch` function also applies the same re-scan logic for rejected submissions
- [x] **AC-US5-04**: Existing dedup tests are updated to cover the rejected-re-scan path

---

## Implementation

**Increment**: [0393-crawl-pipeline-throughput](../../../../../increments/0393-crawl-pipeline-throughput/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
