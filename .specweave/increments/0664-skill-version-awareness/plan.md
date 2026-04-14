---
increment: 0664-skill-version-awareness
title: "Skill Version Management - Phase 1: Know What You Have"
status: planned
architect: sw:architect
created: 2026-04-14
---

# Architecture Plan: Skill Version Management - Phase 1

## Overview

Add version awareness across 3 surfaces: a batch check-updates API on vskill-platform, `vskill outdated` command + post-install hints in the CLI, and version badges on the platform skill detail page.

**Key constraint**: Phase 1 is read-only version awareness. No upgrade/pinning/downgrade actions. Surface version staleness so users know when they're behind.

**Builds on**: Increment 0659 (E2E Skill Versioning) which wired SkillVersion creation into `publishSkill()`, added version API endpoints, and fixed CLI version resolution.

## Architecture Decisions

### AD-1: Batch POST for Check-Updates

**Decision**: `POST /api/v1/skills/check-updates` with skill list in request body.

**Rationale**: Installed skills typically number 5-30. Individual GET requests create N round-trips and waste Workers cold starts. POST body avoids URL length limits (~2KB) that constrain `GET ?skills=owner/repo/skill@1.0.0,...` with hierarchical names containing slashes.

**Precedent**: Follows `POST /api/v1/skills/installs` batch pattern in `installs/route.ts` (type-guard validation, per-item error handling, rate limiting).

### AD-2: Server-Side Version Comparison

**Decision**: Platform compares installed versions against `Skill.currentVersion` and returns the diff. CLI does not fetch/compare locally.

**Rationale**: `Skill.currentVersion` is already maintained by `publishSkill()` (0659). A single `WHERE name IN (...)` Prisma query resolves all skills. Moving comparison to CLI would require N calls to the versions API plus client-side semver logic.

### AD-3: Non-Blocking Post-Install Hint

**Decision**: After `vskill install`, print a dim advisory if installed version != latest. Never block, warn, or error.

**Rationale**: Install must always succeed. Staleness is the `outdated` command's concern. The hint plants awareness without friction. Same pattern as npm "X packages are looking for funding."

### AD-4: Platform Page Badges Using Existing Data

**Decision**: Enhance skill detail page at `/skills/[owner]/[repo]/[skill]` with version badge using already-fetched `getSkillVersions()` data. No new API calls.

**Rationale**: The page already fetches versions for the version history section. A "Latest" badge is a rendering-only change.

## Component Design

### C-1: Batch Check-Updates API Endpoint

**Project**: vskill-platform
**File**: `src/app/api/v1/skills/check-updates/route.ts` (new)
**Placement**: Parallel to `src/app/api/v1/skills/installs/route.ts`

**Contract** (aligned with spec AC-US1-01 through AC-US1-04):

```
POST /api/v1/skills/check-updates
Content-Type: application/json

Request:
{
  "skills": [
    { "name": "owner/repo/skill", "version": "1.0.0" },
    { "name": "owner/repo/other", "version": "1.0.2" }
  ]
}

Response 200:
{
  "results": [
    {
      "name": "owner/repo/skill",
      "installed": "1.0.0",
      "latest": "1.0.3",
      "updateAvailable": true
    },
    {
      "name": "owner/repo/other",
      "installed": "1.0.2",
      "latest": null,
      "updateAvailable": false
    }
  ]
}

Response 400 (>100 skills):
{ "error": "Maximum 100 skills per request" }
```

**Implementation pattern** (model: `installs/route.ts`):

