---
increment: 0430G-test-import-from-github
title: "Test import from GitHub"
---

# Tasks

### T-001: Verify import creates a SpecWeave increment
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given external GitHub issue #1492 → When imported → Then SpecWeave increment 0430G created with correct metadata

### T-002: Verify bidirectional sync works
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given imported increment → When sync-progress runs → Then GitHub issue #1492 updated with progress
