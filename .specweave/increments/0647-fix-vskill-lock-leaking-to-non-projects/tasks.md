# Tasks: Fix vskill.lock leaking to non-SpecWeave directories

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

---
tasksCompleted: 5
tasksTotal: 5
---

### T-001: Write failing test — copyPluginSkillsToProject uses global lock (static analysis)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02
**Test Plan**:
- Given the source code of `copyPluginSkillsToProject` in plugin-copier.ts
- When we extract the function body
- Then it should contain `ensureGlobalLockfile` and `writeGlobalLockfile`
- And it should NOT contain `ensureLockfile(projectRoot)` or `writeLockfile(lock, projectRoot)`

### T-002: Write failing test — copyPluginSkillsToProject does not write vskill.lock (functional)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02
**Test Plan**:
- Given a mocked filesystem with `copyPluginSkillsToProject` invoked
- When the function completes
- Then `writeFileSync` should never be called with a path containing `vskill.lock`
- And `writeFileSync` should be called with a path containing `plugins-lock.json`

### T-003: Fix copyPluginSkillsToProject to use global lockfile
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Depends on**: T-001, T-002
**Test Plan**:
- Given `copyPluginSkillsToProject()` source code
- When hash-checking and state-writing execute
- Then `ensureGlobalLockfile()` is used (not `ensureLockfile(projectRoot)`)
- And `writeGlobalLockfile()` is used (not `writeLockfile(lock, projectRoot)`)
- And a try/catch with in-memory fallback exists for cross-platform safety

### T-004: Add post-install migration in refresh-plugins.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**AC**: AC-US2-01
**Test Plan**:
- Given `refresh-plugins.ts` source code
- When the install loop completes
- Then `migrateBundledToGlobalLock(projectRoot)` is called after the loop inside the `if (isClaude)` block

### T-005: Verify all tests pass
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01
**Depends on**: T-003, T-004
**Test Plan**:
- Given all changes are applied
- When running `npx vitest run` on all 3 test files
- Then all tests pass with no failures
