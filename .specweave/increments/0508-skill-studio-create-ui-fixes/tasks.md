# Tasks: Fix Skill Studio Create Skill UI

## Phase 1: Fix Preview crash (React error #60)

### T-001: Split dangerouslySetInnerHTML from children in CreateSkillInline.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02
**Test**: Given body has content → When Preview toggled → Then markdown renders without error; Given body is empty → When Preview toggled → Then placeholder text shows

### T-002: Split dangerouslySetInnerHTML from children in CreateSkillPage.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02
**Test**: Same as T-001 for the standalone page variant

## Phase 2: Collapsible + formatted AI reasoning banner

### T-003: Add collapsible markdown-rendered reasoning banner in CreateSkillInline.tsx
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02
**Test**: Given AI generates a skill → When banner shows → Then it is collapsed with chevron; When chevron clicked → Then reasoning expands with rendered markdown

### T-004: Add collapsible markdown-rendered reasoning banner in CreateSkillPage.tsx
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02
**Test**: Same as T-003 for the standalone page variant

## Phase 3: Verification

### T-005: Build and run Playwright tests
**Status**: [x] completed
**Test**: Build passes clean, 17/18 Playwright tests pass (1 pre-existing failure unrelated)
