---
increment: 0740-studio-update-routing-and-version-truth
title: "Studio #/updates routing + skill-version single-source-of-truth + sidebar dedupe"
type: bug
priority: P1
status: active
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
discovered_during: 0736 closure follow-up + user manual verification on vskill@0.5.116
---

# Bug: View Updates click goes nowhere + version drift + sidebar duplicates

## Overview

After shipping 0736 (vskill@0.5.116) the user verified the fixes manually and surfaced four intertwined regressions in the Skill Studio sidebar + update notification path:

1. **`#/updates` route is dead.** Clicking "View Updates" in the bottom toast or "View all" in the bell dropdown sets `window.location.hash = "#/updates"`, but `App.tsx` only matches `#/create`. The URL changes, the page renders the default empty state ("Select a skill to view details"), and the user has no way to reach the bulk Updates view.
2. **Same skill appears in multiple sidebar sections at conflicting versions.** `obsidian-brain` shows up as: AVAILABLE > PROJECT > .CLAUDE (1.1.0), AUTHORING > SKILLS > PERSONAL (1.3.0), AUTHORING > PLUGINS > personal (1.3.0). The last two point to the **same** physical directory because the server scanner emits the same `dir` twice with different `scopeV2`.
3. **Push toast lies about installed version.** The bell/toast shows `obsidian-brain 1.0.0 → 1.0.6` while the on-disk frontmatter is 1.3.0. Cause: `vskill outdated --json` reads the `vskill.lock` `currentVersion`, which has drifted from the actual SKILL.md `metadata.version` on disk.
4. **The ↑ glyph contaminates every row sharing a short name.** `mergeUpdatesIntoSkills` matches by `s.skill` only, so all four `obsidian-brain` rows inherit the same `updateAvailable: true` regardless of whether they originate from the lockfile-tracked install or from authoring sources.

These bugs are intertwined because they share the same install/version/sidebar surface. Fixing them together avoids three separate commit churns.

## Personas

- **Skill Studio user** (Anton-style power user): authors skills locally in `plugins/<name>/skills/...` AND installs upstream skills via `vskill install`. Currently sees confusing version numbers and a non-functional "View Updates" button.
- **First-time studio user**: clicks the highlighted "View Updates" button after seeing the toast — gets dropped on an empty page with no feedback.

## User Stories

### US-001: View Updates button reaches the Updates view
**Project**: vskill

**As a** Skill Studio user
**I want** clicking "View Updates" or "View all" to navigate me to a panel listing every skill with an available update
**So that** I can act on the toast/bell affordances instead of being dumped on an empty default page

**Acceptance Criteria**:
- [x] **AC-US1-01**: Clicking "View Updates" in `UpdateToast` (bottom-right toast) sets `window.location.hash = "#/updates"` AND `App.tsx` renders the bulk Updates view in the main content area instead of the default empty `<RightPanel>` placeholder.
- [x] **AC-US1-02**: Clicking "View all" in the bell `UpdateDropdown` performs the same navigation and renders the same view.
- [x] **AC-US1-03**: When the hash is `#/updates`, the StudioLayout chrome (TopRail, sidebar, ⌘K) remains visible — the user is NOT teleported to a standalone page (parity with `#/create` behavior added in 0703).
- [x] **AC-US1-04**: Navigating back (browser back button or clearing the hash) returns to the previous skill detail / empty state without a full page reload.
- [x] **AC-US1-05**: A unit test exercises the `useIsUpdatesRoute()` hook, and a Playwright E2E click-flow test asserts that clicking "View Updates" results in the Updates panel rendering with the expected list.

### US-002: Sidebar shows each skill exactly once per scope
**Project**: vskill

**As a** Skill Studio user
**I want** each on-disk skill directory to appear in exactly one sidebar bucket
**So that** I'm not confused by the same skill appearing under "AUTHORING > SKILLS > PERSONAL" AND "AUTHORING > PLUGINS > personal" at the same time

**Acceptance Criteria**:
- [x] **AC-US2-01**: When a `plugins/<name>/.claude-plugin/plugin.json` manifest exists, the legacy "Layout 2" walker (`scanSkills` / `scanPluginDirs`) MUST skip that `plugins/<name>/skills/...` subtree, leaving emission to `scanAuthoredPluginSkills`.
- [x] **AC-US2-02**: After scanner concatenation in `api-routes.ts`, no two emitted `SkillInfo` rows share the same canonical `dir`. If a duplicate is detected at runtime, the entry with `scopeV2 === "authoring-plugin"` wins (manifest-bearing entry is the source of truth) and a `console.warn` once per session reports the dedupe.
- [x] **AC-US2-03**: A unit test verifies that for a fixture project with `plugins/personal/.claude-plugin/plugin.json` AND `plugins/personal/skills/foo/SKILL.md`, the `/api/skills` response contains exactly ONE entry for `foo` with `scopeV2 === "authoring-plugin"`, NOT two.
- [x] **AC-US2-04**: A regression test for the historical Layout 2 path: when a `plugins/<name>/` exists WITHOUT a `.claude-plugin/plugin.json` manifest, the legacy walker still emits the skills (back-compat).

### US-003: "Installed version" is the disk truth, not the lockfile pin
**Project**: vskill

**As a** Skill Studio user who edits skills in place AND uses `vskill install`
**I want** the bell/toast "installed → latest" pair to reflect the actual on-disk version of the installed file
**So that** I'm not told my obsidian-brain is at 1.0.0 when its SKILL.md frontmatter clearly says 1.3.0

