# Preserve project icons when renaming

## Problem

The automatic project badge derives its monogram and color from the mutable project title, so renaming changes its visual identity. The saved icon update path already preserves omitted projectIcon and faviconPath; regression coverage must establish that behavior too.

## Scope

In: durable automatic badge identity across desktop/web renames; existing chosen icons, emoji, monograms and favicons; linked-checkout icon precedence; regression tests and reviewed PR merge. Out: app release and native mobile visual redesign.

## Acceptance Criteria

- [ ] AC-01: Renaming preserves the automatic badge letters and color across repeated renames and reloads, without converting it to a chosen icon or hiding a favicon or linked checkout icon.
- [ ] AC-02: Renaming preserves chosen Lucide icons, emoji, monograms and favicon paths; explicit icon changes and reset still work.
- [ ] AC-03: Focused tests and production builds pass, and the exact PR head has fresh-context SHIP review before merge.

## Approach

Store the original automatic identity title in the existing durable workspace settings JSON on first rename. Keep it separate from projectIcon so automatic favicon discovery and PR 1261 linked-icon precedence remain intact. ProjectFavicon uses this seed only for its generated fallback; the visible title remains current. Guard the seed from generic settings patches. Test the public project service with an isolated in-memory database and the real favicon component. No live database access.

## Decisions

### Asked
- None.

### Defaulted
- D-01: Preserve automatic identity independently of chosen icons, using an optional server-owned setting with backward-compatible decoding and no database migration.
- D-02: No app release; finish at reviewed merge as requested.

### Open
- None.

## Tasks

### T-01 Preserve identity and cover rename regressions
- AC: AC-01, AC-02 | Files: packages/contracts/src/projectWorkspace.ts, apps/server/src/orchestration-v2/ProjectCommands.ts, apps/server/src/orchestration-v2/ProjectCommands.test.ts, apps/server/src/project/ProjectService.test.ts, apps/web/src/components/ProjectFavicon.tsx, apps/web/src/components/ProjectFavicon.test.tsx, apps/web/src/components/studio/ProjectIconEditor.tsx, apps/web/src/environmentGrouping.test.ts | Test: cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/ProjectCommands.test.ts src/project/ProjectService.test.ts

### T-02 Review and merge
- AC: AC-03 | Files: none | Test: gh pr checks --repo anton-abyzov/specwithcode-dev

## Closure

Verify and close 1210.
