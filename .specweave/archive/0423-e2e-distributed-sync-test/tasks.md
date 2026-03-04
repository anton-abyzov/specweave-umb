# Tasks: E2E Distributed Sync Routing Test

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed

## User Story: US-001 - Distributed sync routes to child project repos

**Linked ACs**: AC-US1-01
**Tasks**: 1 total, 0 completed

### T-001: Verify distributed sync creates tickets in child project repos

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [ ] pending

**Test Plan**:
- **Given** umbrella.enabled is true and syncStrategy is distributed
- **When** sync-progress runs for this increment with Project: specweave
- **Then** GitHub issue is created in anton-abyzov/specweave (child repo) and JIRA in WTTC (child project)

**Implementation**:
1. Run sync-progress and verify per-project routing
