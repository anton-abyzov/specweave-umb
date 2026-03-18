# Tasks: 0573 - Fix sw@specweave Silent Corruption

### T-001: Add sw@specweave health check to SessionStart hook
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given settings.json with sw@specweave=false -> When session starts -> Then sw@specweave is set to true and system message emitted. Given sw@specweave=true -> When session starts -> Then no change (fast path).

### T-002: Wire migrateUserLevelPlugins into refresh-plugins
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given refresh-plugins runs -> When migrateUserLevelPlugins executes -> Then sw@specweave is restored to true after any corruption.

### T-003: Add unit test for session-start health check
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Bash script test with mock settings.json files verifying repair behavior.

### T-004: Add integration test for refresh-plugins migration wiring
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Verify refresh-plugins imports and calls migrateUserLevelPlugins.
