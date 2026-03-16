# Architecture Plan: Rename Authors to Publishers

## Overview

Large-scale terminology rename from "Authors" to "Publishers" across the vskill-platform UI layer, TypeScript types, CSS, and file/directory names. The rename is purely cosmetic at the frontend and data-layer naming level -- no database migration, no API route changes, no KV cache key value changes.

**Project**: `repositories/anton-abyzov/vskill-platform/`

## Architecture Decision: Execution Order

### Why types-first matters

Renaming types and function signatures first turns the TypeScript compiler into a verification tool. Every downstream consumer that still references the old name will produce a compile error, giving us a deterministic checklist of files to update rather than relying on text search alone.

### Execution phases (strict order)

```
Phase 1: Types + Data Layer (compile-error-driven)
  |
Phase 2: Cache/Cron Utilities (internal plumbing)
  |
Phase 3: Component Renames (AuthorLink -> PublisherLink, etc.)
  |
Phase 4: Page Directory Move (authors/ -> publishers/)
  |
Phase 5: Navigation + Layout Text
  |
Phase 6: CSS Class Renames
  |
Phase 7: Skill Pages (publisher/skill-name format)
  |
Phase 8: Next.js Redirects (301 config)
  |
Phase 9: Compile + Test Verification
```

**Rationale**: Phase 1 breaks all downstream imports, making Phases 2-6 mechanically traceable. Phase 4 (directory move) is the highest-risk step since it changes Next.js routing; placing it mid-sequence means types are already stable but CSS/nav can still be adjusted after. Phase 8 (redirects) comes last because it only matters for the production URL layer and has zero compile-time dependencies.

## Component Inventory

### Files to rename (move)

| Current Path | New Path |
|---|---|
| `src/app/authors/` (directory) | `src/app/publishers/` |
| `src/app/authors/page.tsx` | `src/app/publishers/page.tsx` |
| `src/app/authors/AuthorsSearch.tsx` | `src/app/publishers/PublishersSearch.tsx` |
| `src/app/authors/[name]/page.tsx` | `src/app/publishers/[name]/page.tsx` |
| `src/app/authors/[name]/AuthorSkillsList.tsx` | `src/app/publishers/[name]/PublisherSkillsList.tsx` |
| `src/app/authors/[name]/CollapsibleRepos.tsx` | `src/app/publishers/[name]/CollapsibleRepos.tsx` (no rename needed) |
| `src/app/components/AuthorLink.tsx` | `src/app/components/PublisherLink.tsx` |
| `src/lib/cron/authors-cache-refresh.ts` | `src/lib/cron/publishers-cache-refresh.ts` |
| `src/lib/cache/author-cache.ts` | `src/lib/cache/publisher-cache.ts` |

### Files to edit in-place (no move)

| File | What Changes |
|---|---|
| `src/lib/types.ts` | `AuthorSummary` -> `PublisherSummary`, `AuthorFilters` -> `PublisherFilters`, `AuthorRepo` -> `PublisherRepo` |
| `src/lib/data.ts` | `getAuthors` -> `getPublishers`, `getAuthorCount` -> `getPublisherCount`, `getAuthorStats` -> `getPublisherStats`, `getAuthorBlockedSkills` -> `getPublisherBlockedSkills`, `getAuthorRepos` -> `getPublisherRepos` |
| `src/app/layout.tsx` | Nav link text "Authors" -> "Publishers", href `/authors` -> `/publishers` |
| `src/app/components/MobileNav.tsx` | Same nav text + href change |
| `src/app/globals.css` | `.author-card` -> `.publisher-card`, `.authors-grid` -> `.publishers-grid`, `.author-link` -> `.publisher-link` |
| `src/app/skills/page.tsx` | Import `PublisherLink` from new path, publisher/skill-name display |
| `src/app/skills/[name]/page.tsx` | Publisher link href `/publishers/...`, publisher/skill-name format |
| `src/app/skills/[name]/security/page.tsx` | Label "Author" -> "Publisher" |
| `next.config.ts` | Add `redirects()` config for 301s |
| `src/lib/submission-store.ts` | Update import of cache invalidation function |
| `src/app/api/v1/admin/taint-rescan/route.ts` | Update import of cache invalidation function |
| `src/app/api/v1/admin/repo-block/route.ts` | Update import of cache invalidation function |
| `src/app/api/v1/admin/skills/[name]/block/route.ts` | Update import of cache invalidation function |
| `src/app/api/v1/authors/[name]/route.ts` | Update imports of renamed data functions (file stays at this path) |
| `src/app/api/v1/authors/route.ts` | Update imports of renamed data functions (file stays at this path) |
| `src/lib/trust/taint-backfill.ts` | Update references to author data functions |

### Files explicitly NOT changed

