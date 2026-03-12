---
id: US-001
feature: FS-506
title: "Delete a Source Skill (P3)"
status: not_started
priority: P3
created: 2026-03-12
tldr: "**As a** skill author."
project: vskill
---

# US-001: Delete a Source Skill (P3)

**Feature**: [FS-506](./FEATURE.md)

**As a** skill author
**I want** to delete a source skill from the Skill Studio UI
**So that** I can remove skills I no longer need without leaving orphaned directories on disk

---

## Acceptance Criteria

- [ ] **AC-US1-01**: A DELETE endpoint exists at `/api/skills/:plugin/:skill` that recursively removes the skill directory from disk and returns `{ ok: true }`
- [ ] **AC-US1-02**: The DELETE endpoint returns 403 if the skill's origin is "installed" (read-only) and does not delete anything
- [ ] **AC-US1-03**: The DELETE endpoint returns 404 if the skill directory does not exist
- [ ] **AC-US1-04**: A `deleteSkill(plugin, skill)` method exists on the client-side `api` object that calls the DELETE endpoint
- [ ] **AC-US1-05**: The DetailHeader component shows a delete button (trash icon) for source skills only -- hidden when `isReadOnly` is true
- [ ] **AC-US1-06**: Clicking the delete button opens a confirmation dialog that names the skill and requires explicit confirmation before proceeding
- [ ] **AC-US1-07**: Confirming deletion calls the API, refreshes the sidebar skill list, and clears the current selection
- [ ] **AC-US1-08**: Canceling the confirmation dialog closes it without side effects
- [ ] **AC-US1-09**: The delete button is disabled while a benchmark or other operation is running for that skill

---

## Implementation

**Increment**: [0506-skill-studio-delete](../../../../../increments/0506-skill-studio-delete/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Add DELETE /api/skills/:plugin/:skill server endpoint
- [ ] **T-002**: Add `api.deleteSkill()` client method
- [ ] **T-003**: Add delete button with confirmation to DetailHeader
- [ ] **T-004**: Wire onDelete in SkillWorkspaceInner and pass through RightPanel
