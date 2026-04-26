---
status: completed
---
# 0764 — Studio: detect installed skill version when lockfile is empty

## Problem

When a user opens the Studio skill detail page (`/#/skills/<plugin>/<skill>`) for an installed skill that has **no lockfile entry**, the version timeline lists upstream versions correctly but:

1. None of them is marked `installed` (the dot/badge is missing on every row).
2. No "Update to <latest>" button appears, even when an upstream version is newer than what's on disk.
3. The header version chip falls back to the literal `1.0.0` rendered in italic ("inherited / not declared"), which reads to the user as "current is 1.0.0" — that's misleading.

Concrete example reported on `2026-04-26`: `http://localhost:3170/#/skills/.claude/scout` shows four versions (1.0.3, 1.0.2, 1.0.1, 1.0.0); the actual on-disk `SKILL.md` has no `version:` frontmatter and is not in the lockfile; the user sees italic 1.0.0 with no update affordance.

## Root cause

`/api/skills/:plugin/:skill/versions` enriches with `isInstalled` from a single source — the vskill lockfile (`src/eval-server/api-routes.ts:1911-1917`):

```ts
const installedVersion = lock?.skills[params.skill]?.version;
const enriched = versions.map((v: any) => ({
  ...v,
  isInstalled: installedVersion ? v.version === installedVersion : undefined,
}));
```

For Anthropic-style installed skills (copied into `.claude/skills/<name>/`), there is typically no lockfile entry, so `installedVersion` is `undefined` and every row gets `isInstalled: undefined`. The frontend (`VersionHistoryPanel.tsx:60-62`) then has `installed = null` and `showAutoLink = false`, hiding the update button.

## User Stories

### US-001: Show installed version even without a lockfile entry
**As** a Studio user with an Anthropic-installed skill (under `.claude/skills/<name>/`)
**I want** the version timeline to mark the installed version on the timeline
**So that** I can see at a glance which version I'm on, and tell whether an update is available.

**Acceptance Criteria:**
- [x] AC-US1-01: When the on-disk `SKILL.md` for the skill carries a `version:` field in frontmatter, `/api/skills/:plugin/:skill/versions` returns `isInstalled: true` on the matching version row.
- [x] AC-US1-02: When no `version:` frontmatter and no lockfile entry exist, the endpoint computes the on-disk file's `contentHash` and returns `isInstalled: true` on any upstream version row whose `contentHash` matches.
- [x] AC-US1-03: When neither the frontmatter version nor the contentHash matches any upstream row, no row is marked `isInstalled` (legacy behavior preserved).
- [x] AC-US1-04: Lockfile entry continues to take precedence over both frontmatter and contentHash (no regression for tracked installs).

### US-002: Show the "Update to <latest>" button when newer version exists
**As** a Studio user
**I want** the "Update to <latest>" button to appear whenever a newer upstream version is available
**So that** I don't have to remember the CLI command.

**Acceptance Criteria:**
- [x] AC-US2-01: With AC-US1-01 or AC-US1-02 satisfied and `installed.version !== latest.version`, the button renders.
- [x] AC-US2-02: Button label includes the target version (e.g. "Update to 1.0.3").

### US-003: Stop misleading italic "1.0.0" fallback for the scout skill
**As** the user reading the scout detail page
**I want** the header version chip to show the actually installed version, not a literal `1.0.0` fallback
**So that** I'm not confused about what's on my disk.

**Acceptance Criteria:**
- [x] AC-US3-01: `.claude/skills/scout/SKILL.md` carries an explicit `version:` field in its frontmatter (data fix; ensures the chip shows a real version).

## Out of scope

- Re-architecting the studio's "installed" model across all panels (sidebar SkillRow, RightPanel header, etc.) — this increment only changes the versions API enrichment + scout's frontmatter. UI components consuming `isInstalled` from that endpoint immediately benefit.
- Lockfile back-fill or migration utility.
- Changing the `VersionBadge` italic-fallback logic.
