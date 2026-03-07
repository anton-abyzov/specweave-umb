# Architecture Plan: Hierarchical Skill URLs

## Overview

Restructure the verified-skill.com URL scheme from flat slugs (`/skills/dailydotdev-daily`) to hierarchical 3-segment paths (`/skills/{owner}/{repo}/{skillSlug}`). This touches the full stack: Prisma schema, Next.js routing, KV cache keys, publishing pipeline, email templates, and the vskill CLI.

---

## ADR Check

Relevant ADRs reviewed:

- **ADR-0141** (Repo Name as Project ID): Confirms the pattern of using repo names directly as identifiers after normalization. The hierarchical slug follows the same philosophy -- `ownerSlug/repoSlug/skillSlug` uses normalized repo data directly.
- **ADR-0195** (Repositories/{org}/{repo} Folder Structure): Established the `{org}/{repo}` namespace convention. The URL structure aligns: `owner` maps to GitHub org/username, `repo` maps to GitHub repo name.

No conflicting ADRs found. No new ADR needed -- this is a schema and routing change, not a new architectural pattern.

---

## Architecture Decisions

### AD-1: Additive Schema Migration with Phased Rollout

**Decision**: Add columns as nullable first, deploy code, run data migration, then make columns non-nullable in a second migration.

**Rationale**: The platform runs on Cloudflare Workers + Neon Postgres. Prisma `migrate deploy` applies atomically, but making columns non-nullable before data exists would fail. A two-phase approach avoids downtime.

**Schema changes on `Skill` model:**

```
Skill (additions)
-----------------------------------------
ownerSlug       String?   @db.VarChar(100)
repoSlug        String?   @db.VarChar(100)
skillSlug       String?   @db.VarChar(200)
legacySlug      String?   @db.VarChar(500)

@@unique([ownerSlug, repoSlug, skillSlug])
@@index([legacySlug])
@@index([ownerSlug])
```

`Skill.name` format changes from `flat-slug` to `owner/repo/skillSlug`. The `@unique` on `name` remains -- it is still the primary lookup key. The new composite unique constraint `(ownerSlug, repoSlug, skillSlug)` provides an additional integrity guard.

**Phase 1**: Nullable columns + composite unique constraint (allows nulls in unique)
**Phase 2** (post-migration): `ALTER COLUMN ... SET NOT NULL` via a second Prisma migration

### AD-2: Shared Handler Pattern for Dual-Route Coexistence

**Decision**: Extract route handler logic into shared functions in `src/lib/api/`. New hierarchical routes and old `[name]` redirect routes both call the same handler.

**Rationale**: There are 9 API route files under `src/app/api/v1/skills/[name]/` plus 2 admin routes. Duplicating logic across old and new routes would be fragile. Instead:

```
src/lib/api/skill-handlers.ts      -- shared GET/POST logic
src/lib/api/skill-params.ts        -- resolveSkillName({ owner, repo, skill })
src/lib/api/legacy-redirect.ts     -- legacySlug lookup + 301 redirect builder
```

New route files (`[owner]/[repo]/[skill]/route.ts`) call the handler directly. Old route files (`[name]/route.ts`) check for legacy slug, redirect if found, 404 otherwise.

### AD-3: Catch-All Routes for Admin Endpoints

**Decision**: Convert admin skill routes from `[name]` to `[...name]` catch-all segments.

**Rationale**: Admin routes receive skill names with slashes (`acme/tools/linter`). Next.js `[name]` only matches a single segment. Options:

1. **Catch-all `[...name]`** -- simple, parse segments in handler
2. **Nested `[owner]/[repo]/[skill]`** -- type-safe but creates deep directory trees for admin routes

Since admin routes have minimal sub-routes (just `block/` and `delete/`), catch-all is simpler and avoids directory explosion.

```
src/app/api/v1/admin/skills/[...name]/block/route.ts
src/app/api/v1/admin/skills/[...name]/delete/route.ts
```

Handler parses: `const skillName = name.join("/");`

### AD-4: KV Key Strategy -- Dual Write with Alias

**Decision**: New KV key format `skill:{owner/repo/skillSlug}`. Legacy aliases `skill:alias:{legacySlug}` point to the hierarchical name for fast redirect resolution.

**Rationale**: The platform uses KV as a hot cache for published skills. Changing keys in-place would break reads during migration. Dual-write ensures zero-downtime:

```
skill:acme/tools/linter        --> { repoUrl, ... }  (primary)
skill:alias:acme-tools-linter  --> "acme/tools/linter" (redirect)
```

On read:
1. Try `skill:{name}` (covers new format)
2. If not found, try `skill:alias:{name}` to get hierarchical name, then read `skill:{hierarchicalName}`

### AD-5: New `src/lib/skill-url.ts` Module for URL Construction

