# Architecture Plan: Install Command Skill Discovery & Disambiguation

## Overview

Add a search-first flow to `vskill install` for flat-name inputs (no slashes). When a user types `vskill install skill-creator`, the CLI searches the registry, ranks results, and either auto-installs (single match) or presents an interactive disambiguation prompt (multiple matches). The existing `owner/repo` and `owner/repo/skill` paths are untouched.

## Architecture Decision

**Search-then-delegate over inline install**: The disambiguation layer resolves a flat name to a fully-qualified `owner/repo/skill` path, then re-invokes `addCommand()` with that path. This reuses the entire battle-tested 3-part install pipeline (marketplace detection, blocklist checks, trust tier validation, agent selection) without duplicating any logic.

No ADR required -- this is a localized routing change within a single command module. No new services, protocols, or cross-cutting concerns introduced.

## Component Design

### 1. Shared Display Module: `src/utils/skill-display.ts` (NEW)

**Purpose**: Extract display helpers currently private in `find.ts` so both `find` and `add` can render search results identically.

**Extracted functions**:
- `extractBaseRepo(repoUrl: string | undefined): string | null`
- `formatSkillId(r: SkillSearchResult): string`
- `getSkillUrl(r: SkillSearchResult): string`
- `getTrustBadge(certTier: string | undefined, trustTier: string | undefined): string`

**Ranking function** (new, shared):
- `rankSearchResults(results: SkillSearchResult[], exactQuery?: string): SkillSearchResult[]`
  - Blocked at end
  - Exact `skillSlug` match (case-insensitive) promoted to first among non-blocked
  - Then cert tier: CERTIFIED > VERIFIED > other
  - Then GitHub stars descending
  - Then score descending

**Why a new file**: `find.ts` is a command module (213 lines). These helpers are pure formatting/sorting with no command-level side effects. Extracting them into a utility keeps both `find.ts` and `add.ts` focused on their command flows. The file will be ~80 lines.

**Migration**: `find.ts` re-imports from `skill-display.ts` and deletes its local copies. No behavior change.

### 2. Search-First Resolver in `add.ts`

**Location**: New private function `resolveViaSearch()` in `add.ts`, called from the existing flat-name branch (lines 1919-1924).

**Current flow** (flat name, `parts.length !== 2` and not 3):
```
addCommand("skill-creator", opts)
  -> prints "Tip: Prefer owner/repo format"
  -> calls installFromRegistry("skill-creator", opts)
  -> getSkill("skill-creator") -> 404 -> error + "use vskill find"
```

**New flow**:
```
addCommand("skill-creator", opts)
  -> resolveViaSearch("skill-creator", opts)
    -> searchSkills("skill-creator")
    -> rankSearchResults(results, "skill-creator")
    -> filter installable (non-blocked, has ownerSlug/repoSlug/skillSlug)
    -> BRANCH:
      a) 0 installable: print ranked list (blocked with labels), error, exit 1
      b) 1 installable: auto-install via addCommand("owner/repo/skill", opts)
      c) N installable + TTY: interactive promptChoice -> addCommand(selected, opts)
      d) N installable + non-TTY: print ranked list, exit 1
      e) N installable + --yes: auto-pick first -> addCommand(first, opts)
    -> ON SEARCH ERROR: fall back to installFromRegistry(flatName, opts)
```

**Function signature**:
```typescript
async function resolveViaSearch(
  flatName: string,
  opts: AddOptions,
): Promise<void>
```

**Key design choices**:
- `resolveViaSearch` is private to `add.ts` -- it is install-command routing logic, not reusable
- Re-invokes `addCommand()` with the 3-part path so the full install pipeline handles the rest
- `--yes` already exists on `AddOptions`; no new CLI flags needed
- Results with missing `ownerSlug`/`repoSlug`/`skillSlug` display in the list but are excluded from the selectable set

### 3. Data Flow

```
User: vskill install skill-creator

addCommand("skill-creator", opts)
  |
  +-- parts.length === 3? --> existing 3-part handler (unchanged)
  +-- parts.length === 2? --> existing owner/repo handler (unchanged)
  +-- else (flat name) ---+
                           |
  resolveViaSearch("skill-creator", opts)
    |
    +-- searchSkills("skill-creator") -- API call
    |     |
    |     +-- ERROR --> installFromRegistry() (fallback)
    |     |
    |     +-- OK --> rankSearchResults(results, "skill-creator")
    |           |
    |           +-- 0 installable --> error + exit 1
    |           +-- 1 installable --> addCommand("owner/repo/skill", opts)
    |           +-- N + --yes    --> addCommand("owner/repo/skill", opts)  [first]
    |           +-- N + TTY     --> promptChoice --> addCommand(selected, opts)
    |           +-- N + non-TTY --> print list + exit 1
```

### 4. Circular Re-entry Safety

`resolveViaSearch` calls `addCommand()` with a 3-part path (`owner/repo/skill`). This hits the `parts.length === 3` branch at line 1910 -- it never re-enters the flat-name branch, so no circular recursion is possible.

### 5. File Size Constraint

`add.ts` is 2474 lines (over the 1500-line limit). `resolveViaSearch` adds ~80 lines. This increment does not address the overall file size -- that is a separate refactoring concern. The function is self-contained and positioned near the existing `installFromRegistry` for locality.

## Changes Summary

| File | Action | Est. Lines |
|------|--------|------------|
| `src/utils/skill-display.ts` | CREATE | ~80 |
| `src/commands/find.ts` | MODIFY | replace 4 local helpers with imports from skill-display |
| `src/commands/add.ts` | MODIFY | +~85 (resolveViaSearch + new imports, replace flat-name branch) |
| `src/utils/skill-display.test.ts` | CREATE | ~120 (ranking, display, edge cases) |
| `src/commands/add.test.ts` | MODIFY | +~150 (resolveViaSearch: single/multi/blocked/--yes/non-TTY/fallback) |
| `src/commands/find.test.ts` | MODIFY | ~5 (update imports if tests reference moved helpers) |

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Testing**: Vitest
- **All imports**: Must use `.js` extensions per project convention
- **Existing deps only**: `searchSkills` (api/client), `promptChoice`/`isTTY` (utils/prompts), output helpers

## Testing Strategy

- **Unit** (`skill-display.test.ts`): `rankSearchResults` with exact-match promotion, blocked sorting, cert tier ordering, missing slug handling
- **Unit** (`add.test.ts`): `resolveViaSearch` scenarios mocking `searchSkills`, `isTTY`, `createPrompter`, verifying `addCommand` re-invocation with correct 3-part path
- **Regression**: Existing `add.test.ts` tests for `owner/repo` and `owner/repo/skill` paths remain unchanged
- **TDD mode**: RED -> GREEN -> REFACTOR per increment config

## Technical Challenges

### Challenge: Display consistency between find and install
**Solution**: Single source of truth in `skill-display.ts` -- both commands import the same functions. Any future display change applies everywhere.

### Challenge: Search API failure graceful degradation
**Solution**: Wrap `searchSkills()` in try/catch; on any error, fall back to the existing `installFromRegistry()` path which uses `getSkill()`. Users see the same behavior as before the change.

### Challenge: Non-installable results in selection list
**Solution**: Results missing `ownerSlug`/`repoSlug`/`skillSlug` are displayed (so the user knows they exist) but excluded from the `promptChoice` options and auto-pick logic. If all non-blocked results lack slugs, treat as 0 installable.
