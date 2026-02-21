# Tasks: 0270 — Auto-Close Increments in Auto/Team-Lead Modes

## Phase 1: Stop Hook Change

### T-001: Change stop-auto-v5.sh all-complete path from approve to block
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] pending
**Test**: Given an active auto session with all tasks/ACs complete -> When the stop hook fires -> Then it emits `{"decision":"block"}` with reason code `all_complete_needs_closure` and a systemMessage containing `/sw:done --auto` and the increment ID(s)

**Implementation Details**:
- In `stop-auto-v5.sh` section 9 (line 188), replace `loud_approve` with `block`
- Use reason code `all_complete_needs_closure` (not `work_remaining`)
- Do NOT clean up session state files (remove the `rm -f` on line 189)
- Build a systemMessage listing increment IDs and instructing `/sw:done --auto <id>`
- Read increment IDs from session marker's `incrementIds` field for the message

**Dependencies**: None

---

### T-002: Update stop-auto-v5 integration tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [ ] pending
**Test**: Given the updated stop-auto-v5.sh -> When running the test suite -> Then all tests pass including the new all-complete-blocks-for-closure test

**Implementation Details**:
- Update test "should approve when all increments are completed" to expect `block` instead of `approve`
- Update test "should NOT auto-close increments" to verify `block` with `/sw:done` in systemMessage
- Add new test: "should block with all_complete_needs_closure reason code when all work done"
- Add new test: "should NOT clean up session state on all-complete block"
- Existing quick-exit, staleness, turn-counter, dedup tests remain unchanged

**Dependencies**: T-001

---

## Phase 2: /sw:done --auto Flag

### T-003: Add --auto flag to /sw:done SKILL.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [ ] pending
**Test**: Given the updated done SKILL.md -> When reading it -> Then it documents `--auto` in argument-hint and Options, and Step 4 conditionally skips user confirmation when `--auto` is present

**Implementation Details**:
- Update `argument-hint` from `"<increment-id>"` to `"<increment-id> [--auto]"`
- Add an Options table documenting `--auto`: "Skip user confirmation prompt (for auto/team-lead modes). All quality gates still enforced."
- In Step 4 (Status Validation), add: "If `--auto` flag is present, skip the explicit user confirmation. Proceed directly to closure."
- Clarify that `--auto` does NOT bypass grill, judge-llm, Gate 0, or PM gates

**Dependencies**: None

---

## Phase 3: Auto Skill Closure Loop

### T-004: Add closure step to /sw:auto SKILL.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test**: Given the updated auto SKILL.md -> When reading Step 3 -> Then it contains explicit instructions to run `/sw:done --auto <id>` after all tasks complete, handle success/failure, and clean up session state

**Implementation Details**:
- Amend Step 3 (Execute Tasks) to add a closure substep after item 4 (quality gates):
  - "5. When all tasks are complete: run `/sw:done --auto <id>` for each increment in the session"
  - "6. If /sw:done succeeds: clean up session state (rm auto-mode.json, turn counter, dedup) and output `<!-- auto-complete:DONE -->`"
  - "7. If /sw:done fails (gate failure): report the failure, do NOT clean up session state. The stop hook will block again on next turn."
- Update the "Core Loop" diagram to include `/sw:done` as the final step

**Dependencies**: T-003

---

## Phase 4: Team-Lead Auto-Close

### T-005: Add auto-close step to /sw:team-lead SKILL.md
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03 | **Status**: [ ] pending
**Test**: Given the updated team-lead SKILL.md -> When reading Section 8 -> Then it contains an explicit step to run `/sw:done --auto <id>` in dependency order after quality gates pass

**Implementation Details**:
- In Section 8 (Quality Gates > Orchestrator Quality Gate), after step 4 (grill), add:
  - "5. Run `/sw:done --auto <id>` for each increment in dependency order"
  - "6. If any `/sw:done --auto` fails, report the failure and continue with remaining increments"
- Renumber existing step 5 (team-merge) to step 7

**Dependencies**: T-003

---

### T-006: Update /sw:team-merge to use --auto flag
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending
**Test**: Given the updated team-merge SKILL.md -> When reading Step 4 -> Then it uses `/sw:done --auto <id>` instead of bare `/sw:done <id>`

**Implementation Details**:
- In Step 4 (Close Each Increment), change `/sw:done <increment-id>` to `/sw:done <increment-id> --auto`
- Update the example output to reflect `--auto` usage

**Dependencies**: T-003

---

## Phase 5: Sync Mirror Copies

### T-007: Sync all changes to mirror directories
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: all | **Status**: [ ] pending
**Test**: Given all source changes are made -> When running rebuild/sync -> Then all mirror directories (.claude, .cursor, .kiro, .pi, .windsurf, .antigravity, node_modules/specweave) contain the updated files

**Implementation Details**:
- Run `npm run rebuild` or equivalent sync command in the specweave repo
- Verify stop-auto-v5.sh is synced to all mirror locations
- Verify SKILL.md files are synced to all mirror locations

**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006
