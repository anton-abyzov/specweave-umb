# Tasks: E2E Centralized Sync Routing Test

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed

## User Story: US-001 - Centralized sync routes to global targets

**Linked ACs**: AC-US1-01
**Tasks**: 1 total, 0 completed

### T-001: Verify centralized sync creates tickets in global repos

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [ ] pending

**Test Plan**:
- **Given** umbrella.enabled is false in config
- **When** sync-progress runs for this increment
- **Then** GitHub issue is created in anton-abyzov/specweave (global) and JIRA in SWE2E (global)

**Implementation**:
1. Run sync-progress and verify routing
