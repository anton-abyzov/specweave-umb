---
increment: 0659-skill-versioning-e2e
title: "End-to-End Skill Versioning"
status: planned
architect: sw:architect
created: 2026-04-05
---

# Architecture Plan: End-to-End Skill Versioning

## Overview

Wire the existing SkillVersion Prisma model into the submission pipeline so every publish creates a versioned snapshot, add API endpoints for version queries, and fix the CLI's stale-version bug.

## Architecture Decisions

### AD-1: Store SKILL.md Content in KV During Scan (Not in StoredScanResult)

**Decision**: Add a separate KV key `skillmd:{id}` to persist SKILL.md content during the Tier 1 scan phase, rather than embedding it in the `StoredScanResult` interface.

**Rationale**: `StoredScanResult` is already a large serialized blob (findings, dependency analysis, socket scores). Adding full SKILL.md content (~5-50KB) inflates every scan read/write. A separate key keeps scan results lean and is only read once at publish time. KV reads are cheap; the `skillmd:{id}` key shares the same 7-day TTL as the submission.

**Alternative considered**: Add `skillMdContent` to `StoredScanResult` — rejected because it bloats every consumer that reads scan results and couples content storage to security data.

### AD-2: Auto-Patch Version Bump on contentHash Change

**Decision**: Compare the new submission's `contentHash` (SHA-256 of SKILL.md) against the latest SkillVersion's `contentHash`. If different, bump patch version. If identical, re-certify only (update cert fields on existing version, no new row).

**Rationale**: Patch bumps are the right granularity — SKILL.md changes are typically refinements, not breaking changes. The `contentHash` comparison is already computed in the scan pipeline and stored in both KV and DB. No additional crypto operations needed.

**Version resolution**: `frontmatter version > auto-bump > "1.0.0"`. If SKILL.md contains `version: X.Y.Z` in frontmatter, use that (author intent). Otherwise auto-bump from the latest SkillVersion.

### AD-3: Fix CLI fetchGitHubFlat by Extracting Version from Fetched Content

**Decision**: In `fetchGitHubFlat`, extract the version from the fetched SKILL.md frontmatter using `extractFrontmatterVersion()` (already exists in `src/utils/version.ts`). Fall back to `entry.version` if no frontmatter version found.

**Rationale**: `fetchGitHubFlat` bypasses the registry API (fetches raw from GitHub), so it has no access to the server's `currentVersion`. But the SKILL.md content is already fetched — extracting the frontmatter version is zero-cost and gives a more accurate version than the stale lockfile value. This mirrors how `fetchPlugin` uses `getPluginVersion()` from marketplace.json.

**Alternative considered**: Add an API call to get the server version — rejected because it adds latency and a network round-trip to a function designed for direct GitHub access (offline/rate-limited scenarios).

## Component Design

### C-1: Prisma Schema Migration

**Project**: vskill-platform

Add `content` column to SkillVersion model:

```
SkillVersion (existing)         SkillVersion (after)
──────────────────────────      ──────────────────────────
id          String PK           id          String PK
skillId     String FK → Skill   skillId     String FK → Skill
version     String              version     String
contentHash String              contentHash String
gitSha      String              gitSha      String
certTier    CertificationTier   certTier    CertificationTier
certMethod  CertificationMethod certMethod  CertificationMethod
certScore   Int?                certScore   Int?
certifiedAt DateTime            certifiedAt DateTime
scanResults ScanResult[]        scanResults ScanResult[]
diffSummary String?             diffSummary String?
versionBump String?             versionBump String?
labels      String[]            labels      String[]
createdAt   DateTime            createdAt   DateTime
                                content     String?  ← NEW
```

**File**: `prisma/schema.prisma` line ~347
**Migration**: `npx prisma migrate dev --name add-skill-version-content`

### C-2: Persist SKILL.md Content in Scan Pipeline

**Project**: vskill-platform

Store the raw SKILL.md content in KV during the Tier 1 scan so it's available at publish time.

**File**: `src/lib/queue/process-submission.ts`
**Location**: After line 328 (contentHash computation), before the file boundaries block

```typescript
// After: const contentHash = await computeContentHash(repoFiles.skillMd);
// Add:
const kvForContent = await getKV();
await kvForContent.put(`skillmd:${id}`, repoFiles.skillMd, {
  expirationTtl: 7 * 24 * 3600,
});
```

**Note**: `getKV` is already available via imports. The TTL matches submission TTL (7 days). This is a single KV write of the raw SKILL.md content — no JSON wrapping needed.

### C-3: SkillVersion Creation in publishSkill()

**Project**: vskill-platform

**File**: `src/lib/submission-store.ts`
**Location**: After the `db.skill.upsert()` block (line ~1174), before KV slug mapping (line ~1179)

Logic:
1. Read `skillmd:{id}` from KV to get `skillMdContent`
2. Read `contentHash` and `commitSha` from the stored scan result (already loaded as `scan` at line 1020)
3. Query latest SkillVersion: `db.skillVersion.findFirst({ where: { skillId: skill.id }, orderBy: { createdAt: 'desc' } })`
4. Determine version:
   - Extract frontmatter version from `skillMdContent` if available
   - If latest version exists AND `contentHash` matches latest → skip (re-cert only, update certifiedAt)
   - If latest version exists AND `contentHash` differs → `bumpPatch(latest.version)`, or use frontmatter version if present
   - If no latest version → frontmatter version or `"1.0.0"`
5. Create SkillVersion row with all cert data
6. Update `skill.currentVersion` to the new version
7. Clean up: delete `skillmd:{id}` from KV

