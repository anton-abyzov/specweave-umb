# Implementation Plan: Vendor & Provider Skill Discovery Enhancement

## Overview

Four-part increment spanning two repos (vskill-platform, vskill). US-001 is a deploy-only fix (push .env.vm2 to VM-2). US-002 adds post-sort dedup to the existing search pipeline. US-003 surfaces the new `alternateRepos` field in CLI output. US-004 creates a typed provider registry that replaces the flat `VENDOR_ORGS`/`TRUSTED_ORGS` constants while preserving full backward compatibility.

No database schema changes. No new infrastructure. All changes are additive TypeScript/JS modifications to existing modules.

## Architecture

### Component Map

```
crawl-worker (VM-2)                 vskill-platform (CF Workers)            vskill CLI
+---------------------------+       +--------------------------------+      +--------------------+
| .env.vm2                  |       | src/lib/trust/                 |      | src/api/client.ts  |
|  ASSIGNED_SOURCES=...     |       |   provider-registry.ts  [NEW]  |      |   SkillSearchResult|
|  vendor-org-discovery     |       |   trusted-orgs.ts  [MODIFIED]  |      |   + alternateRepos |
+---------------------------+       +--------------------------------+      +--------------------+
| sources/                  |       | src/lib/search.ts  [MODIFIED]  |      | src/commands/       |
|   vendor-org-discovery.js |       |   dedup logic post-sort        |      |   find.ts [MODIFIED]|
|   [SYNC vendorOrgs const] |       +--------------------------------+      |   + alternate lines |
+---------------------------+       | src/app/api/v1/skills/search/  |      +--------------------+
                                    |   route.ts  [MODIFIED]         |
                                    |   dedup applied after merge    |
                                    +--------------------------------+
```

### Data Flow: Search Dedup

```
Edge KV shards ──> searchSkillsEdge() ──> sorted results ──+
                                                            |
Postgres fallback ──> searchSkills() ──> sorted results ───>+ merge
                                                            |
                                                            v
                                         route.ts final sort + blocklist enrichment
                                                            |
                                                            v
                                         deduplicateBySkill() [NEW]
                                         group by ownerSlug+skillSlug
                                         keep highest githubStars
                                         attach alternateRepos
                                                            |
                                                            v
                                         JSON response with alternateRepos
```

Dedup runs once in route.ts after the final merge/sort, not inside `searchSkillsEdge` or `searchSkills`. This keeps both search functions pure (no dedup awareness) and ensures dedup applies regardless of which search path contributed results.

### Data Flow: Provider Registry

```
provider-registry.ts (NEW -- source of truth)
  |
  |-- PROVIDER_REGISTRY: readonly ProviderDefinition[]
  |-- derives VENDOR_ORG_IDS: Set<string>
  |-- derives TRUSTED_ORG_IDS: Set<string>
  |
  v
trusted-orgs.ts (MODIFIED -- thin re-export layer)
  |-- VENDOR_ORGS = VENDOR_ORG_IDS  (same Set<string>)
  |-- TRUSTED_ORGS = derived from registry + extra trusted orgs
  |-- isVendorOrg(), isTrustedOrg(), checkVendorRepo() -- unchanged signatures
  |
  v
crawl-worker/sources/vendor-org-discovery.js
  |-- VENDOR_ORGS array -- manually synced from registry
  |-- SYNC comment references provider-registry.ts
```

### Components

**1. provider-registry.ts** (new file, vskill-platform)

Single source of truth for provider definitions. Read-only array, not a database table.

```typescript
interface ProviderDefinition {
  id: string;                              // e.g. "anthropics"
  type: "github-org" | "external-api";
  name: string;                            // human-readable
  trustLevel: "vendor" | "trusted" | "community";
  config: Record<string, unknown>;         // future: API keys, endpoints
}
```

**2. trusted-orgs.ts** (modified, vskill-platform)

Imports `PROVIDER_REGISTRY` and derives `VENDOR_ORGS` and `TRUSTED_ORGS` from it. All existing exports remain identical in type and value. The additional trusted-only orgs (`github`, `anton-abyzov`) are added via a `TRUSTED_ONLY_ORGS` local constant merged with registry-derived sets.

