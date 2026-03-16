# Implementation Plan: Critical Sync Integration Bug Fixes

## Overview

This is a pure bugfix increment targeting the sync subsystem at `repositories/anton-abyzov/specweave/src/sync/`. No architectural changes — just fixing broken logic, removing stubs, and adding missing error handling. All fixes are localized to existing files with no new modules needed.

## Affected Components

| File | Issues | Severity |
|------|--------|----------|
| `src/sync/sync-coordinator.ts` | Stub task parsing (mock data), JIRA idempotency format mismatch, ADO PAT sync/async | Critical, Critical, High |
| `src/sync/external-item-sync-service.ts` | Two TODO stubs in production paths | Critical |
| `src/sync/github-reconciler.ts` | Profile bypass, missing `paused` status | Critical, Medium |
| `src/sync/external-issue-auto-creator.ts` | Hardcoded `develop` branch, JIRA wiki markup in ADF, title format mismatch | High, Medium, Critical |
| `src/sync/providers/github.ts` | No pagination, missing response checks | High |
| `src/sync/providers/jira.ts` | No pagination, missing response checks | High |
| `src/sync/providers/ado.ts` | No pagination, hardcoded work item type/state, missing response checks | High |
| `src/sync/config.ts` | PartialSyncConfig missing fields, validation gaps | Medium |
| `src/sync/status-mapper.ts` | Default inconsistency with coordinator | Medium |

## Implementation Strategy

### Phase 1: Critical Fixes (P0)
**Goal**: Fix data-loss and broken-flow bugs first.

1. **Remove stub code** in sync-coordinator.ts and external-item-sync-service.ts
2. **Fix profile resolution** in github-reconciler.ts
3. **Fix JIRA idempotency** format comparison
4. **Fix issue title search** format mismatch in auto-creator

### Phase 2: High Priority Fixes (P1)
**Goal**: Fix significant user-facing issues.

5. **Replace hardcoded branch** with detection
6. **Add pagination** to all three providers
7. **Add response.ok checks** across providers
8. **Fix ADO work item type** assumption
9. **Fix getAdoPat async/sync** mismatch

### Phase 3: Medium Priority Fixes (P2)
**Goal**: Polish and consistency.

10. **Fix JIRA wiki markup** to ADF/plain text
11. **Add `paused` to reconciler** open-state list
12. **Fix config schema** inconsistencies

## Testing Strategy

- **Unit tests**: One test per bug fix, verifying the specific behavior change
- **Existing tests**: Must not break — run full `npx vitest run` after each phase
- **Mock-based**: All external API calls mocked (no live API calls)
- **Test location**: `tests/unit/sync/` directory

## Technical Notes

### Default Branch Detection
Use `git symbolic-ref refs/remotes/origin/HEAD` or parse config for `repository.defaultBranch`, fallback to `main`.

### Pagination Approach
- **GitHub**: Follow `Link: <url>; rel="next"` header
- **JIRA**: Use `startAt` + `total` from response until all results fetched
- **ADO**: WIQL returns all IDs — batch GET requests in groups of 200 (ADO max)

### JIRA ADF vs Plain Text
JiraClient.getLastComment() returns ADF body. For idempotency comparison, extract text content from ADF and compare, or use a comment marker/ID approach.

### ADO Process Templates
Rather than runtime detection (which requires extra API calls), make work item type configurable via `sync.ado.workItemType` config property with smart defaults.

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing tests | Run full test suite after each fix |
| API behavior differences | All tests use mocks, no live API dependency |
| Config schema changes | Only additive changes, backward compatible |
| Pagination affecting performance | Add configurable max page limit (default 5 pages) |
