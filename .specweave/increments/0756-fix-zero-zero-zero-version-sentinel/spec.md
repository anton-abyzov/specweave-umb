---
status: completed
---
# 0756 — Studio: stop showing `0.0.0` — treat it as a sentinel placeholder

## Problem

The Skill Studio sidebar still renders `0.0.0` for plugin-sourced skills (e.g. `codex-cli-runtime`, `codex-result-handling`, `gpt-5-4-prompting`) even though the platform DB has correct `1.0.0` rows for those same skills. Previous increments (0728, 0741, 0750) added a fallback chain and a default of `"1.0.0"` but did **not** fix the actual rendering on these plugin skills — they still show `0.0.0` in the live UI.

## Diagnosis (verified)

1. **DB is clean** — query against Neon production DB shows zero `Skill` rows with `currentVersion = '0.0.0'` and zero `SkillVersion` rows with `version = '0.0.0'`. Codex skills sit at `currentVersion = '1.0.0'`. Total skills: 116,503. (Evidence: `scripts/check-zero-versions.ts` output.)
2. **Studio sends `"0.0.0"` placeholder** to `/api/v1/skills/check-updates` for skills it doesn't yet know the version of (`api.ts:807`, `api.ts:870`).
3. **Platform echoes the placeholder back** as `installed: "0.0.0"`.
4. **`mergeUpdatesIntoSkills` writes that into `merged.currentVersion`** (`api.ts:1178`).
5. **`resolveSkillVersion` accepts `"0.0.0"` as valid semver** (`version-resolver.ts:28`), so it returns `"0.0.0"` via the `registry` priority — beating the real `pluginVersion: "1.0.4"` and the `"1.0.0"` default.
6. UI renders the badge with the literal `0.0.0` text.

The DB has the right answers; the client is overriding them with its own placeholder.

## User Stories

### US-001: Studio never displays `0.0.0` for any skill

- [x] **AC-US1-01**: Given a plugin skill with no frontmatter `version:` and registry `currentVersion = "1.0.0"`, when the studio renders its sidebar row, the badge shows `1.0.0`, not `0.0.0`.
- [x] **AC-US1-02**: Given a plugin skill where the platform's `/check-updates` response echoes `installed: "0.0.0"` (because the studio sent it as a placeholder), when the resolver runs, it ignores the `0.0.0` and falls through to `pluginVersion` or the `"1.0.0"` default.
- [x] **AC-US1-03**: Given the codex plugin skills (`codex-cli-runtime`, `codex-result-handling`, `gpt-5-4-prompting`) loaded into the studio, when the user opens the AVAILABLE list, none of those rows show `v0.0.0`; the Playwright screenshot confirms this.

### US-002: Database state is verifiably free of `0.0.0` rows

- [x] **AC-US2-01**: A diagnostic script (`scripts/check-zero-versions.ts`) queries both `Skill.currentVersion` and `SkillVersion.version` and prints counts of any row equal to `''` or `'0.0.0'`. Both counts MUST be 0.
- [x] **AC-US2-02**: The codex plugin's Skill rows are present in the DB and all sit at `currentVersion = '1.0.0'`.

## Out of scope

- Changing the platform's `/api/v1/skills/check-updates` placeholder contract (server-side change).
- Re-architecting the local plugin scanner.
- Backfilling DB rows (no `0.0.0` rows exist; nothing to backfill).