1. **Rate limiting**: `applyRateLimit(request, "check-updates", 60, 3600)` — 60 req/hour per IP (higher than installs' 30 since this is read-only)
2. **Validation** (type-guard pattern from installs/route.ts lines 44-57):
   - `body && typeof body === "object"`
   - `Array.isArray(body.skills)`
   - Each item: `typeof item.name === "string" && typeof item.version === "string"`
   - `skills.length > 100` → 400
   - Empty array → 200 with `{ results: [] }` (AC-US1-03)
3. **Query**: Single Prisma call:
   ```typescript
   const skills = await db.skill.findMany({
     where: { name: { in: names } },
     select: { name: true, currentVersion: true }
   });
   ```
4. **Comparison**: Build lookup map from DB results; for each requested skill, check if `currentVersion !== installed`. Skills not found → `{ latest: null, updateAvailable: false }` (AC-US1-02)
5. **Caching**: `Cache-Control: public, max-age=60, s-maxage=300` (matches versions endpoint)

**Auth**: Public — no auth required (same as all `/api/v1/skills/*` endpoints).

### C-2: API Client Extension

**Project**: vskill
**File**: `src/api/client.ts` (modify existing, add after `reportInstallBatch` at ~line 382)

**New function** (modeled on `reportInstallBatch()` pattern — POST, retry, timeout):

```typescript
export interface CheckUpdateResult {
  name: string;
  installed: string;
  latest: string | null;
  updateAvailable: boolean;
}

export async function checkUpdates(
  skills: Array<{ name: string; version: string }>
): Promise<CheckUpdateResult[]> {
  const data = await apiRequest<{ results: CheckUpdateResult[] }>(
    "/api/v1/skills/check-updates",
    {
      method: "POST",
      body: JSON.stringify({ skills }),
    }
  );
  return data.results ?? [];
}
```

**Error handling**: Unlike `reportInstallBatch` which silently swallows errors (telemetry), `checkUpdates` should propagate errors so the `outdated` command can display warnings (AC-US2-04).

### C-3: `vskill outdated` Command

**Project**: vskill
**Files**:
- `src/commands/outdated.ts` (new)
- `src/index.ts` (modify — add command registration)

**Command registration** (pattern from `src/index.ts`, see `update` command at ~line 93):
```typescript
program
  .command("outdated")
  .description("Check for outdated installed skills")
  .option("--json", "Output raw JSON")
  .action(async (opts) => {
    const { outdatedCommand } = await import("./commands/outdated.js");
    await outdatedCommand(opts);
  });
```

**Implementation** (`outdated.ts`):

1. **Read lockfile**: `readLockfile()` to get all installed skills with versions
2. **Resolve names**: For each entry, use `resolveFullName()` pattern from `versions.ts` (lines 15-30) — reads lockfile `source` field, parses via `parseSource()` to construct `owner/repo/skill` format
3. **Call API**: `checkUpdates(skills)` with resolved names
4. **Format output**:
   ```
   Outdated Skills (3 of 12 installed)

   Skill              Installed  Latest
   architect          1.0.0      1.0.3
   skill-creator      1.0.1      1.0.4
   debug              1.0.0      1.0.1

   Run `vskill update` to update all, or `vskill update <name>` for one.
   ```
5. **No outdated skills**: Print `"All skills are up to date."` (AC-US2-03)
6. **API error**: Print warning, exit code 1 (AC-US2-04)
7. **Exit codes**: 0 = all up to date, 1 = updates available or error (CI-friendly)
8. **`--json` flag**: Output raw `CheckUpdateResult[]` array (AC-US2-05)

### C-4: Post-Install Version Hint

**Project**: vskill
**File**: `src/commands/add.ts` (modify, insert after post-install summary at ~line 1982)

**Data source**: During install, the CLI calls `getSkill(skillName)` for registry-sourced skills to fetch content. The `SkillDetail` response includes `version` (the latest published version). Store this during fetch and compare after install.

**Implementation**:
1. During the install flow, capture `registryVersion` from `getSkill()` response when it's called
2. After the summary block (line 1982), for each installed skill where registry data was fetched:
   ```typescript
   if (registryVersion && registryVersion !== installedVersion) {
     console.log(
       dim(`  Hint: v${registryVersion} available (installed v${installedVersion}).`) +
       dim(` Run ${cyan(`vskill update ${name}`)} to update.`)
     );
   }
   ```
3. For batch plugin installs, collect hints and print after the summary block
4. **Non-blocking**: Entire hint block wrapped in `try { ... } catch { /* silent */ }` (AC-US3-03)
5. **No extra API calls**: Only uses data already fetched during install

### C-5: Version Badge on Skill Detail Page

**Project**: vskill-platform
**File**: `src/app/skills/[owner]/[repo]/[skill]/page.tsx` (modify)

The page already fetches `getSkillVersions()` and shows `Skill v{skill.currentVersion}` with a version count link (lines ~209-221).

**Enhancement**:
1. Add a "Latest" badge next to the current version (green pill, consistent with existing badge patterns)
2. If `versions.length > 1` and `versions[0].diffSummary` exists, show a one-line changelog snippet below the version link
3. If the skill has `certTier === "CERTIFIED"`, badge uses yellow color scheme (`--yellow` / `--yellow-muted` from design tokens) (AC-US4-03)

**No new data fetching** — uses `versions` array already loaded by the page component.

## Data Flow

```
┌──────────────────────────────────┐
│  vskill outdated                 │
│                                  │
│  1. readLockfile()               │
│  2. resolveFullName() per entry  │
│  3. Build {name, version}[]      │
└────────────┬─────────────────────┘
             │
             ▼  POST /api/v1/skills/check-updates
┌──────────────────────────────────┐
│  vskill-platform API (Workers)   │
│                                  │
│  1. applyRateLimit()             │
│  2. Validate body (type guards)  │
│  3. db.skill.findMany({          │
│       where: { name: { in } }    │
│     })                           │
│  4. Compare currentVersion vs    │
│     each installed version       │
│  5. Return results[]             │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│  CLI Output                      │
│                                  │
│  Table: skill | installed |      │
│         latest                   │
│  Exit code: 0 (up to date)      │
│             1 (updates exist)    │
└──────────────────────────────────┘


┌──────────────────────────────────┐
│  vskill install <skill>          │
│                                  │
│  ... normal install flow ...     │
│  getSkill() → registryVersion    │
│                                  │
│  Post-install:                   │
│  if (registryVersion > installed)│
│    print dim hint                │
└──────────────────────────────────┘
```

## Implementation Order

```
C-1: Platform API endpoint  ──────────┐
  (unblocks C-2)                      │
                                      ▼
C-2: API client checkUpdates() ───────┐
  (unblocks C-3)                      │
                                      ▼
C-3: vskill outdated command          │  ← core deliverable
                                      │
C-4: Post-install hint  ──────────────┤  ← parallel (different file, no deps on C-2/C-3)
                                      │
C-5: Platform page badge  ────────────┘  ← parallel (different repo, no deps on C-2/C-3)
```

**Parallelizable**: C-4 + C-5 can run alongside C-2/C-3 since they touch different files/repos.

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Batch API with 100 skills is slow | Single `WHERE IN` query on indexed `name` column. 100 skills = trivial for Prisma. |
| Skills in lockfile have short names, API needs full names | Reuse `resolveFullName()` from `versions.ts:15-30`, which reads lockfile `source` field to reconstruct `owner/repo/skill`. |
| Installed skills not in platform registry (local/private) | API returns `{ latest: null, updateAvailable: false }` for unknowns. CLI skips with dim note. |
| Post-install hint fires when version data unavailable | Only fires when `getSkill()` was called during install (registry path). Wrapped in try/catch. |
| Semver comparison edge cases | Use string `!==` comparison for Phase 1 (sufficient for patch-only auto-bumps). Complex semver deferred to Phase 2. |
| Rate limiting too aggressive for CI | 60 req/hour for check-updates (double the installs rate) covers typical CI cadence. |

## Testing Strategy

- **C-1 tests**: Batch endpoint with valid/invalid/missing/empty skills, >100 limit, rate limiting
- **C-2 tests**: `checkUpdates()` function with mocked `apiRequest()`, error propagation
- **C-3 tests**: `outdatedCommand()` with mocked lockfile + API, table formatting, JSON output, exit codes, name resolution
- **C-4 tests**: Post-install hint presence/absence based on version comparison, silent failure on error
- **C-5 tests**: Badge rendering with single/multiple versions, certified color scheme
- **E2E**: Not required — all changes are read-only with no state mutations

## Backward Compatibility

All changes are **additive**:
- New API endpoint: no changes to existing endpoints
- New CLI command: no changes to existing commands
- Post-install hint: appends dim text after existing output
- Version badge: cosmetic enhancement to existing page

## Out of Scope

- `vskill update` enhancements (already exists, works)
- Version pinning (`vskill add skill@1.0.3`)
- Auto-update on install
- Studio eval-ui badges (eval-ui is the local dev testing tool; US-004 targets the platform web UI)
- Version notifications/webhooks
- Major/minor version awareness (Phase 1 is patch-only)
- Breaking change detection between versions
