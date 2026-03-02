---
id: US-003
feature: FS-230
title: "Marketplace Dashboard Page (P1)"
status: completed
priority: P1
created: "2026-02-16T00:00:00.000Z"
tldr: "**As a** SpecWeave user
**I want** a Marketplace page showing scanner status, queue, and verified skills
**So that** I can monitor the skill discovery pipeline in real-time."
project: specweave
---

# US-003: Marketplace Dashboard Page (P1)

**Feature**: [FS-230](./FEATURE.md)

**As a** SpecWeave user
**I want** a Marketplace page showing scanner status, queue, and verified skills
**So that** I can monitor the skill discovery pipeline in real-time

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given no scanner running, when page loads, then shows onboarding CTA with Start Scanner button
- [x] **AC-US3-02**: Given active scanner, when page loads, then shows KPIs: worker health, last scan time, repos scanned, rate limit remaining
- [x] **AC-US3-03**: Given submissions in queue, when page loads, then shows filterable table with status, tier, date, security score
- [x] **AC-US3-04**: Given verified skills, when page loads, then shows gallery cards with security scores and author info
- [x] **AC-US3-05**: Given a submission status change, when SSE event fires, then page updates without refresh

---

## Implementation

**Increment**: [0230-marketplace-scanner-dashboard](../../../../../increments/0230-marketplace-scanner-dashboard/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
