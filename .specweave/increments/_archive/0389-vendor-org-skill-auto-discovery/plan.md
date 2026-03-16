# Implementation Plan: Vendor org skill auto-discovery and import

## Overview

Add a new `vendor-org-discovery` crawl source to the Hetzner VM crawl-worker that periodically enumerates all public repos from vendor organizations and discovers SKILL.md files. The source follows the exact same patterns as `github-sharded.js` (token rotation, `InlineSubmitter`, adaptive delay) and plugs into the existing scheduler. A companion admin endpoint on the Next.js platform enables on-demand triggering. Submissions flow through the standard bulk pipeline where the existing vendor fast-path handles `VENDOR_APPROVED` state transitions.

## Architecture

### Component Diagram

```
  Scheduler (VM-2)               Platform (Cloudflare Workers)
  ┌─────────────────────┐       ┌────────────────────────────────┐
  │ scheduler.js        │       │                                │
  │  ├─ github-graphql  │       │  POST /api/v1/submissions/bulk │
  │  ├─ sourcegraph     │       │        ↓                       │
  │  ├─ submission-scan │       │  processSubmission()           │
  │  └─ vendor-org-disc ←──────►│    isVendorRepo() → fast-path │
  │       ↓             │  HTTP │        ↓                       │
  │  InlineSubmitter    │───────│  VENDOR_APPROVED → PUBLISHED   │
  └─────────────────────┘       │                                │
                                │  POST /admin/discovery/        │
                                │       vendor-orgs              │
                                │    ↓                           │
                                │  runVendorOrgDiscovery()       │
                                │    ↓                           │
                                │  DiscoveryRecord (dedup)       │
                                └────────────────────────────────┘
```

### Components

#### 1. `crawl-worker/sources/vendor-org-discovery.js` (NEW)

The main crawl source module. Follows the scheduler source contract:

```javascript
export default async function crawl(config) → { totalDiscovered, totalSubmitted, errors, orgBreakdown, durationMs }
```

**Internal structure:**
- `createTokenRotator(tokensStr)` — reused from `github-sharded.js` pattern
- `computeDelay(remaining, resetEpoch)` — adaptive delay, reused pattern
- `listOrgRepos(org, getToken)` — paginated `GET /orgs/{org}/repos?type=public&per_page=100&sort=updated`
- `scanRepoTree(owner, repo, getToken)` — `GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1` to find SKILL.md files
- Inline skill path filtering via regex (mirrors `isAgentConfigPath` logic — no TS imports in .js modules)

**Design decision**: The source module is a plain .js file (ESM) matching all other crawl-worker sources. The VENDOR_ORGS list is duplicated as a constant array (matching the existing pattern in `vendor-detect.js`). This avoids cross-importing from the TypeScript `trusted-orgs.ts`.

#### 2. `crawl-worker/scheduler.js` (MODIFIED)

Add entries to `SOURCE_TIMEOUTS` and `SOURCE_COOLDOWNS` maps:
- Timeout: 30 minutes (`30 * 60 * 1000`)
- Cooldown: 6 hours (`6 * 60 * 60 * 1000`)

#### 3. `crawl-worker/server.js` (MODIFIED)

Add `"vendor-org-discovery"` to the `VALID_SOURCES` array so the HTTP `/crawl` endpoint also accepts it for ad-hoc triggering.

#### 4. `src/lib/crawler/vendor-org-discovery.ts` (NEW)

Platform-side discovery logic for the admin endpoint. Shares the same algorithmic approach as the crawl-worker source but uses:
- `TokenRotator` from `github-discovery.ts` (not raw token strings)
- `hasBeenDiscovered()` / `markDiscovered()` / `logDiscoveryRun()` from `discovery-dedup.ts`
- `WORKER_SELF_REFERENCE` for submission via platform's own API

This mirrors how `github-discovery.ts` is the platform-side counterpart to `github-sharded.js`.

#### 5. `src/app/api/v1/admin/discovery/vendor-orgs/route.ts` (NEW)

Next.js API route for the admin endpoint. Follows the exact pattern of the existing `admin/discovery/route.ts`:
- Auth: `hasInternalAuth(request)` OR `requireRole(request, "SUPER_ADMIN")`
- Parses optional body: `{ orgs?: string[], force?: boolean, dryRun?: boolean }`
- Calls `runVendorOrgDiscovery()` from the platform-side module
- Returns JSON with `candidatesFound`, `newSubmissions`, `skippedDedup`, `skippedFiltered`, `orgBreakdown`, `durationMs`

#### 6. `src/lib/crawler/github-discovery.ts` (MODIFIED)

Register `"vendor-orgs"` in the `SOURCE_FUNCTIONS` map so the general discovery endpoint can include vendor org scanning when explicitly requested via the `sources` option.

### Data Model

No new database models. Reuses existing:

