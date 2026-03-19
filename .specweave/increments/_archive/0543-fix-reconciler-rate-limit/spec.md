---
increment: 0543-fix-reconciler-rate-limit
title: Fix GitHub API rate limit exhaustion caused by reconciler search fallback
status: completed
priority: P1
type: bug
created: 2026-03-16T00:00:00.000Z
---

# Fix GitHub API Rate Limit Exhaustion in Reconciler

## Problem Statement

`GitHubReconciler.scanIncrements()` exhausts the 5000/hour GitHub REST API quota. For each increment directory (~161) without GitHub metadata in `metadata.json`, it calls `searchGitHubForIssues()` which executes `gh issue list --search "[FS-XXX]" in:title` -- one REST API call per increment. With ~346 metadata files lacking the `github` key and reconciliation triggered by hooks (task completion, increment planning, session start), the quota is burned through in under an hour.

Root cause: line 354 of `github-reconciler.ts` -- no caching of search results, no negative cache for "not found" results, no status filtering (searches completed/abandoned increments), no rate limit awareness.

## Goals

- Reduce GitHub API calls from ~161 per scan to near-zero for typical workloads
- Prevent rate limit exhaustion during normal SpecWeave sessions
- Maintain correctness: increments with real GitHub issues must still be discovered

## User Stories

### US-001: Status-Based Search Filtering
**Project**: specweave
**As a** SpecWeave user
**I want** the reconciler to skip searches for completed/abandoned/created increments
**So that** only active-like increments consume API calls

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given an increment with `metadata.status` of "completed", when `scanIncrements()` processes it, then `searchGitHubForIssues()` is not called
- [x] **AC-US1-02**: Given an increment with `metadata.status` of "abandoned", when `scanIncrements()` processes it, then `searchGitHubForIssues()` is not called
- [x] **AC-US1-03**: Given an increment with `metadata.status` of "active", when it has no GitHub metadata and no user story issues, then `searchGitHubForIssues()` is called
- [x] **AC-US1-04**: Given an increment with `metadata.status` of "planning", "in-progress", "backlog", "ready_for_review", or "paused", when it has no GitHub metadata, then `searchGitHubForIssues()` is called
- [x] **AC-US1-05**: Given an increment with `metadata.status` of "created", when `scanIncrements()` processes it, then `searchGitHubForIssues()` is not called

### US-002: Negative Search Cache in Metadata
**Project**: specweave
**As a** SpecWeave user
**I want** the reconciler to remember when a search found no results
**So that** it does not re-search the same increment on future scans

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `searchGitHubForIssues()` returns zero results and the increment has no existing `metadata.github.issue`, when the search completes, then `metadata.json` is updated with `github.searched: true`, `github.searchedAt: <ISO timestamp>`, and `github.noIssuesFound: true`
- [x] **AC-US2-02**: Given an increment whose `metadata.json` contains `github.noIssuesFound: true`, when `scanIncrements()` processes it, then `searchGitHubForIssues()` is not called
- [x] **AC-US2-03**: Given `searchGitHubForIssues()` returns one or more results, when the search completes, then no negative cache markers are written to `metadata.json`
- [x] **AC-US2-04**: Given an increment with `metadata.github.issue: 123` (existing main issue) but zero user story issues found by search, when the search completes, then no negative cache is written (main issue presence means US issues may exist later)

### US-003: Session Search Cache in GitHub Client
**Project**: specweave
**As a** SpecWeave user
**I want** search results to be cached in-memory during a scan session
**So that** repeated searches for the same feature ID within 30 seconds reuse cached results

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `searchIssuesByFeature("FS-100")` is called, when it completes, then the result is stored in a static class-level Map on `GitHubClientV2` with a 30-second TTL
- [x] **AC-US3-02**: Given a cached entry for "FS-100" exists and is less than 30 seconds old, when `searchIssuesByFeature("FS-100")` is called again, then the cached result is returned without executing `gh issue list`
- [x] **AC-US3-03**: Given a cached entry for "FS-100" exists and is older than 30 seconds, when `searchIssuesByFeature("FS-100")` is called, then a fresh `gh issue list` call is made and the cache is updated

