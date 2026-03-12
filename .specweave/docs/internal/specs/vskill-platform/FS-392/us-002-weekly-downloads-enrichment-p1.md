---
id: US-002
feature: FS-392
title: "Weekly Downloads Enrichment (P1)"
status: completed
priority: P1
created: "2026-03-01T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-002: Weekly Downloads Enrichment (P1)

**Feature**: [FS-392](./FEATURE.md)

**As a** platform operator
**I want** the enrichment cron to fetch weekly npm downloads alongside monthly
**So that** the `npmDownloadsWeekly` field is populated automatically each cycle

---

## Acceptance Criteria

- [x] **AC-US2-01**: `fetchNpmDownloadsBulk` accepts a `period` parameter (`"last-month"` | `"last-week"`) defaulting to `"last-month"`
- [x] **AC-US2-02**: Enrichment batch makes two bulk API calls: one to `https://api.npmjs.org/downloads/point/last-month/...` (existing) and one to `https://api.npmjs.org/downloads/point/last-week/...` (new)
- [x] **AC-US2-03**: Weekly download count is written to `npmDownloadsWeekly` in the same DB transaction as other metric updates
- [x] **AC-US2-04**: If the weekly API call fails, existing `npmDownloadsWeekly` value is preserved (null-means-preserve pattern)
- [x] **AC-US2-05**: Weekly download count is included in the `MetricsSnapshot` row created during enrichment
- [x] **AC-US2-06**: The existing `npmDownloads` (monthly) field and trending formula SQL are not modified

---

## Implementation

**Increment**: [0392-npm-weekly-downloads](../../../../../increments/0392-npm-weekly-downloads/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add period parameter to fetchNpmDownloadsBulk
- [x] **T-004**: Add weekly bulk fetch to enrichment batch
- [x] **T-005**: Regression test - trending formula unchanged
