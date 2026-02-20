# Tasks: Context-Aware Auto Mode: Intent-Based Increment Selection

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)
- TDD markers: `[RED]` write failing test, `[GREEN]` make it pass, `[REFACTOR]` clean up

## Phase 1: Foundation -- Scoring Function + userGoal Wiring

### US-001: Intent-Based Increment Selection / US-002: Wire Up userGoal

#### T-001: [RED] Write tests for score_increment function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Test script that sources `score-increment.sh` and validates scoring against known inputs.

**Test Plan**: `~/.claude/commands/sw/hooks/lib/tests/score-increment.test.sh` (9 tests, all pass)

**Dependencies**: None

---

#### T-002: [GREEN] Implement score_increment function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Created `~/.claude/commands/sw/hooks/lib/score-increment.sh`. Keyword overlap scoring (0-100) using increment dir name + metadata title + spec.md overview + task titles as corpus.

**Test Plan**: Run T-001 tests — 9/9 pass.

**Dependencies**: T-001

---

#### T-003: [RED] Write tests for userGoal wiring in setup-auto.sh
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [x] completed

**Description**: Tests verifying `setup-auto.sh` writes `userGoal` to `auto-mode.json`.

**Test Plan**: `~/.claude/commands/sw/scripts/tests/test-setup-auto-usergoal.sh` (7 tests, all pass)

**Dependencies**: None

---

#### T-004: [GREEN] Wire userGoal into setup-auto.sh session marker
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [x] completed

**Description**: Modified `setup-auto.sh` to write `userGoal` from `$PROMPT` to `auto-mode.json` BEFORE the session start banner (lines 515-527). Updates existing file or creates stub.

**Test Plan**: Run T-003 tests — 7/7 pass.

**Dependencies**: T-003

---

#### T-005: Fix SKILL.md userGoal schema example
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed

**Description**: Changed `~/.claude/commands/sw/auto/SKILL.md` line 78: `"userGoal": "optional"` → `"userGoal": null`.

**Test Plan**: Manual verification — confirmed.

**Dependencies**: None

## Phase 2: Smart Selection -- setup-auto.sh

### US-001: Intent-Based Increment Selection

#### T-006: [RED] Write tests for scored increment selection
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Description**: Tests verifying scored selection picks the correct increment based on prompt.

**Test Plan**: `~/.claude/commands/sw/scripts/tests/test-setup-auto-selection.sh` (6 tests, all pass)

**Dependencies**: T-002

---

#### T-007: [GREEN] Implement scored selection in setup-auto.sh
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Description**: Replaced blind first-match with `select_best_increment()` function. With prompt: scores via score-increment.sh, picks best. Without prompt: picks most-recently-modified. Logs selection to auto-sessions.log.

**Test Plan**: Run T-006 tests — 6/6 pass.

**Dependencies**: T-002, T-006

---

#### T-008: [REFACTOR] Clean up setup-auto.sh selection logic
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Selection logic extracted into `select_best_increment()` function with header comment. Old first-match code removed. All paths log selection reason to auto-sessions.log.

**Test Plan**: Re-run T-006 tests — no regressions.

**Dependencies**: T-007

## Phase 3: Stop Hook Enrichment -- stop-auto-v5.sh

### US-003: Semantic Stop Hook Feedback / US-004: Multi-Increment Prioritization

#### T-009: [RED] Write tests for enriched stop hook feedback
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Tests for stop hook helper functions.

**Test Plan**: `~/.claude/commands/sw/hooks/tests/test-stop-auto-enriched.sh` (10 tests, all pass)

**Dependencies**: T-002

---

#### T-010: [GREEN] Implement enriched feedback in stop-auto-v5.sh
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Added `count_completed_tasks()` and `get_next_task_title()` helpers to `stop-auto-v5.sh`. Block message now includes: next pending task title, done/total progress fraction, Goal line (when userGoal set), increments ordered by relevance score (or pending count when no goal).

**Test Plan**: Run T-009 tests — 10/10 pass.

**Dependencies**: T-002, T-009

---

#### T-011: [REFACTOR] Extract stop hook enrichment into helper functions
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed

**Description**: Helper functions `count_completed_tasks()`, `get_next_task_title()` added. Enrichment uses existing `_get_duration_ms()` timing infrastructure. Block JSON `systemMessage` properly escaped via jq.

**Test Plan**: Run full test suite (T-009) — all pass.

**Dependencies**: T-010

## Phase 4: Integration Verification

#### T-012: Integration test -- full auto session with scored selection
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01 | **Status**: [x] completed

**Description**: End-to-end integration test with two mock increments verifying scored selection, userGoal wiring, and stop hook enrichment.

**Test Plan**: `~/.claude/commands/sw/hooks/tests/test-auto-context-integration.sh` (6 tests, all pass)

**Dependencies**: T-007, T-010
