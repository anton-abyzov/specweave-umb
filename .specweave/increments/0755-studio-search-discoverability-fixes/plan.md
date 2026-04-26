# Implementation Plan: Studio search discoverability fixes

## Overview

Four discrete fixes in `vskill-platform`, each with its own RED→GREEN cycle and live production smoke. Sequenced from highest user-visibility (ranking) to lowest blast-radius last (KV auto-reindex). All four ship as a single increment for atomic closure, but each phase has its own deploy gate so we can stop after any phase if a problem appears.

## Design

### Phase 1 — US-001 Ranking up-weight cert tier (P1)

**File**: `vskill-platform/src/lib/search.ts`

**Existing sort** at lines 269-275:
```typescript
filtered.sort((a, b) => {
  const certA = a.certTier === "CERTIFIED" ? 0 : 1;
  const certB = b.certTier === "CERTIFIED" ? 0 : 1;
  if (certA !== certB) return certA - certB;
  if (b.githubStars !== a.githubStars) return b.githubStars - a.githubStars;  // ← problem
  return computeSearchRank(b, queryWords) - computeSearchRank(a, queryWords);  // ← never reached for distinct stars
});
```

**Problem**: when two skills are both CERTIFIED, `b.githubStars - a.githubStars` is the second sort key, which dominates over the blended rank. Since competitor "skill-builder" skills (most owned by major orgs) have higher star counts, the user's 24-star vendor skill loses.

**Fix**: replace the secondary sort key with the blended rank, AND scale `computeCertBonus` by trustTier so T4 gets a bigger boost than T3:
```typescript
function computeCertBonus(certTier: string, trustTier: string): number {
  if (certTier !== "CERTIFIED" && certTier !== "VERIFIED") return 0;
  const certBase = certTier === "CERTIFIED" ? 100 : 20;
  // T4 vendor gets a 2× multiplier; T3=1.5×; T2=1.0×; T1=0.7×; T0=0.4×
  const trustMul = trustTier === "T4" ? 2.0
    : trustTier === "T3" ? 1.5
    : trustTier === "T2" ? 1.0
    : trustTier === "T1" ? 0.7
    : 0.4;
  return certBase * trustMul;
}
```

Then in the sort:
```typescript
filtered.sort((a, b) => {
  const certA = a.certTier === "CERTIFIED" ? 0 : 1;
  const certB = b.certTier === "CERTIFIED" ? 0 : 1;
  if (certA !== certB) return certA - certB;
  // Use blended rank as primary tiebreaker (was githubStars before — hurt T4 vendors)
  const rankDiff = computeSearchRank(b, queryWords) - computeSearchRank(a, queryWords);
  if (rankDiff !== 0) return rankDiff;
  return b.githubStars - a.githubStars;  // ← demoted to last tiebreaker
});
```

The `computeSearchRank` function signature changes to take `trustTier` (passed via `entry.trustTier`).

### Phase 2 — US-002 LIST endpoint filter wiring (P1)

**File**: `vskill-platform/src/app/api/v1/skills/route.ts` + `vskill-platform/src/lib/data.ts` (`getSkills`)

The route currently parses `category`, `tier`, `extensible`, `search` but not `q`, `author`, `source`. Add them:

```typescript
const author = sanitizeFilter(searchParams.get("author"), 200);
const source = sanitizeFilter(searchParams.get("source"), 50);
const q = sanitizeFilter(searchParams.get("q"), 200);
// pass into getSkills filters:
const filters = { ...existing, author, source, q };
```

`sanitizeFilter` is a shared helper applying the charset whitelist and length cap (extracted from existing search-route validation).

`getSkills` in `src/lib/data.ts` extends its where-clause:
```typescript
where: {
  ...existing,
  ...(author && { OR: [{ author }, { ownerSlug: author }] }),
  ...(source && { source }),
  ...(q && { OR: [
    { name: { contains: q, mode: "insensitive" } },
    { displayName: { contains: q, mode: "insensitive" } },
    { description: { contains: q, mode: "insensitive" } },
  ] }),
}
```

### Phase 3 — US-003 isVendor backfill on submission (P2)

**File**: `vskill-platform/src/lib/submission/publish.ts`

