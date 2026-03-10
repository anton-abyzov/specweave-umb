---
id: US-003
feature: FS-461
title: "Admin Refresh-Skills Endpoint"
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** platform admin."
project: vskill-platform
---

# US-003: Admin Refresh-Skills Endpoint

**Feature**: [FS-461](./FEATURE.md)

**As a** platform admin
**I want** to trigger targeted metric re-enrichment with immediate search shard sync
**So that** I can fix stale star counts for specific skills without waiting for the next cron cycle

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given a POST to `/api/v1/admin/refresh-skills` with body `{ repoUrl }`, when the endpoint runs, then it re-fetches GitHub metrics and dispatches search shard updates for all non-deprecated skills matching that repoUrl
- [x] **AC-US3-02**: Given a POST with body `{ author }`, when the endpoint runs, then it re-enriches all non-deprecated skills by that author
- [x] **AC-US3-03**: Given a POST with body `{ skillNames: ["a", "b"] }`, when the endpoint runs, then it re-enriches exactly those named skills
- [x] **AC-US3-04**: Given a POST with body `{ dryRun: true }`, when the endpoint runs, then it returns the list of skills that would be refreshed without making any DB or shard updates
- [x] **AC-US3-05**: Given a POST with an empty body (no filters), when the endpoint runs, then it returns 400 with an error message requiring at least one filter

---

## Implementation

**Increment**: [0461-skill-star-freshness](../../../../../increments/0461-skill-star-freshness/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
