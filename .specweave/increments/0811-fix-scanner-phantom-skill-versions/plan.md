# Implementation Plan: Fix scanner phantom SkillVersion bumps

## Architecture

```
Scanner.scanOneSkill (existing)                Backfill endpoint (new)
─────────────────────────────                   ───────────────────────
fetchLatestCommit (HEAD SHA)                    POST /api/v1/admin/skills/{id}/
                                                  backfill-content-hashes
   │
   ▼  (new SHA)                                 require admin
existing idempotency guards                       │
   │  - lastSeenSha === sha → unchanged            ▼
   │  - SkillVersion at gitSha → unchanged       SELECT versions
   ▼  (passes)                                    ORDER BY createdAt
                                                  │
NEW: fetchSkillMdAtSha(repo, sha, path)          ▼  for each "sha256:pending:" row
   │   raw.githubusercontent.com                fetch SKILL.md at row.gitSha
   ▼                                            compute real SHA-256
sha256(content)                                  UPDATE row.contentHash
   │                                              │
   ▼                                              ▼  after all real
NEW: getLatestSkillVersion(skillId)              find adjacent dup contentHash
   │   SELECT WHERE skillId LIMIT 1              DELETE later duplicates
   │   ORDER BY createdAt DESC                    │
   │                                              ▼
   ▼                                            UPDATE Skill SET
contentHash === prev.contentHash ?                currentVersion = surviving max,
   │                                              lastSeenSha = original HEAD
   ├── YES → advance lastSeenSha + lastChecked   │
   │         emit dedup metric, return unchanged  ▼
   │                                              return summary JSON
   └── NO → existing deriveNextVersion + writeSkillVersionWithOutbox path
            with REAL contentHash (no pending: prefix)
```

## Modules

### Modified — `src/lib/skill-update/scanner.ts`
- Add helper `fetchSkillMdAtSha(repoUrl, sha, skillPath?)` — async, returns `{ ok: true, content: string } | { ok: false, error: string }`. Pulls `https://raw.githubusercontent.com/<owner>/<repo>/<sha>/<skillPath ?? 'SKILL.md'>`. Uses existing `GITHUB_TOKEN` if set (for rate limit). 5s timeout.
- Add helper `sha256Hex(content: string)` — uses Web Crypto `crypto.subtle.digest("SHA-256", ...)` and returns lowercase hex (no prefix).
- Add helper `getLatestSkillVersion(db, skillId)` — `db.skillVersion.findFirst({ where: { skillId }, orderBy: { createdAt: "desc" }, select: { id, contentHash, version, gitSha } })`.
- Modify `scanOneSkill`: after the existing idempotency guards (line 152), call the helpers above. If real-hash matches the latest SkillVersion's contentHash → write `lastSeenSha` + `lastCheckedAt`, emit metric `scanner.contenthash.dedup.hits`, return `{ status: "unchanged" }`. If different (or fetch fails) → fall through to the existing bump path, but use the REAL hash when fetch succeeded.

