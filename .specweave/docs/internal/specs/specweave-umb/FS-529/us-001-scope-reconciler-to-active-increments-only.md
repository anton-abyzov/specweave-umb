---
id: US-001
feature: FS-529
title: "Scope reconciler to active increments only"
status: completed
priority: P1
created: 2026-03-15
tldr: "**As a** SpecWeave user with 175+ features."
---

# US-001: Scope reconciler to active increments only

**Feature**: [FS-529](./FEATURE.md)

**As a** SpecWeave user with 175+ features
**I want** the reconciler to only scan active increments
**So that** API calls scale with active work, not total history

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given 529 total increments (175 active, 354 archived/abandoned), when reconciler runs, then only active increments trigger GitHub API calls
- [x] **AC-US1-02**: Given a completed increment with all issues already closed, when reconciler runs, then no `getIssue()` calls are made for that increment
- [x] **AC-US1-03**: Given reconciler ran less than 5 minutes ago, when triggered again, then it returns immediately (debounced) unless force=true

---

## Implementation

**Increment**: [0529-fix-github-api-rate-limit](../../../../../increments/0529-fix-github-api-rate-limit/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