**Decision**: Create a single module that all components and templates use to build skill URLs.

**Rationale**: Currently, 15+ files construct skill URLs via `encodeURIComponent(skill.name)`. Changing each independently is error-prone. A centralized helper:

```typescript
// src/lib/skill-url.ts
export function skillUrl(name: string): string {
  const parts = name.split("/");
  if (parts.length === 3) {
    return `/skills/${parts.map(encodeURIComponent).join("/")}`;
  }
  return `/skills/${encodeURIComponent(name)}`; // legacy fallback
}

export function skillApiPath(name: string): string {
  const parts = name.split("/");
  if (parts.length === 3) {
    return `/api/v1/skills/${parts.map(encodeURIComponent).join("/")}`;
  }
  return `/api/v1/skills/${encodeURIComponent(name)}`;
}

export function skillBadgeUrl(name: string): string {
  return `https://verified-skill.com${skillApiPath(name)}/badge`;
}
```

### AD-6: CLI Path Detection in API Client

**Decision**: The vskill CLI API client detects 3-segment names and routes to the hierarchical API path. Falls back to single-segment `encodeURIComponent` for old names.

**Rationale**: The CLI must work with both old and new API formats during the transition period. Old CLI versions will hit the old `[name]` route which returns a 301 redirect -- HTTP clients follow redirects by default, so backward compat is automatic.

```typescript
// src/api/client.ts
function skillApiPath(name: string): string {
  const parts = name.split("/");
  if (parts.length === 3) {
    return `/api/v1/skills/${parts.map(encodeURIComponent).join("/")}`;
  }
  return `/api/v1/skills/${encodeURIComponent(name)}`;
}
```

---

## Component Design

### 1. Database Layer

**Files changed:**
- `prisma/schema.prisma` -- add 4 columns, 1 composite unique, 2 indexes
- `prisma/migrations/YYYYMMDD_add_hierarchical_slugs/` -- Phase 1 migration

**Data flow:**
```
publishSkill() --> buildHierarchicalName() --> Skill.create/upsert with ownerSlug, repoSlug, skillSlug, legacySlug
```

### 2. Slug System (`src/lib/slug.ts` + `src/lib/skill-url.ts`)

**Changes to `slug.ts`:**
- `makeSlug()` -- mark as deprecated, keep for legacy compat
- Add `buildHierarchicalName(repoUrl, skillPath)`:

```
buildHierarchicalName("https://github.com/acme/tools", "plugins/linter/skills/eslint-helper/SKILL.md")
--> { ownerSlug: "acme", repoSlug: "tools", skillSlug: "eslint-helper", name: "acme/tools/eslint-helper" }
```

- Add `deriveSkillSlug(skillPath, repoName)`:

```
"plugins/linter/skills/eslint-helper/SKILL.md"  --> "eslint-helper"
"SKILL.md"                                       --> repoName
null                                              --> repoName
```

**New file `src/lib/skill-url.ts`:** (see AD-5 above)

### 3. Data Access Layer (`src/lib/data.ts`)

**Add:**
- `getSkillByLegacySlug(slug: string)` -- `WHERE legacySlug = slug`, returns `SkillData | null`
- `mapDbSkillToSkillData()` -- extend to include `ownerSlug`, `repoSlug`, `skillSlug`, `legacySlug` fields

**Unchanged:**
- `getSkillByName()` -- still queries `WHERE name = X`. The value of `name` changes format, but the function signature and behavior are identical.

### 4. Publishing Pipeline (`src/lib/submission-store.ts`)

**Changes to `resolveSlug()`:**
- Replace the multi-level collision resolution (base --> owner-prefixed --> owner-repo-prefixed --> hash) with a single call to `buildHierarchicalName()`.
- `owner/repo/skillSlug` is inherently unique per repository -- no collision resolution needed.
- Keep function signature but simplify body.

**Changes to `publishSkill()`:**
- Populate `ownerSlug`, `repoSlug`, `skillSlug` on the `Skill` upsert `create` and `update` blocks.
- Set `legacySlug` to the old flat slug on create (null on first publish of new skills since they never had a flat slug).
- KV write: `skill:{owner/repo/skillSlug}` instead of `skill:{flat-slug}`.
- Cross-repo overwrite guard: compare `ownerSlug + repoSlug` instead of hash.

### 5. Page Routes (Next.js App Router)

**New directories:**
```
src/app/skills/[owner]/[repo]/[skill]/
  page.tsx
  RepoHealthBadge.tsx
  security/page.tsx
  security/[provider]/page.tsx
  evals/page.tsx
