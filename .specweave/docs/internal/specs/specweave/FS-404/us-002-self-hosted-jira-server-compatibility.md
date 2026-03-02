---
id: US-002
feature: FS-404
title: Self-Hosted JIRA Server Compatibility
status: completed
priority: P1
created: 2026-03-02
tldr: "**As a** user running JIRA Server or Data Center (self-hosted),."
external:
  github:
    issue: 1470
    url: https://github.com/anton-abyzov/specweave/issues/1470
---

# US-002: Self-Hosted JIRA Server Compatibility

**Feature**: [FS-404](./FEATURE.md)

**As a** user running JIRA Server or Data Center (self-hosted),
**I want** the plugin to detect my JIRA deployment type and use the correct API version,
**So that** API calls don't 404 on my instance.

---

## Acceptance Criteria

- [x] **AC-US2-01**: Plugin auto-detects JIRA deployment type (Cloud vs Server/DC) via `/rest/api/2/serverInfo`
- [x] **AC-US2-02**: API version (`/rest/api/2` vs `/rest/api/3`) is selected based on detected deployment type
- [x] **AC-US2-03**: All 4 files with hardcoded `/rest/api/3` are updated to use the dynamic version
- [x] **AC-US2-04**: `jira-resource-validator/SKILL.md` removes the hard-block on self-hosted JIRA
- [x] **AC-US2-05**: Wiki markup is used for API v2 (Server), ADF for API v3 (Cloud)

---

## Implementation

**Increment**: [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
