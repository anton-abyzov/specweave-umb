# Architecture Plan: Fix Skill Naming with Plugin as Separate Metadata

## Overview

Extract plugin folder name as a `pluginName` metadata field, derive skill names from the leaf folder, and surface plugin context via teal badges in the UI and CLI. No schema changes required -- the `pluginName` column already exists in the Skill table.

## Architecture Decision

**Approach: Pure function in slug.ts + wiring at publish/backfill + display-only UI changes**

This is a metadata-derivation change that touches 5 files across 2 repos. No new services, no new database columns, no new API endpoints. The function is pure (input path string, output string or null), making it trivially testable and safe to wire into the existing publish and backfill flows.

### Why not alternatives

- **Separate utility module**: `derivePluginName()` operates on the same path format as `deriveSkillSlug()` and shares the same normalization concerns. Co-locating in `slug.ts` keeps related path-parsing logic together and avoids import sprawl.
- **Derive at read-time instead of write-time**: Computing `pluginName` on every read (in `data.ts` or search) would require the `skillPath` to always be present and waste cycles. Write-time derivation stores the result once and makes it available to all consumers (search index, API responses, CLI) without re-derivation.

## Component Design

### 1. `derivePluginName()` -- Pure Function (slug.ts)

**File**: `repositories/anton-abyzov/vskill-platform/src/lib/slug.ts`

```
Input:  skillPath: string | null | undefined
Output: string | null
```

**Algorithm**:
1. If `skillPath` is null/undefined, return `null`
2. Normalize backslashes to forward slashes
3. Find the `plugins/` segment in the path
4. If found, return the immediate child folder name (the segment after `plugins/`)
5. If no `plugins/` segment, return `null`

**Examples**:

| Input | Output |
|-------|--------|
| `plugins/specweave-release/skills/release-expert/SKILL.md` | `specweave-release` |
| `plugins/sw/skills/pm/SKILL.md` | `sw` |
| `skills/architect/SKILL.md` | `null` |
| `SKILL.md` | `null` |
| `null` | `null` |

**Key constraint**: The function does NOT prettify the folder name. It returns the raw folder name as-is (e.g., `specweave-release`, not `Specweave Release`).

### 2. Publish-Time Wiring (submission-store.ts)

**File**: `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts`

**Change**: In `publishSkill()`, call `derivePluginName(sub.skillPath)` and pass the result to both the `create` and `update` branches of the `db.skill.upsert()` call.

Current code sets `pluginName: null` in `create` and does not touch it in `update`. The fix:

```typescript
const pluginNameVal = derivePluginName(sub.skillPath);

// In upsert create:
pluginName: pluginNameVal,

// In upsert update:
pluginName: pluginNameVal,
```

**Import**: Add `derivePluginName` to the existing import from `./slug`.

### 3. Backfill Extension (backfill-slugs/route.ts)

**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-slugs/route.ts`

**Changes**:

a. **Import** `derivePluginName` from `@/lib/slug`

b. **Extend the `Change` interface** with a `pluginName` field:
```typescript
interface Change {
  // ...existing fields...
  pluginName: string | null;
}
```

c. **Compute `pluginName`** alongside existing slug derivation in the skills loop:
```typescript
const pluginNameVal = derivePluginName(skill.skillPath);
```

d. **Include in `db.skill.update()` data**:
```typescript
data: {
  // ...existing fields...
  pluginName: change.pluginName,
}
```

e. **Add `pluginName` to the select clause** of the initial `findMany` so it is available for dry-run reporting.

f. **Flat-name enforcement**: The existing logic already converts flat names to hierarchical `owner/repo/skillSlug` format. No changes needed for AC-US3-04 -- this is already implemented.

g. **Dry-run reporting**: The `pluginName` field is included in the `changes` array, so dry-run output shows planned values.

### 4. UI: Teal Plugin Badge (3 Components)

**Badge spec**: Teal pill, non-clickable, font monospace, color `#0D9488`, background `rgba(13, 148, 136, 0.1)`, border `rgba(13, 148, 136, 0.3)`. Only shown when `pluginName` is truthy.

#### 4a. SearchPalette.tsx

**File**: `repositories/anton-abyzov/vskill-platform/src/app/components/SearchPalette.tsx`

The `pluginName` field is already in the `SearchResult` interface and already mapped into `allItems`. Add a teal pill badge after the publisher badge in the flex row containing `item.label`:

```tsx
{item.pluginName && (
  <span style={{
    fontSize: "0.5625rem",
    padding: "0.05rem 0.3rem",
    borderRadius: "3px",
    color: "#0D9488",
    backgroundColor: "rgba(13, 148, 136, 0.1)",
    border: "1px solid rgba(13, 148, 136, 0.3)",
    whiteSpace: "nowrap",
    flexShrink: 0,
  }}>
    {item.pluginName}
  </span>
)}
```

**Location**: After the publisher badge (line 486), before the closing `</div>` of the name row.

#### 4b. Skills List Page (page.tsx)

**File**: `repositories/anton-abyzov/vskill-platform/src/app/skills/page.tsx`

The `pluginName` field is already returned by `getSkills()` via `data.ts` (line 69). Add the badge in the skill card header row, alongside the extensible badge:

```tsx
{skill.pluginName && (
  <span style={{
    fontFamily: MONO, fontSize: "0.625rem", fontWeight: 600,
    textTransform: "uppercase",
    padding: "0.1rem 0.35rem", borderRadius: "4px",
    color: "#0D9488",
    backgroundColor: "rgba(13, 148, 136, 0.1)",
    border: "1px solid rgba(13, 148, 136, 0.3)",
  }}>
    {skill.pluginName}
  </span>
)}
```

**Location**: After the `PublisherLink` component (line 265), inside the `alignItems: "baseline"` flex div.

#### 4c. Skill Detail Page (page.tsx)

**File**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/page.tsx`

Add the badge in the byline metadata row, after the repo link and before the `skillPath` link:

```tsx
{skill.pluginName && (
  <>
    <span style={bylineSep}>.</span>
    <span style={{
      fontFamily: MONO, fontSize: "0.6875rem", fontWeight: 600,
      textTransform: "uppercase",
      padding: "0.1rem 0.35rem", borderRadius: "4px",
      color: "#0D9488",
      backgroundColor: "rgba(13, 148, 136, 0.1)",
      border: "1px solid rgba(13, 148, 136, 0.3)",
    }}>
      {skill.pluginName}
    </span>
  </>
)}
```

**Location**: After the `RepoHealthBadge` block (after line 201), before the `skillPath` block (before line 204).

### 5. CLI: Plugin Suffix in `vskill find` (find.ts)

**File**: `repositories/anton-abyzov/vskill/src/commands/find.ts`

#### 5a. SkillSearchResult Type

The `pluginName` field already exists in `SkillSearchResult` (client.ts line 28). No type changes needed.

#### 5b. TTY Mode

In the TTY display loop (lines 120-136), append plugin suffix after stars/trust badge:

```typescript
const pluginSuffix = r.pluginName ? `  ${dim(`[${r.pluginName}]`)}` : "";
console.log(`${bold(label)}  ${dim(starsStr)}${badge ? "  " + badge : ""}${pluginSuffix}`);
```

#### 5c. Non-TTY (Piped) Mode

In non-TTY output (lines 169-176), add `pluginName` as an additional tab-separated field:

```typescript
const pluginField = r.pluginName ? `\t${r.pluginName}` : "";
console.log(`${name}\t${repo}\t${r.githubStars ?? 0}\t${r.trustTier ?? ""}${pluginField}`);
```

## Data Flow

```
Skill Path (from repo scan)
        |
        v
derivePluginName(skillPath)  <-- pure function in slug.ts
        |
        v
   pluginName: string | null
        |
   +----+----+
   |         |
   v         v
publishSkill()   backfill-slugs POST
(write-time)     (batch fix)
   |         |
   v         v
  Skill DB record (pluginName column)
        |
   +----+----+----+----+
   |    |    |    |    |
   v    v    v    v    v
 Search  Skills  Detail  CLI
 Palette  List   Page   find
```

## File Change Summary

| File | Change | Lines (est.) |
|------|--------|-------------|
| `vskill-platform/src/lib/slug.ts` | Add `derivePluginName()` export | ~15 |
| `vskill-platform/src/lib/__tests__/slug.test.ts` | Tests for `derivePluginName()` | ~30 |
| `vskill-platform/src/lib/submission-store.ts` | Wire `derivePluginName` in `publishSkill()` | ~5 |
| `vskill-platform/src/app/api/v1/admin/backfill-slugs/route.ts` | Add pluginName to backfill + change interface | ~15 |
| `vskill-platform/src/app/components/SearchPalette.tsx` | Teal pill badge for pluginName | ~12 |
| `vskill-platform/src/app/skills/page.tsx` | Teal pill badge in skills list | ~12 |
| `vskill-platform/src/app/skills/[owner]/[repo]/[skill]/page.tsx` | Teal pill badge in byline | ~15 |
| `vskill/src/commands/find.ts` | Plugin suffix in TTY + piped output | ~5 |

**Total estimated: ~110 lines of new/changed code**

## Testing Strategy

- **Unit tests** for `derivePluginName()`: Cover all path formats from spec (plugin path, non-plugin path, root SKILL.md, null/undefined). TDD red-green-refactor.
- **Existing tests**: `publishSkill()` tests in `submission-store.test.ts` should be updated to verify `pluginName` is set correctly.
- **Backfill**: Dry-run mode test (no DB mutation) + verify `pluginName` appears in change output.
- **UI components**: Verify badge renders when `pluginName` is set, absent when null. Extend existing SearchPalette test.
- **CLI**: Test TTY and non-TTY output formatting with/without `pluginName`.

## Risk Assessment

**Low risk**. This change:
- Adds a pure function with no side effects
- Uses an existing DB column (no migration)
- Is additive to existing publish/backfill flows (no removal of existing logic)
- UI changes are display-only badges with no interactivity

**Only risk**: Backfill must handle the flat-name-to-hierarchical conversion correctly, but this logic already exists and is tested. The new pluginName derivation is orthogonal.

## Delegation

No domain skills needed. This is a straightforward backend utility + UI display change within the existing vskill-platform (Next.js) and vskill (Node.js CLI) codebases. The changes are small enough that a single implementation pass covers both repos.
