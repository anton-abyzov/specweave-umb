---
increment: 0304-fix-external-work-item-creation
title: "Fix External Work Item Creation"
type: bug
priority: P0
status: planned
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix External Work Item Creation

## Overview

Two bugs in the external work item creation pipeline cause garbage GitHub issues:

1. **Template placeholders leak into GitHub issues**: The `post_increment_planning` hook fires `autoCreateExternalIssue` immediately after `createIncrementTemplates`, but at that point spec.md is still a template with placeholders like `[Story Title]`, `[user type]`, etc. The `ExternalIssueAutoCreator.parseUserStories()` treats these as real user stories, creating GitHub issues with titles like `[FS-304][US-001] [Story Title]`.

2. **Living docs sync not triggering for new increments**: The `LifecycleHookDispatcher.onIncrementPlanned()` only dispatches `autoCreateExternalIssue`. It does NOT trigger `LivingDocsSync.syncIncrement()`. Living docs sync only runs on `post_task_completion` and `post_increment_done`, so newly created increments never get living docs until the first task completes or the increment is done. Without living docs, the proper `UserStoryIssueBuilder` pipeline (which reads us-*.md files with real content) never runs.

## Root Cause Analysis

### Bug 1: Template placeholder leaking

**Flow**:
1. `specweave create-increment` calls `createIncrementTemplates()` which writes spec.md with `[Story Title]`, `[user type]` etc.
2. `create-increment.ts` line 63: `void LifecycleHookDispatcher.onIncrementPlanned(projectRoot, id).catch(() => {})`
3. `onIncrementPlanned()` calls `autoCreateExternalIssue(projectRoot, incrementId)`
4. `ExternalIssueAutoCreator.parseUserStories()` regex `/^### (US-\d+):?\s*(.+)$/gm` matches `### US-001: [Story Title] (P1)` and extracts `[Story Title] (P1)` as the title
5. GitHub issues get created with placeholder titles and bodies

**Fix**: Check if spec.md is still a template before creating external issues. The `isTemplateFile()` function in `template-creator.ts` already exists and detects template markers.

### Bug 2: Missing living docs sync on increment planning

**Flow**:
1. `LifecycleHookDispatcher.onIncrementPlanned()` only checks `hooks.post_increment_planning.auto_create_github_issue`
2. There is no `sync_living_docs` option in `post_increment_planning` hooks
3. Living docs are only synced in `post_task_completion.sync_tasks_md` and `post_increment_done.sync_living_docs`
4. Without living docs, the proper GitHub sync pipeline (UserStoryIssueBuilder reading us-*.md) is never triggered for new increments

**Fix**: Add `sync_living_docs` option to `post_increment_planning` hooks and wire it in `LifecycleHookDispatcher.onIncrementPlanned()`. Also ensure the auto-create guard prevents creating issues from template content.

## User Stories

### US-001: Guard external issue creation against template content (P0)
**Project**: specweave

**As a** SpecWeave user with GitHub sync enabled
**I want** the auto-create GitHub issue hook to skip creation when spec.md is still a template
**So that** placeholder text like `[Story Title]` never appears in my GitHub issues

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `ExternalIssueAutoCreator.createForIncrement()` checks `isTemplateFile(specPath)` before parsing user stories, and returns `skipped: true` with reason `spec.md is still a template` when true
- [ ] **AC-US1-02**: `autoCreateExternalIssue()` gracefully handles the template guard, logging a message that external issue creation was deferred
- [ ] **AC-US1-03**: Unit test verifies that when spec.md contains template markers (`[Story Title]`, `[user type]`, `{{RESOLVED_PROJECT}}`), no GitHub API calls are made
- [ ] **AC-US1-04**: Unit test verifies that when spec.md has real user stories (no template markers), GitHub issues ARE created normally

---

### US-002: Add living docs sync to post-increment-planning hook (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** living docs to be synced after increment planning is complete (spec.md fully written)
**So that** the proper GitHub issue creation pipeline (UserStoryIssueBuilder) has living docs to work with

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `HookConfiguration.post_increment_planning` type includes optional `sync_living_docs: boolean` field
- [ ] **AC-US2-02**: `LifecycleHookDispatcher.onIncrementPlanned()` calls `LivingDocsSync.syncIncrement()` when `hooks.post_increment_planning.sync_living_docs` is true
- [ ] **AC-US2-03**: Living docs sync runs BEFORE external issue auto-creation (order matters: living docs must exist for the proper sync pipeline)
- [ ] **AC-US2-04**: Config templates and defaults include `sync_living_docs: true` in `post_increment_planning`
- [ ] **AC-US2-05**: Unit test verifies that `onIncrementPlanned` triggers both living docs sync and external issue creation in the correct order

---

### US-003: Update test coverage (P1)
**Project**: specweave

**As a** developer maintaining SpecWeave
**I want** comprehensive test coverage for the template guard and hook wiring changes
**So that** regressions in external issue creation are caught early

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Unit test for `ExternalIssueAutoCreator` verifies the template guard with multiple template marker variants
- [ ] **AC-US3-02**: Unit test for `LifecycleHookDispatcher.onIncrementPlanned` verifies living docs sync is called when enabled
- [ ] **AC-US3-03**: Unit test for `LifecycleHookDispatcher.onIncrementPlanned` verifies order: living docs sync THEN external issue creation
- [ ] **AC-US3-04**: Existing tests continue to pass after changes

## Functional Requirements

### FR-001: Template guard in ExternalIssueAutoCreator
In `loadIncrementInfo()` or `createForIncrement()`, call `isTemplateFile(specPath)` before parsing. If the file is a template, return early with `{ success: true, provider: 'none', skipped: true, skipReason: 'spec.md is still a template - external issue creation deferred until spec is complete' }`.

### FR-002: Living docs sync in post_increment_planning
Add `sync_living_docs?: boolean` to `HookConfiguration.post_increment_planning`. In `onIncrementPlanned()`, check this flag and call `LivingDocsSync.syncIncrement()` before `autoCreateExternalIssue`.

### FR-003: Config defaults update
All config template locations (`config.json.template`, `directory-structure.ts`, `sync-config-writer.ts`, `smart-defaults.ts`) should include `sync_living_docs: true` in `post_increment_planning`.

## Success Criteria

- No GitHub issues are created with `[Story Title]` or other template placeholders
- Living docs are created for new increments when planning is complete
- All existing tests pass
- New tests cover both template guard and hook wiring

## Out of Scope

- Deleting the two garbage GitHub issues (#1241, #1242) already created -- those can be manually closed
- Changing the overall architecture of the sync pipeline
- Modifying how `createIncrementTemplates()` generates templates

## Dependencies

- `template-creator.ts` `isTemplateFile()` function (already exists, no changes needed)
- `LifecycleHookDispatcher` (needs modification)
- `ExternalIssueAutoCreator` (needs modification)
- `HookConfiguration` type (needs extension)
