---
increment: 0604-fix-ado-per-us-sync-scoping
title: Fix ADO Per-US Sync Scoping Bug
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: ADO Per-US Sync Scoping

## Overview

`per-us-sync.ts:findExistingWorkItem()` searches by `[US-001]` without Feature ID, matching work items from other increments. FS-597's US-001 was mapped to ADO #194 (from FS-591).

## User Stories

### US-001: Feature-Scoped Per-US ADO Search (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** per-US ADO sync to only match work items from the current Feature
**So that** stories don't get mapped to work items from other increments

**Acceptance Criteria**:
- [x] **AC-US1-01**: `findExistingWorkItem()` searches by `[featureId][usId]` pattern instead of just `[usId]`
- [x] **AC-US1-02**: Corrupted FS-597 living docs have wrong ADO IDs removed
