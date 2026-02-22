# Implementation Plan: Fix skill naming -- strip org/repo prefix from slugs

## Overview

Fix the `makeSlug()` function to produce clean skill slugs (base name only) instead of org-prefixed slugs. Add collision detection, migrate existing KV records, and maintain backward compatibility for old URLs.

## Architecture

### Components Affected

1. **`submission-store.ts`** (`src/lib/submission-store.ts`): Core slug generation and publishing logic
   - `makeSlug()` -- fix to return clean base name
   - `publishSkill()` -- add collision detection before writing KV
   - `getPublishedSkill()` -- add fallback lookup for old-format slugs

2. **`data.ts`** (`src/lib/data.ts`): Skill data layer that renders published skills in the registry
   - Uses `pub.slug` as `name` field -- will automatically benefit from cleaner slugs

3. **Admin migration endpoint** (new): `src/app/api/v1/admin/migrate-slugs/route.ts`
   - One-shot migration of existing KV records

### Data Flow

```
Discovery/Submission → skillName (clean, e.g. "sw-frontend")
     ↓
publishSkill() → makeSlug(repoUrl, skillName) → NOW returns "sw-frontend" (was "anton-abyzov-specweave-sw-frontend")
     ↓
KV write: skill:sw-frontend → { slug: "sw-frontend", ... }
     ↓
Published index: [{ slug: "sw-frontend", ... }]
     ↓
data.ts getSkills() → SkillData { name: "sw-frontend", ... }
     ↓
Frontend: /skills/sw-frontend
```

### Collision Detection Strategy

When publishing, before writing the KV key:

1. Compute `baseSlug` from `skillName` only
2. Check if `skill:{baseSlug}` exists in KV
3. If exists AND belongs to a different `repoUrl`:
   - Try `{owner}-{baseSlug}` (e.g. `anthropics-sw-frontend`)
   - If that also collides with a different repo, use `{owner}-{repo}-{baseSlug}` (original behavior)
4. If exists AND belongs to the same `repoUrl`: overwrite (same skill being re-published)

## Technology Stack

- **Language**: TypeScript (ESM, Node.js)
- **Runtime**: Cloudflare Workers (via OpenNext)
- **Storage**: Cloudflare KV (SUBMISSIONS_KV)
- **Testing**: Vitest with `vi.mock()`/`vi.hoisted()`

**Architecture Decisions**:
- **Collision fallback to owner-prefix (not UUID)**: Keeps slugs human-readable. Full org-repo-name is the worst-case fallback that matches current behavior, so no data loss risk.
- **Migration via admin API (not automatic)**: Gives operator control over when migration runs. Idempotent so safe to re-run.
- **Backward compat via fallback lookup**: `getPublishedSkill()` tries old slug format as fallback. Zero-cost for new slugs (single KV read), small overhead for legacy (two KV reads).

## Implementation Phases

### Phase 1: Fix slug generation
- Update `makeSlug()` to return base name only
- Add `makeSlugWithCollision()` that checks KV for existing keys
- Update `publishSkill()` to use collision-aware slug generation

### Phase 2: Backward compatibility
- Update `getPublishedSkill()` to try old slug format as fallback
- No frontend changes needed (slug is used as URL param, resolves via `getSkillByName` -> `getPublishedSkill`)

### Phase 3: Migration
- Create admin endpoint to migrate existing records
- Read index, recompute slugs, copy records, delete old keys, rewrite index

## Testing Strategy

- Unit tests for `makeSlug()` with various inputs
- Unit tests for collision detection
- Unit tests for migration logic (mock KV)
- Integration: verify `publishSkill()` + `getPublishedSkill()` round-trip with clean slugs
- Backward compat test: old slug still resolves

## Technical Challenges

### Challenge 1: KV Eventual Consistency During Migration
**Solution**: Migration reads entire index first, then processes sequentially. Since this is an admin-triggered one-shot operation (not real-time), eventual consistency is acceptable.
**Risk**: Low. Migration is idempotent.

### Challenge 2: Collision Detection Requires KV Read Before Write
**Solution**: Add an async `makeSlugWithCollision()` that does a KV `get()` before deciding on the final slug. This adds one extra KV read per publish, which is negligible.
**Risk**: Low. KV reads are fast and free within Workers.
