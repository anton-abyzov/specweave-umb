# Tasks — 0359 Fix SKILL.md Branch Detection

### T-001: Export detectBranch and fix scanner functions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test**: Given a repo with default_branch "develop" → When checkSkillMdExists/fetchRepoFiles is called → Then it fetches from the "develop" branch

### T-002: Fix rejection error message
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given a submission with skillPath "plugins/foo/SKILL.md" → When SKILL.md not found → Then message includes the path

### T-003: Update tests
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01 through AC-US1-06, AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given updated scanner functions → When tests run → Then all pass including new branch detection test
