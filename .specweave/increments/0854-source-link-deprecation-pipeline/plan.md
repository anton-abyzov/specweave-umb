# Implementation Plan — Increment 0854: Source-Link Auto-Deprecation Pipeline + Backfill

## Context

Three converging bugs in the source-link verification flow + a cron backlog. Diagnosis is complete in the spec. This document captures the architectural design for implementation. Approved plan file: `~/.claude/plans/mutable-growing-sundae.md`.

## Architecture

### Component A — `check-source` route ctx.waitUntil

**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/check-source/route.ts`

The route currently does:
```ts
deprecateStaleSkill(skillName, url).catch(...);
undeprecateSkill(skillName).catch(...);
```

On Cloudflare Workers the isolate terminates after `NextResponse.json(...)` returns. The promise never resolves → DB write never lands. Confirmed live.

Fix follows the pattern at `src/app/api/v1/auth/login/route.ts:91-105`:
```ts
const { getCloudflareContext } = await import("@opennextjs/cloudflare");
const ctx = await getCloudflareContext({ async: true });
if (typeof ctx.ctx?.waitUntil === "function") {
  ctx.ctx.waitUntil(deprecateStaleSkill(skillName, url).catch(...));
} else {
  await deprecateStaleSkill(skillName, url).catch(...);
}
```

Note the nested `ctx.ctx.waitUntil` — OpenNext exposes `{ env, ctx, cf }` where `ctx` is the ExecutionContext.

### Component B — DeprecationBanner mount guard

**File**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/page.tsx:313`

Current guard: `{skill.isDeprecated && !recentlyPublished && (<DeprecationBanner ...>)}` creates a chicken-and-egg.

Change: mount the new `<SourceLinkAndBanner>` wrapper whenever `repoUrl + skillPath` are set; that wrapper renders the banner regardless of `isDeprecated`. The banner handles three states (`checking` → `online` → `offline`) with appropriate visuals.

### Component C — SourceLink broken-state visual + shared fetch

**Files**:
- New: `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/SourceLinkAndBanner.tsx`
- Modify: `DeprecationBanner.tsx` → accept `sourceState` prop instead of running its own fetch
- Modify: `page.tsx:291-303` → replace inline `<a>` + banner block with `<SourceLinkAndBanner ...>`

The wrapper owns one `useEffect` that calls `/api/v1/skills/check-source`. The result drives BOTH the source-link visual and the banner state. Single fetch per page view.

`SourceLink` renders the same `<a>` shape as the current inline anchor, plus:
- When `sourceState === "offline"`: add `text-decoration: line-through`, a `⚠` glyph prefix, `title="Source file removed from upstream — link 404s"`, `aria-label="Removed source: ${skillPath}"`. Link stays clickable.

### Component D — Backfill script

**File**: New, `repositories/anton-abyzov/vskill-platform/scripts/backfill-stale-source.ts`

Modeled on `scripts/backfill-vskill-source-repo.ts` + `scripts/purge-orphaned-kv.ts`.

```ts
import { PrismaClient } from "@prisma/client";
import pLimit from "p-limit";
const prisma = new PrismaClient();
const DRY = process.argv.includes("--dry-run");
// ... flags: --limit, --max-age-days
const stale = await prisma.skill.findMany({
  where: {
    isDeprecated: false,
    skillPath: { not: null },
    OR: [
      { metricsRefreshedAt: null },
      { metricsRefreshedAt: { lt: new Date(Date.now() - MAX_AGE_DAYS * 86400_000) } },
    ],
  },
  select: { id: true, name: true, repoUrl: true, skillPath: true, sourceBranch: true },
});
```

For each skill: HEAD raw.githubusercontent.com with `sourceBranch ?? "HEAD"`. Only 404 → deprecate. Concurrency=10 via `p-limit`.

KV cleanup uses `scripts/purge-orphaned-kv.ts:26-36`'s `cfFetch()` pattern to call `/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/bulk/delete` for affected search-index keys.

Env required:
- `DATABASE_URL` — direct Hetzner Postgres
- `CF_API_TOKEN`, `CF_ACCOUNT_ID`, `CF_KV_NAMESPACE_ID` (SEARCH_INDEX_KV)

### Component E — runStaleSourceSweep cron

**Files**:
- New: `repositories/anton-abyzov/vskill-platform/src/lib/cron/stale-source-sweep.ts`
- Modify: `repositories/anton-abyzov/vskill-platform/src/lib/cron/cohort-dispatch.ts` — add to LIGHT cohort with minute gate
- Modify: `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` — invoke from scheduled handler

`runStaleSourceSweep(opts)`:
- Query non-deprecated skills with `skillPath` not null, ordered by `metricsRefreshedAt asc nulls first`, `take: opts.batchSize ?? 500`.
- p-limit concurrency 10, HEAD raw.githubusercontent.com via `sourceBranch ?? "HEAD"`.
- For each 404: `db.skill.update({ where: { id }, data: { isDeprecated: true } })` + `updateSearchShard(searchKv, entry, "remove")`.
- Stop on circuit-breaker (3 consecutive non-404 errors). Don't deprecate on 5xx/429.

Dispatch wiring: add to LIGHT cohort at a gated minute (e.g., `minute === 0` of the `*/10 * * * *` cron — so once/hour). LIGHT cohort runs cheap recurring tasks; this fits the pattern.

## ADR Reference

Reuses existing patterns:
- `ctx.waitUntil` pattern: see auth/login/logout routes.
- Cohort cron dispatch: see `src/lib/cron/cohort-dispatch.ts`.
- KV search-shard updates: see `src/lib/search-index.ts` `updateSearchShard()`.
- Backfill script bootstrap: see `scripts/backfill-vskill-source-repo.ts`.

No new ADR needed.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Every skill page now fires `/check-source` on view | 1hr cache header on positive results; check is cheap (HEAD to raw.gh.com). Rollback = restore the guard. |
| False-positive deprecation during GitHub outage | Only `res.status === 404` triggers deprecation (already in route + script + cron). 5xx/429 ignored. 24h-since-update guard in `deprecateStaleSkill` prevents flapping during fresh publishes. |
| Backfill KV cleanup fails | Script writes DB first, then KV. DB state is authoritative; next enrichment cycle will pick up KV drift. |

## Test Strategy

| Layer | Approach |
|---|---|
| Unit (check-source) | Mock `getCloudflareContext`; assert waitUntil called with the deprecation promise; await it; verify Prisma update. |
| Unit (stale-source-sweep) | Insert mixed-status fake skills, run sweep, assert only 404s deprecated. |
| Component (SourceLinkAndBanner) | Render with mocked `fetch`; assert `online`/`offline` visuals. |
| E2E (Playwright) | Fixture skill with 404 skillPath; assert link strike-through + banner DEPRECATED appears within 10s. |
| Script (manual) | `--dry-run` against prod DB → expect kie-ai in report. |
