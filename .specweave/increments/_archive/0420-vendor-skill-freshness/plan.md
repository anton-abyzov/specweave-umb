# Implementation Plan: Vendor Skill Freshness

## Overview

Two surgical changes to the vskill-platform discovery pipeline to ensure vendor skills are always fresh:

1. **Dedup bypass** — Skip `hasBeenDiscovered` check for `vendor-orgs` source candidates in `processRepo`
2. **Cron inclusion** — Add `"vendor-orgs"` to the hourly cron discovery sources

No new components, no schema changes, no new endpoints. The existing infrastructure (incremental KV shard update on publish, vendor auto-certification) handles the rest.

## Architecture

### Data Flow (Current → Fixed)

```
Current:
  Cron (hourly) → runGitHubDiscovery(sources: ["npm"])
                   └─ processRepo → hasBeenDiscovered? → SKIP (vendor skills blocked)

Fixed:
  Cron (hourly) → runGitHubDiscovery(sources: ["npm", "vendor-orgs"])
                   └─ processRepo → source === "vendor-orgs"? → BYPASS dedup → submit
                                  → other source? → hasBeenDiscovered? → normal dedup
```

### Components Modified

| File | Change | AC |
|------|--------|----|
| `src/lib/crawler/github-discovery.ts` | Add `source === "vendor-orgs"` conditional before `hasBeenDiscovered` in `processRepo` (line ~765) | AC-US1-01, AC-US1-02 |
| `scripts/build-worker-entry.ts` | Change cron sources from `["npm"]` to `["npm", "vendor-orgs"]` (line 136) | AC-US2-01 |

### No Schema/API Changes

- No Prisma migrations
- No new endpoints
- No KV key format changes
- `DiscoveredRepo.source` field already exists and carries `"vendor-orgs"`

## Technology Stack

- **Language**: TypeScript (existing)
- **Testing**: Vitest with `vi.hoisted()` mocks (existing pattern in `__tests__/github-discovery.test.ts`)

## Implementation Phases

### Phase 1: Dedup Bypass (US-001)
1. TDD RED: Write test asserting vendor-orgs candidates bypass dedup
2. TDD GREEN: Add conditional in `processRepo`
3. Verify existing dedup tests still pass (non-vendor sources unchanged)

### Phase 2: Cron Integration (US-002)
1. Add `"vendor-orgs"` to cron discovery sources in `build-worker-entry.ts`
2. No test needed (generated wrapper, verified by deploy)

### Phase 3: Deploy & Backfill
1. Build and deploy vskill-platform
2. Trigger `POST /api/v1/admin/discovery/vendor-orgs` with `{ "force": true }` for immediate backfill
3. Verify `npx vskill find pptx` returns Anthropic's skill

## Testing Strategy

- **Unit**: Vitest tests in `src/lib/crawler/__tests__/github-discovery.test.ts`
  - Test vendor-orgs source bypasses dedup
  - Test non-vendor sources still respect dedup (regression)
- **Integration**: Post-deploy manual verification via `npx vskill find pptx`
- **Performance**: Not applicable (vendor repos are ~50 skills total)

## Technical Challenges

### Challenge 1: Write-ahead marking still runs for vendor candidates
**Impact**: `markDiscovered` is called before POST for all candidates (line ~783). For vendor sources, this means dedup records are still created/updated, but they won't block future runs because the bypass skips the check.
**Decision**: Leave write-ahead marking in place — it provides audit trail and doesn't cause harm.
