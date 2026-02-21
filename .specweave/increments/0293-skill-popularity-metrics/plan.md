# Implementation Plan: Populate Skill Popularity Metrics from APIs

## Overview

Add a server-side popularity metrics fetcher that pulls real GitHub stars/forks and npm download counts for skills, enriches the data layer, and hides zero-value metrics in the UI. The implementation adds a new module (`src/lib/popularity-fetcher.ts`) with TTL-cached API calls, extends the `SkillData` type with `npmPackage`, wires enrichment into the existing data layer, and updates three UI pages to conditionally render metrics.

## Architecture

### Components

- **`src/lib/popularity-fetcher.ts`** (NEW): GitHub + npm API clients with TTL cache. Exports `fetchGitHubMetrics()`, `fetchNpmDownloads()`, and `enrichSkillWithMetrics()`.
- **`src/lib/types.ts`** (MODIFY): Add `npmPackage?: string` to `SkillData`.
- **`prisma/schema.prisma`** (MODIFY): Add `npmPackage String?` to `Skill` model.
- **`src/lib/seed-data.ts`** (MODIFY): Add `npmPackage` values to skills that have real npm packages.
- **`src/lib/data.ts`** (MODIFY): Wire enrichment into `getSkillByName()` and `getSkills()` behind `ENABLE_LIVE_METRICS` flag.
- **`src/app/skills/[name]/page.tsx`** (MODIFY): Hide zero-value Stars/Forks stat cards.
- **`src/app/page.tsx`** (MODIFY): Filter zero-value skills from dashboard aggregation.

### Data Flow

```
User requests skill page
  -> getSkillByName(name)
     -> seed data / KV lookup (existing)
     -> if ENABLE_LIVE_METRICS:
        -> enrichSkillWithMetrics(skill)
           -> fetchGitHubMetrics(skill.repoUrl) [cached]
           -> fetchNpmDownloads(skill.npmPackage) [cached]
           -> merge non-null results into skill object
     -> return enriched skill
```

### TTL Cache Design

```typescript
// Simple Map-based cache (same pattern as existing _publishedCache)
const cache = new Map<string, { data: unknown; ts: number }>();
const TTL = parseInt(process.env.METRICS_CACHE_TTL_SECONDS ?? "3600", 10) * 1000;

function getCached<T>(key: string): T | null {
  const entry = cache.get(key);
  if (entry && Date.now() - entry.ts < TTL) return entry.data as T;
  return null;
}
function setCache<T>(key: string, data: T): void {
  cache.set(key, { data, ts: Date.now() });
}
```

### API Contracts

- **GitHub REST API v3**: `GET https://api.github.com/repos/{owner}/{repo}` -> `{ stargazers_count, forks_count, pushed_at }`
- **npm registry**: `GET https://api.npmjs.org/downloads/point/last-month/{package}` -> `{ downloads }`

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15 (existing)
- **Libraries**: Native `fetch` (no new deps)
- **Testing**: Vitest with `vi.mock` for fetch stubbing

**Architecture Decisions**:

- **In-memory cache over KV**: Simpler, no extra KV bindings needed. Cloudflare Workers have short lifetimes so cache auto-clears. When we add cron refresh later, we'll persist to KV/DB.
- **Feature flag over always-on**: `ENABLE_LIVE_METRICS=true` opt-in avoids breaking production if APIs are slow or rate-limited.
- **Enrich in data layer, not UI**: Centralizes metric fetching so all consumers (pages, API routes) get enriched data.
- **No new npm dependencies**: `fetch` is native in Node.js 18+ and Cloudflare Workers.

## Implementation Phases

### Phase 1: Core Fetcher (T-001, T-002, T-003)
- Build and test `fetchGitHubMetrics()` and `fetchNpmDownloads()`
- Implement TTL cache
- Add `npmPackage` to types and schema

### Phase 2: Data Layer Integration (T-004, T-005)
- Wire enrichment into `getSkillByName()` and `getSkills()`
- Feature flag gating
- Update seed data with `npmPackage` values

### Phase 3: UI Updates (T-006, T-007)
- Hide zero-value metrics on skill detail page
- Adjust homepage aggregation to exclude zeros

### Phase 4: Verification (T-008)
- End-to-end verification
- Run full test suite

## Testing Strategy

- **Unit tests**: Mock `fetch` globally, test each API function in isolation
- **Integration tests**: Test `enrichSkillWithMetrics` with mocked fetchers
- **UI tests**: Snapshot or assertion tests for conditional rendering
- **TDD mode**: RED -> GREEN -> REFACTOR for all new functions

## Technical Challenges

### Challenge 1: Rate Limiting
**Solution**: In-memory TTL cache (1 hour default) plus optional `GITHUB_TOKEN` for 5000 req/hr. The enrichment is also gated by feature flag.
**Risk**: If cache expires during a traffic spike, many concurrent requests could hit the API. Mitigated by the fact that cache is process-level (shared across all requests in the same worker).

### Challenge 2: Slow External API Calls
**Solution**: Use `Promise.allSettled` for parallel fetching with short timeouts (5s). If APIs are slow, cached values or existing seed data are returned.
**Risk**: First request after cache expiry may be slow. Acceptable trade-off vs. cron complexity.

### Challenge 3: URL Parsing Edge Cases
**Solution**: Handle `github.com`, `www.github.com`, trailing slashes, `.git` suffix, and monorepo paths. Reject non-GitHub URLs gracefully.
**Risk**: Some skills may have non-standard URLs. The function returns null for unparseable URLs.
