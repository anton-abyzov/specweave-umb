# Implementation Plan: 0708 follow-up — tracking source resolution + ID format

## Overview

Three coupled changes in `vskill-platform`, all behind feature-flag-free additive code paths:

1. **Resolver precedence chain** — extend `discovery/resolver.ts` to fall back through `SKILL.md → plugin.json → marketplace.json`.
2. **Scanner write-at-discovery** — persist `sourceRepoUrl`/`sourceBranch` directly when minting Skill rows in `scanner.ts:362–389`.
3. **DO filter dual-format support** — at publish time, the event payload carries both UUID (`skillId`) and slug (`skillSlug`); UpdateHub matches against either.

Plus **one ops tool**: idempotent backfill script (`scripts/backfill-source-repo-url.ts`) to retroactively unblock the 91 orphan rows in production Neon.

## Architecture

### Components touched

| Component | File | Change |
|---|---|---|
| Discovery resolver | `src/lib/skill-update/discovery/resolver.ts` | Add `resolveTrackingSource()` helper with 3-step precedence |
| Scanner | `src/lib/skill-update/scanner.ts` | Pass `sourceRepoUrl`/`sourceBranch` to `db.skill.create` |
| Publish endpoint | `src/app/api/v1/internal/skills/publish/route.ts` | Augment payload with `skillSlug` before forwarding to DO |
| UpdateHub DO | `src/lib/skill-update/update-hub.ts` | Filter check matches `skillId` OR `skillSlug` |
| Backfill | `scripts/backfill-source-repo-url.ts` (NEW) | Standalone Node ESM script |
| Tests | `src/lib/skill-update/__tests__/*.test.ts` | TDD coverage per AC |

### Data flow (after fix)

```
Author commit pushed to anton-abyzov/vskill@main
        │
        ▼
Cloudflare cron */10 (scheduled() handler)
        │
        ▼
runSkillUpdateScan()  ──► db.skill.findMany(WHERE sourceRepoUrl IS NOT NULL)
        │                  ▲
        │                  └── populated by:
        │                        (a) write-at-discovery in scanner (FR-002)
        │                        (b) resolver precedence chain (FR-001)
        │                        (c) backfill script (FR-004) — one-shot
        ▼
GitHub API: GET /repos/{owner}/{repo}/commits/{branch}
        │
        ▼
new SHA detected ─► writeSkillVersionWithOutbox(skill, version, sha, ...)
        │                  │
        │                  └─► SkillVersion + UpdateEvent (transactional outbox)
        ▼
outbox-reconciler ─► publishToUpdateHubWithEventId(event, env)
        │              │
        │              └─► env.WORKER_SELF_REFERENCE.fetch (post-665a63c)
        │
        ▼
POST /api/v1/internal/skills/publish
        │
        ├─► augment event with `skillSlug` (FR-005)  [NEW]
        ▼
UpdateHub DO `global` ─► fanout to clients where filter matches UUID or slug (FR-005)
        │
        ▼
SSE: event: skill.updated
```

### Resolver precedence (FR-001) — pseudocode

```ts
// src/lib/skill-update/discovery/resolver.ts
async function resolveTrackingSource(skill: Skill, ctx: ResolveCtx): Promise<{ url: string; branch: string } | null> {
  // 1. SKILL.md frontmatter (existing — wins for 3rd-party stand-alone skills)
  const fm = parseFrontmatter(ctx.skillMd ?? "");
  if (fm.repository && validateGitHubUrl(fm.repository)) {
    return { url: fm.repository, branch: fm.branch ?? "main" };
  }

  // 2. NEW — parent plugin.json
  const pluginJson = await ctx.readPluginJson?.();
  if (pluginJson?.repository && validateGitHubUrl(pluginJson.repository)) {
    // SKILL.md branch wins over plugin.json.tracking.branch (AC-US1-03)
    const branch = fm.branch ?? pluginJson.tracking?.branch ?? "main";
    return { url: pluginJson.repository, branch };
  }

  // 3. NEW — marketplace.json owner inference (last-resort)
  const market = await ctx.readMarketplaceJson?.();
  if (market) {
    const inferred = inferRepoFromMarketplace(market, skill.name);
    if (inferred) return { url: inferred.url, branch: inferred.branch ?? "main" };
  }

  return null;
}
```

