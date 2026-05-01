# Implementation Plan: Skill Versionless Rows Fix

## Overview

Eliminate "discovered but unversioned" Skill rows in vskill-platform. Today, `rebuild-index/route.ts:130` writes `Skill.upsert(...)` with `currentVersion: "1.0.0"` but never creates a paired `SkillVersion` row, leaving the `/versions` API returning `count: 0` for verified skills (e.g. `gitroomhq/postiz-agent/postiz`). The architecture invariant in `outbox-writer.ts:18` bans raw `skillVersion.create()` outside the outbox helper, but does not enforce that every `Skill` has at least one `SkillVersion`.

This plan introduces:
1. A single helper (`createSkillWithVersion()`) that wraps `Skill.upsert` + `writeSkillVersionWithOutbox` in one `$transaction` — the structural fix.
2. An architecture test that fails CI when any new caller writes a `Skill` row outside the helper or the existing `submission/publish.ts` allowlist.
3. An admin backfill route to remediate the existing orphan population.
4. A `/versions` route shape (`unversioned: true`) plus a Studio UI copy variant so users see "discovered, no published version yet" instead of an indistinguishable "no versions found".

## Architecture

### Architecture Decisions (ADR-style)

#### ADR-0819-01: Every `Skill` row must have ≥1 paired `SkillVersion`

**Decision**: Treat the absence of a `SkillVersion` for an existing `Skill` as an architectural defect. New code paths that create `Skill` rows MUST also write the first version in the same transaction.

**Why**: The studio detail panel, the `/versions` API, and `/check-updates` all assume the join is non-empty. A `Skill` row alone is a half-state that nothing downstream can render correctly. The outbox already guarantees pair-writes for `SkillVersion + UpdateEvent`; we are extending that contract one level outward.

**Alternatives rejected**: Synthesizing a "fake version" lazily on read in the `/versions` route — pushes the inconsistency to every reader, breaks `check-updates` chronology assumptions, and creates a perpetual schema lie.

#### ADR-0819-02: `createSkillWithVersion()` is the single callsite for paired writes

**Decision**: New helper at `src/lib/skills/create-skill-with-version.ts` accepts `{ where, create, update }` for `Skill.upsert` plus a `SkillVersionInput`, runs both inside `db.$transaction`, and returns `{ skill, skillVersion, eventId, payload }`. All future Skill-row writers route through it. Allowlist exception: `src/lib/submission/publish.ts:300` — already pair-writes via `writeSkillVersionWithOutbox` at line 676 inside its own transaction; refactoring that caller is out of scope and would add risk without value.

**Why**: One place to enforce the invariant, one place to test it, one place for the architecture grep to allow.

#### ADR-0819-03: `bumpSource: "discovery-backfill"` distinguishes synthesized versions from authored ones

**Decision**: Add a new `bumpSource` value alongside the existing `frontmatter` / `auto-patch` / `legacy-backfill`. The helper passes it via `extraData` to `writeSkillVersionWithOutbox`. Any consumer that later wants to filter "real publishes" from "discovery synthesis" has the discriminator.

**Why**: Honest imprecision over silent forgery. Phase 2 (lockfile, `check-updates`, trust scoring) can opt in.

**Alternatives rejected**: Reusing `legacy-backfill` — overloads a value with two different remediation contexts and would prevent future filtering.

#### ADR-0819-04: Backfill chronology — `SkillVersion.createdAt = skill.certifiedAt`

**Decision**: When the backfill route mints a `SkillVersion` for a pre-existing orphan `Skill`, set `SkillVersion.createdAt` to `skill.certifiedAt ?? skill.createdAt`, NOT `now()`.

**Why**: `/api/v1/skills/check-updates` (`route.ts:250`) uses `orderBy: { createdAt: "desc" }, distinct: ["skillId"]` to detect "newer than installed". Backfilling 1000 synthetic v1.0.0 rows with `createdAt = now()` would mark them all as fresh updates and fan out spurious update notifications to every lockfile holder. Aligning `createdAt` with the original discovery timestamp keeps chronology honest.

**Mitigation if a consumer still flags noise**: the `bumpSource: "discovery-backfill"` discriminator is the secondary filter.

#### ADR-0819-05: Degraded `contentHash` handling for SKILL.md cache misses

**Decision**: When the backfill route or the `rebuild-index` create-branch lacks a real SKILL.md (KV cache miss, no submission), use `sha256("")` as the placeholder `contentHash` — a well-defined, non-empty hash. The `bumpSource: "discovery-backfill"` flag is the explicit "this hash is degraded, do not trust for diff" signal.

