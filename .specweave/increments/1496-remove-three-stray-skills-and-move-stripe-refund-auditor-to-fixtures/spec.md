# Remove three stray skills and move stripe-refund-auditor to fixtures

## Problem

The skills audit for increment 1486 listed four skills in vskill that are not real user skills. The owner decided on November 26, 2026:

- `hi-atlantis` is a joke skill whose description makes it activate on every prompt. It is published on verified-skill.com as a CERTIFIED skill.
- `tiktokpost` is a placeholder ("Describe what this skill does").
- `stub-skill-76f6713e` is output of the 0857 stub provider (`src/eval/llm.ts:730`) that was committed by mistake.
- `stripe-refund-auditor` is sample output of the multi-file skill generator (0815) that sits in the owner's `personal` plugin with broad triggers ("audit refunds") and a "Run this immediately" step.

The first three are removed. The fourth is moved to test fixtures and deprecated with a pointer, the same way `task-skill-announcer` was handled in 1486 (1.0.5).

### Inventory (found November 26, 2026, before any deletion)

| Skill | vskill source (all tracked in Git) | Registry (verified-skill.com) | Installed on m4 |
|---|---|---|---|
| hi-atlantis | `skills/hi-atlantis/SKILL.md` | listed, 1.0.0, `isDeprecated: false`, path `skills/hi-atlantis/SKILL.md` | none |
| tiktokpost | `.claude/skills/marketing/tiktokpost/SKILL.md` (tracked, so not local-only as the audit said) | already delisted: `isDeprecated: true`, path `plugins/marketing/skills/tiktokpost/SKILL.md` (gone), 1.0.21 | none |
| stub-skill-76f6713e | `.claude/skills/stub-skill-76f6713e/SKILL.md` | no row ("Skill not found") | none |
| stripe-refund-auditor | `plugins/personal/skills/stripe-refund-auditor/` (SKILL.md, `.env.example`, `evals/evals.json`, `references/refund-schema.md`, `scripts/audit.py`, `scripts/grader.py`, `tests/integration_test.py`) | listed, versions `["1.0.0"]` | none |

References: none outside each skill's own folder in vskill, vskill-platform, specweave or the umbrella. These hits are records, not references:

- Increments 1486 and 0815, and the 0744 log `trusted-author-backfill-failed-response.json` (names tiktokpost).
- vskill `src/core/__tests__/skill-generator.multiFile.test.ts` uses the string "stripe-refund-auditor" as a mocked generator name.
- vskill-platform `src/lib/generated-plugin-catalog.ts` lists stripe-refund-auditor under `personal` (the skill stays in the plugin, so that is still correct).

Installed copies: no agent skill folder on m4 (`~/.claude`, `~/.agents`, `~/.codex`, `~/.copilot`, `~/.gemini`, `~/.cursor`, opencode, project `.claude/skills`), `~/vskill.lock` or `~/.vskill` holds any of the four. Two folders contain them only as repository checkouts, not installs, and are left alone: `~/.specwithcode/m4/verify/vskill` and `~/.specwithcode/release-scripts.noindex/release-script-vskill`.

## Scope

In: delete the three skills from vskill with a changelog note; stop the stub provider's output from being tracked again; deprecate stripe-refund-auditor and add its fixture with a test; delist hi-atlantis on verified-skill.com; republish stripe-refund-auditor on the platform so its 1.0.1 row carries the deprecation; vskill release.

Out: any vskill-platform code change (none is needed, so no platform release); data migrations; deleting registry rows or user data; other machines.

## Acceptance Criteria

