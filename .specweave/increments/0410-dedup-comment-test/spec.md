# FS-410: Dedup Comment Test

## Overview
Verify that when all ACs are marked complete at once, only one comment (the close comment) is posted — not both a progress comment AND a close comment.

## User Stories

### US-001: Verify Single Comment on Full Completion
**As a** SpecWeave user
**I want** only one comment when all ACs complete simultaneously
**So that** GitHub issues don't have redundant duplicate comments

#### Acceptance Criteria
- [x] AC-US1-01: Only the auto-close comment is posted when all ACs are complete