| File/Path | Reason |
|---|---|
| `src/app/api/v1/authors/` (API route directory + files) | CLI backwards compatibility -- URL paths stay `/api/v1/authors/*` |
| `prisma/schema.prisma` | DB column `author` unchanged -- avoids migration |
| KV cache key string values (`"authors:detail:"`, `"authors:list:"`, `"authors:skills:"`) | Avoids KV data invalidation across all environments |
| `SkillData.author` field in `types.ts` | Maps directly to Prisma `author` column -- renaming would break DB-to-TS mapping |
| `SkillFilters.author` field in `types.ts` | Used in query parameters that filter by DB column |

## Detailed Phase Design

### Phase 1: Types + Data Layer

**`src/lib/types.ts`** -- rename interfaces only, NOT the `author` field on `SkillData` or `SkillFilters`:

```
AuthorSummary   -> PublisherSummary
AuthorFilters   -> PublisherFilters
AuthorRepo      -> PublisherRepo
```

Section comment `// ---- Author browsing ----` changes to `// ---- Publisher browsing ----`.

**`src/lib/data.ts`** -- rename exported functions:

```
getAuthors             -> getPublishers
getAuthorCount         -> getPublisherCount
getAuthorStats         -> getPublisherStats
getAuthorBlockedSkills -> getPublisherBlockedSkills
getAuthorRepos         -> getPublisherRepos
```

Internal variable names and console.warn tags update correspondingly. Prisma queries like `groupBy({ by: ["author"] })` and `where: { author: ... }` stay unchanged because they reference the DB column.

### Phase 2: Cache/Cron Utilities

**`src/lib/cache/author-cache.ts`** -> rename file to `publisher-cache.ts`. Rename exported symbols:

```
AUTHOR_DETAIL_PREFIX   -> PUBLISHER_DETAIL_PREFIX   (value stays "authors:detail:")
AUTHOR_SKILLS_PREFIX   -> PUBLISHER_SKILLS_PREFIX   (value stays "authors:skills:")
AUTHOR_LIST_PREFIX     -> PUBLISHER_LIST_PREFIX     (value stays "authors:list:")
invalidateAuthorCaches -> invalidatePublisherCaches
resolveKV              -> no change (generic utility)
```

**`src/lib/cron/authors-cache-refresh.ts`** -> rename file to `publishers-cache-refresh.ts`:

```
AUTHORS_CACHE_PREFIX   -> PUBLISHERS_CACHE_PREFIX   (value stays "authors:list:")
refreshAuthorsCache    -> refreshPublishersCache
```

Update all importers:
- `src/lib/submission-store.ts`
- `src/app/api/v1/admin/taint-rescan/route.ts`
- `src/app/api/v1/admin/repo-block/route.ts`
- `src/app/api/v1/admin/skills/[name]/block/route.ts`
- `src/app/api/v1/authors/[name]/route.ts` (uses `AUTHOR_DETAIL_PREFIX`)
- `src/app/authors/[name]/page.tsx` (uses `AUTHOR_DETAIL_PREFIX`)
- Cron worker entrypoint (imports `refreshAuthorsCache`)

### Phase 3: Component Renames

**`src/app/components/AuthorLink.tsx`** -> `PublisherLink.tsx`:
- Interface `AuthorLinkProps` -> `PublisherLinkProps`
- Function `AuthorLink` -> `PublisherLink`
- Keep prop name `author` (matches `SkillData.author` field)
- href changes from `/authors/...` to `/publishers/...`
- CSS class `author-link` -> `publisher-link`
- Add optional `skillName` prop for publisher/skill-name display (used in Phase 7)

**Extended component API**:

```tsx
interface PublisherLinkProps {
  author: string;       // kept as "author" to match SkillData field
  fontSize?: string;
  skillName?: string;   // NEW: when provided, renders "publisher/skill-name"
}

export default function PublisherLink({ author, fontSize = "0.75rem", skillName }: PublisherLinkProps) {
  return (
    <span style={{ fontFamily: "var(--font-geist-mono)", fontSize }}>
      <span
        role="link"
        tabIndex={0}
        onClick={...}
        className="publisher-link"
        style={{ color: "var(--text-faint)", cursor: "pointer" }}
      >
        {author}
      </span>
      {skillName && (
        <>
          <span style={{ color: "var(--text-faint)" }}>/</span>
          <span style={{ color: "var(--text-muted)" }}>{skillName}</span>
        </>
      )}
    </span>
  );
}
```

This keeps the component backwards compatible -- existing callers that omit `skillName` see identical behavior.

### Phase 4: Page Directory Move

Strategy: `git mv` for clean history tracking.

```bash
git mv src/app/authors src/app/publishers
```

Then rename component files within the moved directory:
```bash
git mv src/app/publishers/AuthorsSearch.tsx src/app/publishers/PublishersSearch.tsx
git mv src/app/publishers/[name]/AuthorSkillsList.tsx src/app/publishers/[name]/PublisherSkillsList.tsx
```