```

**Page params type:**
```typescript
interface PageProps {
  params: Promise<{ owner: string; repo: string; skill: string }>;
}
```

**Handler pattern:**
```typescript
const { owner, repo, skill } = await params;
const name = `${decodeURIComponent(owner)}/${decodeURIComponent(repo)}/${decodeURIComponent(skill)}`;
const skillData = await getSkillByName(name);
```

**Legacy redirect in `src/app/skills/[name]/page.tsx`:**
```typescript
const { name } = await params;
const decoded = decodeURIComponent(name);
// If it looks like a single segment (no slashes), try legacy lookup
const skill = await getSkillByLegacySlug(decoded);
if (skill) {
  redirect(skillUrl(skill.name), 301);
}
notFound();
```

The old `[name]` directory retains minimal redirect-only handlers for all sub-pages (security, evals, etc.).

### 6. API Routes

**New directories (same shared-handler pattern for all):**
```
src/app/api/v1/skills/[owner]/[repo]/[skill]/
  route.ts
  badge/route.ts
  badge/[provider]/route.ts
  installs/route.ts
  security/route.ts
  security/[provider]/route.ts
  eval/route.ts
  eval/history/route.ts
  repo-health/route.ts
```

**Shared handler (`src/lib/api/skill-handlers.ts`):**
```typescript
export async function handleGetSkill(name: string): Promise<NextResponse> {
  const skill = await getSkillByName(name);
  if (!skill) return NextResponse.json({ error: "Skill not found" }, { status: 404 });
  return NextResponse.json({ skill }, {
    headers: { "Cache-Control": "public, max-age=60, s-maxage=300" },
  });
}
```

**Legacy `[name]/route.ts` becomes redirect:**
```typescript
export async function GET(req, { params }) {
  const { name } = await params;
  const decoded = decodeURIComponent(name);
  const skill = await getSkillByLegacySlug(decoded);
  if (skill) {
    return NextResponse.redirect(new URL(skillApiPath(skill.name), req.url), 301);
  }
  return NextResponse.json({ error: "Skill not found" }, { status: 404 });
}
```

### 7. Admin Routes

**Changed directories:**
```
src/app/api/v1/admin/skills/[...name]/block/route.ts
src/app/api/v1/admin/skills/[...name]/delete/route.ts
```

**Handler update:** `const skillName = (await params).name.join("/");`

The `bulk-delete` route does not use `[name]` and needs no change.

### 8. Component URL Updates

All 15 files that construct skill URLs switch to `skillUrl(skill.name)`:

| File | Current Pattern | New Pattern |
|------|----------------|-------------|
| `skills/page.tsx` | `encodeURIComponent(s.name)` | `skillUrl(s.name)` |
| `TrendingSkills.tsx` | `encodeURIComponent(s.name)` | `skillUrl(s.name)` |
| `PublisherSkillsList.tsx` | `encodeURIComponent(skill.name)` | `skillUrl(skill.name)` |
| `SearchPalette.tsx` | `encodeURIComponent(...)` | `skillUrl(...)` |
| `VerifiedSkillsTab.tsx` | `encodeURIComponent(skill.name)` | `skillUrl(skill.name)` |
| `submit/[id]/page.tsx` | `encodeURIComponent(...)` | `skillUrl(...)` |
| `TaintWarning.tsx` | `encodeURIComponent(...)` | `skillUrl(...)` |
| `skills/[name]/page.tsx` (badge) | `encodeURIComponent(skill.name)` | `skillBadgeUrl(skill.name)` |
| `email.ts` (buildBadgeUrl) | `encodeURIComponent(skillName)` | `skillBadgeUrl(skillName)` |

### 9. Email Templates (`src/lib/email.ts`)

**Changes:**
- `buildBadgeUrl()` uses `skillBadgeUrl()` from `skill-url.ts`
- Email subjects already use `skillName` directly -- now shows `acme/tools/linter` format
- Badge embed markdown in auto-approved email uses hierarchical URL

### 10. vskill CLI

**Files changed:**

| File | Change |
|------|--------|
| `src/api/client.ts` | `getSkill()` and `reportInstall()` use `skillApiPath()` for 3-segment names |
| `src/commands/find.ts` | `getSkillUrl()` builds 3-segment URL; `formatRepoSkill()` simplified (API already returns hierarchical name) |
| `src/commands/add.ts` | `installFromRegistry()` uses new name format for display and lockfile keys |
| `src/utils/validation.ts` | `classifyIdentifier()` already handles 3-segment `owner/repo/skill` -- no change needed |
| `src/lockfile/types.ts` | Lockfile keys switch to hierarchical format; reader handles both for backward compat |

### 11. Data Migration Script

**New file: `src/scripts/migrate-to-hierarchical-slugs.ts`**

Standalone script (not a Prisma migration -- runs after schema migration):

```
1. Query all Skills (batches of 50)
2. For each skill:
   a. owner = extractOwner(skill.repoUrl) ?? skill.author.toLowerCase()
   b. repoName = extractRepoName(skill.repoUrl) ?? "unknown"
   c. skillSlug = deriveSkillSlug(skill.skillPath, repoName)
   d. legacySlug = skill.name (current flat slug)
   e. newName = `${owner}/${repoName}/${skillSlug}`
