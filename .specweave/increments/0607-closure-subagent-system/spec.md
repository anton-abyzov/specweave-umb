---
increment: 0607-closure-subagent-system
title: Closure Subagent System
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Closure Subagent System

## Overview

Team-lead and auto mode complete all tasks (100%) but never close increments because context overflow prevents the closure pipeline (grill → judge-llm → PM gates → specweave complete) from running. This increment introduces a `sw-closer` subagent that runs `sw:done` in a fresh context, plus a `sw:close-all` batch closure skill.

## User Stories

### US-001: Fresh-Context Closure via Subagent (P1)
**Project**: specweave

**As a** SpecWeave user running team-lead or auto mode
**I want** increment closure to run in a fresh, isolated context
**So that** context overflow never prevents increments from closing

**Acceptance Criteria**:
- [x] **AC-US1-01**: `sw-closer` subagent definition exists at `agents/sw-closer.md` with frontmatter matching the sw-pm/sw-architect/sw-planner pattern
- [x] **AC-US1-02**: sw-closer preloads `sw:done` skill and runs the full closure pipeline (grill, judge-llm, PM validation, specweave complete)
- [x] **AC-US1-03**: sw-closer has built-in retry awareness — if Gate 0 fails (desync), auto-fixes and retries once
- [x] **AC-US1-04**: sw-closer reports SUCCESS with closure summary or FAILURE with specific gate details

---

### US-002: Auto-Closure from Team-Lead and Auto Mode (P1)
**Project**: specweave

**As a** SpecWeave team-lead or auto-mode user
**I want** closure to automatically spawn sw-closer subagents when all tasks complete
**So that** increments close without manual intervention

**Acceptance Criteria**:
- [x] **AC-US2-01**: team-lead SKILL.md Section 8c spawns sw-closer subagent per increment (dependency order) instead of invoking sw:team-merge inline
- [x] **AC-US2-02**: team-merge SKILL.md Step 4 adds sw-closer subagent path (4a) with non-cloud fallback (4b)
- [x] **AC-US2-03**: do/SKILL.md Step 9 splits into 9a (sw-closer subagent) and 9b (direct sw:done for non-cloud)
- [x] **AC-US2-04**: auto/SKILL.md Step 3.5 spawns sw-closer on `all_complete_needs_closure` signal

---

### US-003: Batch Closure for Stuck Increments (P1)
**Project**: specweave

**As a** SpecWeave user with multiple stuck increments at 100%
**I want** a batch closure command
**So that** I can recover stuck increments without manual per-increment closure

**Acceptance Criteria**:
- [x] **AC-US3-01**: `sw:close-all` skill discovers all increments at 100% completion (active/in-progress/ready_for_review with 0 pending tasks)
- [x] **AC-US3-02**: close-all spawns sw-closer subagents per increment (Claude Code) or invokes sw:done sequentially (non-cloud)
- [x] **AC-US3-03**: close-all supports `--dry-run` flag to preview without closing
- [x] **AC-US3-04**: close-all prints summary table with ID, status (CLOSED/FAILED), and reason

---

### US-004: Non-Cloud Environment Support (P1)
**Project**: specweave

**As a** SpecWeave user on Cursor, OpenCode, Copilot, or Aider
**I want** closure to work without the Agent() tool
**So that** non-cloud tools can also close increments reliably

**Acceptance Criteria**:
- [x] **AC-US4-01**: All modified SKILL.md files have explicit non-cloud fallback paths that invoke sw:done directly
- [x] **AC-US4-02**: Non-cloud paths follow the Step N / Step Na pattern established by sw:increment (Step 4 / Step 4a)

## Out of Scope

- Changes to the `sw:done` skill itself (it already has the correct closure logic)
- Changes to `specweave complete` CLI command
- Changes to stop-auto-v5.sh hook (it already emits `all_complete_needs_closure`)
- Changes to LifecycleHookDispatcher