### US-004: Search Budget Per Scan
**Project**: specweave
**As a** SpecWeave user
**I want** the reconciler to cap API searches at 20 per `scanIncrements()` call
**So that** a single scan cannot exhaust the rate limit even if many increments lack metadata

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `scanIncrements()` is running and 20 search calls have been made, when the next increment needs a search, then the search is skipped and the increment is processed with metadata-based references only
- [x] **AC-US4-02**: Given the search budget is exhausted, when `scanIncrements()` continues processing remaining increments, then increments with existing `metadata.github` data are still processed correctly (no data loss)
- [x] **AC-US4-03**: Given the search budget is exhausted, when the scan completes, then a log message reports how many searches were skipped due to budget exhaustion
- [x] **AC-US4-04**: Given a new `scanIncrements()` call begins, when the budget counter is checked, then it starts at zero (budget resets per call, not per session)

## Out of Scope

- Configurable search budget via `config.json` (YAGNI -- Phases 1-2 reduce searches to near-zero)
- Proactive `gh api rate_limit` checks (adds complexity without proportional benefit given the budget cap)
- Migrating existing metadata.json files to add negative cache markers (lazy population on next scan)
- Rate limiting for non-reconciler GitHub API paths (different problem, different increment)

## Non-Functional Requirements

- **Performance**: A scan of 161 increments with 3 active-like statuses must complete in under 10 seconds (down from 60+ seconds with 161 API calls)
- **Compatibility**: Negative cache markers (`github.searched`, `github.searchedAt`, `github.noIssuesFound`) must coexist with existing `github.issue`, `github.url`, `github.issues[]` keys without breaking `extractGitHubState()`
- **Reliability**: Budget exhaustion must not cause data loss -- increments with existing metadata references continue to be processed

## Edge Cases

- **Increment with main issue but no US issues**: `metadata.github.issue` exists, `userStoryIssues` is empty. Search still runs (US issues may be missing). No negative cache written.
- **Metadata missing status field**: Defaults to "unknown" via `metadata.status || 'unknown'`. Treated as non-searchable (skip search).
- **Archive directory**: Already handled by existing `isArchiveDir` check at line 354. No change needed.
- **Concurrent scans**: Static Map cache is shared. Two concurrent scans benefit from shared cache, no race condition since Map operations are synchronous in Node.js single-thread.
- **Search returns error (network failure)**: Existing `catch` block logs warning. No negative cache written on error (only on confirmed empty results).

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Negative cache prevents discovery of late-created issues | 0.2 | 4 | 0.8 | Only cache when zero results AND no main issue; manual reconcile can clear cache |
| Status filter misses a valid status string | 0.1 | 3 | 0.3 | Use allowlist matching base-reconciler.ts patterns; unit test all statuses |
| Budget cap too low for repos with many active increments | 0.1 | 2 | 0.2 | 20 is generous given Phase 1 reduces active searches to ~3; can raise later |

## Technical Notes

### Dependencies
- `github-reconciler.ts` (primary changes: status filter, budget counter, negative cache write)
- `github-client-v2.ts` (add static `searchCache` Map mirroring `issueCache` pattern)
- Existing `base-reconciler.ts` status constants for allowlist reference

### Constraints
- Budget is hard-coded at 20 (no config surface)
- Negative cache uses existing `github` namespace in metadata.json
- Search cache follows existing `issueCache` pattern: static class-level Map, 30s TTL

### Architecture Decisions
- **Existing namespace**: Negative cache fields go under `metadata.github.*` since `extractGitHubState()` only reads specific sub-keys and ignores unknown ones
- **Static cache**: Search cache is class-level static Map, consistent with existing `issueCache`
- **Budget scope**: Per `scanIncrements()` call, not per session, to keep the mechanism stateless

## Success Metrics

- GitHub API calls per reconciler scan reduced from ~161 to 3 or fewer under normal conditions
- Zero rate limit errors during a typical SpecWeave session (8-hour window)
- Scan completion time under 10 seconds for 161-increment workspace
