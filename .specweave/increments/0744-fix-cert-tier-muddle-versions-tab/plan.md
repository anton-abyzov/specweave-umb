# Implementation Plan: Fix CERTIFIED/VERIFIED cert-tier muddle on Versions tab

> Source approved plan: `~/.claude/plans/parsed-fluttering-sphinx.md`

## Architecture Decisions

### AD-001: Reuse `deriveCertTier()` instead of duplicating logic
The submission/publish path already encodes the canonical derivation rules. The scanner path must call the same function — never reimplement, never hardcode. This eliminates the class of bug where two paths drift over time.

### AD-002: Display labels are a UI concern; DB enum is unchanged
Renaming the user-facing badge text (`Trusted Publisher` / `Security-Scanned`) is decoupled from the persisted enum (`CERTIFIED` / `VERIFIED`). A single `formatTierLabel()` helper resolves enum → display string. No migration. No backwards-compat shim needed because no external consumer reads the enum as display text.

### AD-003: Per-version data, not per-publisher data
The Versions tab swap (drop `certTier` chip → show `certMethod` + `certScore`) is justified because `certTier` is a property of the publisher (vendor or not), while `certMethod`/`certScore` change per release based on what scanner ran. This is the only semantically honest fix.

### AD-004: Idempotent backfill via dedicated admin endpoint
Stale rows (vendor author + `VERIFIED`) need correction. Options considered:
- One-shot SQL in deploy notes (no audit trail, no test surface) — rejected.
- Live with it (1.0.6 mismatch stays visible in prod) — rejected.
- Idempotent admin endpoint (`POST /api/v1/admin/recompute-version-cert-tiers`) — chosen. Mirrors existing `trusted-author-backfill` pattern, reusable for future drift, fully tested.

### AD-005: TDD red→green→refactor per project config
`.specweave/config.json` has `testing.tddEnforcement: "strict"`. Every code change is preceded by a failing test. No exceptions.

## Component Design

### 1. `src/lib/skill-update/scanner.ts` — Phase 1 fix site
Replace lines ~183-187 (hardcoded extraData):
```ts
extraData: {
  certTier: "VERIFIED",
  certMethod: "AUTOMATED_SCAN",
  certifiedAt: new Date(),
}
```
with:
```ts
const isVendor = isVendorOrg(skill.author);
const { certTier, certMethod } = deriveCertTier(null, { isVendor });
// scan=null because scanner runs on a fresh git SHA with no scan record yet
extraData: {
  certTier,
  certMethod,
  certifiedAt: new Date(),
}
```
Imports added: `deriveCertTier` from `@/lib/submission/types`, `isVendorOrg` from `@/lib/trust/trusted-orgs`. The `ScannableSkill` interface already exposes `author` — no signature change needed.

### 2. `src/lib/data.ts` (Phase 2A) — `getSkillVersions()` SELECT
Add `certMethod: true` to the Prisma SELECT around lines 656-668. Single field addition, no extra query.

### 3. `src/app/skills/[owner]/[repo]/[skill]/versions/page.tsx` (Phase 2B) — VersionCard refactor
Around lines 178-212:
- Add `certMethod: string` to the VersionCard prop type
- Replace the `certTier`-keyed badge (lines 204-212) with two cells:
  - `certMethod` chip: `formatCertMethodLabel(method)` → "Trusted Publisher" / "LLM-judged scan" / "Automated scan"
  - `certScore` cell: `<span>{score}/100</span>` when non-null; entire span omitted when null
- Drop the page-local `TIER_COLORS`/`TIER_TEXT_COLORS` lookups tied to certTier (lines 25-32) since they're no longer used here

### 4. `src/app/components/TierBadge.tsx` (Phase 3) — Label resolver
- Add export: `export function formatTierLabel(tier: 'VERIFIED' | 'CERTIFIED'): string` returning "Security-Scanned" / "Trusted Publisher"
- Update component's render path: text content uses `formatTierLabel(displayTier)` instead of raw `displayTier`
- Style/icon lookups (`TIER_STYLES`, icon switch at line 84) continue to key off the enum value — unchanged

