---
increment: 0806-studio-version-badge-stable-source
title: "Architecture & Implementation Plan"
created: 2026-04-29
---

# Architecture

## Problem

`/api/skills` (server) returns `currentVersion: null` for every row. The client-side `parseRawSkill` (api.ts:320) feeds this into `resolveSkillVersion` with `installedCurrentVersion: null`, so the resolver short-circuit at version-resolver.ts:60-63 fails and the chain falls through to `frontmatterVersion` → `versionSource: "frontmatter"` → **not italic**.

Italic only appears after `mergeUpdatesIntoSkills` (api.ts:1306-1352) runs against the polled `/api/skills/updates` payload, which sets `currentVersion = u.installed` and re-resolves with `preferInstalled: true` → `versionSource: "registry"` → italic.

Because the two fetches are independent and any `refreshSkills()` resets `state.skills` (which strips client-stamped fields but **not** `versionSource` — see StudioContext.tsx:518-530), the badge visibly bounces between non-italic and italic.

## Fix

Stamp `currentVersion` server-side in `/api/skills` from the existing `vskill.lock`. Lockfile lookups are already happening per-row inside `resolveSourceLink` (api-routes.ts:1030); we hoist the read above the loop and reuse it.

### File touched

`repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` — `/api/skills` handler (lines ~1955-2076).

### Change shape

```ts
router.get("/api/skills", async (req, res) => {
  // ... existing setup ...
  const skills: SkillInfo[] = dedupeByDir([...]);

  // NEW: hoist lockfile read once per request (was per-row via resolveSourceLink)
  const lock = readLockfile(root);

  const enriched = await Promise.all(
    skills.map(async (s) => {
      // ... existing per-row enrichment ...
      const meta = buildSkillMetadata(s.dir, s.origin, root);

      // NEW: pin currentVersion from lockfile when available
      const lockEntry = lock?.skills?.[s.skill];
      const currentVersion = lockEntry?.version ?? null;

      return {
        ...s,
        // ... existing fields ...
        version: meta.version,
        currentVersion,           // NEW: was implicit null
        // ... existing fields ...
      };
    }),
  );
  // ... existing post-processing ...
});
```

### Why this works

`parseRawSkill` (api.ts:320) already passes `info.currentVersion` into `installedCurrentVersion`. With it non-null on the first response, `resolveSkillVersion` (version-resolver.ts:60-63) returns `{ versionSource: "registry" }` immediately. No race, no flicker.

The subsequent `mergeUpdatesIntoSkills` either confirms the same value (no-op render) or overwrites with a fresher `u.installed` (rare drift case, same final state as today).

## Non-changes

- `vskill.lock` schema — unchanged
- `/api/skills` request shape — unchanged
- `/api/skills/updates` — unchanged
- Client `parseRawSkill` — unchanged (it already reads `currentVersion`)
- Client `mergeUpdatesIntoSkills` — unchanged
- `VersionBadge` styling — unchanged

## Compatibility

- **Skills with lockfile entry** → italic on first paint (new stable behavior)
- **Skills without lockfile entry** → non-italic (unchanged behavior, source-origin/hand-authored)
- **Lockfile missing entirely** → `lock = null`, `currentVersion = null` everywhere, behavior identical to today

## ADRs

No new ADR. This is a bug fix that aligns existing code with documented intent (increment 0750 source-aware rendering, refined in 0759 Phase 7).

## Test plan

Vitest unit test against the existing `api-routes.ts` handler:

1. **Lockfile-present, leaf matches** → response `currentVersion === lockEntry.version`
2. **Lockfile-present, leaf does NOT match** → response `currentVersion === null`
3. **Lockfile missing entirely** → all rows have `currentVersion === null`
4. **Lockfile entry has no `version` field** → `currentVersion === null`

Manual verification post-deploy:
- Launch `npx vskill@<new> studio` against `specweave-umb`
- Confirm anymodel/greet-anton/obsidian-brain/skill-creator render italic immediately on first paint
- Edit anymodel SKILL.md (triggers `refreshSkills`) — confirm badge stays italic with no transitional non-italic frame