**Acceptance Criteria**:
- [x] **AC-US3-01**: `vskill outdated --json` (the command consumed by `/api/skills/updates`) MUST resolve each lockfile entry's installed file path, parse the `metadata.version` from the on-disk SKILL.md frontmatter, and emit that as `currentVersion` to the platform `/check-updates` call (not `lock.skills[name].version`).
- [x] **AC-US3-02**: When the on-disk frontmatter is unreadable or missing, `outdated` falls back to `lock.skills[name].version` and surfaces a `warning` field on the entry (not a hard error).
- [x] **AC-US3-03**: When the on-disk version is GREATER than the platform's `latestVersion`, the entry's `updateAvailable` is `false` (don't tell the user to "update" to an older version they've already authored past).
- [x] **AC-US3-04**: A unit test covers (i) on-disk > lockfile drift → emit disk version, (ii) on-disk missing → fall back to lockfile + warning, (iii) on-disk > latest → `updateAvailable: false`.
- [x] **AC-US3-05**: A doc-comment block at the top of `outdated.ts` describes the disk-vs-lockfile contract so the next dev doesn't undo it.

### US-004: Update merge keys by full identity, not bare short name
**Project**: vskill

**As a** Skill Studio user with multiple skills sharing a leaf name (e.g. one obsidian-brain installed, another authored locally)
**I want** the ↑ glyph to appear ONLY on the row that's actually outdated
**So that** my locally-authored copy doesn't show a misleading update arrow when the registry-pinned install is the only one with a real update

**Acceptance Criteria**:
- [x] **AC-US4-01**: `mergeUpdatesIntoSkills` MUST gate the merge on `s.origin === "installed"`. Authoring rows (`origin === "authored"` / `scopeV2.startsWith("authoring-")`) never receive `updateAvailable: true` from a `SkillUpdateInfo` payload.
- [x] **AC-US4-02**: When matching a `SkillUpdateInfo` to a `SkillInfo`, use the full lockfile-derived identity (`pluginName/skill` or canonical `owner/repo/skill`) — not the bare leaf `s.skill`.
- [x] **AC-US4-03**: A unit test covers a fixture with two `obsidian-brain` rows (one installed, one authored) and asserts only the installed row receives the merged update flag.
- [x] **AC-US4-04**: The push toast/dropdown's `installed → latest` text uses the disk version emitted by US-003 (not lockfile), so the toast reflects what the user actually has.

## Functional Requirements

- **FR-001 (route handler)**: New `useIsUpdatesRoute()` hook in `App.tsx` mirroring `useIsCreateRoute()`. When true, the main slot renders an `<UpdatesPage>` (or hoisted `<UpdatesPanel>`) with the bulk update list.
- **FR-002 (scanner dedupe — primary)**: `src/eval/skill-scanner.ts` Layout 2 walker (`scanPluginDirs(<root>/plugins/...)`) MUST skip directories where `<plugin>/.claude-plugin/plugin.json` exists.
- **FR-003 (scanner dedupe — defensive)**: `src/eval-server/api-routes.ts` post-concat dedupe by canonical `dir` path with `authoring-plugin` precedence.
- **FR-004 (lockfile reconcile)**: `src/commands/outdated.ts` resolves each entry to its installed SKILL.md path, reads `metadata.version`, and emits that as `currentVersion`. Falls back to lockfile on read error.
- **FR-005 (merge gating)**: `src/eval-ui/src/api.ts:mergeUpdatesIntoSkills` filters by `origin === "installed"` and matches on `pluginName/skill` (or full lockfile name).
- **FR-006 (doc comments)**: Top-of-file contract blocks in `App.tsx` (route map), `skill-scanner.ts` (Layout 2 exclusion), `outdated.ts` (disk-vs-lockfile), and `api.ts mergeUpdatesIntoSkills` (origin-gating) so the next dev doesn't reintroduce these regressions.

## Non-Functional Requirements

- **NFR-001 (correctness)**: For any installed skill, `installed` value reported by `/api/skills/updates` MUST equal `metadata.version` of the file at the resolved install path (or surface a structured `warning` if unresolvable).
- **NFR-002 (sidebar uniqueness)**: For any project, `count(skills where dir === X) === 1` for all `X` in `/api/skills` response.
- **NFR-003 (route parity)**: `#/updates` and `#/create` behave identically with respect to chrome (TopRail/sidebar visible) and back-navigation.

## Success Criteria

- **SC-001**: Clicking "View Updates" in the bottom toast renders the Updates panel within 300ms (no empty placeholder visible).
- **SC-002**: A studio session in `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/` shows `obsidian-brain` exactly twice in the sidebar (once in PROJECT > .CLAUDE at 1.1.0, once in AUTHORING > PLUGINS > personal at 1.3.0) — NOT three times.
- **SC-003**: The push toast for `obsidian-brain` reports the on-disk version (1.3.0), not the lockfile version (1.0.0). If lockfile says 1.0.0 but disk says 1.3.0 and platform `latest` is 1.0.6, `updateAvailable` is `false`.
- **SC-004**: vskill@0.5.117 ships with all four fixes; a clean `npm install -g vskill@0.5.117 && vskill studio` repro shows all four bugs resolved.

## Out of Scope

- Healing the lockfile to match disk on every `outdated` call (this increment only changes the *reported* version, not the lockfile state — that lives in a future "vskill heal" command).
- Hash-based router refactor (still using ad-hoc `useIsCreateRoute`-style hooks, not adopting react-router).
- Personal-global vs project precedence redesign (existing behavior preserved).
- Removing the legacy `startSkillUpdate` export from `api.ts` (deferred from 0736 as F-008).