After the existing `db.skill.upsert(...)` in the PUBLISHED transition path, add a sibling write to the submission row:

```typescript
const isVendorClassification = labels.includes("vendor") || certMethod === "VENDOR_AUTO";
if (isVendorClassification && !submission.isVendor) {
  await db.submission.update({
    where: { id: submission.id },
    data: { isVendor: true },
  });
}
```

Wrapped in a transaction with the skill upsert if the existing code uses `db.$transaction`; otherwise sequential with try/catch and a logged warning on failure (Postgres remains source of truth — failure here is a drift, not a publish failure).

### Phase 4 — US-004 KV auto-reindex on publish (P2)

**Files**:
- `vskill-platform/src/lib/submission/publish.ts` — enqueue at PUBLISHED transition
- `vskill-platform/src/lib/search-index/` (existing folder per 0751 untracked work — verify) OR new `vskill-platform/src/lib/search-index/queue-consumer.ts` — consumer that updates KV
- `vskill-platform/wrangler.jsonc` — declare a new `search-index-update` queue producer + consumer (TBD if existing infrastructure can be reused)

**Approach** (TBD in implementation — pick whichever existing pattern is cleanest):
1. **CF Queue** (preferred): existing `submission-processing` queue infrastructure suggests this is the dominant pattern. Add a new queue name like `search-index-update`.
2. **Workers Cache invalidation**: lighter-weight if just busting cache on the existing search route is sufficient.
3. **Direct KV write inline (non-blocking)**: `ctx.waitUntil(kvUpdate(...))` from the publish handler — simplest, avoids new queue infra, but couples publish to KV.

We'll pick option 3 (`waitUntil`) unless plan-time investigation shows a strong reason for queue. Simpler is better; the existing manual rebuild endpoint stays as the escape hatch.

## Rationale

**Why ranking is phase 1**: it's the user's actual pain point. The other three are quality-of-life improvements but the user will see the ranking change immediately when they search for their skill.

**Why we tune existing weights instead of rewriting the algorithm**: the current `computeSearchRank` is structurally sound — the problem is the *sort caller* uses `githubStars` as the secondary key, bypassing the blended rank. Tuning weights + fixing the sort tiebreaker is a minimal change with clear test coverage. A full algorithm rewrite (e.g., learning-to-rank with engagement signals) is out of scope.

**Why LIST endpoint filter wiring is phase 2**: medium-impact (internal tooling) with low blast radius (additive, default behavior unchanged). Easy to ship after phase 1.

**Why isVendor backfill is phase 3**: low user-visibility (admin-only). Single-line conditional in publish.ts. Cheap.

**Why KV auto-reindex is phase 4 (last)**: highest blast radius — touches the publish path, possibly adds queue infrastructure. Ship last so a problem here doesn't block phase 1-3.

**Why we don't add a `/find/<owner>/<repo>/<skill>` page route here**: out of scope per spec.md. The 404 was noted but doesn't affect search visibility.

## Architecture

