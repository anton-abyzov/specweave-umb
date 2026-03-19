---
increment: 0540-plugin-lifecycle-core-only-install
title: 'Plugin lifecycle: core-only install + stale cache cleanup'
type: bugfix
priority: P0
status: completed
created: 2026-03-16T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Plugin Lifecycle: Core-Only Install + Stale Cache Cleanup

## Problem Statement

Two bugs degrade the SpecWeave plugin experience:

1. **Stale vskill cache causes "Plugin not found" errors** -- `~/.claude/plugins/cache/vskill/` contains phantom plugin directories (frontend, backend, payments, etc.) from a previous vskill version removed on March 9. `cleanup-stale-plugins.ts` only cleans `@specweave` marketplace plugins, ignoring `@vskill` and other marketplaces entirely. Stale cache directories are never cleaned.

2. **All 8 plugins auto-install on update instead of core-only** -- `refresh-plugins.ts` unconditionally installs ALL plugins from marketplace.json. On-demand loading was explicitly removed in v1.0.535, leaving the `llm-plugin-detector.ts` infrastructure dormant. Users pay the cost of installing and loading 8 plugins when most sessions only need `sw`.

## Goals

- Only install the `sw` core plugin by default during `refresh-plugins` and `update`
- Reactivate on-demand plugin loading for non-core plugins via hooks + llm-plugin-detector
- Extend stale plugin cleanup to all marketplaces dynamically
- Clean stale cache directories, not just settings.json references
- Provide `--plugin <name>` flag for targeted single-plugin install

## User Stories

### US-001: Core-Only Default Install
**Project**: specweave
**As a** SpecWeave user
**I want** `specweave refresh-plugins` to install only the `sw` core plugin by default
**So that** my environment stays lean and plugin load times are minimal

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given no flags, when `specweave refresh-plugins` runs, then only the `sw` plugin is installed/refreshed
- [x] **AC-US1-02**: Given the `--all` flag, when `specweave refresh-plugins --all` runs, then all plugins from marketplace.json are installed (backward compat)
- [x] **AC-US1-03**: Given existing non-core plugins already installed, when `specweave refresh-plugins` runs without `--all`, then existing non-core plugins are left in place (not uninstalled)
- [x] **AC-US1-04**: Given `specweave update` runs (no flags), then only the `sw` core plugin is refreshed in the plugins step

---

### US-002: Single Plugin Install Flag
**Project**: specweave
**As a** SpecWeave user
**I want** a `--plugin <name>` flag on `refresh-plugins`
**So that** I can install a specific plugin without installing all of them

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `specweave refresh-plugins --plugin frontend`, when the plugin exists in marketplace.json, then only that plugin is installed
- [x] **AC-US2-02**: Given `specweave refresh-plugins --plugin nonexistent`, when the plugin does not exist in marketplace.json, then the command exits with a non-zero code and prints an error listing available plugin names
- [x] **AC-US2-03**: Given `--plugin` combined with `--all`, when both flags are provided, then `--plugin` takes precedence (only the named plugin is installed)

---

### US-003: Multi-Marketplace Stale Plugin Cleanup
**Project**: specweave
**As a** SpecWeave user
**I want** stale plugin cleanup to cover all marketplaces, not just `@specweave`
**So that** phantom plugins from vskill or other marketplaces do not cause "Plugin not found" errors

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `~/.claude/plugins/cache/` contains marketplace subdirectories (e.g., `specweave/`, `vskill/`), when cleanup runs, then each marketplace is discovered dynamically by scanning cache subdirectories
- [x] **AC-US3-02**: Given a marketplace has a resolvable `marketplace.json`, when cleanup runs, then settings.json entries referencing plugins not in that marketplace's plugin list are removed
- [x] **AC-US3-03**: Given a marketplace's `marketplace.json` cannot be resolved (no local file, no fetchable remote), when cleanup runs, then that marketplace is skipped without error
- [x] **AC-US3-04**: Given stale cache directories exist under `~/.claude/plugins/cache/<marketplace>/<plugin-name>/` for plugins not in the marketplace's current list, when cleanup runs, then those directories are removed from disk

