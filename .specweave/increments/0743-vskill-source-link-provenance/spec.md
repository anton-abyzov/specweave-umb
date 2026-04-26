---
increment: 0743-vskill-source-link-provenance
title: "vskill source-link provenance: persist sourceSkillPath, drop wrong fallbacks"
type: bug
priority: P2
status: planned
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill source-link provenance: persist sourceSkillPath, drop wrong fallbacks

## Overview

The studio detail header at `http://localhost:3136/#/skills/{workspace}/{skill}` shows a clickable `SKILL.md ↗` anchor for installed skills. For any skill installed from a multi-skill repo (e.g. `anton-abyzov/vskill`), the anchor 404s — it points at `https://github.com/{owner}/{repo}/blob/HEAD/SKILL.md`, but the actual file lives at `plugins/.../skills/<name>/SKILL.md`.

Real reproduction: `TestLab/greet-anton/vskill.lock` carries `"source": "github:anton-abyzov/vskill"` with no `sourceSkillPath`. `vskill` is a multi-skill repo with no SKILL.md at root, so the synthesised anchor 404s every time.

Three layers compound the failure:

1. **CLI install** (`vskill add`) writes the lockfile with the repo URL but throws away the path it already knows from `DiscoveredSkill.path`.
2. **Eval-server resolver** (`resolveSourceLink`), when no explicit path is recorded, defaults to `"SKILL.md"` and synthesises a confidently-wrong URL.
3. **Frontend** (`DetailHeader`) falls back to the author-declared `homepage` if `repoUrl` is missing — `homepage` routinely points at an unrelated repo.

A wrong link is worse than no link. The fix lands at all three layers; the safe fallback (when path information is missing) is the existing copy-chip showing the local path.

## Goals

- Persist enough provenance on install (`sourceRepoUrl` + `sourceSkillPath`) for the studio to construct correct GitHub anchors.
- Stop synthesising wrong URLs server-side when path information is missing.
- Stop falling back to `homepage` for the SKILL.md anchor on the frontend (keep it for the author profile link, which is harmless).

## Non-goals

- **Backfill migration tool for existing lockfiles.** Natural reinstall fixes them; legacy entries get the safe copy-chip fallback in the meantime.
- **Marketplace plugin install path** (`add.ts:595-621`). Plugin-level entries hold multiple skills; the existing flat-layout fallback is documented and out of scope here.
- **AuthorLink homepage handling.** It only routes to `https://github.com/{owner}` (profile), can't 404 from a repo mismatch.

---

## User Stories

### US-001: Studio anchor opens the correct SKILL.md after install

**Project**: vskill

**As a** vskill studio user
**I want** the SKILL.md anchor in the detail header to open the actual file on GitHub
**So that** I can read source / contribute / file issues against the real upstream

**Acceptance Criteria**:
- [ ] **AC-US1-01**: When I run `vskill add anton-abyzov/vskill/greet-anton`, the resulting `vskill.lock` entry contains both `sourceRepoUrl: https://github.com/anton-abyzov/vskill` AND `sourceSkillPath` set to the actual repo-relative path (e.g. `plugins/sw/skills/greet-anton/SKILL.md` or whatever `DiscoveredSkill.path` resolves to).
- [ ] **AC-US1-02**: When the studio renders this skill, the SKILL.md anchor href is `https://github.com/anton-abyzov/vskill/blob/HEAD/<sourceSkillPath>` — a working URL, not a 404.
- [ ] **AC-US1-03**: When I install via the single-skill legacy path (`vskill add owner/repo --skill foo`), the lockfile carries `sourceSkillPath` derived from the in-scope `skillSubpath` variable (defaults to `skills/foo/SKILL.md` or `SKILL.md`).

### US-002: Resolver returns null instead of fabricating wrong paths

**Project**: vskill

**As a** vskill maintainer
**I want** `resolveSourceLink()` to return `skillPath: null` when a legacy lockfile entry has no recorded path
**So that** the UI can fall back to the safe copy-chip instead of rendering a confidently-wrong GitHub URL

**Acceptance Criteria**:
- [ ] **AC-US2-01**: For a legacy entry with `source: github:owner/repo` and no `sourceSkillPath`, `buildSkillMetadata()` returns `repoUrl: <github-url>` AND `skillPath: null` (was previously `"SKILL.md"`).
- [ ] **AC-US2-02**: For a forward-compat entry with explicit `sourceSkillPath`, `buildSkillMetadata()` continues to return that path verbatim (no regression).
- [ ] **AC-US2-03**: For an authored skill (no lockfile entry at all), `buildSkillMetadata()` continues to return `{repoUrl: null, skillPath: null}` (no regression).

### US-003: Frontend stops misusing `homepage` as a source-repo URL

**Project**: vskill

**As a** studio user looking at an authored or legacy-installed skill
**I want** the SKILL.md affordance to show me my local path (copy-chip) instead of pointing at an unrelated GitHub repo
**So that** I can trust the link to do what it says

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When `skill.repoUrl` is null, `DetailHeader` renders the `source-file-copy` chip (existing fallback) instead of a `source-file-link` anchor — even if `skill.homepage` is a github.com URL.
- [ ] **AC-US3-02**: When `skill.repoUrl` is present, the byline still renders the SKILL.md anchor (no regression on the happy path).
- [ ] **AC-US3-03**: `AuthorLink` continues to use the existing `repoUrl ?? homepage` chain — author profile link is unchanged. Both anchors still coexist in the byline (no truncation collapse).

### US-004: End-to-end verification on a real skill

**Project**: vskill

**As a** developer reviewing this fix
**I want** a reproducible end-to-end check that the bug is gone
**So that** I can sign off with confidence

**Acceptance Criteria**:
- [ ] **AC-US4-01**: After rebuilding the local vskill, removing `TestLab/greet-anton`, and reinstalling via the local CLI, `TestLab/greet-anton/vskill.lock` contains both `sourceRepoUrl` and `sourceSkillPath`.
- [ ] **AC-US4-02**: After restarting `vskill studio`, opening `http://localhost:3136/#/skills/TestLab/greet-anton`, and clicking the `SKILL.md ↗` anchor, the browser opens the actual file on GitHub (HTTP 200, file content visible).
- [ ] **AC-US4-03**: For a legacy lockfile entry without `sourceSkillPath`, the studio renders the copy-chip with the local path instead of a broken anchor (regression check for AC-US3-01).
