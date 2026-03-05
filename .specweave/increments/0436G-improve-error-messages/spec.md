---
increment: 0436G-improve-error-messages
title: "[EXTERNAL] Improve error messages"
status: active
priority: P2
type: bug
created: 2026-03-05
external:
  platform: github
  ref: "github#anton-abyzov/specweave#1497"
  url: "https://github.com/anton-abyzov/specweave/issues/1497"
---

# Improve Error Messages

**Imported from**: GitHub #1497 (anton-abyzov/specweave)

## Problem Statement

When sync fails, error messages are not helpful. Improve them to show specific details about what went wrong.

## User Stories

### US-001: Improve Sync Error Messages
**Project**: specweave

**As a** developer
**I want** sync error messages to show specific details
**So that** I can quickly diagnose and fix sync failures

**Acceptance Criteria**:
- [x] **AC-US1-01**: Error messages include the platform name (GitHub/JIRA/ADO)
- [x] **AC-US1-02**: Error messages include the specific API endpoint that failed
- [x] **AC-US1-03**: Error messages suggest common fixes (check credentials, verify project exists)
