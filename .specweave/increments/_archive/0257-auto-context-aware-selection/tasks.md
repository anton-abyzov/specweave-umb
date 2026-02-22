# Tasks: Context-Aware Auto Mode: Intent-Based Increment Selection

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)
- TDD markers: `[RED]` write failing test, `[GREEN]` make it pass, `[REFACTOR]` clean up

## Phase 1: Port existing work to source repo

### US-001 / US-002: Port scoring + userGoal from installed plugin to source

#### T-001: Port score-increment.sh to source repo
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-06 | **Status**: [x] completed

**Description**: Copy `score-increment.sh` from installed plugin to source repo. Verify identical content.

**Files**:
- From: `~/.claude/commands/sw/hooks/lib/score-increment.sh`
- To: `repositories/anton-abyzov/specweave/plugins/specweave/hooks/lib/score-increment.sh`

**Dependencies**: None

---

#### T-002: Port setup-auto.sh scoring + userGoal changes to source
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-06 | **Status**: [x] completed

**Description**: Replace blind first-match loop (source lines 252-267) with `select_best_increment()` from installed version. Add userGoal wiring block. Verify scoring script path resolves correctly.

**Files**:
- Source (old): `repositories/anton-abyzov/specweave/plugins/specweave/scripts/setup-auto.sh`
- Reference (new): `~/.claude/commands/sw/scripts/setup-auto.sh`

**Dependencies**: T-001

---

#### T-003: Port test files to source repo
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-06, AC-US2-06 | **Status**: [x] completed

**Description**: Copy 4 test files from installed plugin to source repo. Adjust paths if needed.

**Files**:
- `~/.claude/commands/sw/scripts/tests/test-setup-auto-usergoal.sh` → source
- `~/.claude/commands/sw/scripts/tests/test-setup-auto-selection.sh` → source
- `~/.claude/commands/sw/hooks/tests/test-stop-auto-enriched.sh` → source
- `~/.claude/commands/sw/hooks/tests/test-auto-context-integration.sh` → source

**Dependencies**: None

## Phase 2: Enrich stop hook feedback (THE CORE FIX)

### US-003 / US-004: Semantic Stop Hook Feedback + Multi-Increment Prioritization

#### T-004: Modify stop-auto-v5.sh — enriched block message
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Modify `stop-auto-v5.sh` section 7 (scan) and section 9 (block message) to include:
1. Read `userGoal` from auto-mode.json
2. For each incomplete increment: extract next pending task title, done/total progress
3. Score increments against userGoal (if set) using score-increment.sh
4. Build enriched BMSG with: Goal line, per-increment progress + next task, explicit `Continue: /sw:do <id>` guidance
5. All ops must stay within 100ms budget

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/hooks/stop-auto-v5.sh`

**Dependencies**: T-001

---

#### T-005: Write/update tests for enriched stop hook
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05, AC-US4-01, AC-US4-03 | **Status**: [x] completed

**Description**: Update test file to verify enriched block message content: next task title, userGoal, progress fraction, increment ordering, explicit `/sw:do <id>` guidance.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/hooks/tests/test-stop-auto-enriched.sh`

**Dependencies**: T-004

## Phase 3: `/sw:do` auto-mode awareness (THE MISSING PIECE)

### US-005: `/sw:do` Auto-Mode Context Override

#### T-006: Modify /sw:do SKILL.md — respect auto-mode context
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed

**Description**: Add Step 1.5 "Auto-Mode Context Override" between Step 1 (auto-selection) and Step 2 (load context). When running inside active auto session: read `incrementIds` from `auto-mode.json`, use first entry. If stop hook mentions specific ID, use that. Explicit ID always takes priority. Skip filesystem scanning when auto-mode provides ID.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/skills/do/SKILL.md`

**Dependencies**: None

## Phase 4: SKILL.md schema fix + auto.ts

### US-002: Wire Up userGoal

#### T-007: Fix /sw:auto SKILL.md schema
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed

**Description**: Change `"userGoal": "optional"` → `"userGoal": null`. Add instruction: "Set `userGoal` to the user's stated intent from conversation context. If no clear intent, set to null."

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/skills/auto/SKILL.md`

**Dependencies**: None

---

#### T-008: Wire userGoal into auto.ts CLI path
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed

**Description**: Add `userGoal` field (default `null`) to the session marker JSON created by `printStartMessage()`. This is a secondary entry point — `setup-auto.sh` is primary.

**File**: `repositories/anton-abyzov/specweave/src/cli/commands/auto.ts`

**Dependencies**: None

## Phase 5: Verification

#### T-009: Run all tests and verify integration
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed

**Description**: Run all test files from Phase 1 against the source repo versions. Verify stop hook timing stays under 500ms. Manual spot-check of enriched block message format.

**Dependencies**: T-001, T-002, T-003, T-004, T-005
