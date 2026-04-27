---
increment: 0795-studio-plugin-list-cli-removed
title: Studio /api/plugins 500 — claude plugin list no longer exists
type: bug
priority: P1
status: completed
created: 2026-04-27T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug: Studio /api/plugins 500 — `claude plugin list` removed from Claude Code CLI

## Overview

Studio polls `GET /api/plugins` every 60s (via `usePluginsPolling`) and on every plugin mutation. The handler at [plugin-cli-routes.ts:81](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli-routes.ts:81) shells out to `claude plugin list`. Confirmed via `claude plugin --help`:

```
$ claude plugin --help
Commands:
  validate <path>
  marketplace
  install|i <plugin>
  uninstall|remove <plugin>
  enable <plugin>
  disable <plugin>

$ claude plugin list
error: unknown command 'list'
```

The `list` subcommand has been removed from the Claude Code CLI. Every Studio session emits 3+ failed 500s before the polling hook backs off, and the Sidebar's Enable/Disable button state is broken because `rawPluginList` is empty.

The same dead call path also lives in [plugin-cli.ts:60](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli.ts:60) `fetchPluginList()` which the mutation routes (enable/disable/install/uninstall) use to refresh the list after action — meaning post-mutation refresh has been silently failing too.

## User Stories

### US-001: Studio shows the correct list of installed plugins (P1)
**Project**: vskill

**As a** Studio user
**I want** the Sidebar's plugin tree (and the Enable/Disable button states) to reflect what Claude Code actually has installed
**So that** I'm not staring at a stale or empty plugin list and Claude Code's settings.json is the source of truth

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GET /api/plugins` returns `{ plugins: InstalledPlugin[] }` for a workspace where `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/.claude-plugin/plugin.json` exists.
- [x] **AC-US1-02**: A plugin enabled in `~/.claude/settings.json` `enabledPlugins["<name>@<marketplace>"]: true` is returned with `enabled: true, scope: "user"`.
- [x] **AC-US1-03**: A plugin enabled only in `<projectDir>/.claude/settings.json` is returned with `enabled: true, scope: "project"`.
- [x] **AC-US1-04**: A plugin present on disk but absent from any `enabledPlugins` is returned with `enabled: false`.
- [x] **AC-US1-05**: When `~/.claude/plugins/cache/` does not exist, the endpoint returns `{ plugins: [] }` with status 200 (no 500).
- [x] **AC-US1-06**: When a plugin cache dir has no `.claude-plugin/plugin.json`, that plugin is skipped silently (no 500).
- [x] **AC-US1-07**: The endpoint never invokes `claude plugin list`. Regression-guarded by a vitest spec that sets PATH to a fake `claude` binary that fails on `list` — the endpoint must still return 200.

### US-002: Mutation refresh still works after enable/disable/install/uninstall (P1)
**Project**: vskill

**As a** Studio user clicking Enable/Disable/Install/Uninstall
**I want** the resulting plugin list returned inline to reflect the post-mutation state
**So that** I don't see stale data after my own action

**Acceptance Criteria**:
- [x] **AC-US2-01**: `POST /api/plugins/:name/enable` returns `plugins[]` derived from `discoverInstalledPlugins`, not from the dead `claude plugin list`.
- [x] **AC-US2-02**: Same for `/disable`, `/install`, `/uninstall`.
- [x] **AC-US2-03**: The mutation routes still call `claude plugin <action>` (those subcommands DO exist); only the post-action *refresh* changes.

### US-003: No regression in path safety (P1)
**Project**: vskill

**As an** operator
**I want** the cache walk to refuse paths outside `cacheRoot`
**So that** a maliciously named plugin folder can't trick the walker into reading arbitrary JSON

**Acceptance Criteria**:
- [x] **AC-US3-01**: The walker's marketplace/plugin/version names are validated against the established `isInside(resolve(...), cacheRoot + sep)` pattern from [plugin-orphan-cleanup.ts:49](repositories/anton-abyzov/vskill/src/eval-server/plugin-orphan-cleanup.ts:49).
- [x] **AC-US3-02**: The walker never writes to disk.

## Functional Requirements

### FR-001: New helper module `plugin-discovery.ts`
Pure function `discoverInstalledPlugins({ cacheRoot, projectDir? }): InstalledPlugin[]`. Walks the cache, reads each plugin.json, joins against `enabledPlugins` from user + project settings.

### FR-002: Replace both call sites
- [plugin-cli-routes.ts:81](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli-routes.ts:81) — inline GET handler
- [plugin-cli.ts:60](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli.ts:60) — `fetchPluginList()` helper used by mutation routes

Both swap `runClaudePlugin(["list"], …)` → `discoverInstalledPlugins(…)`.

### FR-003: Keep the response contract
`{ plugins: InstalledPlugin[] }` where `InstalledPlugin` is the existing exported type from [plugin-cli.ts:23](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli.ts:23). Frontend code (`usePluginsPolling`, `Sidebar`) is unchanged.

## Success Criteria

- Studio session against TestLab/hi-anton has zero `/api/plugins` 500s in the network tab.
- Sidebar's Enable/Disable button state correctly reflects the plugin's enabled flag.
- Existing `parseInstalledPlugins` tests still pass — they remain valid for any future regression where `claude plugin list` returns; for now we don't delete them, just stop calling them in production code paths.

## Out of Scope

- Removing `runClaudePlugin` itself (still used for `install/uninstall/enable/disable` mutations — those subcommands DO exist).
- Removing `parseInstalledPlugins` or its tests (kept for forward compatibility if Claude Code ever restores `list`).
- Per-version listing (a plugin with multiple cached versions emits one row, the most recent by mtime).

## Dependencies

- Existing `listEnabledPlugins(opts)` in [src/settings/settings.ts:64](repositories/anton-abyzov/vskill/src/settings/settings.ts:64).
- Existing `InstalledPlugin` type in [src/eval-server/plugin-cli.ts:23](repositories/anton-abyzov/vskill/src/eval-server/plugin-cli.ts:23).
- Path-safety pattern from [plugin-orphan-cleanup.ts:49](repositories/anton-abyzov/vskill/src/eval-server/plugin-orphan-cleanup.ts:49).