---

### US-004: On-Demand Plugin Loading Reactivation
**Project**: specweave
**As a** SpecWeave user
**I want** non-core plugins to load on-demand when my prompt requires them
**So that** I get the right plugin capabilities without pre-installing everything

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given only `sw` is installed, when the user submits a prompt mentioning React/frontend work, then the `user-prompt-submit.sh` hook triggers on-demand detection and installs the `frontend` plugin
- [x] **AC-US4-02**: Given `llm-plugin-detector.ts` infrastructure exists, when on-demand detection is triggered, then the existing detector is invoked (not a new parallel system)
- [x] **AC-US4-03**: Given Claude CLI is unavailable, when on-demand detection fails, then the hook degrades gracefully with no user-visible error
- [x] **AC-US4-04**: Given a plugin was already installed on-demand in the current session, when a subsequent prompt triggers the same plugin, then it is not re-installed (idempotent)

## Out of Scope

- Removing or uninstalling previously installed non-core plugins during default refresh
- Adding new marketplaces or marketplace discovery protocols
- Changing the vskill marketplace publishing pipeline
- UI changes to Claude Code's plugin management interface
- Rewriting llm-plugin-detector.ts internals (reuse existing infrastructure)

## Technical Notes

### Dependencies
- `cleanup-stale-plugins.ts` -- extend marketplace scanning
- `refresh-plugins.ts` -- add core-only default + `--plugin` flag
- `update.ts` -- pass through core-only behavior
- `llm-plugin-detector.ts` -- reactivate dormant on-demand loading
- `user-prompt-submit.sh` -- restore on-demand hook section
- `claude-plugin-enabler.ts` -- ensure single-plugin enable works

### Constraints
- Must preserve `--all` flag backward compatibility
- Must not break existing installations with non-core plugins already installed
- On-demand loading must work with both native CLI and direct-copy install modes
- Stale cleanup must be safe -- skip marketplaces with unresolvable manifests

### Architecture Decisions
- Dynamic marketplace discovery via `~/.claude/plugins/cache/` directory scan (no hardcoded list)
- Compare cache contents against each marketplace's `marketplace.json` for staleness
- Reuse existing `llm-plugin-detector.ts` rather than building new detection system
- Core plugin identity (`sw`) determined by marketplace.json `core: true` flag or hardcoded name

## Non-Functional Requirements

- **Performance**: Stale cache cleanup completes in under 2 seconds for typical installations (< 20 cached plugins)
- **Compatibility**: Works on macOS, Linux, and Windows path formats
- **Security**: No remote fetches during cleanup unless marketplace.json is missing locally (fetch from known GitHub repos only)

## Edge Cases

- **No cache directory exists**: Cleanup returns success with zero removals
- **Cache directory exists but is empty**: Cleanup returns success with zero removals
- **marketplace.json is malformed JSON**: Skip that marketplace, log warning, continue
- **Plugin cache dir is a symlink**: Follow symlink for staleness check, remove symlink (not target) if stale
- **Concurrent refresh and cleanup**: File operations are atomic per-plugin (rename pattern)
- **`--plugin` with marketplace prefix**: `--plugin sw-github` works; `--plugin sw-github@specweave` also works (strip marketplace suffix)

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| On-demand loading adds latency to first prompt | 0.4 | 3 | 1.2 | LLM detection runs in parallel with prompt processing; cache after first detection |
| Stale cleanup removes a plugin the user intentionally kept | 0.2 | 5 | 1.0 | Only remove if not in marketplace.json; skip unresolvable marketplaces |
| Remote marketplace.json fetch fails (network) | 0.3 | 2 | 0.6 | Skip marketplace on fetch failure; only fetch when local copy missing |

## Success Metrics

- `specweave refresh-plugins` installs exactly 1 plugin (sw) by default
- Zero "Plugin not found" errors from stale vskill cache after running `specweave update`
- On-demand loading successfully installs a non-core plugin within 5 seconds of prompt detection
- `--plugin <name>` flag works for all plugins listed in marketplace.json
