# Tasks — 0363 Search Repo Name Matching

### T-001: Update route.ts — supplement edge with Postgres when results < limit
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given edge returns 2 results and limit is 10 → When search API is called → Then Postgres is also queried and merged results contain up to 10 unique skills

### T-002: Create migration — add repoUrl to search vector
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given a skill with repoUrl "github.com/anton-abyzov/specweave" → When search_vector is computed → Then tsvector contains tokens "github", "com", "anton", "abyzov", "specweave"

### T-003: Update route.test.ts — fix existing tests and add merge/dedup tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given edge returns 1 result and Postgres returns 5 (with 1 overlap) → When merged → Then 5 unique results returned with X-Search-Source "edge+postgres"

### T-004: Run tests and verify
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: All tests pass, no regressions
