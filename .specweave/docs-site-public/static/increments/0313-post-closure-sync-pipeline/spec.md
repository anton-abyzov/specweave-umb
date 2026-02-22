---
increment: 0313-post-closure-sync-pipeline
title: "Fix post-closure sync pipeline"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Fix post-closure sync pipeline

## Overview

The post-closure sync pipeline has a critical architectural problem: the `/sw:done` skill directly edits `metadata.json` to set status to `completed` (Step 8 in SKILL.md), bypassing the `completeIncrement()` function in `status-commands.ts`. This means `LifecycleHookDispatcher.onIncrementDone()` never fires from the skill path, so living docs sync, GitHub issue closure, and GitHub Project sync silently fail.

Additionally, the `sw:sync-docs` skill referenced in Step 10 of the done skill does not exist, and the `sync_to_github_project` hook handler is declared in config types but has no implementation in `LifecycleHookDispatcher`.

This increment eliminates the dual-path architecture, creates the missing skill, wires the dispatcher, and adds the missing handler.

## User Stories

### US-001: Eliminate dual-path completion architecture (P1)
**Project**: specweave

**As a** SpecWeave framework maintainer
**I want** the `/sw:done` skill to use the CLI `completeIncrement()` function as its single completion path
**So that** post-closure hooks (living docs sync, GitHub issue closure, external sync) fire reliably regardless of how an increment is closed

**Acceptance Criteria**:
- [x] **AC-US1-01**: The done skill's Step 8 instructs the LLM to call `specweave complete <id>` CLI command instead of directly editing metadata.json
- [x] **AC-US1-02**: `completeIncrement()` in `status-commands.ts` awaits `LifecycleHookDispatcher.onIncrementDone()` instead of fire-and-forget (void async IIFE)
- [x] **AC-US1-03**: The fire-and-forget pattern is replaced with a logged-but-non-blocking await pattern that reports hook results to the user
- [x] **AC-US1-04**: Existing unit tests for `completeIncrement()` continue to pass

---

### US-002: Create sw:sync-docs skill (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** a `/sw:sync-docs` skill that syncs living docs for an increment
**So that** Step 10 of `/sw:done` can invoke it and I can also run it manually

**Acceptance Criteria**:
- [x] **AC-US2-01**: A new skill at `plugins/specweave/skills/sync-docs/SKILL.md` exists with proper frontmatter (description, argument-hint)
- [x] **AC-US2-02**: The skill invokes `LivingDocsSync.syncIncrement()` for the given increment ID
- [x] **AC-US2-03**: The skill accepts an optional "review" mode argument that validates sync completeness without modifying files
- [x] **AC-US2-04**: The skill handles errors gracefully and reports sync results (files created/updated count)

---

### US-003: Add sync_to_github_project handler to LifecycleHookDispatcher (P1)
**Project**: specweave

**As a** SpecWeave user with GitHub Project integration
**I want** the `sync_to_github_project` hook to fire after increment completion
**So that** my GitHub Project items are automatically updated when I close an increment

**Acceptance Criteria**:
- [x] **AC-US3-01**: `LifecycleHookDispatcher.onIncrementDone()` checks `hooks.post_increment_done.sync_to_github_project` config flag
- [x] **AC-US3-02**: When enabled, it invokes the GitHub feature sync CLI (`github-feature-sync-cli.js`) for the increment's feature ID
- [x] **AC-US3-03**: Feature ID is resolved from the increment's spec.md frontmatter or metadata.json
- [x] **AC-US3-04**: Handler failure does not block other post-closure operations (error-isolated)
- [x] **AC-US3-05**: Unit test verifies the handler dispatches when flag is true and skips when false

---

### US-004: Wire LifecycleHookDispatcher into done skill post-closure (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** the done skill to explicitly report sync results after closure
**So that** I can see which post-closure operations succeeded or failed

**Acceptance Criteria**:
- [x] **AC-US4-01**: The done skill's Step 9 (Post-Closure Sync) is updated to show the sync result summary table after `specweave complete` runs
- [x] **AC-US4-02**: If any sync operation fails, the skill shows "Run /sw:progress-sync to retry" guidance

## Functional Requirements

### FR-001: Single completion path via CLI
The `specweave complete <id>` CLI command is the ONLY way to transition an increment to `completed` status. The done skill MUST call this command rather than directly editing metadata.json.

### FR-002: sync_to_github_project handler
The handler reads the increment's feature ID (from spec.md frontmatter `feature_id` field or from metadata.json `feature_id`), then invokes the GitHub feature sync CLI to push the spec to GitHub Project. Uses dynamic import of the sync module to avoid hard dependency on the github plugin.

### FR-003: sw:sync-docs skill
A lightweight skill that wraps `LivingDocsSync.syncIncrement()`. In "review" mode it performs a dry-run check. In normal mode it performs the actual sync. Reports results in a structured format.

## Success Criteria

- All post-closure hooks fire reliably when using `/sw:done`
- `sw:sync-docs` skill is discoverable and invocable
- `sync_to_github_project` flag in config actually triggers GitHub Project sync
- No regression in existing hook dispatcher tests

## Out of Scope

- JIRA or ADO project sync handlers (future increment)
- Changing the hook configuration schema
- Modifying the `specweave init` flow
- Bidirectional sync from GitHub Project back to SpecWeave

## Dependencies

- Existing `LifecycleHookDispatcher` (src/core/hooks/LifecycleHookDispatcher.ts)
- Existing `completeIncrement()` (src/core/increment/status-commands.ts)
- Existing `LivingDocsSync` (src/core/living-docs/living-docs-sync.ts)
- GitHub feature sync CLI (plugins/specweave-github/lib/github-feature-sync-cli.js)
- Done skill (plugins/specweave/skills/done/SKILL.md)
