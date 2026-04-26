---
status: completed
---
# 0781 — Hotfix: Studio updater popup and sidebar installed-version

## Problem

User reported four small but visible UX bugs in `vskill studio` after a save bumped greet-anton's frontmatter version from `1.0.2` to `1.0.3` while the platform release at `1.0.3` had no file changes:

1. The **left sidebar** shows the *frontmatter* version (`1.0.3`) for an installed skill, but the version-history panel correctly marks `1.0.2` as `[installed]`. The two views disagree. For installed skills, the *installed* version (lockfile/platform truth) is what the user runs — frontmatter is a static copy of file content and can drift after a save.
2. The **update notification popup** (UpdateBell → UpdateDropdown) is `width: 320` so the per-row "Update" button gets truncated to "Upda…" when the skill name is long (`anton-abyzov/greet-anton/…`).
3. The **update notification popup** still renders a "Platform crawler degraded" banner from increment 0778. The bell icon already conveys the degraded state via its colour and tooltip; stuffing the banner into the *updater* popup mixes two unrelated concerns. The user explicitly said: "this updater has nothing to do with the crawler — remove it."
4. The **version-history panel** displays `diffSummary: "0 files"` (returned by the platform when a publish has no manifest entries) verbatim. The label is unhelpful — the user reads it as "the latest release is empty/broken." A friendlier label is needed until the upstream platform stops emitting empty publishes (handled separately in 0779).

## Out of scope

- Stopping empty publishes upstream (covered by 0779).
- The standalone `Bell` indicator's degraded state — keep as is.
- Right-panel header VersionBadge for installed skills — kept consistent with sidebar via the same resolver change.

## User stories

### US-001 — Sidebar shows installed version for installed skills

**As** a Studio user with an installed skill whose frontmatter on disk has drifted past the installed version,
**I want** the sidebar version badge to show the version I am actually *running* (per the lockfile / upstream check-updates poll),
**so that** the sidebar agrees with the "[installed]" marker on the Versions tab and I'm not confused about what's deployed.

#### Acceptance criteria

- [x] AC-US1-01: When `skill.origin === "installed"` and `skill.currentVersion` is a valid semver, the sidebar VersionBadge renders `currentVersion` (not `version`/frontmatter).
- [x] AC-US1-02: When `skill.origin === "installed"` and `skill.currentVersion` is absent (no platform poll yet), the sidebar VersionBadge falls back to the existing precedence (`frontmatter > registry > plugin > default`).
- [x] AC-US1-03: For `origin === "own"` (authored) and plugin-bundled skills, behavior is unchanged — the frontmatter remains the source of truth.
- [x] AC-US1-04: The right-panel `DetailHeader` VersionBadge agrees with the sidebar — both pick the installed version for installed skills.
- [x] AC-US1-05: `versionSource` for installed-when-from-currentVersion is `"registry"` so the existing italic styling already in `VersionBadge` continues to mark inherited versions.

### US-002 — Wider, scoped updater popup

**As** a Studio user clicking the bell to see what's available to update,
**I want** the popup to be wide enough to display the skill name and the inline "Update" button without truncation,
**so that** I can read every row and click "Update" without expanding anything.

#### Acceptance criteria

- [x] AC-US2-01: `UpdateDropdown` root width is **at least 440px**.
- [x] AC-US2-02: With a skill named `anton-abyzov/greet-anton-abyzov`, the "Update" button text renders fully (no `Upda…`/clip).
- [x] AC-US2-03: The "Platform crawler degraded" banner is **removed** from `UpdateDropdown`. The bell's own colour + tooltip remain the indicator.
- [x] AC-US2-04: The 0778 props `platformDegraded` / `platformReason` are dropped from `UpdateDropdown`'s prop interface (callers in `UpdateBell.tsx` updated).

### US-003 — Friendlier label for empty diffSummary

**As** a Studio user looking at version history for a skill whose latest publish was a metadata-only bump,
**I want** the panel to say "Metadata-only release — no file changes" instead of `0 files`,
**so that** I'm not misled into thinking the release is broken.

#### Acceptance criteria

- [x] AC-US3-01: When a `VersionEntry.diffSummary` matches the strings `"0 files"` or `"no file changes"` (case-insensitive, trimmed), the panel renders **"Metadata-only release — no file changes"** instead.
- [x] AC-US3-02: All other `diffSummary` strings render unchanged.
- [x] AC-US3-03: When `diffSummary` is `null`/empty, no row caption is rendered (current behavior).

### US-004 — Disambiguate plugin-bundled skill version from plugin version

**As** a Studio user opening a plugin-bundled skill (e.g. `mobile › appstore`) whose frontmatter version mirrors the plugin manifest while the upstream version-history track is independent,
**I want** the right-panel header to clearly show both the skill version and the plugin (manifest) version distinctly,
**so that** I'm not confused by the collision between the sidebar/header `2.3.2` (plugin/frontmatter) and the version-history `[installed] 1.0.2` (upstream skill track).

**Background.** Plugin-bundled skills carry three potential version sources:
1. **Frontmatter** of `SKILL.md` — the file's declared version. By convention, plugin authors often mirror the plugin manifest (e.g. `mobile@2.3.2` ⇒ `appstore` frontmatter `version: 2.3.2`).
2. **Plugin manifest** (`plugin.json#version`) — the version of the *plugin* this skill ships in.
3. **Upstream skill track** (`verified-skill.com/api/v1/skills/.../versions`) — the independent version sequence that the skill is *published as* on the marketplace, identified by content hash. This may not align with either of the above (e.g. the `appstore` skill is at `1.0.0–1.0.3` upstream while shipping in `mobile@2.3.2`).

When all three diverge, the user sees `2.3.2` on the left + header and `1.0.2 [installed]` on the right and reasonably wonders which is the "real" version. The cleanest mitigation is to surface the *plugin* version explicitly so the user can read both numbers without guessing.

#### Acceptance criteria

- [x] AC-US4-01: When a skill has `pluginName != null` AND `pluginVersion != null`, the `DetailHeader` renders a `data-testid="detail-header-plugin-chip"` element with the text `from {pluginName}@{pluginVersion}` next to the version badge.
- [x] AC-US4-02: When `pluginName` is null (plain authored skills, non-plugin installs), the chip is **not** rendered.
- [x] AC-US4-03: The chip uses muted secondary-text colour and `font-mono` for the version segment, mirroring the existing inherited-from tooltip vocabulary so it reads as informational rather than a primary action.
- [x] AC-US4-04: The sidebar VersionBadge remains unchanged for authoring plugin-bundled skills — the frontmatter (which is already the author's chosen version, often inherited) still wins. The chip is the disambiguation surface.
- [x] AC-US4-05: For installed plugin-bundled skills (`origin === "installed"` AND `source === "plugin"`), the US-001 rule applies and the sidebar badge still tracks `currentVersion` over frontmatter — the chip continues to label the plugin context.

## Non-goals / explicit decisions

- The `pickInstalledVersion` server logic stays as is — the sidebar fix is purely client-side, using `currentVersion` already populated by `mergeUpdatesIntoSkills`.
- We **do not** remove the platform-health banner everywhere; it remains where it semantically belongs (the bell icon, the global health UI). Only the dropdown is decluttered.
- We **do not** strip or reset the upstream version-history `[installed]` marker for plugin-bundled skills. The marker is computed by content-hash match and is correct upstream-side; the user's frontmatter convention (mirror plugin version) is what creates the visual collision. The plugin chip explains the layering instead of altering data.
