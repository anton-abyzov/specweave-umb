# Tasks: Plugin Security Self-Scan

## US-001: SKILL.md Security Linter

### T-001: Define detection rules as structured data
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given detection rules → When loaded → Then each rule has id, category, severity, pattern (regex), and suggested fix

### T-002: Build SKILL.md parser (extract bash code blocks)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 through AC-US1-04 | **Status**: [x] completed
**Test**: Given a SKILL.md with 3 bash blocks → When parsed → Then returns 3 code block objects with line numbers

### T-003: Implement CREDENTIALS_UNSAFE detector
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given SKILL.md with `cat >> .env << EOF` and `Please provide your API token` → When scanned → Then flags CREDENTIALS_UNSAFE with MEDIUM severity

### T-004: Implement DATA_EXFILTRATION detector
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given SKILL.md with `curl` using `$DOMAIN` without strict validation → When scanned → Then flags DATA_EXFILTRATION

### T-005: Implement COMMAND_EXECUTION detector
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given SKILL.md with unquoted `$VAR` in bash → When scanned → Then flags COMMAND_EXECUTION

### T-006: Implement PROMPT_INJECTION detector
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given SKILL.md interpolating user input without sanitization → When scanned → Then flags PROMPT_INJECTION

### T-007: Generate scan report with line references
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test**: Given scan with 2 findings → When report generated → Then includes file, line, category, severity, fix suggestion, and exit code = 1

## US-002: Pre-Publish Hook

### T-008: Add security scan step to /sw:npm workflow
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given plugin with CRITICAL finding → When /sw:npm runs → Then publish is blocked with scan report

## US-003: Batch Scan

### T-009: Implement batch scan across all plugins
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given 5 plugins with mixed findings → When batch scan runs → Then summary table shows all 5 with per-severity counts and JSON export