- **`DiscoveryRecord`** — composite key `(repoFullName, skillPath)`, fields: `source`, `submissionId`, `firstSeenAt`, `lastSeenAt`
- **`DiscoveryRunLog`** — fields: `trigger`, `candidatesFound`, `newSubmissions`, `skippedDedup`, `errors`, `durationMs`, `sourceBreakdown`
- **`Submission`** — existing model, receives entries via `/api/v1/submissions/bulk`

### API Contracts

#### `POST /api/v1/admin/discovery/vendor-orgs`

**Auth**: `X-Internal-Key` header or `SUPER_ADMIN` JWT

**Request body** (all optional):
```json
{
  "orgs": ["anthropics", "openai"],
  "force": false,
  "dryRun": false
}
```

**Response** (200 OK):
```json
{
  "ok": true,
  "candidatesFound": 42,
  "newSubmissions": 35,
  "skippedDedup": 5,
  "skippedFiltered": 2,
  "durationMs": 15234,
  "orgBreakdown": {
    "anthropics": { "repos": 12, "skills": 28 },
    "openai": { "repos": 3, "skills": 7 }
  }
}
```

#### Crawl source return (scheduler contract)

```json
{
  "totalDiscovered": 42,
  "totalSubmitted": 35,
  "skippedDedup": 5,
  "skippedFiltered": 2,
  "errors": [],
  "orgBreakdown": { "anthropics": 28, "openai": 7 },
  "durationMs": 15234
}
```

## Technology Stack

- **Crawl worker**: Node.js ESM (plain .js), matching existing source modules
- **Platform**: Next.js 15 / TypeScript on Cloudflare Workers
- **GitHub API**: REST API v3 for org listing and Trees API for file discovery
- **Submission**: Existing `InlineSubmitter` → `POST /api/v1/submissions/bulk`
- **Dedup**: Existing `DiscoveryRecord` Prisma model via `discovery-dedup.ts`
- **Auth**: Existing `hasInternalAuth` + `requireRole` middleware

## Architecture Decisions

### ADR-1: Duplicate VENDOR_ORGS in crawl-worker vs single source of truth

**Decision**: Duplicate the VENDOR_ORGS array as a plain JS constant in `vendor-org-discovery.js`, matching the existing pattern in `vendor-detect.js`.

**Rationale**: The crawl-worker is a plain Node.js ESM project without TypeScript compilation. Importing from `src/lib/trust/trusted-orgs.ts` would require a build step. The existing `vendor-detect.js` already duplicates this list, establishing the precedent. The list changes extremely rarely (only when adding new vendor organizations, which is out of scope for this increment).

**Alternatives considered**:
1. Shared JSON file — adds complexity for a 4-element array
2. Environment variable — brittle, harder to validate
3. TypeScript build step for crawl-worker — massive scope creep

### ADR-2: Two implementations (crawl-worker + platform)

**Decision**: Create separate but algorithmically identical implementations — one in JS for the crawl-worker scheduler, one in TS for the platform admin endpoint.

**Rationale**: This mirrors the existing pattern where `github-sharded.js` (crawl-worker) and `github-discovery.ts` (platform) serve the same conceptual purpose but run in different environments. The crawl-worker version runs on Hetzner VMs with raw `fetch` and `InlineSubmitter`; the platform version runs on Cloudflare Workers with `WORKER_SELF_REFERENCE` service binding and Prisma-based dedup. The shared algorithm is simple enough (~150 lines) that duplication is manageable.

### ADR-3: Skip forks and zero-star repos at enumeration time

**Decision**: Filter out `fork: true` and `stargazers_count: 0` repos during the `GET /orgs/{org}/repos` enumeration, before the tree scan phase.

**Rationale**: Vendor orgs (especially `google`) have hundreds of public repos. Most are SDKs, documentation, or samples without SKILL.md files. Filtering at enumeration time avoids wasting Trees API calls. Zero-star forks are unlikely to contain original skills. Original repos with 0 stars are kept because vendor orgs may publish new repos that haven't gained stars yet — wait, the spec says skip zero-star repos. We follow the spec.

**Risk**: A new vendor repo with 0 stars could be missed initially. Mitigation: the admin endpoint with `force: true` can override this filter, and repos gain stars quickly after announcement.

### ADR-4: Dedup at skill-path level via DiscoveryRecord

**Decision**: Use the existing `DiscoveryRecord` table with composite key `(repoFullName, skillPath)` for deduplication, with a 30-day stale threshold.

**Rationale**: This is the exact mechanism used by `github-discovery.ts`. Records older than 30 days are treated as stale and re-submitted, ensuring periodic refresh. The `force` parameter on the admin endpoint bypasses this check entirely for full re-scans.

## Implementation Phases

### Phase 1: Crawl-worker source module (US-001, US-002 partial, US-005)

