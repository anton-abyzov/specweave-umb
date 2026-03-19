---
increment: 0616-fix-validate-owner-error-masking
title: Fix GitHub API error masking in validateOwner
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: GitHub API error masking in validateOwner

## Overview

`validateOwner()` in two files hardcodes `status: 404` regardless of actual HTTP response status. When GitHub returns 403 (rate limit) or 401 (bad token), users see "Resource Not Found (404)" instead of the real error. The existing error handler (`git-error-handler.ts`) already has proper 401/403 handling — it's never triggered because the caller always sends 404.

## Root Cause

Both implementations try `/users/{owner}` then `/orgs/{owner}`. If both return non-200, the code falls through to a hardcoded `{ status: 404, message: 'Not Found' }` error object, discarding the actual response status.

**Affected files**:
- `src/core/repo-structure/providers/github-provider.ts` — `validateOwner()` method (line ~100)
- `src/core/repo-structure/github-validator.ts` — standalone `validateOwner()` function (line ~142)

## User Stories

### US-001: Accurate GitHub API error reporting in owner validation (P1)
**Project**: specweave

**As a** developer configuring a SpecWeave workspace with GitHub
**I want** `validateOwner()` to report the actual HTTP error status from GitHub
**So that** I can distinguish between a non-existent owner (404), an expired/invalid token (401), and rate limiting (403) and take the correct remediation action

**Acceptance Criteria**:
- [x] **AC-US1-01**: When GitHub API returns 401 for owner validation, the error message contains "401" and authentication-related guidance (not "404 Not Found")
- [x] **AC-US1-02**: When GitHub API returns 403 for owner validation, the error message contains "403" and rate-limit/permission guidance (not "404 Not Found")
- [x] **AC-US1-03**: When GitHub API returns 404 (owner genuinely not found), existing behavior is preserved — error message contains "404" and not-found guidance
- [x] **AC-US1-04**: Both `validateOwner()` implementations (github-provider.ts and github-validator.ts) produce consistent error output for the same HTTP status

## Functional Requirements

### FR-001: Capture actual HTTP status from failed API calls
When both `/users/{owner}` and `/orgs/{owner}` return non-200, use the actual HTTP status from the responses instead of hardcoding 404. If the user endpoint returns a more severe error (401/403) and the org endpoint returns 404, prefer the more informative status.

### FR-002: DRY — eliminate duplicate validateOwner implementations
`github-validator.ts` should delegate to `GitHubProvider.validateOwner()` rather than maintaining a parallel implementation. This prevents future divergence.

## Out of Scope

- Changing error handling for other providers (GitLab, Bitbucket)
- Modifying `git-error-handler.ts` itself — it already handles 401/403/404 correctly
- Adding retry logic for rate-limited requests
- Changing the `OwnerValidationResult` type signature

## Dependencies

- `git-error-handler.ts` — `getActionableError()` and `formatActionableError()` (existing, no changes needed)
- `GitApiError` type (existing, no changes needed)

## Success Criteria

- All 4 ACs pass with TDD tests
- No regression in existing owner validation tests
- Single implementation of `validateOwner()` (DRY)
