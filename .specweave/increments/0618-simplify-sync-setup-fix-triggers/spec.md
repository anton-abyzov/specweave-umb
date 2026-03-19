---
increment: 0618-simplify-sync-setup-fix-triggers
title: Simplify sync-setup and fix quadruple-trigger sync
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Simplify sync-setup and fix quadruple-trigger sync

## Problem Statement

Two problems: (A) sync-setup wizard asks 10+ complex questions about repo architecture when 3-5 suffice. (B) Four independent sync triggers fire for the same event, causing 4x API calls and draining the GitHub rate limit.

**Project**: specweave

## User Stories

### US-001: Event Queue Sync Model (P0)
**Project**: specweave

**As a** SpecWeave user
**I want** sync triggers to queue events instead of syncing directly
**So that** each increment is synced exactly once per session, not 4x

**Acceptance Criteria**:
- [x] **AC-US1-01**: `queueSyncEvent()` utility writes events to `.specweave/state/event-queue/pending.jsonl`
- [x] **AC-US1-02**: `LifecycleHookDispatcher.onTaskCompleted()` queues events instead of calling LivingDocsSync directly
- [x] **AC-US1-03**: `LifecycleHookDispatcher.onIncrementDone()` queues events instead of calling SyncCoordinator directly (except when called from `specweave complete`)
- [x] **AC-US1-04**: `StatusChangeSyncTrigger.spawnAsyncSync()` queues events instead of direct sync
- [x] **AC-US1-05**: `post-tool-use.sh` status change detection queues to pending.jsonl instead of calling project-bridge-handler directly
- [x] **AC-US1-06**: `sync.mode` config option: `"queued"` (default) vs `"immediate"` (legacy)

---

### US-002: Simplified Sync-Setup Wizard (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** sync-setup to ask 3-5 questions instead of 10+
**So that** I can configure external tool integration quickly

**Acceptance Criteria**:
- [x] **AC-US2-01**: Single-project setup (childRepos.length <= 1): asks tracker type, project name, validates credentials — done
- [x] **AC-US2-02**: Multi-project setup (childRepos.length > 1): asks tracker type, per-childRepo sync target, validates — done
- [x] **AC-US2-03**: `--quick` flag skips all prompts, auto-detects everything from config/env

## Out of Scope

- Full GraphQL migration (separate increment 0612)
- Persistent file-backed cache (Phase 2)
- Webhook-based sync
