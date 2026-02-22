---
increment: 0290-early-skillmd-rejection
title: "Reject submissions early when SKILL.md is missing"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Reject submissions early when SKILL.md is missing

## Overview

Currently, when a user submits a skill via `POST /api/v1/submissions`, the endpoint creates a submission record, emits events, and enqueues the submission for processing. Only later, inside `processSubmission()`, does the system fetch the repo files and discover that SKILL.md is missing — at which point it rejects the submission.

This wastes queue capacity, KV writes, and processing time. The fix is to add a lightweight SKILL.md existence check at the submission creation endpoint so repos without SKILL.md are rejected with a 422 before any submission record is created or enqueued.

## User Stories

### US-001: Early SKILL.md validation on public submissions (P1)
**Project**: specweave

**As a** skill submitter
**I want** immediate feedback when my repo is missing SKILL.md
**So that** I get a clear, fast error instead of waiting for the scan pipeline to reject my submission

**Acceptance Criteria**:
- [x] **AC-US1-01**: When a non-internal POST to `/api/v1/submissions` is received with a repoUrl pointing to a repo that lacks SKILL.md at the expected path, the endpoint returns HTTP 422 with an error message mentioning SKILL.md before creating any submission record
- [x] **AC-US1-02**: The pre-check uses a lightweight HEAD or GET request to raw.githubusercontent.com to verify SKILL.md existence without fetching the full repo file tree
- [x] **AC-US1-03**: If the pre-check network request fails (timeout, GitHub down), the submission proceeds normally (fail-open) to avoid blocking legitimate submissions
- [x] **AC-US1-04**: Internal/crawler requests (with valid X-Internal-Key) bypass the SKILL.md pre-check since `discoverSkillsEnhanced()` already confirms SKILL.md paths
- [x] **AC-US1-05**: The existing SKILL.md check in `processSubmission()` remains as a safety net for queue-based processing

---

### US-002: Custom skillPath support in pre-check (P1)
**Project**: specweave

**As a** skill submitter with skills in non-root paths
**I want** the SKILL.md pre-check to respect my custom `skillPath` parameter
**So that** submissions with valid SKILL.md at custom paths are not incorrectly rejected

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `skillPath` is provided in the request body, the pre-check fetches from that path instead of the root `SKILL.md`
- [x] **AC-US2-02**: When `skillPath` is not provided, the pre-check defaults to checking `SKILL.md` at the repo root

## Functional Requirements

### FR-001: SKILL.md existence check function
A new function `checkSkillMdExists(repoUrl: string, skillPath?: string)` that performs a lightweight HTTP request to raw.githubusercontent.com to verify SKILL.md exists. Returns `true` if found, `false` if 404, and `true` (fail-open) on network errors.

### FR-002: Integration into POST /api/v1/submissions
The check runs after body validation and dedup check, but before `createSubmission()`. Only applies to non-internal requests.

## Success Criteria

- Submissions to repos without SKILL.md return 422 in <2 seconds (no queue processing)
- Zero false rejections: GitHub API failures result in fail-open behavior
- No regression in existing submission flow for repos that DO have SKILL.md

## Out of Scope

- Bulk submission route (`/api/v1/submissions/bulk`) -- primarily used internally
- Removing the existing SKILL.md check from `processSubmission()` (kept as safety net)
- Caching SKILL.md existence results across submissions

## Dependencies

- `fetchSkillContent()` in `src/lib/scanner.ts` (existing, for reference/reuse pattern)
- GitHub raw.githubusercontent.com availability