### 5. Six inline mini-badge sites (Phase 3) — Replace raw enum render
Each site currently renders `{certTier}` or similar. Replace with `formatTierLabel(certTier)`:
- `src/app/components/SearchPalette.tsx` (around line 284)
- `src/app/components/home/TrendingSkills.tsx` (around line 40)
- `src/app/components/homepage/FeatureSecurityVerified.tsx` (around line 46)
- `src/app/trust/VerifiedSkillsTab.tsx` (around line 130)
- `src/app/publishers/[name]/PublisherSkillsList.tsx` (around line 185)
- `src/app/studio/find/[owner]/[repo]/[skill]/page.tsx` (around line 174)

### 6. `src/app/api/v1/admin/recompute-version-cert-tiers/route.ts` (Phase 4 — new file)
Mirrors `trusted-author-backfill/route.ts` structure:
- Auth: `if (!hasInternalAuth(req)) { const auth = await requireAdmin(req); if (isAuthError(auth)) return auth; }`
- Query: `prisma.skillVersion.findMany({ where: { skill: { author: { in: [...VENDOR_ORGS], mode: 'insensitive' } }, certTier: 'VERIFIED' }, include: { skill: { select: { name: true, author: true } } } })`
- Update each row to `{ certTier: 'CERTIFIED', certMethod: 'VENDOR_AUTO' }`
- Return `{ ok: true, updated, skills: [{ name, version, before: {...}, after: {...} }] }`

### 7. Test files
- Update: `src/lib/skill-update/__tests__/scanner.test.ts` — add vendor + non-vendor branches; if line ~225 pins old hardcoded value, update.
- Update: `src/lib/skill-update/__tests__/scanner.integration.test.ts` — confirm written rows now carry derived values for both vendor and non-vendor authors.
- New: `src/app/skills/[owner]/[repo]/[skill]/versions/__tests__/page.test.tsx` — VersionCard render tests for cert method + score cells.
- New: `src/app/components/__tests__/TierBadge.test.tsx` — label resolver tests for both enum values.
- New: `src/app/api/v1/admin/recompute-version-cert-tiers/__tests__/route.test.ts` — backfill endpoint coverage (4 scenarios from AC-US4-04).

## Reuse Inventory

| Function / Constant | Path | Used in phase |
|---|---|---|
| `deriveCertTier` | `src/lib/submission/types.ts:160` | 1 |
| `isVendorOrg` | `src/lib/trust/trusted-orgs.ts:23` | 1, 4 |
| `VENDOR_ORGS` | `src/lib/trust/trusted-orgs.ts:13` | 4 |
| `requireAdmin`, `isAuthError` | `src/lib/auth.ts` | 4 |
| `hasInternalAuth` | `src/lib/internal-auth.ts` | 4 |
| `jsonResponse`, `errorResponse` | `src/lib/api-helpers.ts` | 4 |
| `getDb` | `src/lib/db.ts` | 4 |

## Risk Assessment

| Risk | Mitigation |
|---|---|
| Tests in scanner.test.ts pin old hardcoded value | Update them in same RED→GREEN cycle as the new tests |
| Inline badge sites use varied prop names (some `certTier`, some `tier`) | `formatTierLabel` accepts both as a string union; verify each site individually |
| `getSkillVersions` consumer expects exact shape | Adding a field is backwards compatible; no removal |
| Backfill on large prod table is slow | Filter is selective (vendor authors only — small subset). Single bulk update query. |
| E2E tests assert "VERIFIED"/"CERTIFIED" text | Grep test files for those literals before claiming green; update if found |

## Verification Plan

1. `npx vitest run` from `repositories/anton-abyzov/vskill-platform/` — all tests green
2. `npx playwright test` — E2E suite green (run only if available locally; otherwise relied on by CI)
3. Local dev server (`npm run dev` in vskill-platform) — manual smoke:
   - Navigate to skill page with vendor author → header shows "Trusted Publisher"
   - Navigate to skill page with non-vendor author → header shows "Security-Scanned"
   - Versions tab → no "VERIFIED"/"CERTIFIED" string in per-row chips; method labels visible
4. Hit backfill endpoint with internal auth → expect non-zero `updated` if stale rows exist; subsequent run returns `updated: 0` (idempotent)

## Out of Scope (carried from spec)

- DB enum rename
- Remotion video re-render
- Admin dashboard inline TierBadge rewrite
- Search ranking weight changes
- Vendor-org membership policy
- Active increment 0670 (stays paused)
