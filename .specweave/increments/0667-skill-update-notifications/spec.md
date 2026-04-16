---
increment: 0667-skill-update-notifications
title: Skill Update Notifications & Upgrade Flow
type: feature
priority: P1
status: completed
created: 2026-04-16T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Update Notifications & Upgrade Flow

## Overview

Users who install skills via vskill have no proactive way to learn about new versions.
The Skill Studio already has an UpdatesPanel with batch update + SSE progress, and a
VersionHistoryPanel with version comparison. But these are disconnected: version history
can't trigger updates, Studio doesn't alert on load, and there's no cross-linking.

This increment connects the dots in the Studio UI.

## User Stories

### US-001: Update Toast on Studio Load (P1)
**Project**: specweave

**As a** skill consumer
**I want** to see a notification when I open Skill Studio and updates are available
**So that** I discover new versions without manually checking

**Acceptance Criteria**:
- [x] **AC-US1-01**: When Studio loads and 1+ installed skills have updates, a toast banner appears showing "N update(s) available" with a "View Updates" button
- [x] **AC-US1-02**: The toast auto-dismisses after 10 seconds
- [x] **AC-US1-03**: The toast has a dismiss (X) button for manual dismissal
- [x] **AC-US1-04**: Clicking "View Updates" navigates to the UpdatesPanel (#/updates hash route)
- [x] **AC-US1-05**: The toast does not appear when all skills are up to date (updateCount === 0)
- [x] **AC-US1-06**: Once dismissed (manually or auto), the toast does not reappear during the same session

---

### US-002: Versions Tab Update Indicator (P1)
**Project**: specweave

**As a** skill consumer viewing a skill in the workspace
**I want** to see a visual indicator on the Versions tab when the current skill has an update
**So that** I know there's a newer version without switching tabs

**Acceptance Criteria**:
- [x] **AC-US2-01**: When the selected skill has updateAvailable: true, the Versions tab shows a yellow dot indicator
- [x] **AC-US2-02**: The dot uses the same visual pattern as other tab indicators (editor dirty, run active, history regressions)
- [x] **AC-US2-03**: The dot disappears when the skill is updated or a skill without updates is selected

---

### US-003: One-Click Update from Version History (P1)
**Project**: specweave

**As a** skill consumer comparing versions
**I want** to update to the latest version directly from the version history panel
**So that** I don't have to navigate away to perform the update

**Acceptance Criteria**:
- [x] **AC-US3-01**: When installed version differs from latest, an "Update to {version}" button appears in the VersionHistoryPanel header
- [x] **AC-US3-02**: Clicking the button triggers the same SSE-based update flow used by UpdatesPanel (api.startSkillUpdate)
- [x] **AC-US3-03**: Update progress is shown inline (updating, scanning, installing, done/error)
- [x] **AC-US3-04**: After successful update, the version list refreshes and the global skill state refreshes
- [x] **AC-US3-05**: If the update fails, an inline error message is shown with option to retry

---

### US-004: Cross-Link to Updates Panel (P2)
**Project**: specweave

**As a** skill consumer with multiple outdated skills
**I want** a link from version history to the batch updates view
**So that** I can manage all updates at once without navigating manually

**Acceptance Criteria**:
- [x] **AC-US4-01**: When updateCount > 1, a "Manage all updates (N)" link appears in the VersionHistoryPanel header
- [x] **AC-US4-02**: Clicking the link navigates to #/updates (existing hash route to UpdatesPanel)

## Out of Scope

- CLI update notifications (Phase 2)
- Push notifications / webhooks (Phase 3)
- Email notifications for skill updates
- Version pinning UI changes
- Rollback / downgrade capability

## Dependencies

- Existing api.startSkillUpdate() SSE endpoint
- Existing api.getSkillUpdates() endpoint
- Existing StudioContext.updateCount computation
- Existing UpdatesPanel SSE progress pattern
