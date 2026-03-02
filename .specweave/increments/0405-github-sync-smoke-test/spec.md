# FS-405: GitHub Sync Smoke Test

## Overview
End-to-end smoke test to verify the SpecWeave → GitHub sync pipeline works correctly: issue creation on increment planning, progress sync on task completion, and issue closure on increment done.

## User Stories

### US-001: Verify Public Docs Sync
**As a** SpecWeave user
**I want** the sync pipeline to create and manage GitHub issues automatically
**So that** external stakeholders can track progress via GitHub

#### Acceptance Criteria
- [x] AC-US1-01: GitHub issue is created for this user story with correct title format `[FS-405][US-001]`
