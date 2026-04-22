# Implementation Plan — `0672-queue-reliability`

> **Scope**: vskill-platform queue reliability fixes
> **Target repo**: `repositories/anton-abyzov/vskill-platform/`
> **Deploy surface**: CF Worker `verified-skill-com` (OpenNext) + Neon Postgres + CF KV + CF Queue

## 1. Overview

Three production issues on [verified-skill.com/queue](https://verified-skill.com/queue):

1. **Empty default render** — cold `GET /queue` returns null from SSR cache read; 60 s TTL + lazy write gives a blank first-load under low traffic and DB circuit-breaker trips.
2. **Duplicate rows** — no `@@unique([repoUrl, skillName])` on `Submission`; app-level dedup leaks via staleness windows, concurrent inserts, fail-open on DB errors, and multiple ingestion sources.
3. **Tier-2 runtime uncertainty** — CF Workers AI cost spike in Feb ($1987) + opaque reliability; need a data-backed ADR before any migration.

Fixes are delivered as one deploy against the existing stack: Next.js 15 + OpenNext @ Cloudflare Workers, Neon Postgres via `@prisma/adapter-neon`, CF Queue `submission-processing`, Hetzner crawl workers pushing to `/api/v1/webhooks/scan-results`.

ADR captures Tier-2 options; actual runtime migration is deferred to a follow-up increment (0673) if the ADR recommends it.

## 2. Architecture

### 2.1 Components in play

| Component | Path | Role in this increment |
|---|---|---|
| `Submission` model | [prisma/schema.prisma:157-209](../../../repositories/anton-abyzov/vskill-platform/prisma/schema.prisma) | Gains `@@unique([repoUrl, skillName])`; existing `@@index([repoUrl, skillName])` is dropped. |
| Prisma migration dir | `repositories/anton-abyzov/vskill-platform/prisma/migrations/` | New dir `20260421_submission_unique_repo_skill/` with custom SQL (collapse) + generated SQL (unique index). |
| Dedup module | [src/lib/submission-dedup.ts](../../../repositories/anton-abyzov/vskill-platform/src/lib/submission-dedup.ts) | Deleted. Multi-branch staleness gone. |
| Submission creation | [src/lib/submission/](../../../repositories/anton-abyzov/vskill-platform/src/lib/submission) | New helper `upsertSubmission` added to the submission module (exported via existing [submission-store.ts:1-47](../../../repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts) shim). |
| Submissions API | [src/app/api/v1/submissions/route.ts:582, 670, 778](../../../repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts) | Replace `checkSubmissionDedup` + `createSubmission` call pattern with `upsertSubmission`; preserve HTTP contract. |
| Queue SSR data | [src/app/queue/data.ts:95-135](../../../repositories/anton-abyzov/vskill-platform/src/app/queue/data.ts) | No change; reads warmed keys via existing fallback chain. |
| Shared list fetcher | `src/lib/queue/fetch-submission-list.ts` (new) | Extracted from route GET handler; called by both the HTTP route and warm-up cron. |
| Warm-up cron | `src/lib/cron/queue-list-warmup.ts` (new) | Populates exact and latest-fallback KV keys for the five visible filters. |
| Scheduled handler | [scripts/build-worker-entry.ts:38-99](../../../repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts) | Wire `warmQueueListCache(env)` alongside existing `refreshQueueStats` call. |
| Migration scripts | `scripts/migrations/0672-collapse-submission-dupes.ts`, `0672-restore-submission-dupes.ts` (new) | Collapse + rollback, idempotent. Used by the generated migration SQL (`npx tsx` invocation) and for manual recovery. |
| TTL constants | Wherever `LIST_CACHE_TTL` lives (route.ts or data.ts constants) | Raise to 5400 s (90 min). `LIST_LATEST_TTL` stays at 24 h. |

### 2.2 Data flow

```
POST /api/v1/submissions
  │
  ▼
upsertSubmission(repoUrl, skillName, …)        ← replaces checkSubmissionDedup + db.submission.create
  │       ┌── create OK ─→ { id, created: true,  state }
  ├───────┤
  │       └── P2002   ─→ findUniqueOrThrow({ repoUrl_skillName }) ─→ { id, created: false, state, verifiedSkill? }
  ▼
HTTP response mapping
  │ pending  ─→ { id, state, duplicate: true }
  │ verified ─→ { skillId, skillName, alreadyVerified: true }
  │ blocked  ─→ { blocked: true, submissionId }
  └ new      ─→ existing 201 path (queue send, etc.)
```

```
Hourly cron (cron="0 * * * *", existing)
  │
  ▼ (in scheduled handler, after refreshQueueStats)
warmQueueListCache(env)
  │
  ├─ for filter in {active, published, rejected, blocked, onHold}:
  │    sort = getDefaultSort(filter)
  │    body = await fetchSubmissionList({ filter, sort, dir: sort.dir, limit: 50, offset: 0 })
  │    SUBMISSIONS_KV.put(`submissions:list:${filter}:::${sort}:${dir}:50:0`, body, {expirationTtl: 5400})
  │    SUBMISSIONS_KV.put(`submissions:latest:${filter}`,                    body, {expirationTtl: 86400})
  ▼
SSR read (data.ts) → warmed exact key → fallback latest key → null
```

### 2.3 Database migration (AC-US2-*)

**Schema diff** (`repositories/anton-abyzov/vskill-platform/prisma/schema.prisma:202`):

```diff
-  @@index([repoUrl, skillName])
+  @@unique([repoUrl, skillName])
```

All other `Submission` indexes (`state`, `skillName`, `createdAt`, `userId`, `repositoryId`, `[repositoryId, skillName]`, `[priority desc, createdAt asc]`, `[state, priority desc, createdAt asc]`) are retained.

**Migration directory**: `prisma/migrations/20260421100000_submission_unique_repo_skill/migration.sql`. Single directory, **two SQL steps in one file**, executed inside one Postgres transaction (Prisma wraps each migration in a transaction by default — confirm by inspecting `migration.sql` header comment, and keep an explicit `BEGIN` / `COMMIT` plus `LOCK TABLE "Submission" IN EXCLUSIVE MODE;` as the first statement to be defensive):

```sql
BEGIN;
LOCK TABLE "Submission" IN EXCLUSIVE MODE;

-- Step 1: collapse duplicates
-- Uses a PL/pgSQL block to: pick survivor per (repoUrl, skillName), re-point FK children,
-- archive victims + children as JSONB to a temp table, then delete victims. The temp
-- table is SELECTed by the pre-migration script (scripts/migrations/0672-collapse-submission-dupes.ts)
-- to persist the archive JSON to backups/dedup-collapse-0672.json before COMMIT.
DO $$
DECLARE
  v_survivor RECORD;
  v_victim RECORD;
BEGIN
  CREATE TEMP TABLE dedup_archive_0672 (row_json JSONB) ON COMMIT DROP;

  FOR v_survivor IN
    SELECT "repoUrl", "skillName", MAX("createdAt") AS survivor_created
    FROM "Submission"
    GROUP BY "repoUrl", "skillName"
    HAVING COUNT(*) > 1
  LOOP
    -- Find survivor id
    DECLARE survivor_id TEXT;
    BEGIN
      SELECT id INTO survivor_id
      FROM "Submission"
      WHERE "repoUrl" = v_survivor."repoUrl"
        AND "skillName" = v_survivor."skillName"
        AND "createdAt" = v_survivor.survivor_created
      LIMIT 1;

      -- Archive victims + their children
      FOR v_victim IN
        SELECT * FROM "Submission"
        WHERE "repoUrl" = v_survivor."repoUrl"
          AND "skillName" = v_survivor."skillName"
          AND id <> survivor_id
      LOOP
        INSERT INTO dedup_archive_0672 SELECT to_jsonb(v_victim) || jsonb_build_object(
          'stateEvents',  (SELECT jsonb_agg(row_to_json(x)) FROM "SubmissionStateEvent"  x WHERE x."submissionId" = v_victim.id),
          'scanResults',  (SELECT jsonb_agg(row_to_json(x)) FROM "ScanResult"            x WHERE x."submissionId" = v_victim.id),
          'jobs',         (SELECT jsonb_agg(row_to_json(x)) FROM "SubmissionJob"         x WHERE x."submissionId" = v_victim.id),
          'emails',       (SELECT jsonb_agg(row_to_json(x)) FROM "EmailNotification"     x WHERE x."submissionId" = v_victim.id),
          'evalRuns',     (SELECT jsonb_agg(row_to_json(x)) FROM "EvalRun"               x WHERE x."submissionId" = v_victim.id)
        );

        -- Re-point FK children
        UPDATE "SubmissionStateEvent"  SET "submissionId" = survivor_id WHERE "submissionId" = v_victim.id;
        UPDATE "ScanResult"            SET "submissionId" = survivor_id WHERE "submissionId" = v_victim.id;
        UPDATE "SubmissionJob"         SET "submissionId" = survivor_id WHERE "submissionId" = v_victim.id;
        UPDATE "EmailNotification"     SET "submissionId" = survivor_id WHERE "submissionId" = v_victim.id;
        UPDATE "EvalRun"               SET "submissionId" = survivor_id WHERE "submissionId" = v_victim.id;

        DELETE FROM "Submission" WHERE id = v_victim.id;
      END LOOP;
    END;
  END LOOP;
END $$;

-- Step 2: drop old index and add unique constraint (Prisma-generated)
DROP INDEX IF EXISTS "Submission_repoUrl_skillName_idx";
CREATE UNIQUE INDEX "Submission_repoUrl_skillName_key" ON "Submission"("repoUrl", "skillName");

COMMIT;
```

**Archive JSON persistence** — the collapse step uses a `TEMP TABLE ... ON COMMIT DROP`, so the archive is only available inside the transaction. Two workable strategies:

- **(Chosen)** Run the collapse via a TS wrapper `scripts/migrations/0672-collapse-submission-dupes.ts` **before** `prisma migrate deploy`:
  1. Open a single Neon transaction via `@neondatabase/serverless`.
  2. Execute the PL/pgSQL collapse (without the unique-index step).
  3. `SELECT row_json FROM dedup_archive_0672;` into memory.
  4. Write JSON to `.specweave/increments/0672-queue-reliability/backups/dedup-collapse-0672.json`.
  5. `COMMIT;`.
  6. Then `npx prisma migrate deploy` applies the unique-index migration (which will now succeed because step-1 already collapsed duplicates).

  The Prisma migration SQL file then contains **only** the `DROP INDEX` + `CREATE UNIQUE INDEX` (step 2). This keeps Prisma's migration graph clean and keeps the archive writeable from a host that has filesystem access.

- (Alternative — rejected) Embed collapse in `migration.sql` and lose the archive. Too risky to roll back.

**Idempotency** — second run of the collapse script finds zero `(repoUrl, skillName)` groups with `count > 1`, exits with `{ archivedCount: 0, changed: false }` without writing a new archive file (or writes an empty JSON array with a timestamped filename if invoked with `--force`).

**Rollback** — `scripts/migrations/0672-restore-submission-dupes.ts` reads `backups/dedup-collapse-0672.json`, re-inserts victim rows (preserving original ids via the archived JSON), re-points FK children back, and drops the unique index. Only usable within the 30-day window during which child records haven't been mutated; beyond that, archive is informational only.

### 2.4 Dedup simplification (AC-US3-*)

Delete `src/lib/submission-dedup.ts` in its entirety. New function in the submission module:

```ts
// src/lib/submission/upsert.ts  (new file, re-exported from src/lib/submission/index.ts)
export interface UpsertSubmissionInput {
  repoUrl: string;
  skillName: string;
  skillPath: string;
  submitterEmail?: string | null;
  userId?: string | null;
  priority?: number;
}

export type UpsertResult =
  | { kind: "created"; id: string; state: SubmissionState; createdAt: string }
  | { kind: "pending";  id: string; state: SubmissionState }          // was in flight
  | { kind: "verified"; id: string; skillId: string; skillName: string } // PUBLISHED with Skill row
  | { kind: "blocked";  id: string }
  | { kind: "rejected"; id: string; state: SubmissionState };

export async function upsertSubmission(input: UpsertSubmissionInput): Promise<UpsertResult> {
  const db = await getDb();
  try {
    const created = await db.submission.create({
      data: {
        repoUrl: input.repoUrl,
        skillName: input.skillName,
        skillPath: input.skillPath,
        submitterEmail: input.submitterEmail ?? null,
        userId: input.userId ?? null,
        priority: input.priority ?? 0,
        state: "RECEIVED",
      },
      select: { id: true, state: true, createdAt: true },
    });
    return { kind: "created", id: created.id, state: created.state, createdAt: created.createdAt.toISOString() };
  } catch (e) {
    if (!isPrismaUniqueViolation(e)) throw e;
    const existing = await db.submission.findUniqueOrThrow({
      where: { repoUrl_skillName: { repoUrl: input.repoUrl, skillName: input.skillName } },
      select: {
        id: true, state: true, skillId: true,
        skill: { select: { id: true, name: true } },
      },
    });
    if (existing.state === "BLOCKED")  return { kind: "blocked",  id: existing.id };
    if (existing.state === "PUBLISHED" && existing.skill) {
      return { kind: "verified", id: existing.id, skillId: existing.skill.id, skillName: existing.skill.name };
    }
    if (existing.state === "REJECTED" || existing.state === "TIER1_FAILED" || existing.state === "DEQUEUED") {
      return { kind: "rejected", id: existing.id, state: existing.state };
    }
    return { kind: "pending", id: existing.id, state: existing.state };
  }
}

function isPrismaUniqueViolation(e: unknown): boolean {
  return typeof e === "object"
    && e !== null
    && "code" in e
    && (e as { code?: string }).code === "P2002";
}
```

**Call-site updates** in [src/app/api/v1/submissions/route.ts](../../../repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts):

- **Line 582** (single non-batch path): replace the `checkSubmissionDedup(...)` + branching with a single `upsertSubmission(...)` call; map kinds to existing HTTP responses.
- **Line 670** (batch dedup path): `checkSubmissionDedupBatch(...)` is also deleted; the batch loop instead calls `upsertSubmission` per skill. Since the new path relies on DB-level uniqueness, the batch no longer needs a pre-query — fewer queries, simpler code. Each iteration returns either a created/queued row or a "skip" kind (`pending|verified|blocked|rejected`).
- **Line 778** (internal sequential path): same replacement.
- **Delete**: `buildDedupConfig`, `DEFAULT_STALE_PENDING_HOURS`, and all staleness logic. `DEDUP_STALE_*` env vars are removed from `wrangler.jsonc` (not actually set in prod — safe to drop).
- **Delete**: `isCliAuto ? { ...dedupConfig, stalePublishedHours: 876000, staleRejectedHours: 876000 }` branch (line 575-577). CLI-auto now just gets the "verified" kind naturally.
- **Preserve**: existing HTTP response shapes for CLI pollers (`{ id, state, duplicate: true }`), admin-blocked (`{ blocked: true, submissionId }`), and published (`{ skillId, skillName, alreadyVerified: true }`). No breaking API change.

**Admin rescan** — the current code has no separate rescan endpoint; rescan flows through `POST /api/v1/submissions` and relies on staleness to re-create. After this change, admin rescan must go through a dedicated route (out of scope here — file a follow-up). For now, admins who need to force re-process can use the existing state-update API or delete the row in the admin panel; documentation update lives in the increment's reports folder.

### 2.5 Cache warm-up (AC-US1-*)

**New file** `src/lib/queue/fetch-submission-list.ts` — extract the existing KV-write body-building from the route's GET handler. Exports:

```ts
export interface FetchSubmissionListParams {
  filter: string;            // "active" | "published" | "rejected" | "blocked" | "onHold"
  reason?: string;           // currently empty string for default cases
  sort: string;              // column name
  sortDir: "asc" | "desc";
  limit: number;
  offset: number;
}
export interface SubmissionListBody {
  submissions: SubmissionRow[];
  total: number;
  queuePositions: Record<string, number> | null;
}
export async function fetchSubmissionList(params: FetchSubmissionListParams): Promise<SubmissionListBody>;
```

Both the HTTP GET handler and the warm-up cron call this. Route handler wraps with KV read/write; cron calls it directly and handles KV write itself.

**New file** `src/lib/cron/queue-list-warmup.ts`:

```ts
import { fetchSubmissionList } from "@/lib/queue/fetch-submission-list";
import { getDefaultSort } from "@/app/queue/data";  // or duplicate if cross-module import is awkward

const FILTERS = ["active", "published", "rejected", "blocked", "onHold"] as const;
const LIST_CACHE_TTL = 5400;       // 90 min — cron runs hourly, 30 min buffer
const LIST_LATEST_TTL = 86400;     // 24 h — long-lived fallback

export async function warmQueueListCache(env: {
  SUBMISSIONS_KV: KVNamespace;
}): Promise<{ written: number; failed: number }> {
  let written = 0, failed = 0;
  for (const filter of FILTERS) {
    const defaults = getDefaultSort(filter);
    const limit = 50, offset = 0;
    try {
      const body = await fetchSubmissionList({
        filter,
        reason: "",
        sort: defaults.col,
        sortDir: defaults.dir as "asc" | "desc",
        limit,
        offset,
      });
      const exactKey = `submissions:list:${filter}::${defaults.col}:${defaults.dir}:${limit}:${offset}`;
      const latestKey = `submissions:latest:${filter}`;
      await Promise.all([
        env.SUBMISSIONS_KV.put(exactKey,  JSON.stringify(body), { expirationTtl: LIST_CACHE_TTL }),
        env.SUBMISSIONS_KV.put(latestKey, JSON.stringify(body), { expirationTtl: LIST_LATEST_TTL }),
      ]);
      written++;
    } catch (err) {
      failed++;
      console.error(`[cron] warm-up failed for filter=${filter}:`, err);
    }
  }
  return { written, failed };
}
```

> **Key format note** — the current SSR read key is `${LIST_CACHE_PREFIX}${filter}:${reason}:${sort}:${sortDir}:${limit}:${offset}` with `reason=""` producing `submissions:list:active::processingOrder:asc:50:0` (two consecutive colons). The warm-up must produce the exact same shape. The snippet above writes two colons to match; `data.ts:104` forms the key identically. Validate this in a unit test (`it("writes the exact key data.ts reads")`).

**Wiring** — in [scripts/build-worker-entry.ts:86-89](../../../repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts):

```ts
const queueStart = Date.now();
await refreshQueueStats({ SUBMISSIONS_KV: env.SUBMISSIONS_KV, QUEUE_METRICS_KV: env.QUEUE_METRICS_KV })
  .then(() => console.log("[cron] queue stats refresh completed in " + (Date.now() - queueStart) + "ms"))
  .catch((err) => console.error("[cron] queue stats refresh failed:", err));

// NEW:
const warmupStart = Date.now();
await warmQueueListCache({ SUBMISSIONS_KV: env.SUBMISSIONS_KV })
  .then((r) => console.log(`[cron] queue list warmup: wrote=${r.written} failed=${r.failed} in ${Date.now() - warmupStart}ms`))
  .catch((err) => console.error("[cron] queue list warmup failed:", err));
```

No new cron trigger — reuse existing hourly `"0 * * * *"` schedule at [wrangler.jsonc:104](../../../repositories/anton-abyzov/vskill-platform/wrangler.jsonc).

**TTL change** — find `LIST_CACHE_TTL` in `src/app/api/v1/submissions/route.ts` (the existing `setex`/`put` call in the GET handler) and raise from `60` to `5400`. Comment explains the warm-up cadence. The lazy write behavior stays as a safety net for requests that hit the API before the cron runs after deploy.

**Concurrent-write safety** — KV `put` is last-write-wins; two concurrent writes (cron + live API lazy write) are acceptable because both produce semantically equivalent payloads. `ctx.waitUntil` keeps the write fire-and-forget without blocking scheduled-handler completion.

### 2.6 HTTP contract preservation (AC-US3-03)

| Callsite | Old response | New response | Preserved? |
|---|---|---|---|
| `POST /submissions` with existing pending row | `{ id, state: "RECEIVED", duplicate: true }` | Same — map `kind: "pending"` → this body | Yes |
| `POST /submissions` with existing PUBLISHED row | `{ skillId, skillName, alreadyVerified: true }` | Same — map `kind: "verified"` → this body | Yes |
| `POST /submissions` with existing BLOCKED row | `{ blocked: true, submissionId }` | Same — map `kind: "blocked"` → this body | Yes |
| `POST /submissions` new row | `201 { id, state, createdAt }` | Same — map `kind: "created"` → this body | Yes |
| Batch `POST /submissions` | `{ submissions, count, skipped, repoUrl }` | Same — `skipped` now populated from `upsert` P2002 hits | Yes |
| CLI (`vskill install`) polling | polls `GET /submissions/:id` until PUBLISHED | Unchanged | Yes |

A contract test fixture lives at `src/app/api/v1/submissions/__tests__/http-contract.test.ts` and is updated to hit the new code path. Same JSON shapes are asserted.

## 3. Technology Stack (unchanged)

- **Runtime**: Next.js 15 + OpenNext @ Cloudflare Workers (worker `verified-skill-com`)
- **DB**: Neon Postgres via `@prisma/adapter-neon` + `@neondatabase/serverless`
- **KV**: `SUBMISSIONS_KV` (primary cache), `QUEUE_METRICS_KV` (stats), plus 5 others (unchanged)
- **Queue**: CF Queue `submission-processing`
- **Scan pipeline**: Hetzner VMs run `crawl-worker/server.js`; Tier-2 LLM scan in [crawl-worker/lib/tier2-scan.js](../../../repositories/anton-abyzov/vskill-platform/crawl-worker/lib/tier2-scan.js) uses CF Workers AI Llama 4 Scout → Llama 3.3 → Gemini fallback (subject of the ADR)

## 4. Implementation Phases

### Phase 1 — Database + dedup (AC-US2, AC-US3)
1. Add `@@unique([repoUrl, skillName])` to Prisma schema; run `prisma generate`.
2. Generate the `20260421100000_submission_unique_repo_skill` migration (step-2 SQL only).
3. Write and test `scripts/migrations/0672-collapse-submission-dupes.ts` against a Neon branch seeded with duplicate fixtures.
4. Write `src/lib/submission/upsert.ts` + export via existing shim.
5. Replace call sites in `src/app/api/v1/submissions/route.ts`; delete `src/lib/submission-dedup.ts`; update contract test.
6. Unit test: 20-parallel upsert → 1 row, 20 identical ids.
7. Integration test: run collapse script twice against Neon branch, assert idempotency.

### Phase 2 — Cache warm-up (AC-US1)
1. Extract `fetchSubmissionList` helper from GET handler.
2. Implement `warmQueueListCache`.
3. Wire into scheduled handler.
4. Raise `LIST_CACHE_TTL` to 5400 s.
5. Unit test: warm-up writes exact + latest keys for all 5 filters with correct default sort.
6. Integration test: trigger the scheduled handler locally via `wrangler dev --test-scheduled`; confirm KV keys populated.

### Phase 3 — Tier-2 ADR (AC-US4)
1. Gather baseline metrics (see ADR-0256 §3).
2. Fill in concrete numbers in the ADR; set status to "Proposed — awaiting CTO decision".
3. Commit ADR; ADR is the deliverable — no code change in this phase.

### Phase 4 — Deploy + verify
1. Merge branch → `push-deploy.sh` runs `prisma generate`, builds OpenNext worker, deploys.
2. Run `npx tsx scripts/migrations/0672-collapse-submission-dupes.ts --prod` (or equivalent), then `npx prisma migrate deploy`.
3. E2E: Playwright hits the new deploy's preview URL; asserts `/queue` cold load shows ≥ 50 rows within 1.5 s p95.
4. Manual check: `curl https://verified-skill.com/queue | grep -c '<tr'` confirms rows on first request. `curl 'https://verified-skill.com/queue?q=d'` shows at most one obsidian-brain row.
5. Watch CF logs for 24 h: warm-up cron success, P2002 count near zero (caught cleanly).

## 5. Testing Strategy

| Test type | Target | Tool | Location |
|---|---|---|---|
| Unit | `upsertSubmission` happy path + P2002 branches | Vitest w/ `vi.mock("@/lib/db")` via `vi.hoisted()` | `src/lib/submission/__tests__/upsert.test.ts` |
| Unit | `warmQueueListCache` writes correct keys | Vitest w/ in-memory KV mock | `src/lib/cron/__tests__/queue-list-warmup.test.ts` |
| Unit | `fetchSubmissionList` returns expected shape per filter | Vitest + Prisma mock | `src/lib/queue/__tests__/fetch-submission-list.test.ts` |
| Integration | 20-parallel upsert → 1 row | Vitest against Neon branch | `src/lib/submission/__tests__/upsert-concurrency.int.test.ts` |
| Integration | Collapse script idempotency | Vitest against Neon branch seeded w/ 7 obsidian-brain rows | `scripts/migrations/__tests__/0672-collapse.int.test.ts` |
| Contract | HTTP response shapes preserved | Vitest, fixture-based | `src/app/api/v1/submissions/__tests__/http-contract.test.ts` |
| E2E | `/queue` cold load renders ≥ 50 rows in 1.5 s p95 | Playwright | `e2e/queue-cold-load.spec.ts` |
| E2E | `/queue?q=d` shows ≤ 1 obsidian-brain row | Playwright | `e2e/queue-dedup.spec.ts` |

**Mocking** — follow existing `vi.hoisted()` + `vi.mock()` patterns already in use across the repo. Integration tests use a dedicated Neon branch (create fresh per test via the Neon API if CI supports it; otherwise reuse a shared `ci-0672` branch and truncate relevant tables in `beforeEach`).

**Coverage targets** — unit 95 %, integration 90 %, E2E covers all 4 ACs end-to-end.

## 6. Rollout + Risks

**Deploy order** (single merge, scripted in `push-deploy.sh`):
1. `prisma generate`.
2. Pre-migration: `npx tsx scripts/migrations/0672-collapse-submission-dupes.ts` (reads live Neon, writes archive JSON to `backups/`, collapses in one transaction).
3. `npx prisma migrate deploy` (adds unique index).
4. Build OpenNext worker.
5. `wrangler deploy`.
6. Smoke-check: POST `/api/v1/submissions` with a known duplicate → expect `{ duplicate: true }`. `GET /queue` → expect rows.

**Risks and mitigations**:

| Risk | Mitigation |
|---|---|
| Collapse deletes wrong rows | Survivor chosen by `max(createdAt)` (most recent = most likely to have live FK children). Archive JSON allows full rollback via `0672-restore-submission-dupes.ts`. Archive is committed to git under `backups/` (size estimate < 1 MB for ~1000 victim rows). |
| P2002 on live insert mis-handled | 20-parallel unit test verifies correct handling. Also manual smoke test post-deploy. |
| Migration locks `Submission` table too long | `LOCK TABLE ... IN EXCLUSIVE MODE` is acquired inside the transaction; estimate < 5 s for collapse (based on ~1000 duplicate candidates). During the lock, POST `/submissions` 500s — acceptable for a planned maintenance window. Schedule deploy during US off-peak (02:00 UTC). |
| Cache warm-up cron failure leaves cache empty | SSR still has the lazy-write safety net via the GET handler. `/queue` degrades to the old behavior, not worse. `ctx.waitUntil` in warm-up ensures errors don't break the hourly schedule. |
| Key-format mismatch between warm-up and SSR read | Unit test asserts exact key produced by warm-up matches the key `data.ts:104` reads. Regression-tested. |
| Tier-2 ADR numbers outdated by review time | ADR status is "Proposed"; review date is set when numbers are pulled (within 7 days of the close of 0672). |

**Rollback plan**:
- If the migration step-2 fails (e.g., a row slipped in post-collapse with a duplicate), `prisma migrate resolve --rolled-back` marks it; run collapse again, retry.
- If production behavior regresses (duplicate CLI responses, crashes), revert the deploy; unique index is already in place (safe); re-apply `submission-dedup.ts` from git history. Archive JSON rollback is only needed if data integrity is compromised.

## 7. Deferred

- **Increment 0673** (conditional on ADR-0256 recommendation) — migrate Tier-2 scan to 1–2 GCP spot e2-small VMs; rewrite `crawl-worker/lib/tier2-scan.js` to call `@google/genai` Gemini 2.0 Flash; add preemption retry; add `TIER2_RUNTIME=cloudflare|gcp` feature flag.
- **Close 0657-dark-theme-semantic-tokens** (31/32) — finish the last task before implementation begins on 0672 to maintain WIP focus.
- **Admin rescan endpoint** — dedicated `POST /api/v1/admin/submissions/:id/rescan` that bypasses the unique constraint by updating state (not inserting). Not required by ACs; file as a follow-up if admin workflows need it after dedup lands.

## 8. File Manifest

### Modify (existing files)

| File | Reason |
|---|---|
| [repositories/anton-abyzov/vskill-platform/prisma/schema.prisma:200-208](../../../repositories/anton-abyzov/vskill-platform/prisma/schema.prisma) | Replace `@@index([repoUrl, skillName])` with `@@unique([repoUrl, skillName])`. |
| [repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts:572-603, 668-679, 775-785](../../../repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts) | Replace `checkSubmissionDedup(Batch)` usages with `upsertSubmission`. Delete staleness env parsing. |
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts` (GET handler, near `LIST_CACHE_TTL`) | Raise TTL from 60 s → 5400 s; switch key-building to shared helper. |
| [repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts:86-99](../../../repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts) | Wire `warmQueueListCache` into scheduled handler. |
| [repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts](../../../repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts) | Add `upsertSubmission` re-export. |
| [repositories/anton-abyzov/vskill-platform/src/lib/submission/index.ts](../../../repositories/anton-abyzov/vskill-platform/src/lib/submission) | Export `upsertSubmission` from new `upsert.ts`. |

### Create (new files)

| File | Purpose |
|---|---|
| `repositories/anton-abyzov/vskill-platform/src/lib/submission/upsert.ts` | `upsertSubmission` implementation. |
| `repositories/anton-abyzov/vskill-platform/src/lib/queue/fetch-submission-list.ts` | Shared list-fetching helper (extracted from GET handler). |
| `repositories/anton-abyzov/vskill-platform/src/lib/cron/queue-list-warmup.ts` | `warmQueueListCache` for the hourly cron. |
| `repositories/anton-abyzov/vskill-platform/scripts/migrations/0672-collapse-submission-dupes.ts` | Pre-migration collapse runner + archive writer. |
| `repositories/anton-abyzov/vskill-platform/scripts/migrations/0672-restore-submission-dupes.ts` | Rollback script (archive JSON → DB). |
| `repositories/anton-abyzov/vskill-platform/prisma/migrations/20260421100000_submission_unique_repo_skill/migration.sql` | Step-2 SQL: drop old index, add unique index. |
| `repositories/anton-abyzov/vskill-platform/src/lib/submission/__tests__/upsert.test.ts` | Unit tests. |
| `repositories/anton-abyzov/vskill-platform/src/lib/submission/__tests__/upsert-concurrency.int.test.ts` | Integration test (Neon branch). |
| `repositories/anton-abyzov/vskill-platform/src/lib/cron/__tests__/queue-list-warmup.test.ts` | Unit tests. |
| `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/fetch-submission-list.test.ts` | Unit tests. |
| `repositories/anton-abyzov/vskill-platform/e2e/queue-cold-load.spec.ts` | E2E — cold load renders rows. |
| `repositories/anton-abyzov/vskill-platform/e2e/queue-dedup.spec.ts` | E2E — no duplicate rows. |
| `.specweave/docs/internal/architecture/adr/0256-tier2-runtime.md` | Tier-2 runtime ADR (see companion file). |
| `.specweave/increments/0672-queue-reliability/backups/dedup-collapse-0672.json` | Generated at migration time. |

### Delete

| File | Reason |
|---|---|
| `repositories/anton-abyzov/vskill-platform/src/lib/submission-dedup.ts` | Replaced by DB-level unique + `upsertSubmission`. |
| `repositories/anton-abyzov/vskill-platform/src/lib/submission-dedup.test.ts` (if exists) | Along with the module. |

### Reuse (no change)

| File | What we depend on |
|---|---|
| [src/lib/db.ts](../../../repositories/anton-abyzov/vskill-platform/src/lib/db.ts) | `getDb`, `dbCircuitAllows` |
| [src/lib/env-resolve.ts](../../../repositories/anton-abyzov/vskill-platform/src/lib/env-resolve.ts) | `resolveEnv` |
| [src/lib/submission-categories.ts](../../../repositories/anton-abyzov/vskill-platform/src/lib/submission-categories.ts) | `expandStateCategory`, `isCategoryName` |
| [src/app/queue/data.ts:38-43](../../../repositories/anton-abyzov/vskill-platform/src/app/queue/data.ts) | `getDefaultSort` — reused by warm-up cron |
| [src/lib/submission/createSubmission](../../../repositories/anton-abyzov/vskill-platform/src/lib/submission) | Called inside `upsertSubmission` for the create path |

## 9. Verification Checklist

- [ ] `npx prisma migrate deploy` succeeds on a Neon branch after collapse script runs (no P2002 errors).
- [ ] `scripts/migrations/0672-collapse-submission-dupes.ts` run twice against the same DB — second run reports `archivedCount: 0, changed: false`.
- [ ] `npx vitest run src/lib/submission/__tests__/upsert.test.ts` — 20-parallel upsert produces 1 row, 20 identical ids.
- [ ] `npx vitest run src/lib/cron/__tests__/queue-list-warmup.test.ts` — writes all 5 filter keys with correct default sort.
- [ ] `npx playwright test e2e/queue-cold-load.spec.ts` — against a freshly-deployed preview, ≥ 50 rows visible within 1.5 s p95.
- [ ] `npx playwright test e2e/queue-dedup.spec.ts` — no obsidian-brain duplicates.
- [ ] Manual: `curl https://verified-skill.com/queue` → HTML contains table rows.
- [ ] Manual: `curl 'https://verified-skill.com/queue?q=d'` → at most one obsidian-brain row.
- [ ] ADR-0256 committed with concrete numbers in §3.
- [ ] 24 h post-deploy log scan: `[cron] queue list warmup` logs show `wrote=5 failed=0` consistently.