- [ ] AC-01: `hi-atlantis`, `tiktokpost` and `stub-skill-76f6713e` are gone from vskill source and catalogs, with a short note in vskill `CHANGELOG.md`. A grep across vskill, vskill-platform, specweave and the umbrella confirms nothing referenced them before deletion (inventory above). `.gitignore` ignores `.claude/skills/stub-skill-*/` so the stub provider cannot get its output committed again.
- [ ] AC-02: On verified-skill.com each removed skill is delisted through `Skill.isDeprecated`, with no data migration and no deleted rows: hi-atlantis through the existing check-source route (a confirmed 404 on its source sets `isDeprecated` and removes it from search); tiktokpost is already delisted; stub-skill-76f6713e has no row. The detail API shows `isDeprecated: true` for hi-atlantis and search no longer returns it.
- [ ] AC-03: `plugins/personal/skills/stripe-refund-auditor/SKILL.md` goes to `metadata.version` "1.0.1" with `deprecated: "true"`, `deprecated-message`, `replaced-by: "none"` and `deprecated-since: "1.0.1"`, a description that starts "DEPRECATED:" and carries no broad trigger, and an inert body. The `personal` plugin version is bumped in `.claude-plugin/marketplace.json` and `plugin.json`. A copy of the original skill folder goes to `e2e/fixtures/skills/stripe-refund-auditor/`, and a vitest loads that fixture through the Studio frontmatter parser and checks its companion files; another assertion reads the deprecation from the plugin copy with `readDeprecation`. After the vskill merge the platform shows 1.0.1 with `deprecated: true`.
- [ ] AC-04: No vskill-installed copy of the four skills exists on m4 (checked with `vskill list` and `vskill list --global` plus the folder search above), so there is nothing to uninstall; the report lists that result. Nothing is removed with `rm` outside the vskill source tree, and no other machine is touched.

## Approach

**vskill (one PR).**

1. `git rm -r skills/hi-atlantis .claude/skills/marketing/tiktokpost .claude/skills/stub-skill-76f6713e`. Add `.claude/skills/stub-skill-*/` to `.gitignore`.
2. Copy `plugins/personal/skills/stripe-refund-auditor/` unchanged (all seven files, including `.env.example`) to `e2e/fixtures/skills/stripe-refund-auditor/`. The fixture is not shipped in the npm package (`files` lists only `dist`, `scripts/preuninstall.cjs`, `agents.json` and `README.md`).
3. Edit the plugin copy's SKILL.md only, following the task-skill-announcer precedent:
   - Drop the top-level `version: 1.0.0` and put the version in `metadata.version` "1.0.1", so there is one version source (contract from 1093 and 1486).
   - Flatten `metadata.tags` from a list to the string "stripe, finance, audit", because the 1486 contract reads flat string keys under `metadata`.
   - Description: "DEPRECATED: Generator sample output, not a user skill; moved to e2e fixtures. Do not activate on any request; it only answers an explicit /stripe-refund-auditor invocation."
   - Body: a short redirect. It names the fixture path and says nothing removes the skill. Until removed, it only runs on an explicit `/stripe-refund-auditor`. The "Trigger when" list and "Run this immediately" steps go.
   - The companion files in the plugin folder stay as they are, as with task-skill-announcer.
4. Bump the `personal` plugin from 1.0.0 to 1.0.1 in `.claude-plugin/marketplace.json` and `plugins/personal/.claude-plugin/plugin.json`.
5. Add `src/core/__tests__/stripe-refund-auditor.fixture.test.ts`:
   - It loads the fixture SKILL.md with `parseFrontmatter` (from `src/eval-ui/src/utils/parseFrontmatter`) and asserts the name equals the folder.
   - It asserts that every file the fixture's "Files in this skill" section names exists next to it.
   - It asserts that `readDeprecation` on the plugin copy returns the message, `replacedBy` "none" and since "1.0.1".
6. `CHANGELOG.md`: move the stale `[Unreleased]` heading above `[1.2.19]` and add the removal and deprecation lines under it.

**Platform data (no code change).** All of this runs after the vskill merge to main.

- hi-atlantis: call `GET https://verified-skill.com/api/v1/skills/check-source?url=https://github.com/anton-abyzov/vskill/blob/HEAD/skills/hi-atlantis/SKILL.md&skill=anton-abyzov/vskill/hi-atlantis`. These are the exact values the skill page sends. Retry after a few minutes if raw.githubusercontent.com still serves the cached file. Confirm with the detail API (`isDeprecated: true`) and with search.
- stripe-refund-auditor: `POST /api/v1/cron/rescan-stale` with `{"names":["anton-abyzov/vskill/stripe-refund-auditor"]}` and the internal key from Obsidian (never printed), as 1486 did. Confirm `currentVersion` 1.0.1 with `deprecated: true`.