**Why**: F-CR-2C invariant at `publish.ts:660` rejects empty `contentHash`. Sending an empty string would crash the helper. `sha256("")` satisfies the schema check while being trivially detectable downstream when paired with the bumpSource flag.

**Alternatives rejected**: Synthesizing a hash from `repoUrl + sha` — looks legitimate, would fool deduplication.

### Components

| Component | Role |
|---|---|
| `createSkillWithVersion()` (new) | Wraps `Skill.upsert` + `writeSkillVersionWithOutbox` in one txn. SINGLE callsite for new pair-writes. |
| `architecture-skill-pair.test.ts` (new) | CI guard. Greps src/ for `db.skill.create` / `db.skill.upsert` outside the allowlist. |
| `backfill-versionless-skills` route (new) | Admin POST endpoint. Scans `Skill` rows with no matching `SkillVersion`, writes synthetic v1.0.0 via the helper. |
| `rebuild-index` route (modify, line 130) | Replace `db.skill.upsert(...)` create-branch with `createSkillWithVersion(...)`. Update branch unchanged. |
| `/versions` route (modify) | When `count === 0` AND skill row exists, return `{ versions: [], count: 0, unversioned: true, currentVersion }`. |
| `SkillDetailPanel.tsx:595` (modify, vskill repo) | When `unversioned: true`, render distinct copy + new `data-testid="skill-detail-unversioned"`. |

### Component Map (file paths)

**NEW** (vskill-platform):
- `repositories/anton-abyzov/vskill-platform/src/lib/skills/create-skill-with-version.ts`
- `repositories/anton-abyzov/vskill-platform/src/lib/skills/__tests__/create-skill-with-version.test.ts`
- `repositories/anton-abyzov/vskill-platform/src/lib/skills/__tests__/architecture-skill-pair.test.ts`
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versionless-skills/route.ts`
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versionless-skills/__tests__/route.test.ts`
- `repositories/anton-abyzov/vskill-platform/tests/e2e/0819-versionless-skills.spec.ts`

**MODIFY** (vskill-platform):
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rebuild-index/route.ts` — line 130: route create-branch through `createSkillWithVersion`; update-branch unchanged.
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts` — when `count === 0` AND skill exists, return `unversioned: true`.

**MODIFY** (vskill — studio UI):
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx` — line 595: branch on `unversioned: true`, render new copy with `data-testid="skill-detail-unversioned"`.

### Data flow

```mermaid
flowchart TD
    A[skills.sh crawler] --> B[KV index]
    B --> C[POST /admin/rebuild-index]
    C --> D{Skill row exists?}
    D -- yes --> E[db.skill.update — unchanged]
    D -- no --> F[createSkillWithVersion]
    F --> G[db.$transaction]
    G --> H[db.skill.upsert]
    G --> I[writeSkillVersionWithOutbox]
    I --> J[SkillVersion + UpdateEvent rows]

    K[POST /admin/backfill-versionless-skills?dryRun=true] --> L[Scan Skill WHERE no SkillVersion]
    L --> M{KV cache hit?}
    M -- yes --> N[Real contentHash from skillmd:id]
    M -- no --> O[sha256\"\" + bumpSource: discovery-backfill]
    N --> P[writeSkillVersionWithOutbox]
    O --> P
    P --> Q[SkillVersion.createdAt = skill.certifiedAt]

    R[GET /skills/owner/repo/skill/versions] --> S{count === 0 AND skill exists?}
    S -- yes --> T[Return unversioned: true + currentVersion]
    S -- no --> U[Return versions array]
    T --> V[Studio renders skill-detail-unversioned]
    U --> W[Studio renders skill-detail-version-row]
```

### Reused functions (cite file:line)

| Function | Path | Use |
|---|---|---|
| `writeSkillVersionWithOutbox` | `src/lib/skill-update/outbox-writer.ts:81` | Sole production writer for `SkillVersion` rows; called inside the helper and the backfill loop |
| `hasInternalAuth` | `src/lib/internal-auth` | First-line auth on the backfill route (matches `backfill-versions/route.ts:40`) |
| `requireAdmin` / `isAuthError` | `src/lib/auth` | Admin JWT fallback when internal-auth header is absent |
| `jsonResponse`, `errorResponse` | `src/lib/api-helpers` | Response shape consistency with sibling admin routes |
| `resolveSkillName` | `src/lib/api/skill-params.ts` | Compute canonical `name` from `[owner]/[repo]/[skill]` params on the `/versions` route |
| `getKV` | `src/lib/kv` (env-aware) | Read `skillmd:${skillId}` for the real `contentHash` in the backfill path |
| `parseSemver` | `src/lib/integrity/semver` | Already used by `backfill-versions/route.ts:29` — synthesize `major/minor/patch` columns for the `SkillVersion` extraData |
| `eventUlid` | `src/lib/skill-update/ulid` | (Indirectly via outbox) — `eventId` generation |
| `deriveCertTier`, `isVendorOrg` | `src/lib/cert/*` | Already imported in `rebuild-index/route.ts`; helper inherits the values from caller |

### Helper signature

```ts
// src/lib/skills/create-skill-with-version.ts
export interface CreateSkillWithVersionResult {
  skill: { id: string; name: string };
  skillVersion: { id: string; version: string };
  eventId: string;
  payload: SkillUpdateEvent;
  /** True when an existing row was found (helper short-circuited the version write). */
  preExisting: boolean;
}

