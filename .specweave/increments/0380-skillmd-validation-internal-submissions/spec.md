---
increment: 0380-skillmd-validation-internal-submissions
title: Enforce SKILL.md validation for internal/crawler submissions
type: feature
priority: P1
status: completed
created: 2026-02-26T00:00:00.000Z
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Enforce SKILL.md validation for internal/crawler submissions

## Overview

Add explicit SKILL.md validation contract to the `enqueue-submissions` internal endpoint. Currently, the endpoint trusts the upstream caller (queue-processor) to have validated SKILL.md, but this trust is implicit. Adding a `skillMdVerified` boolean flag makes the contract explicit and rejects items that weren't validated upstream.

## User Stories

### US-001: Explicit SKILL.md verification contract (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the enqueue-submissions endpoint to require an explicit `skillMdVerified: true` flag
**So that** items cannot enter the processing queue without upstream validation attestation

**Acceptance Criteria**:
- [x] **AC-US1-01**: `EnqueueItem` interface includes `skillMdVerified?: boolean` field
- [x] **AC-US1-02**: Items without `skillMdVerified: true` are filtered out before enqueueing
- [x] **AC-US1-03**: Response includes `skippedNoSkillMd` count showing how many items were filtered
- [x] **AC-US1-04**: Queue-processor sends `skillMdVerified: true` for items that passed `checkSkillMdExists`

## Out of Scope

- Adding expensive GitHub API calls to the endpoint (must remain DB-free and fast)
- Changing the existing validation in processSubmission or finalize-scan
- Modifying the public submissions endpoint
