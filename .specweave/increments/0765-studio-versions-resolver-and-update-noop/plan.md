# 0765 — Plan

## Files

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill/src/eval-server/skill-name-resolver.ts` | Add `plugin` param; when it starts with `.`, skip source-tree probe and use lockfile-first chain. Cache key changes from `skill` to `${plugin}::${skill}`. |
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` | Pass `params.plugin` through the local `resolveSkillApiName(skill)` wrapper to the impl. Affects `/api/skills/:plugin/:skill/versions` and `/api/skills/:plugin/:skill/versions/diff`. |
| `repositories/anton-abyzov/vskill/src/commands/update.ts` | After `newVersion` is resolved, if it differs from the current frontmatter version of the post-install SKILL.md, rewrite frontmatter via `setFrontmatterVersion`. This handles the SHA-equal-but-version-bumped case. |
| `repositories/anton-abyzov/vskill/src/eval-server/__tests__/skill-name-resolver.plugin-aware.test.ts` | New unit tests for AC-US1-01..04. |
| `repositories/anton-abyzov/vskill/src/commands/__tests__/update.frontmatter-bump.test.ts` | New unit test for AC-US2-01. |

## Implementation outline

### Resolver

```ts
export async function resolveSkillApiName(
  skill: string,
  plugin: string | null,
  root: string,
): Promise<string> {
  const cacheKey = `${plugin ?? ""}::${skill}`;
  const cached = resolverCache.get(cacheKey);
  if (cached !== undefined) return cached;

  const isInstalledAgentDir = !!plugin && plugin.startsWith(".");

  if (!isInstalledAgentDir) {
    // Authoring view → existing 0761 source-tree probe wins
    const sourceDir = await findAuthoredSourceTreeSkillDir(root, skill);
    if (sourceDir) { ... existing logic ... }
  }

  // Lockfile (now consulted FIRST for installed-agent-dir plugins)
  const lock = readLockfile();
  const entry = lock?.skills?.[skill];
  if (entry?.source) { ... existing logic ... }

  // ... remaining fallbacks unchanged
}
```

Cache key includes plugin so the same skill name can resolve differently for installed vs source views.

### Update

After `installSymlink` writes `result.content` to disk, read each agent's SKILL.md and call `setFrontmatterVersion(content, newVersion)` if the file's frontmatter doesn't already declare `newVersion`. This guarantees:
- Content-identical re-publishes still bump the on-disk version.
- The Studio header / Versions tab agree with the lockfile after update.

Use the `setFrontmatterVersion` helper already exported from `src/utils/version.ts`.

## Tests

Unit (vitest):
- AC-US1-01..04: mock lockfile + fs; assert resolver returns lockfile-derived name when plugin starts with `.` even if a source-tree match exists.
- AC-US2-01: mock fs; call into the post-install rewrite step; assert SKILL.md ends up with `version: "<newVersion>"`.

Smoke (sub-agent, fresh `npx -y vskill@0.5.132 studio`):
- `.claude/scout` page still shows installed=1.0.3 + 4 versions (no regression from 0764).
- `.claude/greet-anton` Versions tab shows 1.0.1 + 1.0.2 + 1.0.3 with `installed` badge on 1.0.2.
- Click "Update to 1.0.3" → on-disk frontmatter changes to `version: "1.0.3"`, header refreshes.

## Release

vskill `0.5.132` patch.
