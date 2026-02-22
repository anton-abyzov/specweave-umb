---
id: US-003
feature: FS-326
title: Reports as Header Button + Overlay Modal
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
---
# US-003: Reports as Header Button + Overlay Modal

**Feature**: [FS-326](./FEATURE.md)

Trust Center visitor
**I want** the report form accessible from a header button instead of a dedicated tab
**So that** the tab bar stays focused on data views (Verified / Blocked) and reporting feels like a quick action

---

## Acceptance Criteria

- [x] **AC-US3-01**: The "Reports" tab is removed from the TABS array in page.tsx; only "Verified Skills" and "Blocked Skills" tabs remain
- [x] **AC-US3-02**: A "Report a Skill" button appears in the Trust Center header (right of the subtitle text), styled consistently with the page
- [x] **AC-US3-03**: Clicking the button opens a full-page overlay modal: dimmed backdrop (`rgba(0,0,0,0.5)`), centered card, matching the block dialog pattern in VerifiedSkillsTab
- [x] **AC-US3-04**: The modal contains the existing ReportsTab content (submission form + recent reports table)
- [x] **AC-US3-05**: Modal dismisses on clicking outside the card (backdrop click)
- [x] **AC-US3-06**: Modal has an X close button positioned top-right of the card
- [x] **AC-US3-07**: After successful report submission, the recent reports list in the modal updates without closing the modal

---

## Implementation

**Increment**: [0326-trust-center-fixes](../../../../../increments/0326-trust-center-fixes/spec.md)

