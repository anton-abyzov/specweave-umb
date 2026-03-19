---
increment: 0627-team-lead-agent-teams-api
title: Enhance team-lead to leverage Claude Code Agent Teams API
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Enhance team-lead to leverage Claude Code Agent Teams API

## Overview

The sw:team-lead skill uses custom protocols (STATUS heartbeat, PLAN_READY async, Phase 3 tmux cleanup bash script) where Claude Code v2.1.32+ now provides native Agent Teams features. This increment adopts 5 native features: idle agent querying, teammateMode for tmux/iTerm2, broadcast messaging, direct user-to-teammate interaction documentation, and TeammateIdle hook integration.

## User Stories

### US-001: Idle Agent Querying (P1)
**Project**: vskill

**As a** team-lead orchestrator
**I want** agents to stay idle after COMPLETION with full context available
**So that** I can query them for cross-agent verification before authorizing shutdown

**Acceptance Criteria**:
- [x] **AC-US1-01**: SKILL.md Section 6 defines QUERY_READY, QUERY, and SHUTDOWN_AUTHORIZED message types
- [x] **AC-US1-02**: SKILL.md Section 8b excludes QUERY_READY agents from stuck detection
- [x] **AC-US1-03**: SKILL.md Section 9 workflow includes Step 6.5 idle query phase with task-count guard (<12)
- [x] **AC-US1-04**: All 5 implementation agent templates (backend, frontend, database, testing, security) include QUERY_READY idle phase after COMPLETION block
- [x] **AC-US1-05**: SKILL.md Section 9 Step 9 Phase 1 uses SHUTDOWN_AUTHORIZED instead of shutdown_request for QUERY_READY agents

---

### US-002: tmux/iTerm2 Split-Pane Mode (P1)
**Project**: vskill

**As a** developer using team-lead
**I want** agents to run in tmux/iTerm2 split panes automatically
**So that** I can see all agent activity visually and click into panes to interact

**Acceptance Criteria**:
- [x] **AC-US2-01**: SKILL.md has new Section 0.7 documenting teammateMode settings (auto, tmux, in-process) with iTerm2 setup instructions
- [x] **AC-US2-02**: SKILL.md Section 9 Step 9 Phase 3 is demoted from MANDATORY to FALLBACK with conditional guidance

---

### US-003: Broadcast Messaging (P2)
**Project**: vskill

**As a** team-lead orchestrator
**I want** to send messages to all agents simultaneously via broadcast
**So that** shutdown signals and global announcements don't require N individual messages

**Acceptance Criteria**:
- [x] **AC-US3-01**: SKILL.md Section 6 includes broadcast in the message types table with usage guidelines
- [x] **AC-US3-02**: SKILL.md Section 9 Step 9 Phase 1 uses broadcast for shutdown instead of per-agent loop
- [x] **AC-US3-03**: SKILL.md Section 3 mentions broadcast for CONTRACT_READY announcements to downstream agents

---

### US-004: Direct User-to-Teammate Interaction (P2)
**Project**: vskill

**As a** developer using team-lead
**I want** documentation on how to interact with agents directly
**So that** I can unblock stuck agents or ask questions without routing through team-lead

**Acceptance Criteria**:
- [x] **AC-US4-01**: SKILL.md has new Section 6b documenting Shift+Down (in-process) and click-into-pane (tmux) interaction
- [x] **AC-US4-02**: Section 6b documents the coordination hazard and echo-to-team-lead mitigation

---

### US-005: TeammateIdle Quality Hook (P2)
**Project**: vskill

**As a** team-lead orchestrator
**I want** an optional TeammateIdle hook that enforces quality gates before agents go idle
**So that** agents fix quality issues themselves while they still have full context

**Acceptance Criteria**:
- [x] **AC-US5-01**: SKILL.md has new Section 8c documenting TeammateIdle hook configuration in settings.json
- [x] **AC-US5-02**: Section 8c documents the circuit breaker requirement (max 3 re-engagements)
- [x] **AC-US5-03**: Section 8c explicitly states this is supplemental to STATUS heartbeat, not a replacement

## Out of Scope

- **TaskCompleted hook**: STATUS heartbeat already covers task-level quality; hook may serialize all agents
- **Self-claiming shared task list**: Breaks contract-first ordering; explicit assignment is working
- **Formal plan approval**: Reintroduces trust-prompt deadlock that bypassPermissions was designed to solve

## Dependencies

- Claude Code v2.1.32+ with Agent Teams experimental flag enabled
- tmux or iTerm2 with it2 CLI for split-pane mode (optional)
