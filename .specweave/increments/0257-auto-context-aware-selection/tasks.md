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
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started

**Description**: Create a test script that sources `score-increment.sh` and validates the scoring function against known inputs. Tests run via direct bash execution (no bats dependency needed).

**Implementation Details**:
- Create `~/.claude/commands/sw/hooks/lib/tests/test-score-increment.sh`
- Test cases:
  - Exact title match scores > 80
  - Partial keyword match scores 30-80
  - No match scores 0
  - Empty query scores 0
  - Single-word query against multi-word corpus
- Mock increment directories with metadata.json, spec.md, tasks.md
- Each test: set up temp dir, call function, assert score range, clean up

**Test Plan**:
- **File**: `~/.claude/commands/sw/hooks/lib/tests/test-score-increment.sh`
- **Tests**:
  - **TC-001**: Exact title match returns score >= 80
    - Given an increment with title "user-authentication"
    - When scored against query "user authentication"
    - Then score >= 80
  - **TC-002**: No keyword overlap returns 0
    - Given an increment with title "database-migration"
    - When scored against query "frontend styling"
    - Then score == 0
  - **TC-003**: Partial match returns intermediate score
    - Given an increment about "api rate limiting"
    - When scored against query "api throttling rate"
    - Then 30 <= score <= 80
  - **TC-004**: Empty query returns 0
    - Given any increment
    - When scored against empty string
    - Then score == 0

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-002: [GREEN] Implement score_increment function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started

**Description**: Create `score-increment.sh` with the `score_increment()` function. Pure function: takes increment dir path and query string, outputs numeric score 0-100.

**Implementation Details**:
- Create `~/.claude/commands/sw/hooks/lib/score-increment.sh`
- Function signature: `score_increment <increment_dir> <query>`
- Algorithm:
  1. Tokenize query: `echo "$query" | tr '[:upper:]' '[:lower:]' | tr -cs '[:alnum:]' '\n' | sort -u`
  2. Build corpus from: `jq -r '.title // .id' metadata.json` + first 50 lines of spec.md + task titles from tasks.md
  3. For each query token, `grep -qiw` against corpus
  4. Score = `(matches / total_tokens) * 100`
- Guard: empty query -> echo 0; missing dir -> echo 0
- Sourceable: `source score-increment.sh` loads functions only

**Test Plan**: Run T-001 tests, all TC-001 through TC-004 must pass.

**Dependencies**: T-001
**Status**: [ ] Not Started

---

#### T-003: [RED] Write tests for userGoal wiring in setup-auto.sh
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [ ] not started

**Description**: Write tests that verify `setup-auto.sh` writes `userGoal` to `auto-mode.json`.

**Implementation Details**:
- Create `~/.claude/commands/sw/scripts/tests/test-setup-auto-usergoal.sh`
- Test cases:
  - With `--prompt "fix auth bug"`: auto-mode.json has `userGoal: "fix auth bug"`
  - Without prompt: auto-mode.json has `userGoal: null`
  - With positional free-text: auto-mode.json captures it as userGoal
- Use a temp `.specweave/` directory with a dummy increment

**Test Plan**:
- **File**: `~/.claude/commands/sw/scripts/tests/test-setup-auto-usergoal.sh`
- **Tests**:
  - **TC-005**: Prompt flag sets userGoal
    - Given `--prompt "fix auth bug"` argument
    - When setup-auto.sh runs
    - Then auto-mode.json contains `"userGoal": "fix auth bug"`
  - **TC-006**: No prompt sets userGoal to null
    - Given no prompt argument with an active increment
    - When setup-auto.sh runs
    - Then auto-mode.json contains `"userGoal": null`

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-004: [GREEN] Wire userGoal into setup-auto.sh session marker
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [ ] not started

**Description**: Modify `setup-auto.sh` to include `userGoal` in the session JSON output.

**Implementation Details**:
- In the `SESSION_JSON` heredoc (~line 426), add `"userGoal"` field:
  - If `$PROMPT` is non-empty: `"userGoal": "$PROMPT"`
  - If `$PROMPT` is empty: `"userGoal": null`
- Place it after `"currentIncrement"` and before `"completedIncrements"`
- Ensure proper JSON escaping for prompt text (use jq for safe encoding)

**Test Plan**: Run T-003 tests, TC-005 and TC-006 must pass.

**Dependencies**: T-003
**Status**: [ ] Not Started

---

#### T-005: Fix SKILL.md userGoal schema example
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] not started

**Description**: Update `/sw:auto` SKILL.md to show `"userGoal": null` instead of `"optional"` and add instruction for LLM to populate it.