**3. search.ts** (unchanged)

`searchSkillsEdge` and `searchSkills` remain pure search functions. They return raw results without dedup. This is intentional: dedup is a presentation concern, not a storage or retrieval concern.

**4. route.ts** (modified, search API)

New `deduplicateBySkill()` helper applied after blocklist enrichment and before the final response. Groups results by `ownerSlug + skillSlug`, picks the entry with highest `githubStars` as canonical, and attaches `alternateRepos` with the remaining entries from the group.

**5. client.ts** (modified, vskill CLI)

`SkillSearchResult` gains `alternateRepos?: Array<{ ownerSlug: string; repoSlug: string; repoUrl: string }>`. The `searchSkills` function maps it from the raw API response.

**6. find.ts** (modified, vskill CLI)

TTY output: renders `also: owner/other-repo` in dim text below each result that has alternates. JSON output: includes `alternateRepos` array. Piped output: appends alternate repos as tab-separated field.

**7. vendor-org-discovery.js** (sync only, crawl-worker)

The `VENDOR_ORGS` array on line 20 must match the `id` fields from `PROVIDER_REGISTRY` where `type === "github-org"` and `trustLevel === "vendor"`. Updated sync comment to reference `provider-registry.ts` instead of `trusted-orgs.ts`.

### API Contract Changes

**GET /api/v1/skills/search?q=...**

Response body change (additive, backward-compatible):

```
SearchResult {
  ...existing fields...
  alternateRepos?: Array<{
    ownerSlug: string;
    repoSlug: string;
    repoUrl: string;
  }>;
}
```

`alternateRepos` is undefined when no duplicates exist for that skill. Present (non-empty array) only when the same `ownerSlug + skillSlug` appeared in multiple repos.

No other API endpoints change.

## Architecture Decisions

### AD-1: Dedup at search-response time, not at index/crawl time

**Decision**: Apply dedup in route.ts after the final sorted merge, not during KV index building or at crawl time.

**Rationale**: (1) The KV index must remain a faithful representation of all indexed skills for other consumers (admin dashboards, analytics). (2) Dedup grouping depends on sort order (highest stars wins), which varies by query relevance. (3) Centralizing dedup in one place (route.ts) avoids duplicating logic in searchSkillsEdge, searchSkills, and the index builder.

**Trade-off**: Slightly more items returned from KV/Postgres before trimming. Negligible performance impact since result sets are already limited to 50 max.

### AD-2: Provider registry as static TypeScript, not database

**Decision**: `PROVIDER_REGISTRY` is a `const` array in a `.ts` file, not a DB table.

**Rationale**: (1) Trust checks (`isVendorOrg`, `isTrustedOrg`) are called on every submission and search -- they must be zero-latency. (2) Provider additions are rare (new vendor orgs emerge quarterly at most). (3) The crawl-worker JS copy must be kept in sync manually regardless of storage choice, so a DB table doesn't reduce sync burden. (4) Matches the existing zero-DB-dependency pattern for trust checks.

**Future**: When external provider APIs (Smithery, Codex) are added, their config (API keys, rate limits) will use the `config` field. Connection secrets will still live in Cloudflare secrets / env vars, with the registry holding only the structural definition.

### AD-3: Canonical selection by githubStars

**Decision**: When multiple repos from the same org contain the same skillSlug, the repo with the highest `githubStars` becomes the canonical entry.

**Rationale**: Stars are the most stable popularity signal available in the search index. The alternative (latest updated) would require additional timestamp fields not currently in `SearchIndexEntry`. Stars are already the primary sort factor in both edge and Postgres paths.

### AD-4: alternateRepos is optional, not always-present empty array

**Decision**: `alternateRepos` is `undefined` when there are no alternates, not `[]`.

