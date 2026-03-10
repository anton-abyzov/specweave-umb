---
id: US-004
feature: FS-461
title: "Admin Dedup-Skills Endpoint"
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** platform admin."
project: vskill-platform
external:
  github:
    issue: 52
    url: https://github.com/anton-abyzov/vskill-platform/issues/52
---

# US-004: Admin Dedup-Skills Endpoint

**Feature**: [FS-461](./FEATURE.md)

**As a** platform admin
**I want** to detect and deprecate duplicate skill entries
**So that** search results do not show the same skill twice under different slugs

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given a POST to `/api/v1/admin/dedup-skills`, when duplicate skills exist (same `repoUrl` + same `skillPath`), then the endpoint identifies them as duplicates
- [x] **AC-US4-02**: Given duplicates are found, when the endpoint resolves them, then it keeps the entry with the highest `trustScore` (tiebreaker: most recent `certifiedAt`) and deprecates the others by setting `isDeprecated: true`
- [x] **AC-US4-03**: Given a duplicate is deprecated, when the shard is updated, then a `remove` action is dispatched for the deprecated entry's search shard
- [x] **AC-US4-04**: Given a POST with body `{ dryRun: true }`, when the endpoint runs, then it returns the list of duplicate groups and which entry would survive without modifying the DB
- [x] **AC-US4-05**: Given no duplicates exist, when the endpoint runs, then it returns a 200 with `{ duplicateGroups: 0, deprecated: 0 }`

---

## Implementation

**Increment**: [0461-skill-star-freshness](../../../../../increments/0461-skill-star-freshness/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