**Implementation Details**:
- Edit `~/.claude/commands/sw/auto/SKILL.md`
- Change line 78: `"userGoal": "optional"` -> `"userGoal": null`
- Add note after the JSON block: "Set `userGoal` to the user's stated intent from conversation context. If the user said 'fix the auth bug', set it to 'fix the auth bug'. If no clear intent, set to null."

**Test Plan**: Manual verification -- read the file and confirm the change.

**Dependencies**: None
**Status**: [ ] Not Started

## Phase 2: Smart Selection -- setup-auto.sh

### US-001: Intent-Based Increment Selection

#### T-006: [RED] Write tests for scored increment selection
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [ ] not started

**Description**: Write tests verifying that `setup-auto.sh` selects the correct increment based on prompt scoring.

**Implementation Details**:
- Create `~/.claude/commands/sw/scripts/tests/test-setup-auto-selection.sh`
- Test cases:
  - Two active increments, prompt matches second one -> second is selected as currentIncrement
  - One active increment, no prompt -> that one is selected (fast path)
  - Two active increments, no prompt -> most recent lastActivity is selected first
  - Explicit ID provided -> that ID used regardless of prompt

**Test Plan**:
- **File**: `~/.claude/commands/sw/scripts/tests/test-setup-auto-selection.sh`
- **Tests**:
  - **TC-007**: Prompt-based selection picks best match
    - Given increments "0100-user-auth" and "0101-deploy-pipeline"
    - When setup-auto.sh runs with prompt "authentication login"
    - Then currentIncrement is "0100-user-auth"
  - **TC-008**: Single increment fast path
    - Given only "0100-user-auth" is active
    - When setup-auto.sh runs with no prompt
    - Then currentIncrement is "0100-user-auth"
  - **TC-009**: No prompt falls back to lastActivity ordering
    - Given "0100-user-auth" (lastActivity: yesterday) and "0101-deploy-pipeline" (lastActivity: today)
    - When setup-auto.sh runs with no prompt
    - Then currentIncrement is "0101-deploy-pipeline"

**Dependencies**: T-002
**Status**: [ ] Not Started

---

#### T-007: [GREEN] Implement scored selection in setup-auto.sh
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] not started

**Description**: Replace the blind first-match loop in `setup-auto.sh` (lines 253-267) with scored selection.

**Implementation Details**:
- Source `score-increment.sh` at top of script
- When `${#INCREMENT_IDS[@]} -eq 0` (no explicit IDs):
  1. Collect all active/in-progress increments into an array
  2. If only one -> use it directly (fast path, AC-US1-03)
  3. If `$PROMPT` is non-empty:
     - Score each increment via `score_increment`
     - Sort by score descending
     - Use highest-scoring as `currentIncrement`, all go into `incrementQueue`
  4. If `$PROMPT` is empty:
     - Sort by `lastActivity` from metadata.json (most recent first)
     - Use most recent as `currentIncrement`
  5. Log selection reason to `$LOGS_DIR/auto-sessions.log` (AC-US1-05)
- When explicit IDs are provided, skip scoring entirely (AC-US1-02)

**Test Plan**: Run T-006 tests, TC-007 through TC-009 must pass.

**Dependencies**: T-002, T-006
**Status**: [ ] Not Started

---

#### T-008: [REFACTOR] Clean up setup-auto.sh selection logic
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started

**Description**: Extract the selection logic into a well-named function, add comments, ensure the old first-match code is fully removed.

**Implementation Details**:
- Extract `select_best_increment()` function
- Add header comment explaining selection strategy
- Remove dead code from the old first-match loop
- Ensure all paths log their selection reason

**Test Plan**: Re-run T-006 tests to confirm no regressions.

**Dependencies**: T-007
**Status**: [ ] Not Started

## Phase 3: Stop Hook Enrichment -- stop-auto-v5.sh

### US-003: Semantic Stop Hook Feedback / US-004: Multi-Increment Prioritization

#### T-009: [RED] Write tests for enriched stop hook feedback
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [ ] not started

**Description**: Write tests for the stop hook's enriched block message.

**Implementation Details**:
- Create `~/.claude/commands/sw/hooks/tests/test-stop-auto-enriched.sh`
- Source `stop-auto-v5.sh` functions (set `__STOP_AUTO_V5_SOURCED=1`)
- Test cases:
  - Block message includes next pending task title
  - Block message includes userGoal when set
  - Block message includes progress fraction "N/M tasks complete"
  - With userGoal set, increments are ordered by relevance
  - Without userGoal, increments are ordered by pending task count

