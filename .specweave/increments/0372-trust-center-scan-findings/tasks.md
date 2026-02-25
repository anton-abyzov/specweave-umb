# Tasks — 0372: Trust Center scan findings

### T-001: Create shared FindingsList component
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given a findings array → When rendered → Then each finding shows patternId, severity badge, patternName, file:line, and code match sorted by severity

### T-002: Enrich blocklist check API with findings
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given a blocked skill with a matching rejected submission → When GET /api/v1/blocklist/check?name=X → Then response includes findings array, skillPath, submissionId, commitSha

### T-003: Enrich admin rejections API with findings
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given rejected submissions with scan results → When GET /api/v1/admin/rejections → Then scanResults include findings array and commitSha

### T-004: Update BlockedSkillsTab expanded detail
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given a blocked entry with findings → When expanded → Then findings render with GitHub links, skillPath shows in metadata, column header says "Source"

### T-005: Update RejectedSkillsTab expanded detail
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given a rejected entry with findings → When expanded → Then findings render inline with severity badges and file:line references
