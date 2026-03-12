---
increment: 0511-fix-ado-jira-sync
title: Fix ADO/JIRA Sync Bugs
type: bug
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix ADO/JIRA Sync Bugs

## Overview

Five bugs in the ADO and JIRA sync providers cause work items to remain stuck in wrong states, miss parent links, use wrong work item types, skip metadata fallbacks, and silently swallow transition failures. All fixes target `src/sync/providers/ado.ts`, `src/sync/providers/jira.ts`, and `src/sync/sync-coordinator.ts` in the specweave repo.

## User Stories

### US-001: ADO Process-Aware State Transitions (P1)
**Project**: specweave

**As a** SpecWeave user with an ADO Basic process project
**I want** increment closure to transition work items to the correct terminal state (Done, not Closed)
**So that** my ADO board accurately reflects completed work

**Acceptance Criteria**:
- [x] **AC-US1-01**: `closeIssue()` in `ado.ts` calls `detectProcessTemplate()` (lazy-cached) to resolve the correct terminal state per process template (Basic=Done, Agile=Closed, Scrum=Done, CMMI=Closed)
- [x] **AC-US1-02**: A `private cachedTemplate?: AdoProcessTemplateInfo` field caches the result of `detectProcessTemplate()` after first call; subsequent calls reuse it
- [x] **AC-US1-03**: If `detectProcessTemplate()` fails, fallback to `this.config.closedState || 'Closed'` (no regression from current behavior)
- [x] **AC-US1-04**: `mapStatusToAdo()` uses the cached template to resolve `completed` and `done` to the correct terminal state instead of hardcoding `'Closed'`
- [x] **AC-US1-05**: `reopenIssue()` uses the cached template to resolve the correct active state (Basic=Doing, Agile=Active, Scrum=Committed, CMMI=Active) with fallback to `this.config.activeState || 'Active'`

**Root Cause**: `closeIssue()` at line 154 uses `this.config.closedState || 'Closed'` but ADO Basic process only has states To Do/Doing/Done. `mapStatusToAdo()` at lines 371-381 also hardcodes `completed -> 'Closed'`. The existing `detectProcessTemplate()` in `ado-client.ts:885-945` is never called during closure.

---

### US-002: ADO Parent Work Item Linking (P1)
**Project**: specweave

**As a** SpecWeave user syncing to ADO
**I want** user story work items to be linked to their parent epic/feature work item
**So that** my ADO hierarchy reflects the SpecWeave spec structure

**Acceptance Criteria**:
- [x] **AC-US2-01**: `createIssue()` in `ado.ts` reads `feature.externalRef?.id` to obtain the parent work item ID
- [x] **AC-US2-02**: When a parent ID exists, `createIssue()` adds a `System.LinkTypes.Hierarchy-Reverse` relation to the PATCH operations pointing to the parent work item URL
- [x] **AC-US2-03**: When no parent ID exists (feature not yet synced), creation proceeds without parent link (no error)

**Root Cause**: `createIssue()` at lines 84-128 never sets `System.Parent` or adds a hierarchy link. The `feature` parameter already carries external ref data but it is unused for linking.

---

### US-003: ADO Process-Aware Work Item Types (P1)
**Project**: specweave

**As a** SpecWeave user with an ADO Basic process project
**I want** user stories to be created as Issue work items (not User Story)
**So that** work item creation does not fail with a 400 error on Basic projects

**Acceptance Criteria**:
- [x] **AC-US3-01**: `createIssue()` in `ado.ts` uses the cached template from `detectProcessTemplate()` to resolve the correct work item type for user stories (Basic=Issue, Agile=User Story, Scrum=Product Backlog Item, CMMI=Requirement)
- [x] **AC-US3-02**: If template detection fails, fallback to `this.config.workItemType || 'User Story'` (no regression)
- [x] **AC-US3-03**: The existing `detectHierarchy()` method is aligned with the new cached template data (no duplicate detection calls)

