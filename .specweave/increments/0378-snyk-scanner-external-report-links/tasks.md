# Tasks — 0378: External Intelligence for Security Reports

### T-001: Add ExternalIntelligence type and fetcher to security-report.ts
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given a skill with npmPackage → When getUnifiedSecurityReport is called → Then externalIntelligence contains socketScore, URLs, and riskScore

### T-002: Add tests for externalIntelligence
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given mocked Socket.dev responses → When tests run → Then all 3 paths verified (has npm, no npm, failure)

### T-003: Render External Intelligence card on security page
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-03 | **Status**: [x] completed
**Test**: Given security page renders → When skill has npmPackage → Then card shows score breakdown and external links

### T-004: Run tests and verify build
**User Story**: US-001, US-002 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: Given all changes → When vitest run and next build → Then all pass
