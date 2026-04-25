---
increment: 0714-studio-versions-authored-skill-resolver
title: 'Studio Versions: resolve owner/repo for authored skills'
type: bug
priority: P1
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Versions: resolve owner/repo for authored skills

## Overview

The vskill eval-server proxies Skill Studio's Versions tab to the verified-skill platform. Its `resolveSkillApiName` helper translates a bare skill segment (e.g. `appstore`) into the platform's hierarchical name (`owner/repo/skill`) using **only** the lockfile. Authored skills — those that live inside the running vskill repo's `plugins/` tree and were never installed via lockfile — fall through to the bare segment, the platform 404s on `/api/v1/skills/appstore/...`, and the proxy returns an empty envelope.

Result: every authored skill shows "No version history available" in the Versions tab, even when the platform DB has multiple `SkillVersion` rows for the same skill (verified: `anton-abyzov/vskill/appstore` has 2 rows, `obsidian-brain` has 6, etc.).

The same resolver is shared by the `/versions` and `/versions/diff` proxy routes — one helper, two call sites. (Other endpoints like `/update` shell out to the vskill CLI without going through the platform proxy.)

## Background / Evidence

- Resolver: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:1420-1430`.
- Symptom URL: `localhost:3162/?panel=tests#/skills/mobile/appstore` — Versions tab empty.
- Platform DB query (`scripts/list-skills-with-multiple-versions.ts`) returns 5 skills with multi-version history; all are invisible from Studio when authored locally.
- `Skill.name` in platform DB is `anton-abyzov/vskill/appstore`; resolver currently produces `appstore`.

## User Stories

### US-001: Versions tab shows real history for authored skills (P1)
**Project**: vskill

**As a** vskill author working on an authored skill (under plugins/PLUGIN/skills/SKILL/)
**I want** the Skill Studio Versions tab to show the same version history that the platform stores
**So that** I can review past releases, diff between versions, and trust the Studio as a faithful mirror of verified-skill.com.

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `resolveSkillApiName` is called with a skill name that is NOT present in the lockfile (an authored skill), it derives owner/repo from the git remote of the directory containing the skill and returns `${owner}/${repo}/${skill}`.
- [x] **AC-US1-02**: When the resolver succeeds for an authored skill, the proxy `GET /api/skills/:plugin/:skill/versions` calls the platform with the hierarchical path `/api/v1/skills/{owner}/{repo}/{skill}/versions` and forwards the platform response (envelope `{ versions, count, source: "platform" }`) instead of the empty envelope.
- [x] **AC-US1-03**: When git is not available, the directory is not a git repo, or the remote URL cannot be parsed into owner/repo, the resolver falls back to the existing bare-name behavior — no exception, no 5xx, the proxy still returns the safe `{ versions: [], count: 0, source: "none" }` envelope with `X-Skill-VCS: unavailable`.
- [x] **AC-US1-04**: The resolver's git-remote lookup is cached per skill name within a single eval-server process so that the per-request overhead is one map lookup, not a `git` shell-out, after the first call.

### US-002: Diff and Compare endpoints honor the same resolver (P1)
**Project**: vskill

**As a** vskill author
**I want** versions/diff and versions/compare to also resolve authored skills correctly
**So that** I can compare two published versions of an authored skill from the Studio without falling back to platform UI.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GET /api/skills/:plugin/:skill/versions/diff?from=X&to=Y` for an authored skill issues the platform request against `/api/v1/skills/{owner}/{repo}/{skill}/versions/diff?from=X&to=Y` and returns the platform's diff payload.
- [x] **AC-US2-02**: `GET /api/skills/:plugin/:skill/versions/compare?from=X&to=Y` (and any other route currently calling resolveSkillApiName) inherits the same fix without duplicated code — the resolver is the single source of truth.

### US-003: No regression for installed skills or non-skill segments (P1)
**Project**: vskill

**As a** vskill user with skills installed via the lockfile
**I want** version history to keep working as before
**So that** the fix is purely additive.

**Acceptance Criteria**:
- [x] **AC-US3-01**: For a skill present in the lockfile with a parsable source (github, github-plugin, marketplace), the resolver returns the same owner/repo/skill it returned before this increment — git-remote fallback is NOT consulted.
- [x] **AC-US3-02**: For a bare segment that resolves to neither a lockfile entry nor a discoverable authored skill on disk (legacy/unit-test fixture), the resolver returns the bare name unchanged — preserves backwards compatibility.
- [x] **AC-US3-03**: Existing tests for resolveSkillApiName (lockfile cases) and the /versions proxy continue to pass without modification.

## Acceptance Criteria (rolled up)

- [x] AC-US1-01 — authored-skill resolver returns owner/repo/skill
- [x] AC-US1-02 — /versions proxy returns platform envelope for authored skills
- [x] AC-US1-03 — graceful fallback when git/remote unavailable
- [x] AC-US1-04 — per-process cache for resolver lookups
- [x] AC-US2-01 — /versions/diff works for authored skills
- [x] AC-US2-02 — single resolver feeds all callers (no duplicated logic)
- [x] AC-US3-01 — lockfile path unchanged
- [x] AC-US3-02 — unknown skills still return bare name
- [x] AC-US3-03 — existing tests still pass

## Functional Requirements

### FR-001: Git-remote-based owner/repo discovery
Given an authored skill present at `plugins/<plugin>/skills/<skill>/SKILL.md` inside a working tree, the eval-server can determine its hosting owner/repo by parsing the origin remote URL of the enclosing git repository.

Supported remote URL forms:
- `https://github.com/<owner>/<repo>.git`
- `https://github.com/<owner>/<repo>` (no `.git` suffix)
- `git@github.com:<owner>/<repo>.git`
- `ssh://git@github.com/<owner>/<repo>.git`

Unsupported / unparsable URLs MUST fall through silently.

### FR-002: Discovery of skill on disk
Given a bare skill name `appstore` and the running vskill repo's plugins directory, the resolver must locate the skill at `plugins/*/skills/<skill>/SKILL.md`. Multiple matches → first deterministic match (lexicographic by plugin name). Zero matches → fallback to bare name.

### FR-003: Single helper, single behavior
All four current callers (/versions, /versions/diff, /versions/compare, /update) MUST go through the same resolveSkillApiName helper. No call site duplicates the resolution logic.

## Success Criteria

- Skill Studio's Versions tab displays the platform's SkillVersion rows for the local appstore skill (currently 2 versions: 1.0.0 and 1.0.1).
- obsidian-brain (6 versions) renders in full when the user opens it in Studio.
- Zero new 5xx responses on the /api/skills/.../versions* proxy paths under the test matrix.

## Out of Scope

- Creating new SkillVersion rows from authored skills (publish flow).
- Caching beyond the in-process map (no disk/Redis cache).
- Non-GitHub git hosts (GitLab, Bitbucket, self-hosted) — explicit non-goal; can be a follow-up.
- Renaming the lockfile resolver behavior.
- Any changes to the platform-side route handler (vskill-platform/.../versions/route.ts).

## Dependencies

- vskill parseSource helper already handles GitHub URL parsing for lockfile sources — reuse where possible.
- git CLI present on PATH (already a hard requirement of vskill for several other code paths).
- verified-skill.com reachable for end-to-end verification (degrades to local unit/integration tests when unreachable).
