# Tasks: CLI Health Check Command

### T-001: Implement health check command with config and plugin validation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given valid config and plugins → When running specweave health → Then all checks pass with details

### T-002: Add exit code handling and diagnostic error output
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given broken config → When running specweave health → Then exits non-zero with diagnostic details

### T-003: Add JSON output mode for CI/CD integration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given specweave health --json → When command runs → Then outputs valid JSON with check results
