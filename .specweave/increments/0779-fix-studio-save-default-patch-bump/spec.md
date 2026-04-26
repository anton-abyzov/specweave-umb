---
increment: 0779-fix-studio-save-default-patch-bump
title: Studio Save default patch bump
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Save default patch bump

## Overview

The Skill Studio Edit tab has buttons "+patch / +minor / +major / Save / Publish". User report: "When I click a Save button, by default, it must increase the patch and refresh what I see here. Now it was not working." Today, clicking Save without first clicking a manual bump button persists the content without bumping the version — the version badge and preview pane don't change visibly. Backend route `/api/skills/:plugin/:skill/apply-improvement` would auto-bump, but only when the incoming version is not strictly higher than the previous one — the frontend always sends the same version it loaded, never triggering the auto-bump path.

**Fix:** in `EditorPanel.tsx` `handleSave()`, when the editor's frontmatter version equals the last-saved version, call `handleBump("patch")` first to mutate the editor content, then save. When the user has already manually bumped, respect their choice and save as-is.

## User Stories

### US-001: Save bumps patch when no manual bump (P1)
**Project**: vskill

**As a** skill author editing SKILL.md in Studio,
**I want** clicking Save to automatically increment the patch version by default,
**So that** every save produces a distinct version number — visible in the badge and preview — without me needing to click +patch first.

**Acceptance Criteria**:
- [x] **AC-US1-01**: When the editor frontmatter version equals the last-saved version (e.g. both are `1.0.2`), clicking Save mutates the editor content to bump the patch (to `1.0.3`) BEFORE the persist call, so the saved frontmatter declares `1.0.3`.
- [x] **AC-US1-02**: After the save resolves, the version badge and Preview pane reflect the new patch version (driven by the existing `studio:content-saved` event — no new wiring required).
- [x] **AC-US1-03**: The `isDirty` and `saving` guards on the Save button are unchanged — Save remains disabled when content has not been modified.

---

### US-002: Save respects manual version bumps (P1)
**Project**: vskill

**As a** skill author who has explicitly clicked +patch / +minor / +major before saving,
**I want** Save to use my chosen version verbatim,
**So that** my deliberate minor or major bump isn't silently overwritten by an unwanted extra patch increment.

**Acceptance Criteria**:
- [x] **AC-US2-01**: When the editor frontmatter version is strictly higher than the last-saved version (any of patch/minor/major manually applied), Save persists the editor content as-is — does NOT bump again.
- [x] **AC-US2-02**: A manual `+minor` from `1.0.2` followed by Save persists `1.1.0`, never `1.1.1`.
- [x] **AC-US2-03**: A manual `+patch` from `1.0.2` followed by Save persists `1.0.3`, never `1.0.4`.

---

### US-003: Test coverage (P1)
**Project**: vskill

**As a** maintainer,
**I want** vitest assertions covering both the auto-bump and respect-manual paths,
**So that** future refactors don't silently re-introduce the no-bump or double-bump behavior.

**Acceptance Criteria**:
- [x] **AC-US3-01**: Vitest case: render EditorPanel with saved `1.0.2`, do not click any bump button, click Save → assert the persist call (mocked `saveContent` or `api.applyImprovement`) receives content whose frontmatter version is `1.0.3`.
- [x] **AC-US3-02**: Vitest case: render with saved `1.0.2`, simulate `+minor` (textarea now declares `1.1.0`), click Save → assert persisted version is `1.1.0`.
- [x] **AC-US3-03**: Vitest case: render with saved `1.0.2`, simulate `+patch` (textarea declares `1.0.3`), click Save → assert persisted version is `1.0.3` (not `1.0.4`).

## Functional Requirements

### FR-001: Frontend-only change
The fix is confined to `EditorPanel.tsx`. The `apply-improvement` backend route is unchanged.

### FR-002: No new dependencies
Reuses the existing version-parsing/rewriting logic from `handleBump`.

## Success Criteria

- Manual repro: open Studio, edit SKILL.md frontmatter or body trivially, click Save → version badge updates to next patch.
- All three vitest cases pass; existing EditorPanel tests stay green.

## Out of Scope

- Backend `apply-improvement` route (already correctly auto-bumps; we just stop relying on that path).
- Reworking +patch / +minor / +major buttons.
- Changing Publish behavior.
- The preview-pane refresh mechanism (already driven by `studio:content-saved`).

## Dependencies

None. `handleBump("patch")` already exists in the same file.
