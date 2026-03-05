---
increment: 0436G-improve-error-messages
title: "Improve error messages"
---

# Tasks

### T-001: Add platform context to sync error messages
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given a sync failure → When error is displayed → Then message includes platform name and API endpoint

### T-002: Add fix suggestions to common error patterns
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given 401/404 error → When displayed → Then message suggests checking credentials or project config
