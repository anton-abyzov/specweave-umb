# Implementation Plan: Cert-tier safety follow-up

> Source approved plan: `~/.claude/plans/parsed-fluttering-sphinx.md`
> Reference: `.specweave/increments/0744-fix-cert-tier-muddle-versions-tab/logs/backfill-2026-04-26.md`

## Architecture Decisions

### AD-001: New endpoint, not modify existing
`POST /api/v1/admin/recompute-skill-cert-tiers` — new file. Parallel to the existing `recompute-version-cert-tiers` (which targets the SkillVersion table). The existing `trusted-author-backfill` endpoint stays intact because it does richer trust recomputation that may matter for non-vendor edge cases. The new endpoint is the fast vendor-only escape hatch.

### AD-002: Single bulk update, no per-row trust recomputation
Vendor-org status is a closed set (8 orgs in `VENDOR_ORGS`). For these, the target state is always `{ certTier: 'CERTIFIED', certMethod: 'VENDOR_AUTO', trustScore: 100, trustTier: 'T4', isTainted: false }` — no need to recompute per-row. One `prisma.skill.updateMany()` call. Avoids the DB-circuit failure mode of `trusted-author-backfill`.

### AD-003: Centralize derivation via `deriveCertTier()` + enforce by architecture test
Same pattern 0744 established for the scanner. Every code path that writes `certTier` MUST go through `deriveCertTier()` or be on an explicit allowlist (vendor-only backfills + the canonical derivation modules). The test makes the contract executable — any future hardcoded write fails the build with a file-path message.

### AD-004: Structured `console.log` for audit trail (no external sink dependency)
JSON-formatted log lines emitted to stdout land in CF Worker logs viewable via `wrangler tail`. No need for a new logging dependency, audit table, or external sink. Defensive try/catch around the log call so log-serialization failure can't abort the batch.

### AD-005: TDD strict per project config
RED → GREEN per phase. New tests fail before implementation; pass after.

## Component Design

### 1. `src/app/api/v1/admin/recompute-skill-cert-tiers/route.ts` (NEW — Phase 1)

```ts
export async function POST(request: NextRequest) {
  if (!(await hasInternalAuth(request))) {
    const auth = await requireAdmin(request);
    if (isAuthError(auth)) return auth;
  }
  const db = await getDb();
  const vendorOrgList = [...VENDOR_ORGS];

  const result = await db.skill.updateMany({
    where: {
      author: { in: vendorOrgList, mode: "insensitive" },
      OR: [
        { certTier: { not: "CERTIFIED" } },
        { trustScore: { lt: 100 } },
        { isTainted: true },
      ],
    },
    data: {
      certTier: "CERTIFIED",
      certMethod: "VENDOR_AUTO",
      trustScore: 100,
      trustTier: "T4",
      isTainted: false,
      taintedAt: null,
      taintReason: null,
    },
  });

  // Sample (post-state) for response audit — fetch up to 20 vendor skills to confirm
  const sample = await db.skill.findMany({
    where: { author: { in: vendorOrgList, mode: "insensitive" } },
    take: 20,
    select: { name: true, author: true, certTier: true, certMethod: true, trustScore: true, trustTier: true },
  });

  return jsonResponse({ ok: true, updated: result.count, sample });
}
```

### 2. `src/app/api/v1/admin/blocklist/[id]/unblock/route.ts` (EDIT — Phase 2)

Two edits in the same `if (skill) { ... }` block (lines ~52 + ~67):
- Compute `const { certTier, certMethod } = deriveCertTier(null, { isVendor: isVendorOrg(skill.author) })` once at the top of the block.
- Use `certTier` and `certMethod` in both the `db.skill.updateMany({ data })` call and the `updateSearchShard({ certTier })` payload.

Imports added: `deriveCertTier` from `@/lib/submission/types`, `isVendorOrg` from `@/lib/trust/trusted-orgs`.

`skill.author` is already in the SELECT — no schema change needed.

### 3. `src/app/api/v1/admin/recompute-version-cert-tiers/route.ts` (EDIT — Phase 3)

Add structured logging inside the per-row loop (after each successful update):
```ts
try {
  console.log(JSON.stringify({
    event: "recompute-version-cert-tier",
    skillId: row.skillId,
    name: row.skill.name,
    version: row.version,
    before,
    after: target,
    ts: new Date().toISOString(),
  }));
} catch { /* serialization failure must not abort batch */ }
```

