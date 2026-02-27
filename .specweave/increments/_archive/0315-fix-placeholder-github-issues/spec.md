---
increment: 0315-fix-placeholder-github-issues
title: "Fix Placeholder GitHub Issue Creation"
type: bug
priority: P0
status: active
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Bug: Fix Placeholder GitHub Issue Creation

## Overview

11 GitHub issues (#1238-#1248) were auto-created with `[Story Title]` template placeholder text instead of real user story titles. Each affected feature (FS-301 through FS-307) received exactly 2 placeholder issues (US-001, US-002) — matching the template's 2 user stories — while actual specs have 3-7 user stories each.

## Problem Statement

The `ExternalIssueAutoCreator` creates GitHub issues from spec.md. When triggered before the PM skill fills in the template, it reads placeholder text like `### US-001: [Story Title] (P1)` and creates issues with `[Story Title]` as the title. Multiple defense layers are missing or broken:

1. `parseUserStories()` doesn't skip `[Story Title]` placeholders (unlike `github-feature-sync.ts:502`)
2. `github-auto-create-handler.sh` has zero template guards
3. `universal-auto-create-dispatcher.sh` path resolution broken in umbrella repos
4. 10s debounce too short for PM spec completion

## User Stories

### US-001: Placeholder Skip Guard in TypeScript Auto-Creator (P0)
**Project**: specweave

**As a** SpecWeave developer
**I want** the ExternalIssueAutoCreator to skip template placeholder user stories
**So that** GitHub issues are never created with `[Story Title]` text

**Acceptance Criteria**:
- [x] **AC-US1-01**: `parseUserStories()` in `external-issue-auto-creator.ts` skips entries where title equals `[Story Title]`
- [x] **AC-US1-02**: `parseUserStories()` skips any title matching bracket-only placeholder pattern `/^\[.+\]$/`
- [x] **AC-US1-03**: Real titles (e.g., "Queue Search & Filtering") pass through unchanged
- [x] **AC-US1-04**: Unit test covers placeholder skip, bracket-placeholder skip, and real title passthrough

---

### US-002: Template Guards in Bash Handlers (P1)
**Project**: specweave

**As a** SpecWeave developer
**I want** the bash auto-create handlers to detect and skip template specs
**So that** no code path can create placeholder issues

**Acceptance Criteria**:
- [x] **AC-US2-01**: `github-auto-create-handler.sh` exits early when spec.md contains `[Story Title]` markers
- [x] **AC-US2-02**: `universal-auto-create-dispatcher.sh` adds template guard before dispatching to any provider
- [x] **AC-US2-03**: `universal-auto-create-dispatcher.sh` resolves github handler path via fallback when `${PROJECT_ROOT}/plugins/...` doesn't exist (umbrella repo fix)
- [x] **AC-US2-04**: Debounce increased from 10s to 30s in both `github-auto-create-handler.sh` and `universal-auto-create-dispatcher.sh`

---

### US-003: Clean Up Existing Placeholder Issues (P1)
**Project**: specweave

**As a** project maintainer
**I want** the 11 placeholder issues closed with an explanatory comment
**So that** the issue tracker reflects accurate state

**Acceptance Criteria**:
- [x] **AC-US3-01**: Issues #1238-#1248 are closed with a comment explaining they were created from template placeholders
- [x] **AC-US3-02**: No duplicate issues remain open for the same feature/user-story combinations

## Out of Scope

- Rewriting the entire auto-create pipeline
- Changing the template format
- Adding retry logic for previously failed issue creation
