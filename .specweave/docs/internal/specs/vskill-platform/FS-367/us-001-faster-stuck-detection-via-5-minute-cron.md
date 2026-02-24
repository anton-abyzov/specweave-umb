---
id: US-001
feature: FS-367
title: Faster Stuck Detection via 5-Minute Cron
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-001: Faster Stuck Detection via 5-Minute Cron

**Feature**: [FS-367](./FEATURE.md)

platform operator
**I want** the cron to run every 5 minutes instead of hourly
**So that** stuck submissions are detected and recovered within minutes rather than waiting up to an hour

---

## Acceptance Criteria

- [x] **AC-US1-01**: wrangler.jsonc cron schedule changed from `0 * * * *` to `*/5 * * * *`
- [x] **AC-US1-02**: All existing cron tasks (npm discovery, recovery, enrichment, stats refresh) continue to run within the 5-minute schedule without exceeding Worker CPU limits
- [x] **AC-US1-03**: Recovery runs every cron tick (no gating or feature flag needed)

---

## Implementation

**Increment**: [0367-stuck-submission-detection](../../../../../increments/0367-stuck-submission-detection/spec.md)