**Test Plan**:
- **File**: `~/.claude/commands/sw/hooks/tests/test-stop-auto-enriched.sh`
- **Tests**:
  - **TC-010**: Block message includes next task title
    - Given an increment with tasks "[ ] Implement login" as first pending
    - When stop hook generates block message
    - Then message contains "Next: Implement login" or similar
  - **TC-011**: Block message includes userGoal
    - Given auto-mode.json has userGoal "fix authentication"
    - When stop hook generates block message
    - Then message contains "Goal: fix authentication"
  - **TC-012**: Block message includes progress fraction
    - Given tasks.md has 5 `[x]` and 3 `[ ]` tasks
    - When stop hook generates block message
    - Then message contains "5/8 tasks"
  - **TC-013**: With userGoal, increments ranked by relevance
    - Given two increments and userGoal matches second
    - When stop hook generates block message
    - Then second increment appears first in the list
  - **TC-014**: Without userGoal, increments ranked by pending count
    - Given two increments: A has 2 pending, B has 5 pending
    - When stop hook generates block message
    - Then B appears first

**Dependencies**: T-002
**Status**: [ ] Not Started

---

#### T-010: [GREEN] Implement enriched feedback in stop-auto-v5.sh
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [ ] not started

**Description**: Modify `stop-auto-v5.sh` to include semantic context in block messages.

**Implementation Details**:
- Source `score-increment.sh` (relative path from hooks dir)
- After section 7 (scan active increments), add:
  1. Read `userGoal` from `$SESSION`: `USER_GOAL=$(jq -r '.userGoal // ""' "$SESSION")`
  2. For each incomplete increment, extract next pending task title:
     `NEXT_TASK=$(grep -m1 '\[ \]' "$d/tasks.md" | sed 's/.*\] //' | head -c 80)`
  3. Count completed tasks: `DONE=$(grep -c '\[x\]' "$d/tasks.md")`, `TOTAL=$((DONE + p))`
  4. Store in ILIST as: `id|pending|acs|next_task|done|total`
- If `USER_GOAL` is non-empty and multiple increments:
  - Score each via `score_increment "$d" "$USER_GOAL"`
  - Sort ENTRIES by score descending before building DETAILS
- Build enriched BMSG:
  - If USER_GOAL: `"Goal: $USER_GOAL\n"`
  - For each entry: `"  - ${eid}: ${done}/${total} tasks (${ep} remaining) | Next: ${next_task}"`
  - Footer: `"Turn $TURN/$MAX_TURNS | Continue: /sw:do | Complete: /sw:done"`
- Performance: all operations are grep/jq on local files, well within 100ms budget

**Test Plan**: Run T-009 tests, TC-010 through TC-014 must pass.

**Dependencies**: T-002, T-009
**Status**: [ ] Not Started

---

#### T-011: [REFACTOR] Extract stop hook enrichment into helper functions
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] not started

**Description**: Clean up the enrichment code in stop-auto-v5.sh. Extract reusable functions, add timing assertions.

**Implementation Details**:
- Extract `get_next_task_title()` and `build_enriched_message()` as functions
- Add timing check: if enrichment takes >100ms, log a warning
- Ensure the block JSON `systemMessage` field is properly escaped
- Verify total hook time stays under 500ms via `_get_duration_ms()`

**Test Plan**: Run full test suite (T-009), verify timing logged and under budget.

**Dependencies**: T-010
**Status**: [ ] Not Started

## Phase 4: Integration Verification

#### T-012: Integration test -- full auto session with scored selection
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01 | **Status**: [ ] not started

**Description**: End-to-end test that creates a mock `.specweave/` project with two active increments, runs `setup-auto.sh` with a prompt, then runs `stop-auto-v5.sh` and verifies the full flow.

**Implementation Details**:
- Create `~/.claude/commands/sw/hooks/tests/test-auto-context-integration.sh`
- Setup: create temp dir with `.specweave/increments/0100-auth/` and `0101-deploy/`, each with metadata.json, spec.md, tasks.md
- Run `setup-auto.sh --prompt "fix authentication"` with `PROJECT_ROOT` set to temp dir
- Verify `auto-mode.json` has `userGoal: "fix authentication"` and `currentIncrement: "0100-auth"`
- Run `stop-auto-v5.sh` (source it and call main logic)
- Verify block message mentions "Goal: fix authentication" and lists auth increment first
- Clean up temp dir

**Test Plan**:
- **File**: `~/.claude/commands/sw/hooks/tests/test-auto-context-integration.sh`
- **Tests**:
  - **TC-015**: Full flow -- scored selection + enriched feedback
    - Given two increments and prompt "fix authentication"
    - When setup and stop hook both run
    - Then correct increment selected AND enriched feedback shown

**Dependencies**: T-007, T-010
**Status**: [ ] Not Started
