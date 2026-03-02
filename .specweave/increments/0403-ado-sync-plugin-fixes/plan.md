# Implementation Plan: ADO Sync Plugin Critical Fixes

## Overview

Pure bugfix increment targeting `repositories/anton-abyzov/specweave/plugins/specweave-ado/`. No architectural changes -- fixing broken logic, adding missing pagination, removing hardcoded assumptions, and improving HTTP reliability. All fixes are localized to existing files within the ADO plugin directory.

## Affected Components

| File | Issues | Severity |
|------|--------|----------|
| `hooks/post-task-completion.sh` | Reads stale `.ado.item` path instead of `.external_sync.ado.workItemId` | Critical |
| `ado-client-v2.ts` | No batch pagination (>200 fails), broken `testConnection()` URL, area path double-prepend | Critical, High, High |
| `ado-hierarchical-sync.ts` | Project-scoped WIQL for cross-project, no HTTP timeout, filter only from first container, WIQL regex corruption | Critical, High, Medium, Medium |
| `ado-profile-resolver.ts` | `activeProfile` vs `defaultProfile` mismatch | High |
| `ado-spec-sync.ts` | Hardcoded `$Feature` URL, unconditional title/desc overwrite | High, Medium |
| `conflict-resolver.ts` | Hardcoded Agile process states | High |
| `per-us-sync.ts` | Hardcoded `'User Story'` work item type | High |
| `ado-duplicate-detector.ts` | Verification failure returns `success: true` | Medium |
| `enhanced-ado-sync.js` | Hardcoded `repo` in task URL | Medium |
| `commands/sync.md` | `defaultProfile` vs `activeProfile` inconsistency with resolver | High |
| `SKILL.md` | Documents `AZURE_DEVOPS_PAT_MYORG` pattern but code never reads it | High |

## Implementation Strategy

### Phase 1: Critical Fixes (T-001 through T-003)
**Goal**: Restore basic auto-sync functionality.

1. **Fix hook field path** -- Single sed-level change in post-task-completion.sh: replace `.ado.item` with `.external_sync.ado.workItemId`. Verify by tracing the JSON structure that the system actually writes.
2. **Add batch fetch pagination** -- Implement continuation token loop in `ado-client-v2.ts` `batchGetWorkItems()`. ADO batch API returns `$skip`/continuation headers when results exceed 200.
3. **Fix cross-project WIQL endpoint** -- In `ado-hierarchical-sync.ts`, when strategy is FILTERED and multiple projects are involved, use `POST https://dev.azure.com/{org}/_apis/wit/wiql` (org-level) instead of `POST https://dev.azure.com/{org}/{project}/_apis/wit/wiql`.

### Phase 2: High Priority Fixes (T-004 through T-011)
**Goal**: Fix profile resolution, URL construction, and process template support.

4. **Resolve profile field name** -- Audit both `ado-profile-resolver.ts:161` and `commands/sync.md:96`, pick one canonical name (`activeProfile`), update the other.
5. **Fix feature URL work item type** -- In `ado-spec-sync.ts:258`, replace `$Feature` with the computed `workItemType` variable already available in scope.
6. **Fix testConnection() URL** -- In `ado-client-v2.ts:150`, single-project mode must include the project segment in the URL.
7. **Implement org-specific PAT lookup** -- Add code to check `AZURE_DEVOPS_PAT_{ORG}` environment variable as documented in SKILL.md, falling back to `AZURE_DEVOPS_PAT`.
8. **Make conflict resolver process-aware** -- Replace hardcoded Agile states in `conflict-resolver.ts:88-98` with a state mapping table keyed by process template (Agile, Scrum, CMMI, Basic).
9. **Fix per-US work item type** -- In `per-us-sync.ts:270`, read work item type from config/profile instead of hardcoding `'User Story'`.
10. **Add HTTP request timeout** -- Wrap fetch calls in `ado-hierarchical-sync.ts:424-484` with AbortController + configurable timeout (default 30s).
11. **Fix area path double-prepend** -- In `ado-client-v2.ts:459-462`, check if area path already starts with project name before prepending.

### Phase 3: Medium Priority Fixes (T-012 through T-016)
**Goal**: Data integrity and edge case reliability.

12. **Fix container filter scope** -- In `ado-hierarchical-sync.ts:91-97`, iterate containers and apply each container's filters individually.
13. **Fix duplicate detector return value** -- In `ado-duplicate-detector.ts:122-130`, verification failure path must return `success: false`.
14. **Add conditional update logic** -- In `ado-spec-sync.ts:273-303`, compare current vs new values before writing title/description.
15. **Fix hardcoded repo in task URL** -- In `enhanced-ado-sync.js:133`, use the actual repository name from config.
16. **Fix WIQL time range regex** -- In `ado-hierarchical-sync.ts:192-196`, rewrite `addTimeRangeFilter` to properly parse and append to existing WHERE clauses without corruption.

## Testing Strategy

- **Unit tests**: One or more tests per bug fix, verifying the specific behavior change
- **Existing tests**: Must not break -- run full test suite after each phase
- **Mock-based**: All ADO API calls mocked (no live API calls in tests)
- **Test location**: Alongside existing test files in the plugin directory, or in a `__tests__/` subdirectory
- **Coverage**: Target 95% for modified functions

## Technical Notes

### ADO Batch API Pagination
ADO's `_apis/wit/workitemsbatch` returns max 200 items. Use `$skip` query parameter or continuation token from response headers to page through. Accumulate all results before returning.

### Process Template State Mapping
| Template | Active States | Done States |
|----------|--------------|-------------|
| Agile | Active, Resolved | Closed |
| Scrum | Approved, Committed | Done |
| CMMI | Proposed, Active, Resolved | Closed |
| Basic | To Do, Doing | Done |

### Org-Specific PAT Resolution Order
1. `AZURE_DEVOPS_PAT_{ORG_UPPER}` (e.g., `AZURE_DEVOPS_PAT_MYORG`)
2. `AZURE_DEVOPS_PAT` (generic fallback)
3. Profile-stored PAT

## Risk Assessment

- **Low risk**: Fixes 1, 5, 6, 11, 12, 13, 14, 15 -- localized single-line or few-line changes
- **Medium risk**: Fixes 2, 3, 8, 9, 10, 16 -- behavioral changes requiring careful testing
- **Coordination needed**: Fix 4 (profile field name) affects both code and documentation
- **Backward compat**: Fix 7 (org-specific PAT) is additive, no breaking change
