# Implementation Plan: Fix submit page skill discovery bug + remove selection step

## Overview

Three surgical changes across 4 files in `vskill-platform`. No new files, no new endpoints, no database changes. The work is a bug fix (error masking), a code path fix (wrong endpoint), and dead code removal.

## Architecture

### Components Modified

1. **`src/lib/scanner.ts`** -- `DiscoveryResult` type + `discoverSkillsEnhanced` function
2. **`src/app/api/v1/submissions/discover/route.ts`** -- discover route handler
3. **`src/app/submit/page.tsx`** -- submit page client component
4. **`src/app/api/v1/submissions/discover/__tests__/route.test.ts`** -- discover route tests

### Data Model Changes

**`DiscoveryResult` (type-only, no persistence change)**:
```typescript
export interface DiscoveryResult {
  skills: DiscoveredSkill[];
  count: number;
  plugins: DiscoveredPlugin[] | null;
  marketplace: { name: string; version: string } | null;
  truncated: boolean;
  error?: {                          // NEW
    code: "rate_limited" | "auth_failed" | "api_error";
    message: string;
  };
}
```

This is a purely additive, backward-compatible change. Existing callers that don't check `error` continue to work -- they just see `skills: []` as before.

### API Contract Changes

**`POST /api/v1/submissions/discover`**:

Current behavior:
- GitHub API error -> empty skills -> 200 with `skills: []`
- Client shows "No SKILL.md files found" (misleading)

New behavior:
- GitHub 403 (rate limit) -> `result.error.code === "rate_limited"` -> **502** with `{ error: "GitHub API rate limit exceeded...", code: "rate_limited" }`
- GitHub 401 (auth fail) -> `result.error.code === "auth_failed"` -> **502** with `{ error: "GitHub authentication issue...", code: "auth_failed" }`
- Other GitHub errors -> `result.error.code === "api_error"` -> **502** with `{ error: "<message>", code: "api_error" }`
- Empty repo (no error) -> 200 with `skills: []` (unchanged)
- Skills found (no error) -> 200 with full result (unchanged)

**`POST /api/v1/submissions`** (no change): Individual endpoint already works for client-side use. The page will switch from attempting `/api/v1/submissions/bulk` to always using individual submissions.

## Architecture Decisions

### AD-1: Error field on result vs throwing exceptions
**Decision**: Add optional `error` field to `DiscoveryResult` instead of throwing.
**Rationale**: The function already returns a structured result. Adding an error field preserves backward compatibility -- callers that don't check the field still get `skills: []`. Throwing would require all callers to wrap in try/catch and would break the existing API contract where empty results are valid.

### AD-2: HTTP 502 for upstream errors (not 503 or 500)
**Decision**: Return 502 Bad Gateway when GitHub API fails.
**Rationale**: 502 semantically means "the server received an invalid response from an upstream server" which is exactly what's happening. 503 implies our server is down. 500 is too generic and doesn't help clients distinguish between our bugs and upstream issues.

### AD-3: Individual submissions instead of client-facing bulk endpoint
**Decision**: Use `POST /api/v1/submissions` per-skill rather than creating a new client-facing bulk endpoint.
**Rationale**: The existing `/api/v1/submissions/bulk` is intentionally internal-only (requires `X-Internal-Key`). Creating a client-facing bulk endpoint would require auth plumbing, rate limit adjustments, and testing. The individual endpoint already handles user cookies, dedup, rate limiting, and SKILL.md existence checks. Sequential individual calls are sufficient for the typical case (1-30 skills).

### AD-4: Submit all skills, let server dedup
**Decision**: Client submits ALL discovered skills without filtering. Server dedup handles already-verified/pending.
**Rationale**: The `POST /api/v1/submissions` endpoint already has robust dedup logic (`checkSubmissionDedup`). It returns `{ duplicate: true }` for pending skills and `{ alreadyVerified: true }` for verified skills. Client-side filtering would duplicate logic and could get out of sync. The server responses provide the data needed for the done-phase display.

## Implementation Phases

