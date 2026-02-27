# Tasks — 0333: Fix Crawl Dispatch process.env Mismatch

### T-001: Add missing types to CloudflareEnv
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given CloudflareEnv interface → When CRAWLER_WORKERS accessed → Then TypeScript recognizes it

### T-002: Fix crawl-dispatch.ts env access
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x] completed
**Test**: Given dispatchCrawlJob called with cfEnv param → When CRAWLER_WORKERS read → Then uses cfEnv value, not process.env

### T-003: Pass env in scheduled handler
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05 | **Status**: [x] completed
**Test**: Given scheduled() handler fires → When dispatchCrawlJob called → Then env passed as third arg + diagnostic log emitted

### T-004: Update tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given test suite runs → When dispatchCrawlJob called → Then uses mock CloudflareEnv, not process.env

### T-005: Verify build
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given npm run build → When worker-with-queues.js generated → Then contains dispatchCrawlJob(source, crawlConfig, env)