Update internal references within moved files:
- Component names in imports
- Function/type imports from `../../lib/data` and `../../lib/types` (paths stay same since depth is identical)
- Any hardcoded `/authors/` URLs in JSX -> `/publishers/`

**Gotcha check**: No files outside `src/app/authors/` import from within it (confirmed by grep). The only cross-references are the reverse: authors pages importing from `../../lib/` and `../../components/`, which remain valid after the move.

### Phase 5: Navigation + Layout Text

**`src/app/layout.tsx`**:
- Desktop nav: `href="/authors"` -> `href="/publishers"`, text `Authors` -> `Publishers`
- Footer: `href="/authors"` -> `href="/publishers"`, text `Authors` -> `Publishers`

**`src/app/components/MobileNav.tsx`**:
- `href="/authors"` -> `href="/publishers"`, text `Authors` -> `Publishers`

### Phase 6: CSS Class Renames

**`src/app/globals.css`**:

```
.authors-grid          -> .publishers-grid
.author-card           -> .publisher-card
.author-card:hover     -> .publisher-card:hover
.author-link           -> .publisher-link
.author-link:hover     -> .publisher-link:hover
```

Media query references (responsive breakpoints) that target `.authors-grid` also update to `.publishers-grid`.

All JSX files referencing these class names must update in the same operation to avoid broken styles.

### Phase 7: Skill Pages (publisher/skill-name format)

**`src/app/skills/page.tsx`**:
- Import `PublisherLink` from `../components/PublisherLink`
- Replace bare `<AuthorLink author={skill.author} />` with `<PublisherLink author={skill.author} skillName={skill.name} />`

**`src/app/skills/[name]/page.tsx`**:
- Byline: change href to `/publishers/...`
- Replace `{skill.author}` display with publisher/skill-name format using `PublisherLink` with `skillName` prop
- Or inline the format: `<a href="/publishers/...">{skill.author}</a>/{skill.name}`

**`src/app/skills/[name]/security/page.tsx`**:
- MetaItem label `"Author"` -> `"Publisher"`

### Phase 8: Next.js Redirects

**`next.config.ts`** -- add `redirects` to the config:

```ts
const nextConfig: NextConfig = {
  output: "standalone",
  serverExternalPackages: ["@prisma/client", ".prisma/client"],
  outputFileTracingRoot: dirname(fileURLToPath(import.meta.url)),
  typescript: { ignoreBuildErrors: true },
  eslint: { ignoreDuringBuilds: true },
  async redirects() {
    return [
      {
        source: "/authors",
        destination: "/publishers",
        permanent: true,
      },
      {
        source: "/authors/:path*",
        destination: "/publishers/:path*",
        permanent: true,
      },
    ];
  },
};
```

Using `:path*` wildcard catches both `/authors/name` and any deeper paths in a single rule.

### Phase 9: Compile + Test Verification

1. `npx tsc --noEmit` -- zero TypeScript errors
2. `npx vitest run` -- all tests pass
3. Smoke test: `/publishers` renders, `/authors` 301-redirects to `/publishers`
4. Smoke test: `/api/v1/authors/*` endpoints respond identically

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Broken imports after directory move | Types-first approach produces compile errors as checklist. Run `tsc --noEmit` after each phase. |
| Missed CSS class references | Grep for `.author-` across all TSX/JSX files before Phase 6 to build complete list. |
| API route breakage | API routes at `/api/v1/authors/` are explicitly NOT moved. Only internal function imports updated. |
| KV cache invalidation | KV string values stay unchanged. Only TS constant names change. No data loss. |
| SEO impact from URL change | 301 permanent redirects preserve SEO equity and pass link juice. |
| Test failures from field references | `SkillData.author` field is NOT renamed (maps to DB column). Most test fixtures need zero changes. |
| Cron job import breakage | Identify and update the cron worker entrypoint that imports `refreshAuthorsCache`. |

## Test Impact Assessment

69 test files reference "author" but most use the `author` field on skill data (e.g., `author: "some-author"` in test fixtures). Since `SkillData.author` is NOT renamed, the vast majority need zero changes.

**Tests that WILL need updates**:
- Tests importing `AuthorSummary`, `AuthorFilters`, `AuthorRepo` types
- Tests importing `getAuthors`, `getAuthorCount`, etc. from data.ts
- Tests importing `invalidateAuthorCaches` from cache module
- Tests importing from `authors-cache-refresh`
- Component tests for `AuthorLink` (if any exist under `src/app/components/__tests__/`)

## Technology Stack

- **Framework**: Next.js 15 App Router (existing)
- **Runtime**: Cloudflare Workers via OpenNext (existing)
- **No new dependencies required**

## Complexity Assessment

Medium-complexity refactor: high file count but mechanically straightforward. No new components, no new data flows, no new APIs. The `publisher/skill-name` display format is the only net-new UI feature -- a minor extension to an existing component via an optional prop.

No domain skills needed. Standard TypeScript compiler + text search is sufficient for verification.
