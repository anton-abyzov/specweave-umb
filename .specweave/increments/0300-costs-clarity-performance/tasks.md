# 0300 - Tasks

## Backend: CostAggregator Performance

### T-001: Add per-file mtime cache to CostAggregator
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given CostAggregator with 3 session files parsed -> When `getTokenSummaries()` is called again with no file changes -> Then no files are re-parsed and cached summaries are returned

### T-002: Replace 60s TTL cache with file-change detection
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given CostAggregator with cached data -> When a session file is modified -> Then next `getTokenSummaries()` re-parses only that file and returns updated totals immediately (no stale window)

### T-003: Evict deleted files from cache
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test**: Given CostAggregator with 3 cached files -> When one file is deleted from disk -> Then next call evicts the stale entry and totals reflect only 2 files

### T-004: Implement incremental aggregation
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test**: Given CostAggregator with 200 cached files and 1 new file added -> When `getTokenSummaries()` is called -> Then only the new file is parsed, and totals are recomputed from all cached summaries

### T-005: Verify sub-100ms warm response time
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test**: Given CostAggregator with warm cache (all files cached) -> When `getTokenSummaries()` is called -> Then response completes in under 100ms

### T-006: Verify cold-start performance under 500ms for 200 files
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [x] completed
**Test**: Given 200 synthetic JSONL session files -> When CostAggregator is instantiated and `getTokenSummaries()` is called for the first time -> Then response completes in under 500ms

## Frontend: Provider Source Clarity

### T-007: Add provider source header on Costs page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given the Costs page renders -> When viewing the page -> Then a header section displays "Claude Code" as the data source with an icon, and subscription details appear as secondary info beneath it

### T-008: Add "More providers coming soon" footer on Costs page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given the Costs page renders -> When scrolling to bottom -> Then a subtle note reads "More providers coming soon"

### T-009: Update Overview page cost KPI card with source label
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given the Overview page renders -> When viewing the cost KPI card -> Then it displays "Claude Code" as a source indicator (subtitle or tooltip)

## Frontend: Sessions Table Virtualization

### T-010: Implement virtualized sessions table
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04 | **Status**: [x] completed
**Test**: Given 200 sessions in the Costs page -> When the sessions tab is active -> Then only ~20 visible rows + buffer are rendered in the DOM, and scrolling is smooth

### T-011: Support expandable rows in virtualized table
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test**: Given the virtualized sessions table -> When a row is clicked to expand -> Then the detail view renders correctly and the virtual scroll adjusts for the expanded height