**Release.** `bash scripts/release/release.sh ship vskill`, then `release.sh verify vskill`. The platform is unchanged, so `ship platform` is skipped.

Rejected:

- Deleting registry rows: that deletes user data and the owner said to delist.
- A new admin delist route: that is a platform change, and check-source already delists.
- `rescan-stale` for hi-atlantis: it skips unreadable sources, so it cannot delist.

Risks:

- check-source skips a skill updated within 24 hours. hi-atlantis was last updated September 25, 2026.
- The skill page's own check-source call could restore a skill only when the source exists again, which it will not.

## Decisions

### Asked
- none (the owner settled the decisions on November 26, 2026)
### Defaulted (change any before sw-do)
- D-01 stripe-refund-auditor goes to 1.0.1: the registry holds only 1.0.0, and `(skillId, version)` is unique.
- D-02 The fixture is the original, pre-deprecation skill folder, matching the task-skill-announcer fixture.
- D-03 tiktokpost needs no registry write: its row was already delisted when its old plugin path disappeared.
- D-04 The platform is not released: no platform file changes.
### Open
- none

## Tasks

### T-01 Remove the three skills and ignore stub output
- AC: AC-01 | Files: repositories/anton-abyzov/vskill/skills/hi-atlantis/SKILL.md, repositories/anton-abyzov/vskill/.claude/skills/marketing/tiktokpost/SKILL.md, repositories/anton-abyzov/vskill/.claude/skills/stub-skill-76f6713e/SKILL.md, repositories/anton-abyzov/vskill/.gitignore, repositories/anton-abyzov/vskill/CHANGELOG.md | Test: cd repositories/anton-abyzov/vskill && test ! -e skills/hi-atlantis && test ! -e .claude/skills/marketing/tiktokpost && test ! -e .claude/skills/stub-skill-76f6713e && ! git grep -nE "hi-atlantis|tiktokpost|stub-skill-76f6713e" -- . ':!CHANGELOG.md' && git check-ignore -q .claude/skills/stub-skill-0000abcd/SKILL.md

### T-02 Deprecate stripe-refund-auditor and add its fixture with a test
- AC: AC-03 | Files: repositories/anton-abyzov/vskill/plugins/personal/skills/stripe-refund-auditor/SKILL.md, repositories/anton-abyzov/vskill/e2e/fixtures/skills/stripe-refund-auditor/SKILL.md, repositories/anton-abyzov/vskill/e2e/fixtures/skills/stripe-refund-auditor/.env.example, repositories/anton-abyzov/vskill/e2e/fixtures/skills/stripe-refund-auditor/evals/evals.json, repositories/anton-abyzov/vskill/e2e/fixtures/skills/stripe-refund-auditor/references/refund-schema.md, repositories/anton-abyzov/vskill/e2e/fixtures/skills/stripe-refund-auditor/scripts/audit.py, repositories/anton-abyzov/vskill/e2e/fixtures/skills/stripe-refund-auditor/scripts/grader.py, repositories/anton-abyzov/vskill/e2e/fixtures/skills/stripe-refund-auditor/tests/integration_test.py, repositories/anton-abyzov/vskill/src/core/__tests__/stripe-refund-auditor.fixture.test.ts, repositories/anton-abyzov/vskill/.claude-plugin/marketplace.json, repositories/anton-abyzov/vskill/plugins/personal/.claude-plugin/plugin.json | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/core/__tests__/stripe-refund-auditor.fixture.test.ts && npm run lint:skills-spec

### T-03 Local installs check on m4
- AC: AC-04 | Files: .specweave/increments/1496-remove-three-stray-skills-and-move-stripe-refund-auditor-to-fixtures/reports/local-installs.md | Test: test -s .specweave/increments/1496-remove-three-stray-skills-and-move-stripe-refund-auditor-to-fixtures/reports/local-installs.md

### T-04 Review, merge, delist, republish, release
- AC: AC-01, AC-02, AC-03 | Files: .specweave/increments/1496-remove-three-stray-skills-and-move-stripe-refund-auditor-to-fixtures/reports/release.md | Test: test -s .specweave/increments/1496-remove-three-stray-skills-and-move-stripe-refund-auditor-to-fixtures/reports/release.md
