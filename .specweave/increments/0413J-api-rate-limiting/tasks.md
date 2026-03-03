# Tasks: Add API Rate Limiting

## User Story: US-001 - Add API Rate Limiting

**Linked ACs**: AC-US1-01, AC-US1-02
**Tasks**: 2 total, 2 completed

### T-001: Implement rate limit config reader

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given config.json has rateLimit section → When reading config → Then rate limit values are parsed correctly

### T-002: Add rate limiting middleware to API endpoints

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given rate limit config exists → When API receives requests → Then requests exceeding limit are rejected with 429
