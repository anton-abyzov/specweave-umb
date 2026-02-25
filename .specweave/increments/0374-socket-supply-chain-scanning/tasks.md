# Tasks — 0374 Socket.dev Supply Chain Scanning

### T-001: Create DCI package extractor
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given SKILL.md with DCI blocks containing `npm install lodash` → When extracted → Then returns `[{ name: "lodash", manager: "npm" }]`

### T-002: Create Socket.dev API client
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test**: Given valid API key and package names → When fetchSocketScores called → Then returns per-package scores with KV caching

### T-003: Add enrichWithSocketScores to dependency analyzer
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [x] completed
**Test**: Given DependencyAnalysis + Socket scores → When enriched → Then riskScore = local*0.4 + socket*0.6

### T-004: Extend StoredScanResult type
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given scan result with Socket data → When stored → Then socketScore and dci fields present

### T-005: Add SOCKET_API_KEY to CloudflareEnv
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given env.d.ts → When SOCKET_API_KEY added → Then TypeScript recognizes the binding

### T-006: Wire Socket into process-submission pipeline
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given submission with package.json → When processed → Then Socket enrichment runs and affects weighted score

### T-007: Add tests for new modules
**User Story**: US-001, US-002 | **Satisfies ACs**: All | **Status**: [x] completed
**Test**: Given mocked Socket API → When tests run → Then all pass with >80% coverage

### T-008: Update process-submission tests with Socket mocks
**User Story**: US-001, US-002 | **Satisfies ACs**: All | **Status**: [x] completed
**Test**: Given existing process-submission tests → When Socket mocks added → Then all existing + new tests pass
