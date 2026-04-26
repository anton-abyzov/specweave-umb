# 0764 — Plan

## Approach

Single-file backend change + tiny data fix. No frontend change required — the existing `VersionHistoryPanel` already drives `installed` / `showAutoLink` from the per-version `isInstalled` flag, so improving the backend enrichment is enough.

## Files

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` | Extend `/api/skills/:plugin/:skill/versions` enrichment: lockfile → frontmatter `version:` → `contentHash` match |
| `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.versions-isinstalled.test.ts` | New unit test (BDD) covering the four AC paths |
| `repositories/anton-abyzov/vskill/.claude/skills/scout/SKILL.md` | Add `version: 1.0.3` to frontmatter (data fix for AC-US3-01) |

## Implementation outline

In `api-routes.ts` versions handler, after fetching upstream `versions` and reading the lockfile:

1. **Lockfile path** (existing, highest precedence): `installedVersion = lock?.skills[params.skill]?.version`.
2. **Frontmatter fallback** (new): if `installedVersion` is still missing, locate the on-disk skill via the existing skill listing (or a new tiny helper that walks `.claude/skills/<skill>`, `.cursor/skills/<skill>`, etc. and reads the SKILL.md frontmatter); if it has a `version:` value that matches one of the upstream versions, use that.
3. **Content-hash fallback** (new): if still missing and the on-disk SKILL.md exists, compute its sha256 and match against `versions[].contentHash`. The platform stores the same hash family.

Helper notes:
- Reuse the existing `listSkills`/discovery code paths if they already produce frontmatter version + path. Otherwise, a minimal helper: walk a small allowlist of agent dirs (`.claude`, `.cursor`, `.windsurf`, `.codex`, `.openclaw`, `.agent`, `.kiro`) under root for `skills/<skill>/SKILL.md`, then `gray-matter` parse + sha256.
- ContentHash format on the platform is plain sha256 hex (see versions API response `contentHash`). Compare lowercased hex.

## Tests

BDD unit test (vitest) for the enrichment helper with mocked lockfile / fs:

- AC-US1-01: frontmatter `version: 1.0.2` → row `1.0.2` gets `isInstalled: true`.
- AC-US1-02: no frontmatter version, on-disk hash matches upstream `1.0.0` → row `1.0.0` gets `isInstalled: true`.
- AC-US1-03: no frontmatter, no hash match → no rows have `isInstalled: true`.
- AC-US1-04: lockfile says `1.0.1`, frontmatter says `1.0.2` → row `1.0.1` wins (lockfile precedence).

Smoke (manual via studio): hit `http://localhost:3170/#/skills/.claude/scout` after data fix and rebuild — verify `1.0.3` row shows `installed` badge and "Update to 1.0.3" button does not appear (because it now correctly matches), AND for any other skill with frontmatter `< latest`, the button DOES appear.

## Release

vskill `0.5.131` patch. Build, test, publish, install via `npx vskill@latest studio`, verify in browser.
