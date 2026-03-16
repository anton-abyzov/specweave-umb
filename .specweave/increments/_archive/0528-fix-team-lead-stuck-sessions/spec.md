---
title: Fix team-lead stuck sessions in tmux/iTerm2
increment: 0528
status: completed
completed_acs: 8
total_acs: 8
---

# Fix Team-Lead Stuck Sessions in tmux/iTerm2

## Problem Statement

The `/sw:team-lead` skill gets stuck after one agent completes its work when running in iTerm2 + tmux. The orchestrator freezes and remaining agents make no further progress, requiring a manual restart.

## Root Causes

1. **Blocking PLAN_READY/PLAN_APPROVED handshake** — Agents send PLAN_READY and block indefinitely waiting for PLAN_APPROVED. When 3-5 Phase 2 agents spawn simultaneously, they all block and team-lead must review each sequentially.
2. **Per-agent closure during active phase** — When first agent signals COMPLETION, team-lead loads 4+ skill definitions (grill, judge-llm, sync-docs, qa) for closure while other agents are still running and waiting for responses.
3. **Context bloat from full plan file reads** — Team-lead reads every agent's full spec.md + plan.md + tasks.md (~500 lines each), consuming orchestrator context.
4. **No proactive stuck detection** — Only heuristic "hasn't messaged" detection with manual STATUS_CHECK.

## User Stories

### US-001: Async Plan Notification

As a developer using team-lead, I want agents to proceed to implementation without waiting for plan approval, so that sessions don't freeze at the plan review step.

- [x] **AC-US1-01**: Agents send PLAN_READY as a notification and immediately proceed to implementation (no blocking wait)
- [x] **AC-US1-02**: Team-lead reviews plans asynchronously using structured summaries, not full file reads
- [x] **AC-US1-03**: Team-lead sends PLAN_CORRECTION only when a plan has issues; agents handle mid-implementation corrections
- [x] **AC-US1-04**: If agent ignores PLAN_CORRECTION, team-lead sends shutdown_request and reports to user

### US-002: Batch Closure After All Agents Complete

As a developer, I want all closure (grill/done) to happen after ALL agents complete, so that the team-lead stays responsive during the active implementation phase.

- [x] **AC-US2-01**: Team-lead does NOT run /sw:grill or /sw:done until ALL agents have signaled COMPLETION
- [x] **AC-US2-02**: During active phase, team-lead only handles messages, stuck detection, and blocking issues

### US-003: Task-Level Heartbeat Protocol

As a developer, I want agents to send heartbeat STATUS messages, so that the team-lead can proactively detect stuck agents.

- [x] **AC-US3-01**: Agents send `STATUS: T-{N}/{total} complete` after each task completion during auto-mode
- [x] **AC-US3-02**: Team-lead tracks last STATUS per agent and declares stuck after 2 consecutive turns with no STATUS from an expected agent

## Out of Scope

- Changes to the `specweave team` CLI command itself
- Changes to Claude Code's native Agent Teams infrastructure
- Changes to /sw:auto, /sw:do, /sw:done, or /sw:grill skills