The user-locked guard (AC-US1-04) is checked at the **caller** (resolver wrapper or scanner write path), not inside `resolveTrackingSource` — keeps the function pure for testing.

### Scanner write-at-discovery (FR-002) — call site

`scanner.ts:362–389` already invokes `discoverPluginSkills(owner, repo, branch, sourcePath, pluginName, ...)` for each plugin entry in `marketplace.json`. The owner/repo/branch is in scope; today it's discarded. Change: when `discoverPluginSkills` returns a skill that needs `db.skill.create`, pass `sourceRepoUrl: \`https://github.com/\${owner}/\${repo}\``, `sourceBranch: branch` into the create call. No new query, no extra round-trip.

### DO filter dual-format (FR-005)

```ts
// src/app/api/v1/internal/skills/publish/route.ts
const event = parseEvent(raw);
// NEW — derive slug ID for the event so DO can match either format
const skill = await db.skill.findUnique({ where: { id: event.skillId }, select: { name: true }});
const augmented: SkillUpdateEvent = {
  ...event,
  skillSlug: skill ? `sk_published_${skill.name}` : undefined,
};
await stub.fetch(new Request("https://do/publish", { ..., body: JSON.stringify(augmented) }));

// src/lib/skill-update/update-hub.ts:144 (modified)
const matchesFilter = attachment.filter.some(f => f === event.skillId || (event.skillSlug && f === event.skillSlug));
if (!attachment || !matchesFilter) continue;
```

The `SkillUpdateEvent` type gains an optional `skillSlug?: string`. Existing in-flight events without `skillSlug` (e.g. queued before deploy) still match by UUID — backward compatible.

### Backfill script (FR-004) — algorithm

```
1. const orphans = await db.skill.findMany({ where: { sourceRepoUrl: null } })
2. group orphans by name-prefix `{owner}/{repo}`
3. for each `{owner}/{repo}` group:
     - fetch https://raw.githubusercontent.com/{owner}/{repo}/main/.claude-plugin/marketplace.json
     - if 404, log skip-reason and continue
     - parse plugins[]; for each plugin entry, list its skills (walk plugin source dir reference)
     - for each orphan in group whose slug matches a known plugin skill:
         resolved.push({ id, sourceRepoUrl: `https://github.com/${owner}/${repo}`, sourceBranch: 'main' })
