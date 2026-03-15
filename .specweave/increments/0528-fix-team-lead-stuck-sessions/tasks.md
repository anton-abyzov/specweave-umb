---
title: Fix team-lead stuck sessions — Tasks
increment: "0528"
total_tasks: 9
completed_tasks: 9
---

# Tasks

### T-001: Edit SKILL.md §3b — Replace blocking plan handshake with async notify+correct
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given SKILL.md §3b → When read → Then no "WAIT for PLAN_APPROVED" instruction exists; PLAN_CORRECTION protocol documented; structured summary format specified

### T-002: Edit SKILL.md §6 — Add STATUS and PLAN_CORRECTION message types
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given SKILL.md §6 message types table → When read → Then STATUS: and PLAN_CORRECTION: rows exist with correct sender/receiver

### T-003: Edit SKILL.md §7 — Remove PLAN_READY/PLAN_APPROVED references in spawning
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given SKILL.md §7 → When read → Then no "PLAN_READY/PLAN_APPROVED protocol" reference exists

### T-004: Edit SKILL.md §8 — Reinforce batch closure with explicit active-phase rules
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given SKILL.md §8 → When read → Then explicit rule states closure only after ALL completions; active-phase behavior defined

### T-005: Edit SKILL.md §8b — Replace STATUS_CHECK with heartbeat-based stuck detection
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given SKILL.md §8b → When read → Then heartbeat tracking described; stuck = 2 turns no STATUS; loop detection = 3+ same task number

### T-006: Edit SKILL.md §9 — Update workflow summary to reflect async model
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given SKILL.md §9 workflow diagram → When read → Then no "review & approve" in phase flow; closure phase clearly after all completions

### T-007: Edit backend.md — Async plan, heartbeat, structured PLAN_READY
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given agents/backend.md → When read → Then no "WAIT for PLAN_APPROVED"; heartbeat STATUS instruction present; PLAN_READY includes structured summary

### T-008: Edit remaining 4 agent templates (frontend, database, testing, security)
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given all 4 agent templates → When read → Then same changes as T-007 applied consistently

### T-009: Sync plugin cache via specweave refresh-plugins
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: all | **Status**: [x] completed
**Test Plan**: Given source files modified → When `specweave refresh-plugins` runs → Then cached SKILL.md matches source
