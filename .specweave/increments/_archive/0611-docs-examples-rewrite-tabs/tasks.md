---
increment: 0611-docs-examples-rewrite-tabs
---

# Tasks

### T-001: Rewrite examples/index.md with real projects
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given the examples page → When built with Docusaurus → Then no build errors AND all code examples use CommandTabs AND no fabricated content remains

### T-002: Add CommandTabs to 6 reference/skills files
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given the 6 target files → When built with Docusaurus → Then no build errors AND each file imports CommandTabs AND user-facing invocations show three-tab pattern

### T-003: Build verification
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given all changes → When running npm run build → Then build succeeds with zero errors