**Rationale**: (1) Keeps the JSON response lean -- most results have no duplicates. (2) CLI display logic uses a simple truthiness check (`if (r.alternateRepos)`) rather than length check. (3) Matches the existing pattern of optional fields in `SearchResult` (e.g., `isTainted`, `threatType`).

## Technology Stack

- **Language**: TypeScript (vskill-platform, vskill CLI), JavaScript (crawl-worker)
- **Frameworks**: Next.js 15 (vskill-platform), Node.js ESM (vskill CLI)
- **Testing**: Vitest (unit tests)
- **Deployment**: Cloudflare Workers (vskill-platform), Docker on Hetzner VMs (crawl-worker)

No new dependencies. No schema migrations.

## Implementation Phases

### Phase 1: Provider Registry Foundation (US-004)

Build the registry first because US-001 deployment depends on having the correct VENDOR_ORGS list, and migrating trusted-orgs.ts to use the registry establishes the single source of truth before any other changes.

1. Create `src/lib/trust/provider-registry.ts` with `ProviderDefinition` type and `PROVIDER_REGISTRY` constant
2. Migrate `trusted-orgs.ts` to derive `VENDOR_ORGS` and `TRUSTED_ORGS` from the registry
3. Write equivalence tests verifying identical behavior
4. Update crawl-worker `vendor-org-discovery.js` sync comment

### Phase 2: Deploy vendor-org-discovery (US-001)

Pure deployment action. The code already exists.

1. Verify `.env.vm2` has `vendor-org-discovery` in `ASSIGNED_SOURCES` (confirmed: already present locally)
2. Run `deploy.sh` to push to all VMs (VM-2 picks up the new .env.vm2)
3. Verify health endpoint shows `vendor-org-discovery` as active source
4. Trigger on-demand discovery via admin endpoint to confirm skills are indexed

### Phase 3: Search Dedup (US-002)

1. Add `alternateRepos` to `SearchResult` interface in `search.ts`
2. Implement `deduplicateBySkill()` function in search route
3. Apply dedup in route.ts after enrichment, before response
4. Write unit tests for dedup logic (no duplicates, same-org collapse, mixed vendors)

### Phase 4: CLI Display (US-003)

1. Add `alternateRepos` to `SkillSearchResult` in `client.ts`
2. Map `alternateRepos` from API response in `searchSkills()`
3. Update TTY display in `find.ts` to show alternate repos
4. Update piped (non-TTY) output
5. Ensure `--json` output includes `alternateRepos`

## Testing Strategy

**Unit tests** (Vitest):
- Provider registry: equivalence tests (derived sets match current hardcoded values)
- Dedup function: 3+ test cases covering no-dups, same-org collapse, cross-org preservation
- trusted-orgs backward compatibility: all existing function return values unchanged

**Integration verification** (manual, post-deploy):
- `vskill find frontend-design` returns Anthropic results with CERTIFIED tier
- Duplicate skills from same vendor org appear as single entry with alternateRepos
- Health endpoint on VM-2 shows `vendor-org-discovery` active

**No E2E/Playwright** needed -- no web UI changes in scope.

## Technical Challenges

### Challenge 1: Crawl-worker JS sync with TS registry

**Problem**: `vendor-org-discovery.js` is plain JS and cannot import TypeScript. The VENDOR_ORGS array must be kept in sync manually.

**Mitigation**: (1) Comment in both files cross-references the other. (2) The equivalence test in Phase 1 validates the registry produces the same set as the current hardcoded values, catching drift at test time. (3) Future: a codegen script could auto-generate the JS array from the TS registry, but this is out of scope for this increment.

### Challenge 2: Dedup must not break pagination

**Problem**: Dedup reduces the result count. If 10 results are fetched and 3 are collapsed, only 7 unique entries are returned.

**Mitigation**: Dedup runs after the final merge in route.ts, which already over-fetches (limit+1) to detect `hasMore`. The dedup function preserves the `hasMore` flag from the pre-dedup result set. For most queries, same-org duplicates are rare (1-2 per page at most), so the impact on visible result count is minimal. If this becomes a problem, a future optimization can increase the internal fetch limit by a dedup buffer factor.
