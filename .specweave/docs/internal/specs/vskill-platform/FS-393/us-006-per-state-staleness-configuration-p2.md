---
id: US-006
feature: FS-393
title: "Per-State Staleness Configuration (P2)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-006: Per-State Staleness Configuration (P2)

**Feature**: [FS-393](./FEATURE.md)

**As a** platform operator
**I want** per-state staleness windows configurable via environment variables
**So that** published skills are re-scanned more frequently (24h) than rejected ones (48h), with a sensible default fallback (72h)

---

## Acceptance Criteria

- [x] **AC-US6-01**: `submission-dedup.ts` reads `DEDUP_STALE_PUBLISHED_HOURS` (default: 24), `DEDUP_STALE_REJECTED_HOURS` (default: 48), and `DEDUP_STALE_DEFAULT_HOURS` (default: 72) from environment
- [x] **AC-US6-02**: The existing single `DEDUP_STALE_HOURS` env var is replaced by the per-state variables; backward compatibility is maintained by using `DEDUP_STALE_DEFAULT_HOURS` as the fallback
- [x] **AC-US6-03**: The `isStale()` function accepts a state parameter and applies the corresponding staleness window
- [x] **AC-US6-04**: Published skills with a linked Skill record are re-scanned after `DEDUP_STALE_PUBLISHED_HOURS` (24h default)
- [x] **AC-US6-05**: Rejected/DEQUEUED/TIER1_FAILED submissions are re-scannable after `DEDUP_STALE_REJECTED_HOURS` (48h default)
- [x] **AC-US6-06**: All other states use `DEDUP_STALE_DEFAULT_HOURS` (72h default)

---

## Implementation

**Increment**: [0393-crawl-pipeline-throughput](../../../../../increments/0393-crawl-pipeline-throughput/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
