# Tasks — 0285

### T-001: Write failing test for nested dir bug
**Satisfies ACs**: AC-02 | **Status**: [ ] pending
**Test**: Given cwd is ~/.openclaw → When install runs → Then path must NOT contain .openclaw/.openclaw

### T-002: Fix resolveInstallBase() in add.ts
**Satisfies ACs**: AC-01, AC-03, AC-04 | **Status**: [ ] pending
**Test**: Given projectRoot ends with agent base folder → When resolveSkillsPath called → Then no double-nesting

### T-003: Run full test suite and confirm green
**Satisfies ACs**: AC-03 | **Status**: [ ] pending
