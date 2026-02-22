---
increment: 0298-hook-lifecycle-wiring
title: "Hook Lifecycle Wiring"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Hook Lifecycle Wiring

## Overview

The `HookConfiguration` in `config.json` defines three hook triggers (`post_increment_planning`, `post_task_completion`, `post_increment_done`) with configurable behaviors (auto-create GitHub issues, sync tasks, sync living docs, close issues). However, `HookExecutor` exists only as a health-check tool that spawns child processes. No code actually reads the `hooks` config and dispatches actions when lifecycle events occur.

The existing lifecycle events (in `createIncrementTemplates`, `MetadataManager.updateStatus`, `StatusChangeSyncTrigger`, `completeIncrement`) do some inline sync work (e.g., auto-create issues via `StatusChangeSyncTrigger.autoCreateIfNeeded`), but they do NOT consult `config.json` hooks settings. This means:

1. `hooks.post_increment_planning.auto_create_github_issue` is never checked after increment creation
2. `hooks.post_task_completion.sync_tasks_md` and `external_tracker_sync` are never checked
3. `hooks.post_increment_done` settings are never checked during completion

**Goal**: Create a `LifecycleHookDispatcher` that reads hooks config and dispatches configured actions at the right lifecycle points, replacing the current decorative config with functional wiring.

## User Stories

### US-001: Post-Increment-Planning Hook Fires (P1)
**Project**: specweave

**As a** SpecWeave user with hooks.post_increment_planning.auto_create_github_issue=true
**I want** a GitHub issue to be automatically created after increment templates are generated
**So that** I don't have to manually run /sw-github:create

**Acceptance Criteria**:
- [x] **AC-US1-01**: After `createIncrementTemplates()` succeeds, the dispatcher checks `config.hooks.post_increment_planning.auto_create_github_issue` and calls `autoCreateExternalIssue()` if true
- [x] **AC-US1-02**: If `auto_create_github_issue` is false or hooks config is missing, no issue is created
- [x] **AC-US1-03**: Hook dispatch is non-blocking - failures log warnings but don't crash increment creation

---

### US-002: Post-Task-Completion Hook Fires (P1)
**Project**: specweave

**As a** SpecWeave user with hooks.post_task_completion configured
**I want** task-related sync to fire when tasks are marked complete
**So that** external trackers stay in sync automatically

**Acceptance Criteria**:
- [x] **AC-US2-01**: The dispatcher is callable from task completion flows, checks `config.hooks.post_task_completion`, and triggers `sync_tasks_md` sync if enabled
- [x] **AC-US2-02**: External tracker sync fires when `external_tracker_sync=true`
- [x] **AC-US2-03**: When both settings are false, no sync operations run

---

### US-003: Post-Increment-Done Hook Fires (P1)
**Project**: specweave

**As a** SpecWeave user completing an increment
**I want** configured post-done hooks (living docs sync, GitHub project sync, issue closure) to fire
**So that** all external tools are updated on completion per my config

**Acceptance Criteria**:
- [x] **AC-US3-01**: The dispatcher is called from `completeIncrement()` and checks `config.hooks.post_increment_done`
- [x] **AC-US3-02**: Each setting (`sync_living_docs`, `sync_to_github_project`, `close_github_issue`) independently controls whether its action fires
- [x] **AC-US3-03**: When `update_living_docs_first=true`, living docs sync runs before GitHub sync

---

### US-004: Config-Driven Behavior (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** hook behavior to be fully controlled by config.json hooks section
**So that** I can disable/enable specific automations without code changes

**Acceptance Criteria**:
- [x] **AC-US4-01**: When no `hooks` key exists in config, all hook-based actions are skipped (safe default)
- [x] **AC-US4-02**: Each hook trigger can be independently configured
- [x] **AC-US4-03**: The dispatcher gracefully handles partial/missing config (e.g., hooks.post_increment_planning exists but post_task_completion does not)

## Functional Requirements

### FR-001: LifecycleHookDispatcher Module
A new module `src/core/hooks/LifecycleHookDispatcher.ts` that:
- Reads `config.hooks` via `ConfigManager`
- Provides static methods: `onIncrementPlanned()`, `onTaskCompleted()`, `onIncrementDone()`
- Each method checks relevant config flags before dispatching
- All dispatches are non-blocking with error isolation
- Uses existing services (`autoCreateExternalIssue`, `LivingDocsSync`, `SyncCoordinator`) -- no new sync logic

### FR-002: Wiring Points
- `createIncrementCommand()` calls `LifecycleHookDispatcher.onIncrementPlanned()` after successful creation
- `completeIncrement()` calls `LifecycleHookDispatcher.onIncrementDone()` after status update
- Task completion flows can call `LifecycleHookDispatcher.onTaskCompleted()` (entry point exposed)

## Success Criteria

- All three hook triggers fire when configured
- Zero behavior change when hooks config is absent (backward compatible)
- No duplicate sync calls with existing StatusChangeSyncTrigger logic

## Out of Scope

- Rewriting HookExecutor (it serves health-checks, not lifecycle dispatch)
- Rewriting the EDA event queue processor (hooks/processor.ts)
- Adding new hook trigger types beyond the three defined
- Changing the config.json schema

## Dependencies

- `src/sync/external-issue-auto-creator.ts` (auto-create issues)
- `src/core/living-docs/living-docs-sync.ts` (living docs sync)
- `src/sync/sync-coordinator.ts` (issue closure)
- `src/core/config/config-manager.ts` (read hooks config)
