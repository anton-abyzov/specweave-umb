# Plan: Fix GitHub API error masking in validateOwner

## Problem

Both `validateOwner()` implementations hardcode `status: 404` when both `/users/{owner}` and `/orgs/{owner}` return non-200. This masks 401 (bad token) and 403 (rate limit/permissions) errors, preventing `getActionableError()` from routing to the correct handler.

## Architecture Decision

**No ADR needed** — bug fix, no new patterns introduced.

## Approach

### 1. Fix GitHubProvider.validateOwner() — capture actual HTTP status

**File**: `src/core/repo-structure/providers/github-provider.ts` (lines 98-106)

Replace the hardcoded `{ status: 404, message: 'Not Found' }` with the actual response status. Use `orgResponse` (the last attempted endpoint) since it represents the final determination.

**Status priority logic**: If `userResponse` returned a more severe error (401/403) and `orgResponse` returned 404, prefer the `userResponse` status — it's the more informative error. If both return the same class of error, use `orgResponse` (last attempt).

```typescript
// Before (bug):
const apiError: GitApiError = {
  status: 404,
  message: 'Not Found',
  ...
};

// After (fix):
const useUserStatus = userResponse.status !== 404 && orgResponse.status === 404;
const response = useUserStatus ? userResponse : orgResponse;
const apiError: GitApiError = {
  status: response.status,
  message: response.statusText,
  ...
};
```

### 2. DRY — delegate github-validator.ts to GitHubProvider

**File**: `src/core/repo-structure/github-validator.ts` (lines 112-157)

The standalone `validateOwner()` has **zero importers** in `src/`. Replace the duplicated implementation with delegation to `GitHubProvider.validateOwner()`, mapping the type field (`'organization'` → `'org'`) to preserve the local interface contract.

```typescript
export async function validateOwner(owner: string, token?: string): Promise<OwnerValidationResult> {
  const provider = createGitHubProvider();
  const result = await provider.validateOwner(owner, token);
  return {
    valid: result.valid,
    type: result.type === 'organization' ? 'org' : result.type,
    error: result.error,
  };
}
```

### 3. Tests

**github-provider.test.ts** — add to existing `validateOwner` describe block:
- 401 on both endpoints → error contains "Authentication Failed"
- 403 on both endpoints → error contains "Permission Denied"
- 403 on user + 404 on org → error contains "Permission Denied" (prefers informative status)

**github-validator.test.ts** — add 401/403 test cases to verify delegation produces correct errors.

## Files Changed

| File | Change |
|------|--------|
| `src/core/repo-structure/providers/github-provider.ts` | Use actual response status in error path |
| `src/core/repo-structure/github-validator.ts` | Delegate to GitHubProvider, map type field |
| `tests/unit/core/repo-structure/github-provider.test.ts` | Add 401/403 validateOwner tests |
| `tests/unit/repo-structure/github-validator.test.ts` | Add 401/403 validateOwner tests |

## No Changes Needed

| File | Reason |
|------|--------|
| `git-error-handler.ts` | Already handles 401/403/404 correctly |
| `git-provider.ts` | `OwnerValidationResult` type unchanged |
| `multi-repo-configurator.ts` | Already calls `provider.validateOwner()` |

## Risks

- **Low**: Type mapping (`'organization'` → `'org'`) in standalone function. Covered by existing tests.
- **None**: No src/ callers of standalone function — delegation can't break production paths.
