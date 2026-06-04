---
increment: 0872-refresh-plugins-force-sync
title: refresh-plugins force-syncs plugin content (stop stale cache on upgrade)
type: bug
priority: P1
status: completed
created: 2026-06-03T08:30:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug: refresh-plugins reports the new version but never re-copies content

## Overview

After a SpecWeave release, `specweave refresh-plugins` reports the new version (e.g. "active
(v1.0.590)") but does NOT physically refresh users' installed plugin **content** — they keep
stale `hooks.json` / skills. 0871 fixed version *alignment* (so `claude plugin install` now
*detects* the new version), but the content copy is a separate gap.

## Root cause

`refresh-plugins.ts` (native-cli path) calls `installPlugin()` → `claude plugin install`. For the
directory-source specweave marketplace, `claude plugin install` records a FIXED `installPath`
(`~/.claude/plugins/cache/specweave/sw/1.0.0`, version label `1.0.0`) in `installed_plugins.json`
and, on re-run, returns `skipped: true` ("active") **without re-copying content** — and if the
cache dir was wiped it just marks the plugin active without recreating it. Verified live: after
publishing 1.0.590 (correct content), `refresh-plugins` left the cache at the old `plugin.json
1.0.586` + missing the `stop` hook + the `handoff` skill until a manual `rsync` of the global
package's `plugins/specweave/` into the installPath.

## Goal

`refresh-plugins` makes the installed plugin **content** match the current package on every run —
deterministically, not relying on `claude plugin install`'s dedup.

## User Stories

### US-001: Force a content sync into the install path (P1)
**Project**: specweave

**As a** SpecWeave user upgrading the CLI then running `refresh-plugins`
**I want** my installed plugin's hooks + skills to actually update to the new version
**So that** I stop running stale hooks/skills after every upgrade.

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new `syncNativePluginContent(pluginName, specweaveRoot, { homeOverride? })` in `plugin-copier.ts` resolves the plugin's source dir from `.claude-plugin/marketplace.json` `plugins[].source`, reads each `installPath` for `<name>@specweave` from `installed_plugins.json`, and recursively copies the source into each installPath (creating it if missing), fixing hook permissions.
- [x] **AC-US1-02**: It updates the `installed_plugins.json` record's `version` (+ `lastUpdated`) to the source `plugin.json` manifest version, so the stuck `1.0.0`/stale label tracks reality.
- [x] **AC-US1-03**: `refresh-plugins` (native-cli path only) calls it for each installed plugin after the install loop, and prints `↻ <name>: content synced` when an installPath was refreshed. File-copy/adapter paths are untouched.
- [x] **AC-US1-04**: It is a no-op (returns synced:0, never throws) when `installed_plugins.json` is missing/malformed, the plugin isn't in the marketplace, or the source dir is absent; and it recreates a wiped installPath dir.

### US-002: Verified end-to-end (P1)
**Acceptance Criteria**:
- [x] **AC-US2-01**: A unit test (homeOverride + temp dirs) proves: a stale installPath (old content + a removed file) becomes byte-current after `syncNativePluginContent`, the version label is updated, a wiped installPath is recreated, and missing files no-op.
- [x] **AC-US2-02**: Manual/local: after build, deleting a file from the real cache installPath and running `specweave refresh-plugins` restores it (content synced), and the installPath `plugin.json` version equals the global package version.

## Out of Scope

- Changing Claude Code's native `claude plugin install` behavior (we sync around it).
- The cache dir naming `sw/1.0.0` (a stuck Claude-Code default) — we sync into whatever installPath the record holds rather than rename it.

## Success Criteria

- `npx vitest run` for the new test passes; `npm run build` clean; a real `refresh-plugins` run restores a deleted cache file and aligns the installPath plugin.json version.

## Dependencies

- `src/cli/commands/refresh-plugins.ts`, `src/utils/plugin-copier.ts` (`installPlugin`, `fixHookPermissions`), `installed_plugins.json`, `.claude-plugin/marketplace.json`.
