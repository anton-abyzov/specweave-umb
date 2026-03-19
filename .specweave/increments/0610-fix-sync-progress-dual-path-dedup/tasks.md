---
increment: 0610-fix-sync-progress-dual-path-dedup
---

# Tasks

### T-001: Write failing tests for JIRA/ADO field name dedup
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given metadata with `externalLinks.jira.epicKey` → When `checkExistingIssue('jira')` → Then returns epic key (FAILS)
- Given metadata with `externalLinks.jira.issueKey` → When same → Then returns issue key (PASSES, regression)
- Given metadata with `externalLinks.ado.featureId` → When `checkExistingIssue('ado')` → Then returns feature ID (FAILS)
- Given metadata with `externalLinks.ado.workItemId` → When same → Then returns work item ID (PASSES, regression)

### T-002: Fix checkExistingIssue to check epicKey and featureId
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given T-001 tests → When fix applied → Then all 4 pass + full suite green

### T-003: Verify build and run full test suite
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**: `npm run build` succeeds, `npx vitest run` all green
