---
id: US-004
feature: FS-489
title: "Data-driven service controls in ServicesPage (P1)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** developer managing services on the dashboard."
project: specweave
external:
  github:
    issue: 1537
    url: "https://github.com/anton-abyzov/specweave/issues/1537"
---

# US-004: Data-driven service controls in ServicesPage (P1)

**Feature**: [FS-489](./FEATURE.md)

**As a** developer managing services on the dashboard
**I want** start/stop/open controls to appear for any controllable service based on data, not hardcoded name checks
**So that** adding new controllable services does not require UI code changes

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given the `/api/services` response, when a service includes `startCommand` and `stopCommand` fields, then ServicesPage renders start/stop buttons for that service
- [x] **AC-US4-02**: Given "Internal Docs" service, when rendered in ServicesPage, then it shows Open/Stop buttons when running and a Start button when stopped, using its `startCommand`/`stopCommand`
- [x] **AC-US4-03**: Given "Public Docs" service, when rendered in ServicesPage, then it shows the same Open/Stop/Start controls using its own `startCommand`/`stopCommand`
- [x] **AC-US4-04**: Given "Dashboard Server" service (no startCommand/stopCommand), when rendered, then it only shows the Open link, no start/stop buttons
- [x] **AC-US4-05**: Given the old `svc.name === 'Docs Preview'` check in ServicesPage, when the code is updated, then no service-name-specific conditionals exist in the rendering logic

---

## Implementation

**Increment**: [0489-dashboard-docs-services](../../../../../increments/0489-dashboard-docs-services/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Replace name-hardcoded controls with data-driven rendering in ServicesPage.tsx
- [x] **T-005**: Build and manual smoke test