**Root Cause**: `createIssue()` defaults to `this.config.workItemType || 'User Story'` at line 100, which does not exist in ADO Basic process. The existing `detectHierarchy()` at lines 282-329 handles this but is never called during creation.

---

### US-004: ADO Metadata Fallback for Closure (P2)
**Project**: specweave

**As a** SpecWeave user closing an increment with ADO sync
**I want** ADO work item ID resolution to check metadata.json as a fallback
**So that** work items created by the auto-creator are properly closed

**Acceptance Criteria**:
- [x] **AC-US4-01**: `closeAdoWorkItemsForUserStories()` in `sync-coordinator.ts` implements the same 3-layer resolution as the JIRA closure path: `usFile.external_tools?.ado?.id` -> `usFile.external_id` -> `metadata.ado.work_item_id`
- [x] **AC-US4-02**: metadata.json is read once per closure call (not per user story) and cached locally

**Root Cause**: `closeAdoWorkItemsForUserStories()` at lines 287-296 only checks `usFile.external_tools?.ado?.id || usFile.external_id`. The JIRA closure at lines 171-186 already has a 3-layer fallback including metadata.json, but ADO does not.

---

### US-005: JIRA Transition Warning on Skip (P2)
**Project**: specweave

**As a** SpecWeave user syncing to JIRA
**I want** a warning logged when a transition cannot be found
**So that** I can diagnose why work items remain in the wrong status

**Acceptance Criteria**:
- [x] **AC-US5-01**: `transitionIssue()` in `jira.ts` logs a warning (via `console.warn` or logger) when no matching transition is found, including the issue key, target status name, and the list of available transition names
- [x] **AC-US5-02**: `closeIssue()` in `jira.ts` reads the target status from config (`statusSync.mappings.jira.completed`) with fallback to `'Done'` instead of hardcoding `'Done'`
- [x] **AC-US5-03**: No error is thrown on missing transition (resilient sync continues)

**Root Cause**: `transitionIssue()` at lines 348-365 silently returns when no matching transition is found. `closeIssue()` at line 160 hardcodes `'Done'` instead of using configurable status.

## Functional Requirements

### FR-001: Lazy Template Caching in AdoAdapter
AdoAdapter gains a `private cachedTemplate?: AdoProcessTemplateInfo` field. A private async `getTemplate()` method calls `detectProcessTemplate()` on first invocation, caches the result, and returns it. All methods needing process-specific values (`closeIssue`, `createIssue`, `mapStatusToAdo`, `reopenIssue`) call `getTemplate()`.

### FR-002: Consistent 3-Layer ID Resolution
Both JIRA and ADO closure paths in `sync-coordinator.ts` use the same resolution order: frontmatter external_tools -> external_id -> metadata.json.

### FR-003: JIRA Configurable Close Status
`closeIssue()` accepts or resolves the target status from sync config, defaulting to `'Done'` only when no config is present.

## Success Criteria

- ADO Basic process projects transition to "Done" on increment closure
- ADO work items are created with correct type per process template
- Parent hierarchy links appear in ADO when feature has an external ref
- JIRA transitions log warnings when no matching transition exists
- No regressions: projects with explicit `closedState`/`workItemType` config continue to work

## Out of Scope

- ADO SAFe/Enterprise template support improvements (existing `detectProcessTemplate` already handles SAFe)
- JIRA fuzzy transition matching
- New UI for sync status visibility
- Bidirectional sync from ADO/JIRA back to SpecWeave
- Refactoring the adapter pattern or engine interfaces

## Dependencies

- `AdoClient.detectProcessTemplate()` in `src/integrations/ado/ado-client.ts` (existing, lines 885-945)
- `AdoProcessTemplateInfo` type definition (existing in ado-client.ts)
- `FeatureData.externalRef` field (existing in engine.ts)
- `SyncConfigurationExtended.statusSync.mappings.jira.completed` config path (existing)