export async function createSkillWithVersion(
  db: PrismaClient,
  upsertArgs: {
    where: Prisma.SkillWhereUniqueInput;
    create: Prisma.SkillCreateInput;
    update: Prisma.SkillUpdateInput;
  },
  versionInput: SkillVersionInput,
  source: OutboxSource,
  env: unknown,
): Promise<CreateSkillWithVersionResult>;
```

Behavior:
1. Open `db.$transaction(async (tx) => { ... })`.
2. `findUnique({ where: upsertArgs.where, select: { id: true } })` to detect pre-existing rows. If present, run the `update` branch only (no version write — those rows have prior versions); return `preExisting: true`.
3. If absent, `tx.skill.upsert(upsertArgs)` (still uses upsert defensively against race), then `writeSkillVersionWithOutbox(tx, { id, name, currentVersion }, versionInput, source, env)`.
4. After commit, caller is responsible for `publishOutboxEventAfterCommit(payload, env)` (fire-and-forget). Helper returns `payload` to make this explicit.

## Risks & gotchas

(Verbatim from `compiled-questing-aurora.md` — these are the source-of-truth risks the architect signed off on.)

1. **`/api/v1/skills/check-updates` chronology** — query at `src/app/api/v1/skills/check-updates/route.ts:250` uses `orderBy: { createdAt: "desc" }, distinct: ["skillId"]`. Backfilling synthetic v1.0.0 rows with `createdAt = now()` would mark them "newer than nothing" and could trigger spurious update notifications to lockfile holders. **Mitigation**: set `createdAt = skill.certifiedAt ?? skill.createdAt` so the synthetic row's timestamp matches the moment the Skill was discovered. (See ADR-0819-04.)

2. **F-CR-2C contentHash invariant** — `publish.ts:660` refuses empty `contentHash`. The new helper paths must not violate this. **Strategy**: use `sha256("")` (well-defined non-empty hash) plus `bumpSource: "discovery-backfill"` as the explicit "this is degraded" flag. Phase 2 consumers that care can detect it. (See ADR-0819-05.)

3. **`certTier` / `certMethod` required** — `schema.prisma` marks them required on `SkillVersion`. Synthesize from the parent `Skill`'s values; both `rebuild-index` and the backfill route already have those fields populated.

4. **`bumpSource: "discovery-backfill"`** — new value alongside `frontmatter` / `auto-patch` / `legacy-backfill`. No downstream UI filter exists today, so additive only. Add to the inline doc comment listing valid bumpSources.

5. **Duplicate UpdateEvent fanout** — backfilling N orphans emits N events. The reconciler retries any unflushed event past 10s. To avoid SSE-flood for installed-skill subscribers, set the new SkillVersion's `version === currentVersion` so consumers see "no real change" — and rely on bumpSource as the discriminator if needed.

6. **Architecture test false positives** — `db.skill.create()` may legitimately appear in seed scripts or migrations. Allowlist scoped to `src/` only (matches `architecture.test.ts:29` `SRC_ROOT`); migrations live outside `src/` and are unaffected.

## Test strategy

| File | Type | Coverage target |
|---|---|---|
| `src/lib/skills/create-skill-with-version.ts` | Unit + integration | 95% |
| `src/lib/skills/__tests__/architecture-skill-pair.test.ts` | Architecture (CI guard) | n/a — pass/fail |
| `src/app/api/v1/admin/backfill-versionless-skills/route.ts` | Integration | 90% |
| `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts` (modified branch) | Unit | 100% of new branch |
| `tests/e2e/0819-versionless-skills.spec.ts` | Playwright E2E | 100% of AC scenarios |
| `eval-ui` SkillDetailPanel.tsx | Vitest snapshot | Snapshot for the new copy |

### Test scenarios per file

**`create-skill-with-version.test.ts`**:
- (a) Create-path: writes Skill + SkillVersion + UpdateEvent in same txn
- (b) Update-path: pre-existing Skill detected → no version row written; returns `preExisting: true`
- (c) Idempotency: re-running with same `where` does not duplicate version rows
- (d) Txn rollback: when `writeSkillVersionWithOutbox` throws, `Skill.upsert` is rolled back too (verify via post-txn `findUnique` returning null)
- (e) `bumpSource: "discovery-backfill"` propagates into `SkillVersion.bumpSource`
- (f) Returns `payload` for caller to publish post-commit

**`architecture-skill-pair.test.ts`** (mirrors `architecture.test.ts:116`):
- Walk `src/`, comment-strip, regex `/\b(?:tx|prisma|db|client|trx)\.skill\.(?:create|upsert)\s*\(/`
- Allowlist: `lib/skills/create-skill-with-version.ts`, `lib/submission/publish.ts`, test files (markers from `architecture.test.ts:38`)
- Positive assertion: `rebuild-index/route.ts` post-fix uses `createSkillWithVersion(` (regression guard, mirrors the `scanner.ts` positive assertion at `architecture.test.ts:143`)

**`backfill-versionless-skills/__tests__/route.test.ts`** (mirrors `backfill-versions/__tests__/route.test.ts`):
- (a) Auth: returns 401 without internal-auth header AND without admin JWT
- (b) Auth: returns 200 with internal-auth header
- (c) Auth: returns 200 with admin JWT
- (d) `dryRun=true`: scans, returns counts, writes nothing
- (e) Real run: skips already-versioned skills (idempotent)
- (f) Real run: writes SkillVersion via outbox helper for orphan rows
- (g) `createdAt` chronology: synthetic row's `createdAt === skill.certifiedAt`
- (h) KV cache hit path: real `contentHash` from `skillmd:${id}`
- (i) KV cache miss path: `sha256("")` + `bumpSource: "discovery-backfill"`
- (j) Error array: per-skill failures appended, batch continues
- (k) Pagination: `batch=N` honored, `cursor` advances via `id`
- (l) Response shape: `{ dryRun, scanned, updated, skipped, errors }`

**Modified `versions/route.ts`** unit:
- (a) Skill exists, count > 0 → `{ versions, count, unversioned: false }` (or omitted — backwards compat)
- (b) Skill exists, count === 0 → `{ versions: [], count: 0, unversioned: true, currentVersion }`
- (c) Skill not found → 404 (unchanged)

**Playwright E2E** (`tests/e2e/0819-versionless-skills.spec.ts`):
- (a) `GET /api/v1/skills/gitroomhq/postiz-agent/postiz/versions` returns `count >= 1` post-backfill
- (b) `GET /api/v1/skills/postiz/versions` (bare-name) still 404s
- (c) `https://verified-skill.com/skills/gitroomhq/postiz-agent/postiz/versions` page renders without 500
- (d) Studio detail panel: "see all versions →" link `href` is correct + `v1.0.0` row visible (target `data-testid="skill-detail-versions"`)
- (e) Studio detail panel: a synthetic Skill with no version returns `unversioned: true` JSON and renders `data-testid="skill-detail-unversioned"` copy

## Implementation phases

### Phase 1: Helper + invariant (TDD)
1. Write `create-skill-with-version.test.ts` (RED).
2. Implement `create-skill-with-version.ts` (GREEN).
3. Write `architecture-skill-pair.test.ts` (RED — fails because `rebuild-index/route.ts:130` still calls `db.skill.upsert` directly).
4. Refactor `rebuild-index/route.ts:130` to call `createSkillWithVersion()` for the create-branch (GREEN).
5. Refactor pass: pull shared `deriveCertTier`/`autoCategory` synthesis into a small helper inside the route file if duplication appears.

### Phase 2: Backfill route + UI
6. Write `backfill-versionless-skills/__tests__/route.test.ts` (RED).
7. Implement `backfill-versionless-skills/route.ts` mirroring `backfill-versions/route.ts` shape (GREEN).
8. Modify `/versions/route.ts` to add the `unversioned` branch (RED → GREEN with the route unit test).
9. Modify `SkillDetailPanel.tsx:595` to branch on `unversioned: true` (vskill repo, separate PR).

### Phase 3: E2E + deploy
10. Write Playwright E2E `tests/e2e/0819-versionless-skills.spec.ts`.
11. Local verification: dev server, hit `/versions`, run backfill against local DB, verify postiz returns `count >= 1`.
12. Studio local preview per `feedback_video_local_preview.md`: `npx vskill@latest studio`, search "postiz", verify v1.0.0 row visible.
13. Deploy via `scripts/push-deploy.sh` (db:generate → db:migrate → build → build:worker → deploy → cache-warm).
14. Production backfill: dry-run first (`?dryRun=true&batch=100`), review counts, then real run.

## Deploy plan

Deploy entry: `repositories/anton-abyzov/vskill-platform/scripts/push-deploy.sh origin main`.

**Pipeline order** (from the script — chained because each step depends on the previous):
1. `npm run db:generate` — Prisma client regen (no schema changes here, but harmless and required by build).
2. `npm run db:migrate` — no migrations in this increment; the backfill is a one-shot route, not a migration.
3. `npm run build` — Next.js production build.
4. `npm run build:worker` — OpenNext Cloudflare Workers bundle.
5. `npm run deploy` — `wrangler deploy` (note: per `project_vskill_platform_deploy.md`, the bare `npm run deploy` skips build; the script's explicit chain is the right form).
6. Cache-warm step (script).

**Pre-flight**:
- `pkill -f "specweave dashboard"` — per `feedback_dashboard_kills_rate_limit.md`, the dashboard polls GitHub continuously and will collide with the bulk backfill's outbound traffic.
- `npx wrangler tail` running in a side terminal for the first 60s post-deploy.

**Production backfill (gated, two-step)**:
1. `curl -X POST -H "X-Internal-Key: $KEY" "https://verified-skill.com/api/v1/admin/backfill-versionless-skills?dryRun=true&batch=100"` → review `{ scanned, updated, skipped, errors }`.
2. Drop `&dryRun=true` for the real run. Watch wrangler tail + verified-skill.com `/api/v1/stats` for anomalies.

**Rollback**: the increment ships pure additions (helper, new route, new E2E, additive `unversioned` field) plus one refactor (`rebuild-index/route.ts:130`). Rollback is `git revert` of the deploy commit + redeploy. The backfilled `SkillVersion` rows can stay — they are correct data, not corruption.

## Verification (pre-close checklist)

1. **Unit + integration** — `npx vitest run` from `vskill-platform/` passes. Coverage ≥95% on the helper, ≥90% on the backfill route.
2. **Architecture test** — `architecture-skill-pair.test.ts` passes; manually break it by adding a `db.skill.create` to a scratch file → expect CI red.
3. **Studio Vitest snapshot** — `npx vitest run` from `vskill/src/eval-ui/` passes including the new `skill-detail-unversioned` snapshot.
4. **Manual postiz check (local)** — start `vskill-platform` dev (`npm run dev`, port 3000), run backfill against local DB, curl `/api/v1/skills/gitroomhq/postiz-agent/postiz/versions` → expect `{ versions: [{version:"1.0.0", ...}], count: 1, unversioned: false }`.
5. **Studio local preview** — `npx vskill@latest studio` (port-hashed), search "postiz", click into detail, assert v1.0.0 row visible. Required by `feedback_video_local_preview.md`.
6. **Deploy** — `./scripts/push-deploy.sh origin main` from `vskill-platform/`. Watch `npx wrangler tail` for 60s.
7. **Production backfill (gated)** — dry-run first, review counts, then real run.
8. **Playwright E2E** — `npx playwright test tests/e2e/0819-versionless-skills.spec.ts` from `vskill-platform/`; full suite from `vskill/src/eval-ui/` if the panel snapshot changed.
9. **Pre-flight kill** — `pkill -f "specweave dashboard"` before the production backfill (per `feedback_dashboard_kills_rate_limit.md`).

## Out of scope

- Refactoring `submission/publish.ts:300` to go through `createSkillWithVersion()`. It already pair-writes via `writeSkillVersionWithOutbox` at line 676 inside its own txn — moving it would add risk without changing behavior. Allowlisted explicitly.
- Adding lockfile/`check-updates` filtering on `bumpSource`. The discriminator is added; consumers can opt in later (Phase 2).
- Schema migration for an enforced FK constraint (e.g. `Skill.firstVersionId`). The architecture test + helper provide the same guarantee at the application layer; a DB-level constraint is a separate increment.
- Backfilling the `UpdateEvent.publishedAt` for past discovery rows — the reconciler will pick up the new ones; historical telemetry is not retroactive.
