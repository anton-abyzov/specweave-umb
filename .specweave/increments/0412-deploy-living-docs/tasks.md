# Tasks: Deploy Living Docs to Website

## User Story: US-001 - Deploy Living Docs

**Linked ACs**: AC-US1-01, AC-US1-02
**Tasks**: 2 total, 2 completed

### T-001: Build living docs from current codebase

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given the specweave codebase → When running living docs build → Then build completes with no errors and output exists in .specweave/docs/internal/specs/

### T-002: Deploy docs to specweave website and verify accessibility

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given built living docs → When deploying to website → Then docs are accessible and contain latest feature specs
