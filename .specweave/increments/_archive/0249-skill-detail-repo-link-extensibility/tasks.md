# Tasks — 0249: Skill Detail — Repo Link + Extensibility Auto-Detection

### T-001: TDD RED — Write extensibility-detector unit tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given SKILL.md content with/without extensibility signals → When detectExtensibility() called → Then correct extensible flag and extensionPoints returned

### T-002: TDD GREEN — Implement extensibility-detector
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given failing tests from T-001 → When implementation added → Then all tests pass

### T-003: Add repo URL MetaRow to skill detail page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given skill detail page → When skill has repoUrl → Then clickable "Repository" link visible in Meta section

### T-004: Store extensibility in KV on publish + surface in data layer
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given publishSkill() called with extensibility data → When skill fetched via getSkillByName() → Then extensible and extensionPoints present

### T-005: Wire detector into submission pipeline
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**Test**: Given processSubmission() runs on extensible skill → When published → Then KV record includes extensibility data

### T-006: Build and verify
**User Story**: ALL | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test**: Given all changes → When vitest + build → Then pass with no errors
