---
increment: 0257-auto-context-aware-selection
title: "Context-Aware Auto Mode: Intent-Based Increment Selection"
type: feature
priority: P1
status: planned
created: 2026-02-20
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Context-Aware Auto Mode: Intent-Based Increment Selection

## Overview

Auto mode currently selects increments via blind filesystem-order first-match. When a user says `/sw:auto` in a conversation about a specific feature, the system picks whichever active increment happens to appear first in the directory listing -- not the one contextually relevant to the conversation. This increment fixes three concrete problems:

1. **Blind first-match selection** -- `setup-auto.sh` grabs the first `active`/`in-progress` increment found by glob order, ignoring conversation context.
2. **`userGoal` is dead code** -- the `auto-mode.json` schema defines `userGoal` but nothing populates it and the stop hook never reads it.
3. **Stop hook feedback is purely mechanical** -- `stop-auto-v5.sh` outputs raw task/AC counts with no semantic context about what work relates to the user's stated intent.
4. **`/sw:do` ignores auto-mode context** -- it reads `auto-mode.json` only to skip the strategy check, never reading `incrementIds` or `userGoal`, so even with perfect stop hook feedback it picks the wrong increment.

## User Stories

### US-001: Intent-Based Increment Selection (P1)
**Project**: specweave

**As a** developer running `/sw:auto` with multiple active increments
**I want** auto mode to select the increment that matches my conversation context
**So that** I don't waste turns working on the wrong increment

**Acceptance Criteria**:
- [x] **AC-US1-01**: When user provides free-text prompt to `/sw:auto`, the system scores all active/in-progress increments against the prompt using keyword overlap and selects the best match
- [x] **AC-US1-02**: When user provides an explicit increment ID, that ID is used directly (no scoring)
- [x] **AC-US1-03**: When only one active increment exists, it is selected without scoring (fast path)
- [x] **AC-US1-04**: When no prompt is given and multiple increments are active, the system falls back to most-recent-activity ordering instead of filesystem order
- [x] **AC-US1-05**: The selected increment(s) and the reason for selection are logged to `.specweave/logs/auto-sessions.log`
- [x] **AC-US1-06**: All scoring and selection changes exist in the source repo (not just installed plugin)

---

### US-002: Wire Up userGoal in Auto Session (P1)
**Project**: specweave

**As a** developer starting an auto session
**I want** my goal/prompt to be persisted in the auto-mode.json session marker
**So that** the stop hook and other tools can reference why the session was started

**Acceptance Criteria**:
- [x] **AC-US2-01**: `setup-auto.sh` writes `userGoal` field to `auto-mode.json` from the user's free-text prompt or `--prompt` argument
- [x] **AC-US2-02**: When no prompt is provided, `userGoal` is set to `null` (not "optional")
- [x] **AC-US2-03**: The `/sw:auto` SKILL.md schema example shows `userGoal` as `null` instead of `"optional"`, with LLM instructions to populate from conversation context
- [x] **AC-US2-04**: `auto-mode.json` `userGoal` field is populated before the session start banner is displayed
- [x] **AC-US2-05**: `auto.ts` CLI path also sets `userGoal` in the session marker (defaults to `null`)
- [x] **AC-US2-06**: All userGoal wiring exists in the source repo (not just installed plugin)

---

### US-003: Semantic Stop Hook Feedback (P2)
**Project**: specweave

**As a** developer in an active auto session
**I want** stop hook feedback to include semantic context about remaining work
**So that** I can understand at a glance what needs to happen next without reading task files

**Acceptance Criteria**:
- [x] **AC-US3-01**: Stop hook block message includes the title of the next pending task (first `[ ]` in tasks.md) for each incomplete increment
- [x] **AC-US3-02**: When `userGoal` is set in auto-mode.json, the stop hook block message includes it as a "Goal:" line
- [x] **AC-US3-03**: Stop hook block message includes a progress summary per increment (e.g., "7/12 tasks")
- [x] **AC-US3-04**: The enriched feedback does not increase stop hook execution time by more than 100ms (measured via existing timing infrastructure)
- [x] **AC-US3-05**: Stop hook block message ends with explicit increment guidance (e.g., "Continue: /sw:do 0252")

---

### US-004: Multi-Increment Intent Prioritization (P2)
**Project**: specweave

**As a** developer with multiple active increments in auto mode
**I want** the stop hook to prioritize feedback for the increment most relevant to my goal
**So that** the model focuses on the right work first

**Acceptance Criteria**:
- [x] **AC-US4-01**: When multiple increments have pending work AND `userGoal` is set, the block message orders increments by relevance to userGoal (keyword match scoring)
- [x] **AC-US4-02**: The increment listed first in the block message is the one recommended for `/sw:do`
- [x] **AC-US4-03**: When `userGoal` is null, increments are ordered by pending task count (most work first)

---

### US-005: `/sw:do` Auto-Mode Context Override (P1)
**Project**: specweave

**As a** developer in an active auto session
**I want** `/sw:do` to respect the stop hook's increment recommendation
**So that** the execution loop stays focused on the contextually correct increment

**Acceptance Criteria**:
- [x] **AC-US5-01**: When running inside an active auto session and no explicit ID is passed, `/sw:do` reads `incrementIds` from `auto-mode.json` and uses the first entry
- [x] **AC-US5-02**: When the stop hook feedback mentions a specific increment ID (e.g., "Continue: /sw:do 0252"), `/sw:do` uses that ID
- [x] **AC-US5-03**: When an explicit ID is passed to `/sw:do`, it takes priority over auto-mode context
- [x] **AC-US5-04**: `/sw:do` Step 1 filesystem scanning is skipped when auto-mode context provides an increment ID

## Functional Requirements

### FR-001: Increment Scoring Function
A pure function that scores an increment against a text query using keyword overlap between the query and the increment's title, spec.md overview, and tasks.md task titles. Returns a numeric score 0-100.

### FR-002: Session Goal Persistence
`setup-auto.sh` captures the user's free-text prompt (already parsed as `$PROMPT`) and writes it to `auto-mode.json` as `userGoal`. The `/sw:auto` SKILL.md instructs the LLM to populate `userGoal` from conversation context when calling setup.

### FR-003: Stop Hook Enrichment
`stop-auto-v5.sh` reads `userGoal` and the next pending task title from tasks.md. These are included in the `systemMessage` JSON field of the block response, along with explicit increment guidance.

### FR-004: `/sw:do` Auto-Mode Integration
`/sw:do` SKILL.md adds a Step 1.5 that reads `auto-mode.json` for `incrementIds` when running inside auto mode, overriding the default filesystem scanning.

## Success Criteria

- Auto mode selects the contextually correct increment in >90% of multi-increment scenarios
- Stop hook execution time remains under 500ms (current baseline ~200ms)
- Zero regressions in single-increment auto mode behavior

## Out of Scope

- LLM-based semantic matching (too expensive for a stop hook; keyword overlap only)
- Changes to `/sw:team-lead` increment selection (separate concern)
- Persistent learning from past selections

## Dependencies

- Existing `setup-auto.sh` (scripts directory)
- Existing `stop-auto-v5.sh` (hooks directory)
- Existing `auto-mode.json` schema (state directory)
- `/sw:auto` SKILL.md (auto directory)
