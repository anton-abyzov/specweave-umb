# Implementation Plan: Repo Health Check for Skill Detail Pages

## Overview

Add an on-demand GitHub repository health check to skill detail pages. The architecture follows the existing `external-scan-store` pattern: a KV-backed store module, a Next.js API route, and a client component for async rendering. Three new files plus modifications to two existing files.

## Architecture

### Components

1. **`src/lib/repo-health-store.ts`** -- KV-backed storage for repo health results. Follows the exact same pattern as `external-scan-store.ts`: `getKV()` helper using `getCloudflareContext` + `getWorkerEnv` fallback, typed interfaces, get/put with TTL.

2. **`src/lib/repo-health-checker.ts`** -- Pure function that calls the GitHub API to determine repo status. Parses `owner/repo` from a GitHub URL, calls `GET https://api.github.com/repos/{owner}/{repo}`, and returns `ONLINE`, `OFFLINE`, or `STALE` based on HTTP status and `pushed_at` date. Uses optional `GITHUB_TOKEN` env var for authenticated requests (higher rate limits).

3. **`src/app/api/v1/skills/[name]/repo-health/route.ts`** -- Next.js API route. Looks up the skill via `getSkillByName()`, checks KV cache, falls back to live GitHub check, stores result in KV, returns JSON.

4. **`src/app/skills/[name]/RepoHealthBadge.tsx`** -- `"use client"` component. Fetches `/api/v1/skills/{name}/repo-health` on mount, shows loading skeleton, then renders a colored status pill (ONLINE=green, OFFLINE=red, STALE=gray).

5. **Modified: `src/app/skills/[name]/page.tsx`** -- Import and render `RepoHealthBadge` next to the existing Repository link.

6. **Modified: `src/lib/env.d.ts`** -- Add `REPO_HEALTH_KV: KVNamespace` to `CloudflareEnv`.

7. **Modified: `wrangler.jsonc`** -- Add `REPO_HEALTH_KV` binding.

### Data Model

```typescript
interface RepoHealthResult {
  status: "ONLINE" | "OFFLINE" | "STALE";
  checkedAt: string;       // ISO 8601
  lastCommitAt: string | null;  // ISO 8601, from GitHub pushed_at
}
```

KV key pattern: `repo-health:{skillName}`
KV TTL: 86400 seconds (24 hours)

### API Contracts

#### `GET /api/v1/skills/[name]/repo-health`

**Success (200)**:
```json
{
  "status": "ONLINE",
  "checkedAt": "2026-02-20T19:00:00.000Z",
  "lastCommitAt": "2026-02-15T10:30:00.000Z"
}
```

**Skill not found (404)**:
```json
{
  "error": "Skill not found",
  "name": "nonexistent-skill"
}
```

**Headers**: `Cache-Control: public, max-age=3600`

## Technology Stack

- **Framework**: Next.js 15 (App Router) on Cloudflare Workers
- **Storage**: Cloudflare KV (`REPO_HEALTH_KV`)
- **External API**: GitHub REST API v3 (`/repos/{owner}/{repo}`)
- **Testing**: Vitest with `vi.hoisted()` + `vi.mock()` for ESM KV mocking

**Architecture Decisions**:

- **KV over in-memory cache**: KV persists across worker restarts and is shared across edge locations. In-memory caching would not survive Cloudflare's per-request worker model.
- **Lazy check (on-demand) over cron**: Avoids checking repos that nobody views. Cron would waste API quota on rarely-viewed skills. A cron can be added later if needed.
- **Client component over SSR**: The health check should not block page rendering. Server-side fetching would add latency to every page load. A `"use client"` component with `useEffect` provides progressive enhancement.
- **Separate KV namespace**: Dedicated `REPO_HEALTH_KV` keeps health data isolated from scan data. Clear TTL policy. Easy to purge independently.
- **STALE threshold at 365 days**: Aligns with common open-source abandonment signals. Configurable in the future via env var if needed.

## Implementation Phases

### Phase 1: Infrastructure (T-001 to T-003)
- Add `REPO_HEALTH_KV` binding to `env.d.ts` and `wrangler.jsonc`
- Implement `repo-health-store.ts` (KV get/put with TTL)
- Implement `repo-health-checker.ts` (GitHub API call + status logic)

### Phase 2: API Route (T-004)
- Implement `GET /api/v1/skills/[name]/repo-health/route.ts`
- Wire up cache-first pattern: check KV -> miss -> call checker -> store -> return

### Phase 3: Client Component (T-005 to T-006)
- Implement `RepoHealthBadge.tsx` client component
- Integrate into skill detail page

## Testing Strategy

TDD mode: RED -> GREEN -> REFACTOR for each task.

- **Unit tests**: `repo-health-store.test.ts` (KV mock), `repo-health-checker.test.ts` (fetch mock), `route.test.ts` (integration)
- **Component test**: `RepoHealthBadge.test.tsx` (mock fetch, verify render states)
- **Coverage target**: >80%
- **Mocking pattern**: Follow existing `vi.hoisted()` + `vi.mock("@opennextjs/cloudflare")` pattern from `external-scan-store.test.ts`

## Technical Challenges

### Challenge 1: GitHub API Rate Limiting
**Solution**: Use optional `GITHUB_TOKEN` env var for authenticated requests (5000 req/hr vs 60 req/hr). KV caching with 24h TTL drastically reduces call volume. On rate limit (HTTP 403/429), return OFFLINE status gracefully.
**Risk**: Low. Even unauthenticated, 60 req/hr is sufficient given KV caching.

### Challenge 2: Parsing `owner/repo` from Diverse URL Formats
**Solution**: Use `new URL(repoUrl)` to parse, then extract path segments. Handle trailing slashes, `.git` suffix, tree/blob URLs. Return null on parse failure.
**Risk**: Low. `repoUrl` is validated on submission via `SubmissionCreateSchema`.

### Challenge 3: KV Not Available During Build
**Solution**: Follow existing pattern -- wrap KV access in try/catch. The `getKV()` helper mirrors `external-scan-store.ts` which gracefully handles missing KV during `next build`.
**Risk**: None. Pattern is proven.