### Modified — `src/lib/skill-update/__tests__/scanner.test.ts`
- New describe block `scanOneSkill — content-hash dedup gate` with 5 tests:
  - TC-S01 same content → no bump (mock fetch returns identical SKILL.md, mock kv returns "")
  - TC-S02 different content → bump with real hash (no `pending:` prefix on the written row)
  - TC-S03 fetch error → falls through to legacy bump-with-pending-hash (preserves prior behavior on outage)
  - TC-S04 legacy-pending previous row + new fetch matches → still dedups (compares real-vs-pending where pending was just written by a previous scanner pass that didn't have the gate)
  - TC-S05 first publish (no previous row) → bumps with real hash

### New — `src/app/api/v1/admin/skills/[id]/backfill-content-hashes/route.ts`
Shape:
```ts
export async function POST(request: NextRequest, ctx: { params: Promise<{ id: string }> }): Promise<Response> {
  const auth = await requireAdmin(request);
  if (isAuthError(auth)) return auth;

  const { id } = await ctx.params;
  const body = await request.json().catch(() => ({})) as { dryRun?: boolean };
  const dryRun = body.dryRun === true;

  const db = await getDb();
  const skill = await db.skill.findUnique({ where: { id } });
  if (!skill) return errorResponse("skill not found", 404);

  const versions = await db.skillVersion.findMany({
    where: { skillId: id },
    orderBy: { createdAt: "asc" },
    select: { id: true, version: true, contentHash: true, gitSha: true, createdAt: true },
  });

  let recomputed = 0;
  for (const v of versions) {
    if (!v.contentHash.startsWith("sha256:pending:")) continue;
    const fetched = await fetchSkillMdAtSha(skill.repoUrl, v.gitSha, skill.skillPath ?? "SKILL.md");
    if (!fetched.ok) continue; // log + skip
    const realHash = await sha256Hex(fetched.content);
    if (!dryRun) {
      await db.skillVersion.update({ where: { id: v.id }, data: { contentHash: realHash } });
    }
    v.contentHash = realHash; // update local copy for the dedup pass below
    recomputed++;
  }

  // Collapse adjacent identical hashes (newest copy is removed; oldest survives).
  const sorted = [...versions].sort((a, b) => +a.createdAt - +b.createdAt);
  let survivor: typeof sorted[0] | null = null;
  let lastDeletedGitSha: string | null = null;
  let deleted = 0;
  for (const v of sorted) {
    if (survivor && v.contentHash === survivor.contentHash) {
      // duplicate — delete the later row
      if (!dryRun) await db.skillVersion.delete({ where: { id: v.id } });
      deleted++;
      lastDeletedGitSha = v.gitSha;
    } else {
      survivor = v;
    }
  }

  // Reset Skill.currentVersion to the highest surviving version, advance lastSeenSha to the deleted-newest.
  let finalCurrentVersion = skill.currentVersion;
  let finalLastSeenSha = skill.lastSeenSha;
  if (survivor && deleted > 0) {
    finalCurrentVersion = survivor.version;
    if (lastDeletedGitSha) finalLastSeenSha = lastDeletedGitSha;
    if (!dryRun) {
      await db.skill.update({
        where: { id },
        data: { currentVersion: finalCurrentVersion, lastSeenSha: finalLastSeenSha },
      });
    }
  }

  return jsonResponse({ scanned: versions.length, recomputed, deleted, finalCurrentVersion, finalLastSeenSha, dryRun });
}
```

### New — `src/app/api/v1/admin/skills/[id]/backfill-content-hashes/__tests__/route.test.ts`
- TC-B01 — non-admin → 401/403.
- TC-B02 — non-existent skill id → 404.
- TC-B03 — dryRun=true on phantom-shaped fixture (3 rows: real, pending matching real, pending matching real) → returns `{scanned:3, recomputed:2, deleted:2, finalCurrentVersion:"1.1.0"}` with NO DB mutations (verify via mock kv calls).
- TC-B04 — dryRun=false (default) on same fixture → returns the same numbers AND skill row + version rows are mutated.
- TC-B05 — idempotent re-run after collapse → `{scanned:1, recomputed:0, deleted:0}`.

## Reused utilities

- `getDb`, `withDbTimeout` — `@/lib/db`.
- `requireAdmin`, `isAuthError` — `@/lib/auth`.
- `jsonResponse`, `errorResponse` — `@/lib/api-helpers`.
- `writeSkillVersionWithOutbox`, `publishOutboxEventAfterCommit` — `@/lib/skill-update/outbox-writer`.
- `deriveNextVersion` — existing in scanner.ts (`@/lib/skill-update/...`).

## ADR (inline)

**Decision**: Compute the real content hash by fetching SKILL.md from `raw.githubusercontent.com` at the new HEAD SHA, not from a local clone or git tree.
**Rationale**: vskill-platform runs on Cloudflare Workers — no local git checkout is available. The raw URL accepts a commit SHA in place of a branch, which gives us byte-exact content for any historical commit. The existing scanner already uses GitHub's REST API for HEAD discovery; raw fetch is simpler and not rate-limited the same way.
**Alternatives**: (1) Hash the entire skill subtree (e.g., everything under `skills/<name>/**`) for completeness — rejected for v1: SKILL.md is the single source of truth for the version display, and tree-hash diffs catch every UI-relevant change. Tree-hash is a future enhancement when skills carry sibling assets that affect behavior.

**Decision**: Fall through to legacy `pending:` hash on raw fetch failure rather than failing the scan.
**Rationale**: a transient GitHub outage must not block update detection across the entire registry. The fallback path is identical to today's behavior, so failure is no-op in the worst case.

**Decision**: Backfill is on-demand per skill, not a global migration.
**Rationale**: 140+ skills × ~2 versions average × raw fetch (~200 ms) = ~60s budget. Doable but risky to run in a single migration. Per-skill admin endpoint lets us prioritize affected skills (`remotion-best-practices` first) and avoid touching skills with no pending rows.

## Test strategy

| File | Type | Coverage |
|------|------|----------|
| `src/lib/skill-update/__tests__/scanner.test.ts` | vitest unit | TC-S01..TC-S05 (content-hash dedup gate) |
| `src/app/api/v1/admin/skills/[id]/backfill-content-hashes/__tests__/route.test.ts` | vitest unit | TC-B01..TC-B05 (admin auth, dry run, collapse, idempotency) |

TDD discipline: T-001/T-003 are RED, T-002/T-004 are GREEN.

## Deploy + smoke

1. `rm -rf .open-next && npm run build && npm run build:worker && npm run deploy`.
2. POST `/api/v1/admin/skills/<remotion-best-practices-id>/backfill-content-hashes` with admin auth.
   Expected response: `{scanned:3, recomputed:2, deleted:2, finalCurrentVersion:"1.1.0"}`.
3. Verify: `GET /api/v1/skills/anton-abyzov/vskill/remotion-best-practices/versions` returns 1 row, `version:"1.1.0"`, real contentHash.
4. Wait 12 minutes for next `*/10` cron tick. Verify NO new SkillVersion rows for `remotion-best-practices` (still 1).
5. Playwright: assert `/skills/anton-abyzov/vskill/remotion-best-practices/versions` page renders single version row.
