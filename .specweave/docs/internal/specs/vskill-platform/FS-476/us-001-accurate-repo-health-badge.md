---
id: US-001
feature: FS-476
title: "Accurate repo health badge"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** user viewing a skill detail page."
project: vskill-platform
external:
  github:
    issue: 54
    url: https://github.com/anton-abyzov/vskill-platform/issues/54
---

# US-001: Accurate repo health badge

**Feature**: [FS-476](./FEATURE.md)

**As a** user viewing a skill detail page
**I want** the repo health badge to only show OFFLINE when the repo genuinely does not exist (HTTP 404)
**So that** I am not misled about skill availability by transient GitHub failures

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a GitHub API response with status 404, when the repo health check runs, then the result status is `OFFLINE`
- [x] **AC-US1-02**: Given a GitHub API response with status 403 (rate limit), 429, or 5xx, when the repo health check runs, then the result status is `UNKNOWN` (not `OFFLINE`)
- [x] **AC-US1-03**: Given a network error or timeout during the GitHub API call, when the repo health check runs, then the result status is `UNKNOWN`
- [x] **AC-US1-04**: Given a cached `UNKNOWN` status, when the badge component renders, then no badge is displayed (component returns null)
- [x] **AC-US1-05**: Given a cached `UNKNOWN` result, when the KV TTL is checked, then it expires after 300 seconds (same as OFFLINE TTL) for quick retry

---

## Implementation

**Increment**: [0476-skill-metadata-alignment](../../../../../increments/0476-skill-metadata-alignment/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add UNKNOWN status to repo health type and checker
- [x] **T-002**: Hide badge for UNKNOWN status in RepoHealthBadge