**Error handling**: Wrap in try/catch — SkillVersion creation failure must NOT block skill publishing. Log and continue. The `@@unique([skillId, version])` constraint prevents duplicates naturally.

### C-4: Versions API Endpoints

**Project**: vskill-platform

Two new Next.js App Router routes following existing patterns (mirror `[owner]/[repo]/[skill]/route.ts`).

#### C-4a: List Versions

**File**: `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts`

```
GET /api/v1/skills/:owner/:repo/:skill/versions
→ { versions: [...], count: number }
```

- Resolve skill name via `resolveSkillName(params)`
- Look up skill via `getSkillByName(skillName)` → 404 if not found
- Query `db.skillVersion.findMany({ where: { skillId }, orderBy: { createdAt: 'desc' }, take: 50 })`
- Omit `content` field from list response (projection: `select` without content)
- Cache: `Cache-Control: public, max-age=60, s-maxage=300`

#### C-4b: Get Version Detail

**File**: `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/[version]/route.ts`

```
GET /api/v1/skills/:owner/:repo/:skill/versions/:version
→ { version: { ...versionData, content } }
```

- Resolve skill, then query `db.skillVersion.findFirst({ where: { skillId, version } })`
- Include `content` field in detail response
- 404 if version not found
- Cache: `Cache-Control: public, max-age=300, s-maxage=600` (versions are immutable)

### C-5: Fix CLI fetchGitHubFlat Version Resolution

**Project**: vskill

**File**: `src/updater/source-fetcher.ts` lines 100-109

Current (buggy):
```typescript
return {
  content,
  version: entry.version,  // ← stale lockfile value
  sha: computeSha(files),
  tier: entry.tier,
  files,
};
```

Fixed:
```typescript
import { extractFrontmatterVersion } from "../utils/version.js";

// ...inside fetchGitHubFlat:
const frontmatterVersion = extractFrontmatterVersion(content);
return {
  content,
  version: frontmatterVersion || entry.version,
  sha: computeSha(files),
  tier: entry.tier,
  files,
};
```

Import must use `.js` extension per vskill's ESM/nodenext config.

## Data Flow

```
┌──────────────────┐
│  Submit SKILL.md │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  process-submission.ts (Tier 1 Scan)     │
│                                          │
│  1. Fetch repoFiles.skillMd              │
│  2. Compute contentHash (SHA-256)        │
│  3. Resolve commitSha                    │
│  4. Store skillmd:{id} in KV  ← NEW     │
│  5. Run Tier 1 scan                      │
│  6. Store scan result (contentHash,      │
│     commitSha in StoredScanResult)       │
└────────┬─────────────────────────────────┘
         │
         ▼  (on PASS / AUTO_APPROVE)
┌──────────────────────────────────────────┐
│  publishSkill() in submission-store.ts   │
│                                          │
│  1. Read scan result from KV             │
│  2. Upsert Skill row (existing)          │
│  3. Read skillmd:{id} from KV    ← NEW  │
│  4. Compare contentHash vs latest        │
│     SkillVersion                 ← NEW  │
│  5. Create SkillVersion row      ← NEW  │
│  6. Update skill.currentVersion  ← NEW  │
│  7. Delete skillmd:{id} from KV  ← NEW  │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  API: /api/v1/skills/.../versions/       │
│                                          │
│  GET /versions      → list (no content)  │
│  GET /versions/:v   → detail + content   │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  CLI: source-fetcher.ts                  │
│                                          │
│  fetchGitHubFlat() extracts frontmatter  │
│  version from fetched SKILL.md instead   │
│  of using stale lockfile value           │
└──────────────────────────────────────────┘
```

## Backward Compatibility

- **SkillVersion.content is nullable** (`String?`) — existing rows (if any) won't break
- **publishSkill re-cert path**: When contentHash matches, no new version row is created — existing behavior (no version rows) is equivalent to "no versions yet"
- **currentVersion on first publish**: Skills created before this change have `currentVersion: "1.0.0"` — the first version row will be `1.0.0`, matching
- **CLI version resolution**: Falls back to `entry.version` when no frontmatter version found — existing behavior preserved
- **API responses**: Existing skill detail endpoint unchanged. New endpoints are additive.

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SkillVersion creation fails during publish | try/catch — publish succeeds without version row; next submission creates it |
| KV `skillmd:{id}` missing at publish time | publishSkill creates version without content (nullable). Log warning. |
| `@@unique([skillId, version])` conflict | Check for existing version before create; skip if duplicate |
| Large SKILL.md content in DB | `Text` type handles up to 1GB in PostgreSQL. Typical SKILL.md is 5-50KB. |
| Frontmatter version conflicts with auto-bump | Frontmatter takes precedence — author intent wins |

## Testing Strategy

- **Unit tests**: `bumpPatch`, `extractFrontmatterVersion`, version resolution logic
- **Integration tests**: publishSkill creates SkillVersion rows, contentHash comparison, re-cert skip
- **API tests**: Versions endpoints return correct data, 404 on missing, content omitted in list
- **CLI tests**: fetchGitHubFlat returns frontmatter version when present, falls back to entry.version

## Out of Scope

- Major/minor version bump detection (requires diff analysis)
- Version diffing UI
- Version pinning in CLI install
- R2 storage for content (PostgreSQL `Text` is sufficient)
- New CLI `vskill versions` command (can be added later)

## Implementation Order

1. **C-1**: Schema migration (unblocks everything else)
2. **C-2**: Persist SKILL.md in scan pipeline (prerequisite for C-3)
3. **C-3**: SkillVersion creation in publishSkill (core feature)
4. **C-4**: API endpoints (depends on C-3 populating data)
5. **C-5**: CLI fix (independent, can parallelize with C-3/C-4)
