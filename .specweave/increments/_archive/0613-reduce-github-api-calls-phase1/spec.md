---
increment: 0613-reduce-github-api-calls-phase1
title: Reduce GitHub API call volume in sync-progress (Phase 1)
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Reduce GitHub API call volume in sync-progress (Phase 1)

## Overview

`sync-progress` makes ~65+ GitHub API calls per 7-US increment (10-18 per user story), hitting the 5000/hour rate limit after 2-3 increments. Root cause: Step 5 (GitHubACCheckboxSync) and Step 6 (syncACProgressToProviders -> postACProgressComments) duplicate the same work -- both fetch issue bodies, patch checkboxes, and post progress comments. Six surgical fixes to cut calls ~50%.

## User Stories

### US-001: Eliminate duplicate GitHub sync between Step 5 and Step 6 (P1)
**Project**: specweave

**As a** SpecWeave user running sync-progress
**I want** the command to not make redundant GitHub API calls
**So that** I stay well within GitHub's 5000/hour rate limit

**Acceptance Criteria**:
- [x] **AC-US1-01**: When GitHubACCheckboxSync (Step 5) succeeds, syncACProgressToProviders skips the postACProgressComments path for GitHub (autoClose still runs)
- [x] **AC-US1-02**: syncACProgressToProviders accepts a `skipGitHubComments` option that bypasses postACProgressComments for the GitHub provider only
- [x] **AC-US1-03**: JIRA and ADO providers are unaffected by the skipGitHubComments flag
- [x] **AC-US1-04**: When Step 5 fails, Step 6 falls back to the full GitHub sync path (no data loss)
- [x] **AC-US1-05**: For a 7-US increment, GitHub API calls for comment+checkbox operations are reduced from ~49 to ~21

---

### US-002: Optimize autoClose operations (P2)
**Project**: specweave

**As a** SpecWeave user with completed user stories
**I want** the auto-close flow to make fewer API calls
**So that** closing completed issues doesn't waste rate limit budget

**Acceptance Criteria**:
- [x] **AC-US2-01**: ensureLabelExists is called once before the per-US loop, not per-US
- [x] **AC-US2-02**: A module-level cache prevents redundant gh label list calls across sync runs within the same process
- [x] **AC-US2-03**: Issue close + label edit are combined into a single API call using gh api PATCH
- [x] **AC-US2-04**: USs with stored closed status in metadata.json skip the gh issue view state check
- [x] **AC-US2-05**: All auto-close behavior (completion comment, close, labels) is preserved for newly-completed USs

---

### US-003: Skip unnecessary progress comments (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** progress comments posted only when there are actual checkbox changes
**So that** GitHub issues don't accumulate redundant comment noise

**Acceptance Criteria**:
- [x] **AC-US3-01**: GitHubACCheckboxSync skips addComment when body === originalBody (no checkbox changes)
- [x] **AC-US3-02**: Progress comments are still posted when checkboxes actually change

## Success Criteria

- GitHub API calls per 7-US sync-progress reduced from ~65 to ~30-35 (~50% reduction)
- All existing tests continue to pass
- No behavioral changes visible to users (same comments, same issue states)

## Out of Scope

- GraphQL batching (Phase 2)
- Cross-provider caching (Phase 2)
- JIRA/ADO API call optimization
- GitHubClientV2 cache TTL changes