After the loop, before `return jsonResponse(...)`:
```ts
try {
  console.log(JSON.stringify({
    event: "recompute-version-cert-tier-summary",
    updated: skills.length,
    failed: failures.length,
    ts: new Date().toISOString(),
  }));
} catch { /* defensive */ }
```

### 4. `src/lib/__tests__/architecture/cert-tier-derivation.test.ts` (NEW — Phase 4)

Mirror the structure of `src/lib/skill-update/__tests__/architecture.test.ts`:

```ts
const SRC_ROOT = join(process.cwd(), "src");

const ALLOWED_FILE_SUFFIXES = [
  join("lib", "submission", "types.ts"),
  join("lib", "trust", "trust-updater.ts"),
  join("app", "api", "v1", "admin", "trusted-author-backfill", "route.ts"),
  join("app", "api", "v1", "admin", "recompute-version-cert-tiers", "route.ts"),
  join("app", "api", "v1", "admin", "recompute-skill-cert-tiers", "route.ts"),
];

const TEST_FILE_MARKERS = [`${sep}__tests__${sep}`, ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx"];

const FORBIDDEN_PATTERN = /certTier\s*:\s*['"]VERIFIED['"]|certTier\s*:\s*['"]CERTIFIED['"]/;

describe("architecture: certTier writes go through deriveCertTier (0751 AC-US4-02)", () => {
  it("no non-allowlisted source file hardcodes certTier: 'VERIFIED' or 'CERTIFIED'", () => {
    const files = walk(SRC_ROOT);
    const violations: string[] = [];
    for (const f of files) {
      if (isAllowed(f)) continue;
      const contents = readFileSync(f, "utf-8");
      if (FORBIDDEN_PATTERN.test(contents)) violations.push(relative(SRC_ROOT, f));
    }
    expect(violations, `Files writing hardcoded certTier — must use deriveCertTier(): ${violations.join(", ")}`).toEqual([]);
  });
});
```

## Reuse Inventory

| Function / Constant | Path | Used in phase |
|---|---|---|
| `deriveCertTier` | `src/lib/submission/types.ts:160` | 2 |
| `isVendorOrg` | `src/lib/trust/trusted-orgs.ts:23` | 2 |
| `VENDOR_ORGS` | `src/lib/trust/trusted-orgs.ts:13` | 1 |
| `requireAdmin`, `isAuthError` | `src/lib/auth.ts` | 1 |
| `hasInternalAuth` | `src/lib/internal-auth.ts` | 1 |
| `jsonResponse`, `errorResponse` | `src/lib/api-helpers.ts` | 1 |
| `getDb` | `src/lib/db.ts` | 1 |
| `walk()` + allowlist pattern | `src/lib/skill-update/__tests__/architecture.test.ts` | 4 |

## Risk Assessment

| Risk | Mitigation |
|---|---|
| `updateMany` returns count but not the affected rows | Separate `findMany` for sample; return as `sample[]` in response |
| Architecture test produces false positives (legitimate writes flagged) | Carefully crafted initial allowlist; clear error message names file path |
| Pre-existing tests in `blocklist/[id]/unblock/__tests__` (if any) pin the old `"VERIFIED"` value | Update assertion in same RED→GREEN cycle |
| `recompute-version-cert-tiers` test that uses `console.log` spy must not interfere with vitest's stderr/stdout | Use `vi.spyOn(console, 'log')` per test, restore in `afterEach` |
| BLOCKED-tier writes elsewhere (e.g. `block` routes) match the allowlist scope but aren't `'VERIFIED'`/`'CERTIFIED'` | Regex specifically targets only `'VERIFIED'`/`'CERTIFIED'` literals — `'BLOCKED'` writes are unaffected |

## Verification Plan

1. `npx vitest run` — new tests pass; no NEW failures (baseline: 144 pre-existing per 0744 audit)
2. Phase 5 manual smoke (after deploy): `POST /api/v1/admin/recompute-skill-cert-tiers` returns `updated > 0` first run, `updated = 0` idempotent re-run
3. Independent verification: `GET /api/v1/skills/anton-abyzov/specweave/pm` → `Skill.certTier` should now be `CERTIFIED`
4. Architecture test smoke: temporarily inject a hardcoded `certTier: "VERIFIED"` in a non-allowlisted file → test fails with file path in error message → revert

## Out of Scope

- DB enum rename
- Trusted-author-backfill rewrite (kept intact)
- Other certTier-write paths beyond identified ones
- Hetzner VM env updates
- Active increments 0670, 0746, 0747, 0750 (stay paused)