1. Create `crawl-worker/sources/vendor-org-discovery.js` with:
   - VENDOR_ORGS constant array
   - Token rotation (reuse `createTokenRotator` pattern)
   - `listOrgRepos()` with pagination and filtering
   - `scanRepoTree()` with SKILL.md detection
   - `InlineSubmitter` integration for bulk submission
   - Return stats object matching scheduler contract

2. Update `crawl-worker/server.js`:
   - Add `"vendor-org-discovery"` to `VALID_SOURCES`

3. Update `crawl-worker/scheduler.js`:
   - Add `"vendor-org-discovery"` to `SOURCE_TIMEOUTS` (30 min)
   - Add `"vendor-org-discovery"` to `SOURCE_COOLDOWNS` (6 hours)

### Phase 2: Platform-side admin endpoint (US-004, US-002 complete)

4. Create `src/lib/crawler/vendor-org-discovery.ts` with:
   - Shared discovery logic using `TokenRotator`
   - Dedup integration via `hasBeenDiscovered` / `markDiscovered`
   - `logDiscoveryRun()` logging
   - `force` parameter to bypass dedup
   - `dryRun` parameter for preview mode

5. Create `src/app/api/v1/admin/discovery/vendor-orgs/route.ts` with:
   - Auth check (internal key or SUPER_ADMIN)
   - Request parsing (orgs, force, dryRun)
   - Call `runVendorOrgDiscovery()`
   - JSON response

6. Update `src/lib/crawler/github-discovery.ts`:
   - Register `"vendor-orgs"` in `SOURCE_FUNCTIONS` map

### Phase 3: Deployment and VM configuration (US-003)

7. Update VM-2's `.env` file:
   - Add `vendor-org-discovery` to `ASSIGNED_SOURCES`

8. Deploy crawl-worker to all VMs (only VM-2 will run the new source)

## Testing Strategy

### Unit tests (crawl-worker)

- `crawl-worker/__tests__/vendor-org-discovery.test.js`:
  - Mock `fetch` for org repo listing, tree scan, and bulk submission
  - Verify fork/zero-star filtering
  - Verify SKILL.md path detection and agent config exclusion
  - Verify token rotation
  - Verify `InlineSubmitter` integration (buffering, flushing)
  - Verify rate limit handling (adaptive delay, backoff on 403/429)
  - Verify return stats format matches scheduler contract

### Unit tests (platform)

- `src/lib/crawler/__tests__/vendor-org-discovery.test.ts`:
  - Mock GitHub API responses and dedup functions
  - Verify org filtering, force mode, dry run
  - Verify dedup integration (hasBeenDiscovered/markDiscovered)
  - Verify run logging

- `src/app/api/v1/admin/discovery/vendor-orgs/__tests__/route.test.ts`:
  - Auth tests (internal key, JWT, unauthorized)
  - Request parsing (orgs filter, force, dryRun)
  - Response format verification

### Integration tests

- End-to-end submission flow: vendor-org-discovery → bulk submit → processSubmission → VENDOR_APPROVED
- Verify no duplicate submissions on consecutive runs (dedup)
- Verify force mode re-submits previously discovered skills

## Technical Challenges

### Challenge 1: Large org repo counts (google has 2000+ public repos)

**Solution**: Paginate with `per_page=100`, apply fork/zero-star filter at enumeration time to reduce tree scan volume. Use adaptive delay between API calls. The 30-minute timeout provides ample headroom — at 200ms per API call with 4 orgs averaging 200 qualifying repos each, the tree scan phase takes ~3 minutes.

**Risk**: GitHub rate limit exhaustion. **Mitigation**: Token rotation distributes load across multiple tokens. The 6-hour cooldown ensures at most 4 runs per day.

### Challenge 2: Agent config path exclusion without TS imports

**Solution**: Inline a simplified regex check in the JS module. The crawl-worker's `repo-files.js` already imports `isAgentConfigPath` — we can follow the same approach using a dynamic import or inline the same regex pattern used by `skill-path-validation.ts`:

```javascript
const AGENT_CONFIG_RE = /(?:^|\/)\.(?:cursor|windsurf|aider|cline|roo|ai|github\/copilot)/i;
function isAgentConfigPath(path) {
  return AGENT_CONFIG_RE.test(path);
}
```

**Risk**: Pattern drift between TS and JS versions. **Mitigation**: The pattern is stable and rarely changes. The existing `vendor-detect.js` already establishes this duplication pattern.

### Challenge 3: Keeping crawl-worker and platform implementations aligned

**Solution**: Both implementations follow the same two-phase algorithm (list repos → scan trees). The platform version adds dedup and logging. The crawl-worker version adds `InlineSubmitter` batching. Both use the same GitHub API endpoints and filtering logic.

**Risk**: Bug in one but not the other. **Mitigation**: Comprehensive unit tests for both. The admin endpoint is a secondary path — the scheduled crawl-worker source is the primary mechanism.
