---
increment: 0598-fix-ado-sync-parent-linking
title: Fix ADO Sync Wrong Parent Links
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix ADO Sync Wrong Parent Links

## Overview

ADO sync creates user stories linked to wrong parent epics. Two bugs in `ado-spec-sync.ts` cause this:

1. `findStoryByTitle()` searches for `[US-001]` in title across the entire ADO project without scoping to the current feature. Since US-IDs are reused across increments, it matches stories from unrelated features.
2. `updateStory()` silently swallows 409 errors when adding a parent link, assuming the parent is already correct. When the matched story has a *different* parent, the re-linking fails silently and the story stays under the wrong epic.

**Regression from**: Increment 0511-fix-ado-jira-sync

**Evidence**: Increment 0591 created Epic #1448, but US-001 (#194) was matched to an item under Epic #191 (FS-480), and US-002 (#208) to an item under Epic #206 (FS-482) — both completely unrelated.

## User Stories

### US-001: Scope story matching to parent feature (P1)
**Project**: specweave

**As a** SpecWeave user syncing specs to ADO,
**I want** `findStoryByTitle()` to only match stories that are children of the current feature,
**So that** user stories with reused IDs (e.g., `US-001`) are not incorrectly matched to stories from other increments.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `findStoryByTitle()` accepts a `featureId` parameter and adds `[System.Parent] = {featureId}` to the WIQL query to scope matching to children of the specified feature
- [x] **AC-US1-02**: `syncUserStories()` passes the current `featureId` to `findStoryByTitle()`
- [x] **AC-US1-03**: When two features both have a `[US-001]` story, syncing one feature does NOT match the other feature's story
- [x] **AC-US1-04**: When no matching story exists under the current feature, `findStoryByTitle()` returns `null` (creation path is triggered)

---

### US-002: Fix silent parent re-linking failure (P1)
**Project**: specweave

**As a** SpecWeave user syncing specs to ADO,
**I want** `updateStory()` to detect and correct wrong parent links instead of silently ignoring them,
**So that** stories are always linked to the correct feature after sync.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `updateStory()` fetches the story's current relations to determine its existing parent before attempting to add a new parent link
- [x] **AC-US2-02**: When the existing parent matches `updates.parentId`, no parent link operation is performed (no-op, avoids 409)
- [x] **AC-US2-03**: When the existing parent differs from `updates.parentId`, the old parent link is removed and the new parent link is added
- [x] **AC-US2-04**: When the story has no existing parent link, the new parent link is added directly (existing create behavior preserved)
- [x] **AC-US2-05**: The silent catch block (line 833) is replaced with error handling that distinguishes "wrong parent" from genuine API errors

## Technical Context

### Bug 1: Unscoped WIQL query (`ado-spec-sync.ts:674-707`)

Current WIQL in `findStoryByTitle()`:
```sql
SELECT [System.Id], [System.Title], [System.Description], [System.State]
FROM WorkItems
WHERE [System.TeamProject] = '{project}'
  AND [System.WorkItemType] = '{resolvedType}'
  AND [System.Title] CONTAINS '[{usId}]'
```

Missing scope clause. Fix: add `AND [System.Parent] = {featureId}` to restrict matches to children of the current feature. The `featureId` is already available in the caller `syncUserStories()` (line 438) — just needs to be passed through.

### Bug 2: Silent catch swallows wrong-parent error (`ado-spec-sync.ts:816-836`)

`updateStory()` attempts to add a parent link. ADO returns 409 when a parent link already exists. The catch block assumes "parent already correct" — but the existing parent may be a *different* feature. Fix: before adding, fetch the story's relations via `GET /wit/workitems/{id}?$expand=relations`, check if a `System.LinkTypes.Hierarchy-Reverse` relation exists, compare its target work item ID against `updates.parentId`, and if different, remove the old relation then add the new one.

## Out of Scope

- Jira sync (separate integration, not affected by this bug)
- GitHub sync (uses different linking mechanism)
- Retroactive fix of already-mislinked stories (manual ADO cleanup)
- Changes to `createStory()` (already sets parent correctly on creation)
