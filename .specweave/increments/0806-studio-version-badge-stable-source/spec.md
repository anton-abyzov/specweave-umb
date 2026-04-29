---
increment: 0806-studio-version-badge-stable-source
title: Studio version badge — stable source from vskill.lock
type: feature
priority: P1
status: completed
created: 2026-04-29T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio version badge — stable source from vskill.lock

## Overview

Sidebar version badges in vskill Studio flicker between italic (`versionSource: "registry"`) and non-italic (`versionSource: "frontmatter"`). Root cause: the `/api/skills` server response carries `currentVersion: null` for every row, so `parseRawSkill` (api.ts:320) falls through to the frontmatter branch on first paint. Italic only appears after the separately-polled `/api/skills/updates` response lands and `mergeUpdatesIntoSkills` overwrites `currentVersion = u.installed`. Any subsequent `refreshSkills()` (SKILL.md save, install/uninstall, agent switch) bounces the row back to "frontmatter" until the next merge tick — visible flicker.

This increment plumbs the existing `vskill.lock` into the existing `/api/skills` handler so the resolver has the registry-pinned version on the first response. No new files, no schema changes, no client work.

## User Stories

### US-001: Stable italic on first paint
**Project**: vskill

**As a** vskill Studio user with installed skills
**I want** the sidebar version badge to render its final style (italic for lockfile-pinned skills) on the first paint
**So that** the UI doesn't flicker between non-italic and italic as background fetches resolve

**Acceptance Criteria**:
- [x] **AC-US1-01**: `/api/skills` response includes `currentVersion` set to the lockfile `version` for any row whose leaf name has an entry in `vskill.lock`
- [x] **AC-US1-02**: `/api/skills` response keeps `currentVersion: null` for any row whose leaf name has no entry in `vskill.lock` (preserves existing source-origin/hand-authored behavior)
- [x] **AC-US1-03**: With `currentVersion` populated server-side, `parseRawSkill` (client) resolves `versionSource: "registry"` on the first response for installed-origin lockfile-pinned skills
- [x] **AC-US1-04**: After a `refreshSkills()` triggered by SKILL.md save / install / agent switch, badges for lockfile-pinned skills do not transition through a non-italic frame

### US-002: No regression to lockfile-absent skills
**Project**: vskill

**As a** vskill Studio user with hand-authored or Anthropic-style copied skills (no lockfile entry)
**I want** my badges to keep their existing non-italic appearance
**So that** the visual provenance signal still distinguishes lockfile-pinned from author-declared versions

**Acceptance Criteria**:
- [x] **AC-US2-01**: Skills not present in `vskill.lock` continue to render with `versionSource: "frontmatter"` (or `"default"` when frontmatter is missing) — no italic
- [x] **AC-US2-02**: `/api/skills` response shape stays additive only — no existing field is removed or renamed; `currentVersion` is `string | null` exactly as today

## Out of Scope

- `trackedForUpdates` flag (separate concern, comes from platform `/api/skills/updates` poll)
- `latestVersion` / `updateAvailable` (still require platform poll round-trip)
- Client-side `mergeUpdatesIntoSkills` rewrite (the fix removes the race, not the merge)
- Lockfile schema changes
- New endpoints