### Phase 1: Error propagation in scanner (US-001: AC-US1-01 through AC-US1-04)
1. Add `error?` field to `DiscoveryResult` interface
2. In `discoverSkillsEnhanced`, catch GitHub API non-success responses in:
   - `detectBranch()` -- if this fails with 403/401, the whole discovery is blocked
   - Tree fetch (`/git/trees/`) -- the main discovery path
   - Marketplace path already returns `null` on error (falls through to tree path)
3. Map HTTP status codes to error codes:
   - 403 -> `rate_limited`
   - 401 -> `auth_failed`
   - Others (5xx, 404 for private repos) -> `api_error`

**Key implementation detail**: The error should be set at the earliest point of failure. If `detectBranch` fails with 403, we should not attempt the tree fetch -- return early with the error. The marketplace path (`fetchMarketplaceManifest`) already returns `null` on any failure, so the tree path is the critical error point.

### Phase 2: Route layer error handling (US-001: AC-US1-05 through AC-US1-07)
1. Add `console.warn` when `githubToken` is undefined
2. After `discoverSkillsEnhanced` returns, check `result.error`:
   - If set: return 502 with error message and code
   - If not set: continue with existing enrichment + 200 response flow

### Phase 3: Client-side changes (US-002, US-003, US-004)
1. Remove `Phase` "select" value
2. Remove state: `selected`, `collapsed`
3. Remove functions: `toggleSkill`, `toggleAll`, `togglePlugin`, `toggleCollapse`
4. Remove `StatusBadge` component and `btnSmall` style
5. Remove entire select rendering block
6. Rewrite `handleDiscover` to transition directly to submission after discovery
7. Rewrite `handleSubmitAll` to:
   - Submit all `discovered` skills (not `selected`)
   - Use only `POST /api/v1/submissions` (remove bulk attempt + legacy fallback)
   - Map response shapes: `{ duplicate: true }` -> "Already pending", `{ alreadyVerified: true }` -> "Already verified"
8. Clean up `reset()` to remove references to deleted state
9. Update `SubmissionResult` interface to capture dedup states from individual endpoint

## Testing Strategy

### Existing tests to update
- `src/app/api/v1/submissions/discover/__tests__/route.test.ts` -- add tests for error field -> 502 mapping

### New test cases
1. **Scanner error propagation**: When `discoverSkillsEnhanced` encounters a 403 from GitHub, it returns `error: { code: "rate_limited", ... }`
2. **Scanner error propagation**: When `discoverSkillsEnhanced` encounters a 401 from GitHub, it returns `error: { code: "auth_failed", ... }`
3. **Route error handling**: When `result.error` is set, route returns 502 with error message
4. **Route backward compat**: When `result.error` is undefined and skills are empty, route returns 200
5. **Token warning**: When `GITHUB_TOKEN` is undefined, console.warn is called

### No client-side test changes needed
The page.tsx is a client component without existing unit tests. The behavior changes are best validated through manual testing and the existing E2E flows.

## Technical Challenges

### Challenge 1: Error detection point in `discoverSkillsEnhanced`
**Problem**: The function has multiple GitHub API call sites (detectBranch, marketplace fetch, tree fetch, plugin directory listing). Need to detect errors at the right level.
**Solution**: The critical path is the tree fetch (line 449-453 in scanner.ts): `if (!res.ok) return empty;`. This is where we add error detection. The marketplace path already returns `null` on failure and falls through. `detectBranch` silently defaults to "main" on failure (line 308), which is acceptable -- a wrong branch is better than no attempt.
**Risk**: Low. The error field is additive and only populated on the tree fetch path.

### Challenge 2: Client response mapping from individual endpoint
**Problem**: The individual `POST /api/v1/submissions` endpoint has three response shapes: `{ id, state, createdAt }` (new submission), `{ id, state, duplicate: true }` (pending dedup), `{ skillId, skillName, alreadyVerified: true }` (verified dedup). The client `SubmissionResult` interface needs to handle all three.
**Solution**: Add `duplicate` and `alreadyVerified` fields to the client-side result mapping. Map `duplicate: true` -> `status: "skipped"` and `alreadyVerified: true` -> `status: "already-verified"` to match the existing done-phase badge logic.
