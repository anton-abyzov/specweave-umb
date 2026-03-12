---
increment: 0506-skill-studio-delete
title: "Skill Studio: Add Delete Skill Functionality"
type: bug
priority: P3
status: planned
created: 2026-03-12
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio -- Add Delete Skill Functionality

## Overview

The Skill Studio eval-ui currently has no way to delete skills. Users can create and edit skills but cannot remove them, leaving orphaned skill directories on disk. This increment adds a DELETE API endpoint on the eval server, a client-side API method, and a delete button with confirmation dialog in the DetailHeader component. Only skills with `origin: "source"` are deletable; installed (read-only) skills are protected.

## User Stories

### US-001: Delete a Source Skill (P3)
**Project**: vskill

**As a** skill author
**I want** to delete a source skill from the Skill Studio UI
**So that** I can remove skills I no longer need without leaving orphaned directories on disk

**Acceptance Criteria**:
- [x] **AC-US1-01**: A DELETE endpoint exists at `/api/skills/:plugin/:skill` that recursively removes the skill directory from disk and returns `{ ok: true }`
- [x] **AC-US1-02**: The DELETE endpoint returns 403 if the skill's origin is "installed" (read-only) and does not delete anything
- [x] **AC-US1-03**: The DELETE endpoint returns 404 if the skill directory does not exist
- [x] **AC-US1-04**: A `deleteSkill(plugin, skill)` method exists on the client-side `api` object that calls the DELETE endpoint
- [x] **AC-US1-05**: The DetailHeader component shows a delete button (trash icon) for source skills only -- hidden when `isReadOnly` is true
- [x] **AC-US1-06**: Clicking the delete button opens a confirmation dialog that names the skill and requires explicit confirmation before proceeding
- [x] **AC-US1-07**: Confirming deletion calls the API, refreshes the sidebar skill list, and clears the current selection
- [x] **AC-US1-08**: Canceling the confirmation dialog closes it without side effects
- [x] **AC-US1-09**: The delete button is disabled while a benchmark or other operation is running for that skill

## Out of Scope

- Bulk delete (multi-select and delete several skills at once)
- Undo/restore deleted skills
- Archiving skills instead of deleting
- Delete confirmation via typing the skill name (simple confirm/cancel is sufficient)

## Dependencies

- Existing `resolveSkillDir()` for path resolution (eval-server/skill-resolver.ts)
- Existing `scanSkills()` for origin detection (eval/skill-scanner.ts)
- Existing `StudioContext` with `refreshSkills()` and `clearSelection()` (eval-ui/src/StudioContext.tsx)
- Node.js `fs.rm` with `{ recursive: true }` for directory removal