### Components touched
- `src/lib/search.ts` — ranking function + sort (phase 1)
- `src/app/api/v1/skills/route.ts` — query param parsing (phase 2)
- `src/lib/data.ts` — `getSkills` where-clause extension (phase 2)
- `src/lib/submission/publish.ts` — submission update + KV waitUntil (phases 3-4)
- `src/lib/search-index/` — KV update logic (phase 4; folder may exist from 0751's untracked work)

### Components NOT touched
- `/api/v1/studio/search` route (delivered by 0754, working).
- `/api/v1/skills/<owner>/<repo>/<skill>` direct lookup route (working).
- Submission state machine, scan logic, security gates — phase 3-4 only adds writes; no state changes.
- Studio frontend, vskill CLI, vskill-platform UI pages.

## Technology Stack

- TypeScript (existing).
- Prisma 5+ for the LIST endpoint where-clause additions (existing).
- Cloudflare Workers KV via existing `SEARCH_CACHE_KV` binding (phase 4).
- `ctx.waitUntil` from `@opennextjs/cloudflare` for non-blocking post-response work (phase 4).
- Vitest for unit tests (existing).

## Implementation Phases

### Phase 1: Ranking (US-001) — RED→GREEN→DEPLOY→VERIFY
- T-001: Write a golden ranking test: 1 T4 vendor skill (githubStars=24) + 30 T2 community skills (githubStars 0-200) all named `*skill-builder*` → assert T4 ranks #1.
- T-002: Update `computeCertBonus` to take trustTier and apply the trust multiplier.
- T-003: Update `computeSearchRank` signature to pass `trustTier` from the entry.
- T-004: Update the sort caller in `searchSkills` to use blended rank as the secondary tiebreaker (was `githubStars`).
- T-005: Run targeted vitest for `src/lib/search` — both new golden test and existing tests must pass.
- T-006: Deploy. Smoke: `curl /api/v1/studio/search?q=skill-builder&limit=30` includes `anton-abyzov/vskill/skill-builder`.

### Phase 2: LIST endpoint filters (US-002) — RED→GREEN→DEPLOY→VERIFY
- T-007: Write tests asserting `?author=`, `?source=`, `?q=` narrow results AND combine with AND semantics.
- T-008: Add `sanitizeFilter` helper (or reuse existing search-route sanitizer) for q/author/source inputs.
- T-009: Wire the params through to `getSkills` filters in route.ts and the where-clause in data.ts.
- T-010: Run targeted vitest for the route + data layer.
- T-011: Deploy. Smoke: `curl /api/v1/skills?author=anton-abyzov` returns the user's skills.

### Phase 3: isVendor backfill (US-003) — RED→GREEN→DEPLOY→VERIFY
- T-012: Write a test asserting a vendor publish writes `submission.isVendor = true` on the source row.
- T-013: Add the conditional update in `publish.ts` after the Skill upsert.
- T-014: Run targeted vitest for `src/lib/submission/`.
- T-015: Deploy. Smoke: trigger a test vendor publish; verify `/api/v1/submissions/<id>` returns `isVendor: true`.

### Phase 4: KV auto-reindex (US-004) — RED→GREEN→DEPLOY→VERIFY
- T-016: Investigate `src/lib/search-index/` (untracked from 0751 — read its design first).
- T-017: Pick implementation approach (waitUntil vs queue) based on T-016 findings.
- T-018: Write a test asserting publish triggers a non-blocking KV update.
- T-019: Implement the KV update path.
- T-020: Run targeted vitest.
- T-021: Deploy. Smoke: publish a test submission, verify it appears in `/api/v1/skills/search?q=<unique>` within 60s without admin rebuild.

### Phase 5: Closure
- T-022: Run full studio + search vitest suites — no regressions.
- T-023: Sync metadata, close increment, commit, sw:done pipeline.

## Testing Strategy

- **Unit (Vitest)**: golden ranking test + LIST filter tests + isVendor backfill test + KV-update smoke test (mock `ctx.waitUntil`). Existing tests for search.ts and the LIST route stay green.
- **Integration**: not added — each phase has a live production smoke probe in its own task.
- **Production smoke**: per-phase curl probes captured in `reports/`.
- **Coverage**: target stays at 90%; new tests increase coverage for search ranking + LIST filters.

## Technical Challenges

### Challenge 1: anton-abyzov is already CERTIFIED — primary cert sort already favors them
**Resolution**: the issue is competitors are also CERTIFIED with more stars. Phase 1 fixes the secondary sort to use blended rank (which weights cert+trust+relevance) instead of raw stars.

### Challenge 2: ranking change may regress popular-skill discoverability
**Mitigation**: AC-US1-04 requires neutral queries (`q=react`) to keep popularity-driven ranking. The trust multiplier changes the magnitude of certBonus but doesn't zero out popularity. Test cases pin both extremes.

### Challenge 3: `src/lib/search-index/` folder exists in 0751's untracked work
**Mitigation**: T-016 investigates first. If 0751 has already shipped the consumer-side infrastructure, phase 4 just needs to enqueue. If not, we use `waitUntil` for the simplest possible path.

### Challenge 4: deploy bundling 0751 changes
**Mitigation**: same playbook as 0754 closure — when deploying, isolate via stash. 0751 closure should run before us; if it doesn't, we deploy with 0751's changes bundled (reasonable since 0751 is 16/16 done and presumably ready).