3. UPDATE Skill SET ownerSlug, repoSlug, skillSlug, legacySlug, name = newName
4. KV operations:
   a. PUT skill:{newName} with skill data
   b. PUT skill:alias:{legacySlug} pointing to newName
   c. DELETE skill:{legacySlug} (old key)
5. UPDATE BlocklistEntry SET skillName = newName WHERE skillName = legacySlug
6. UPDATE ExternalScanResult SET skillName = newName WHERE skillName = legacySlug
7. UPDATE SecurityReport SET skillName = newName WHERE skillName = legacySlug
```

**Dry-run mode**: `--dry-run` flag logs all changes without writing.

---

## Rollout Strategy

```
Phase 1: Schema (additive, non-breaking)
  |-- Prisma migration: add nullable columns
  |-- Deploy: no behavior change

Phase 2: Code deploy (backward-compatible)
  |-- New routes (hierarchical) + shared handlers
  |-- Old routes convert to redirect handlers
  |-- skill-url.ts utility + component updates
  |-- Publishing pipeline produces hierarchical names
  |-- Deploy: new skills get hierarchical URLs, old still work

Phase 3: Data migration
  |-- Run migrate-to-hierarchical-slugs.ts --dry-run
  |-- Review output
  |-- Run migrate-to-hierarchical-slugs.ts
  |-- Verify: spot-check URLs, redirects

Phase 4: CLI release
  |-- Update vskill CLI with 3-segment path support
  |-- npm publish

Phase 5: Cleanup
  |-- Second Prisma migration: SET NOT NULL on new columns
  |-- Remove deprecated makeSlug calls
  |-- Remove old resolveSlug collision logic
```

---

## Risk Analysis

| Risk | Mitigation |
|------|-----------|
| Migration script produces invalid slugs for edge-case repos | Dry-run mode + validation checks in buildHierarchicalName() |
| Old CLI versions break | 301 redirects from legacy routes ensure old clients follow to new URLs |
| Search index stale after migration | Rebuild search shards after data migration |
| KV and DB drift during migration window | Migration script updates both atomically per skill |
| Next.js route conflicts between `[name]` and `[owner]` | `[name]` only matches single segments; `[owner]/[repo]/[skill]` is 3 segments -- no conflict |

---

## File Inventory

**New files (7):**
- `src/lib/skill-url.ts`
- `src/lib/api/skill-handlers.ts`
- `src/lib/api/skill-params.ts`
- `src/lib/api/legacy-redirect.ts`
- `src/scripts/migrate-to-hierarchical-slugs.ts`
- `prisma/migrations/YYYYMMDD_add_hierarchical_slugs/migration.sql`
- `prisma/migrations/YYYYMMDD_enforce_non_null_slugs/migration.sql` (Phase 5)

**New route directories (2):**
- `src/app/skills/[owner]/[repo]/[skill]/` (page routes -- 5 files)
- `src/app/api/v1/skills/[owner]/[repo]/[skill]/` (API routes -- 9 files)

**Modified files (~25):**
- `prisma/schema.prisma`
- `src/lib/slug.ts`
- `src/lib/data.ts`
- `src/lib/submission-store.ts`
- `src/lib/email.ts`
- `src/app/skills/[name]/page.tsx` (becomes redirect)
- `src/app/skills/[name]/security/page.tsx` (becomes redirect)
- `src/app/skills/[name]/security/[provider]/page.tsx` (becomes redirect)
- `src/app/skills/[name]/evals/page.tsx` (becomes redirect)
- `src/app/skills/[name]/RepoHealthBadge.tsx` (moved)
- `src/app/api/v1/skills/[name]/route.ts` (becomes redirect)
- `src/app/api/v1/skills/[name]/badge/route.ts` (becomes redirect)
- All other `[name]` API sub-routes (become redirects)
- `src/app/api/v1/admin/skills/[name]` --> `[...name]` (catch-all)
- `src/app/skills/page.tsx`
- `src/app/components/home/TrendingSkills.tsx`
- `src/app/publishers/[name]/PublisherSkillsList.tsx`
- `src/app/components/SearchPalette.tsx`
- `src/app/trust/VerifiedSkillsTab.tsx`
- `src/app/submit/[id]/page.tsx`
- CLI: `src/api/client.ts`, `src/commands/find.ts`, `src/commands/add.ts`

---

## Domain Skill Recommendation

No additional domain skills needed. This is a platform-internal restructuring within the existing Next.js + Prisma + Cloudflare Workers stack. The vskill CLI changes are minimal TypeScript modifications. The scope is well-defined by the approved plan and does not introduce new frameworks or technologies.
