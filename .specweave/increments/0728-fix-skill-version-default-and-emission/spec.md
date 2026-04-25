---
increment: 0728-fix-skill-version-default-and-emission
title: Fix skill version default + emission
type: bug
priority: P1
status: completed
created: 2026-04-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# 0728 — Fix Skill Version Default + Emission

## Overview

Newly created skills (especially via save-draft AI flow) land versionless on disk. Fix save-draft + buildSkillMd to default to 1.0.0, update fixtures, and add a stale-dist startup warning so apply-improvement's existing bump logic actually runs in dev.

## Problem

User created a skill at `http://localhost:3162/#/skills/vskill/greet-anton` via the studio's AI generation flow. The resulting `SKILL.md` has no `version:` field in frontmatter. After running an "AI Edit and save" the file STILL has no version. Expectation: every new skill should default to `1.0.0`, and edits should patch-bump (`1.0.1`, `1.0.2`, …).

## Root Causes

All in `repositories/anton-abyzov/vskill`:

1. **`save-draft` route omits version** — `src/eval-server/skill-create-routes.ts:1286` calls `buildSkillMd(body)` with no version resolution, while the sibling `/api/skills/create` route at lines 1166–1174 does default to `"1.0.0"`. Skills generated through the AI-assisted flow land on disk via `save-draft` and are versionless from birth. Zero test coverage for `save-draft`.
2. **`buildSkillMd` emits version conditionally** — lines 242–244 only write `version:` when `data.version?.trim()` is truthy. The accompanying comment ("Keeping it conditional preserves the golden-file fixtures…") is now obsolete; this conditional is the structural reason any caller can produce a versionless skill.
3. **Stale dist served by long-running studio** — `apply-improvement` (improve-routes.ts:357) already calls `setFrontmatterVersion`, which inserts `version:` even when missing (utils/version.ts:87–89). But the user's running studio process loaded `dist/eval-server/improve-routes.js` from before that logic existed. dist mtime 11:51:27 vs edit at 12:13:25 — file still versionless. There is no dist-freshness check at startup.

## User Stories

### US-001: New skills always get a default version on creation
**Project**: vskill

**As a** skill author using the vskill studio
**I want** every new skill (whether scaffolded, AI-generated, or saved as draft) to have `version: "1.0.0"` in its `SKILL.md` frontmatter from the moment it's written
**So that** the studio UI shows a version badge immediately and downstream version-bump logic has a baseline to increment from

**Acceptance Criteria**:
- [x] **AC-US1-01**: `POST /api/skills/save-draft` writes `SKILL.md` with `version: "1.0.0"` when the request body contains no `version` field
- [x] **AC-US1-02**: `POST /api/skills/save-draft` honours an explicit `version` in the request body if a valid semver string is provided
- [x] **AC-US1-03**: Re-saving a draft (overwriting an existing draft.json) preserves the existing on-disk version when present rather than downgrading to `"1.0.0"`

---

### US-002: `buildSkillMd` defends against versionless callers
**Project**: vskill

**As a** maintainer of the eval-server emitter
**I want** `buildSkillMd` to unconditionally emit a `version:` line, defaulting to `"1.0.0"` when `data.version` is missing or blank
**So that** no future caller — test, route, or integration — can accidentally produce a versionless `SKILL.md`

**Acceptance Criteria**:
- [x] **AC-US2-01**: `buildSkillMd({ ...minimal })` (no `version` field, no empty string) returns a string containing `version: "1.0.0"` in the frontmatter block
- [x] **AC-US2-02**: `buildSkillMd({ ...minimal, version: "2.3.4" })` returns frontmatter with `version: "2.3.4"`
- [x] **AC-US2-03**: Existing golden-file fixtures (`skill-emitter-before.md`, `skill-emitter-after.md`) are updated to include `version: "1.0.0"`, with the obsolete inline comment at skill-create-routes.ts:240–241 removed/replaced
- [x] **AC-US2-04**: All existing `skill-emitter-roundtrip` and `skill-emitter-spec-compliance` tests still pass after the fixture update

---

### US-003: Studio warns when running stale compiled code
**Project**: vskill

**As a** developer running the studio locally
**I want** the studio to detect at startup if `dist/` is older than `src/` and print a clearly-visible warning
**So that** I don't burn time debugging behaviour that's already fixed in source but not in the running process

**Acceptance Criteria**:
- [x] **AC-US3-01**: On `eval-server` startup, after binding the port, the server compares the newest mtime in `src/eval-server/` and `src/utils/` against the newest mtime in `dist/eval-server/` and `dist/utils/`
- [x] **AC-US3-02**: When src is newer than dist, the startup banner prints a yellow `Stale dist detected — run \`npm run build\` and restart` warning alongside (not replacing) the normal `Skill Studio: http://localhost:3162` line
- [x] **AC-US3-03**: When dist is current OR when running from a checkout where `dist/` doesn't exist (production install), no warning is printed
- [x] **AC-US3-04**: The check is wrapped in try/catch — any fs error during the check is swallowed silently (warnings are best-effort, never fatal)

## Out of Scope (Follow-ups)

- **Valuable change detection** — `apply-improvement` currently patch-bumps on every save regardless of whether SKILL.md content actually differs. A content-hash diff guard (skip bump when hash unchanged) is a candidate for a future increment.

## Dependencies

- Existing helpers in `repositories/anton-abyzov/vskill/src/utils/version.ts` — `extractFrontmatterVersion`, `bumpPatch`, `setFrontmatterVersion` (no changes needed)
- Existing test helper `buildSkillMdForTest` in `__tests__/helpers/skill-md-test-helpers.ts` (no changes needed)