4. if --dry-run: print resolved/skipped/failed counts and rows; exit 0
5. else: db.skill.updateMany() in batches of 50; print same summary; exit 0 if all clean, 1 if any failed
```

Idempotency (AC-US2-01): the script's `WHERE sourceRepoUrl IS NULL` filter naturally short-circuits on second run.

### Tests added (TDD-first)

| Test file | New tests | What it asserts |
|---|---|---|
| `src/lib/skill-update/__tests__/resolver.test.ts` | 8 | Each precedence step; user-locked guard; branch specificity |
| `src/lib/skill-update/__tests__/scanner.test.ts` | 4 | `sourceRepoUrl`/`sourceBranch` persisted at insert; user-locked skill not overwritten on rescan |
| `src/lib/skill-update/__tests__/update-hub.test.ts` | 3 | UUID match; slug match; mixed-format filter csv |
| `src/app/api/v1/internal/skills/publish/__tests__/route.test.ts` | 2 | Publish payload augmented with `skillSlug` (or absent if skill not found) |
| `scripts/__tests__/backfill-source-repo-url.test.ts` | 5 | Idempotent; --dry-run no writes; non-zero exit on failure; logs summary; happy path |

Total expected delta: ~22 new tests on top of current 134 → ≥150 (matches SC-003).

## Architecture decisions

### ADR-732-01: No new manifest file (`vskill.lock` rejected)

**Status**: Accepted. **Date**: 2026-04-25.

**Context**: 91 first-party skills are silently un-tracked. Need to expose a tracking source to the platform. Considered: extend `plugin.json`, introduce `vskill.lock`, use `package.json`, per-skill sidecar.

**Decision**: Extend the existing `plugin.json.repository` field. Do not introduce any new file.

**Reasoning**:
- `plugin.json.repository` is already authored across every plugin (Anthropic plugin spec) — zero new author surface.
- `vskill.lock` collides with the consumer-side install lockfile created by 0644/0647 — same name, opposite role. Confusing.
- `package.json` is wrong granularity: vskill has one root `package.json` for the npm package; plugins are sub-units.
- Per-skill `skill.json` sidecar duplicates info already in `SKILL.md` and `plugin.json` — drift risk.
- Forcing `repository:` into every SKILL.md = 91 manual edits + ongoing maintenance burden.

**Consequence**: The discovery resolver gains a fallback chain. The scanner persists what's already in scope. Future-proof: optional `plugin.json.tracking` block can extend without breaking existing plugin authors.

### ADR-732-02: Server-side ID-format normalization (FR-005)

**Status**: Accepted. **Date**: 2026-04-25.

**Context**: UpdateHub DO filter uses DB UUIDs (`Skill.id`). Public discovery API surfaces slug IDs (`sk_published_<owner>/<repo>/<skill>`). Studio clients today silently lose events because the formats don't match.

**Decision**: Augment events at publish time with both `skillId` (UUID) and `skillSlug`; DO filter matches either.

**Alternatives considered**:
- (b) Document slug→UUID translation as Studio client responsibility: cheaper to ship, but pushes complexity onto every consumer; testable but error-prone.
- (c) Standardize all server APIs on UUIDs: large blast radius (discovery API, marketplace, install events).

**Reasoning**: Single source of truth on the server, additive (existing payloads still match), backwards compatible for in-flight events without `skillSlug`. Costs one extra `findUnique` per publish — negligible at current rate.

**Consequence**: `SkillUpdateEvent` type gains optional `skillSlug`. UpdateHub filter check becomes `f === skillId || f === skillSlug`. Doc-comments cite the dual-acceptance contract (AC-US3-02).

## Migration plan (production)

1. Land code changes via TDD cycle.
2. Run `wrangler deploy` for `verified-skill-com`.
3. Run `node scripts/backfill-source-repo-url.ts --dry-run` against prod Neon → eyeball ~90 proposed updates.
4. Run `node scripts/backfill-source-repo-url.ts` for real.
5. Push a trivial commit to `anton-abyzov/vskill@main`, wait one cron tick, observe SSE event delivered to a Studio client subscribing with the slug ID (proves FR-005 works in real conditions).

No schema migration required. No secret rotation. No worker downtime.

## Risks

| Risk | Mitigation |
|---|---|
| `marketplace.json` 404 or schema drift breaks backfill | Per-group try/catch; log skip-reason; never crash. 5/5 backfill tests cover this. |
| DO hibernation across new dual-format filter | Filter array stored via `serializeAttachment` — opaque string list, no schema change needed. Existing AC-US2-04 (0708) DO-hibernation test catches regression. |
| Scanner mints duplicate Skill rows on race with discovery resolver | `db.skill.upsert` semantics already in scanner; `name @unique` constraint is the safety net. |
| Backfill writes conflict with concurrent scanner runs | Both paths use `WHERE sourceRepoUrl IS NULL` → naturally serialized; either wins, the other is a no-op. |

## Out of plan

- Path-scoped scanning (separate increment).
- Mandatory `plugin.json.tracking` block (kept fully optional in v1).
- 0680 Phase-2 manifest API.
