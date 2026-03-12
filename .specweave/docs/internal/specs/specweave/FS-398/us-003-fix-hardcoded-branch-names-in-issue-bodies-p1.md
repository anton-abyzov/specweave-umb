---
id: US-003
feature: FS-398
title: "Fix Hardcoded Branch Names in Issue Bodies (P1)"
status: completed
priority: P0
created: "2026-03-02T00:00:00.000Z"
tldr: "**As a** user with a non-standard default branch."
project: specweave
---

# US-003: Fix Hardcoded Branch Names in Issue Bodies (P1)

**Feature**: [FS-398](./FEATURE.md)

**As a** user with a non-standard default branch
**I want** issue body links to use my actual default branch
**So that** links in GitHub/JIRA/ADO issues resolve correctly

---

## Acceptance Criteria

- [x] **AC-US3-01**: `external-issue-auto-creator.ts` buildGitHubIssueBody() and buildFeatureLevelIssueBody() detect default branch instead of hardcoding `develop` (lines 781, 811-812)
- [x] **AC-US3-02**: Default branch detection uses git or config, with fallback to `main`

---

## Implementation

**Increment**: [0398-sync-integration-critical-fixes](../../../../../increments/0398-sync-integration-critical-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
