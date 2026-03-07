---
increment: 0433-marketplace-unregistered-plugin-discovery
title: "Marketplace Unregistered Plugin Discovery"
type: feature
priority: P1
status: active
created: 2026-03-05
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Marketplace Unregistered Plugin Discovery

## Problem Statement

When a repo author adds a new plugin directory (e.g., `plugins/marketing/`) to their GitHub repo but has not updated `.claude-plugin/marketplace.json`, users running `npx vskill i owner/repo` cannot see or install the new plugin. The marketplace manifest is the only source of truth for the plugin picker, so filesystem-only plugins are invisible. This creates a gap where authors ship code but consumers cannot access it until the manifest catches up.

## Goals

- Auto-detect plugin directories not listed in marketplace.json via GitHub Contents API
- Surface unregistered plugins in the interactive picker with clear visual distinction
- Gate unregistered plugin installation behind `--force` to prevent accidental use of unscanned plugins
- Offer repo re-submission for platform scanning when unregistered plugins are detected
- Maintain best-effort semantics: discovery failures never break the existing install flow

## User Stories

### US-001: Discover Unregistered Plugin Directories
**Project**: vskill
**As a** plugin consumer
**I want** the CLI to detect plugin directories not listed in marketplace.json
**So that** I am aware of newly added plugins even before the manifest is updated

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a marketplace repo with `plugins/` containing directories `frontend`, `backend`, and `marketing`, and marketplace.json listing only `frontend` and `backend`, when `discoverUnregisteredPlugins(owner, repo, manifestContent)` is called, then it returns `["marketing"]`
- [x] **AC-US1-02**: Given the GitHub Contents API returns an error or network failure, when `discoverUnregisteredPlugins()` is called, then it returns `[]` without throwing
- [x] **AC-US1-03**: Given the `plugins/` directory contains both files and directories, when discovery runs, then only directory entries are considered (files are ignored)
- [x] **AC-US1-04**: Given all plugin directories are already listed in marketplace.json, when discovery runs, then it returns `[]`

---

### US-002: Display Unregistered Plugins in Picker UI
**Project**: vskill
**As a** plugin consumer
**I want** unregistered plugins to appear in the checkbox picker with a visual indicator
**So that** I can distinguish them from verified marketplace plugins

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given 12 registered and 1 unregistered plugin, when the interactive picker is shown, then unregistered plugins appear at the bottom of the list with a yellow `(new -- not in marketplace.json)` label
- [x] **AC-US2-02**: Given unregistered plugins exist, when the picker header is displayed, then it shows `Marketplace: <name> -- 12 registered, 1 unregistered` with the unregistered count in yellow
- [x] **AC-US2-03**: Given unregistered plugins are present in the picker, when displayed, then they are unchecked by default

---

### US-003: Gate Unregistered Plugin Installation Behind --force
**Project**: vskill
**As a** plugin consumer
**I want** unregistered plugin selection without `--force` to be blocked with a warning
**So that** I do not accidentally install plugins that have not been platform-scanned

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a user selects an unregistered plugin in the picker without `--force`, when confirming the selection, then a warning is printed explaining the plugin is not in marketplace.json, only registered plugins proceed to install, and the user is offered repo re-submission
- [x] **AC-US3-02**: Given a user selects an unregistered plugin with `--force`, when confirming, then the plugin is installed via the existing extraction pipeline, the re-submission prompt is suppressed, and the lockfile entry uses `tier: "UNSCANNED"`
- [x] **AC-US3-03**: Given `--plugin <name>` targets an unregistered plugin without `--force`, when the command runs, then it prints a warning and does not install (explicit naming does not bypass the gate)
- [x] **AC-US3-04**: Given `--force` is used for an unregistered plugin, when the extraction pipeline runs, then the local Tier-1 scan still executes (only the marketplace registration requirement is bypassed)

---

### US-004: Non-TTY and Auto-Select Mode Handling
**Project**: vskill
**As a** plugin consumer using CI or scripted installs
**I want** unregistered plugins to be listed but skipped in non-interactive modes
**So that** automated pipelines are not broken by unscanned plugins

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given non-TTY mode with unregistered plugins detected, when the plugin list is printed, then unregistered plugins are listed with an `(unregistered)` label and a note to use `--force` to include them
- [x] **AC-US4-02**: Given `--yes` or `--all` flag with unregistered plugins detected, when auto-selection runs, then only registered plugins are auto-selected and unregistered plugins are skipped with a message mentioning `--force`
- [x] **AC-US4-03**: Given `--yes --force` together with unregistered plugins, when auto-selection runs, then all plugins (registered and unregistered) are installed

---

### US-005: Repo Re-Submission for Platform Scanning
**Project**: vskill
**As a** plugin consumer who encounters unregistered plugins
**I want** the option to trigger a repo re-submission for platform scanning
**So that** the repo author's new plugins get scanned and added to the verified marketplace

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a user declines `--force` install of an unregistered plugin, when the re-submission prompt appears and the user accepts, then `submitSkill({ repoUrl })` is called and a tracking URL or manual fallback message is printed
- [x] **AC-US5-02**: Given the `submitSkill()` API call fails, when re-submission is attempted, then an error message is printed with the manual submission URL as fallback, and the install flow continues for registered plugins
- [x] **AC-US5-03**: Given `--force` is used, when unregistered plugins are installed, then the re-submission prompt is not shown

## Out of Scope

- Automatic marketplace.json updates or PRs to the repo author's repository
- Platform-side (vskill-platform) changes for handling re-submissions differently
- New CLI flags beyond reusing existing `--force`
- Scanning unregistered plugins at a deeper level than existing Tier-1
- Recursive subdirectory scanning within `plugins/`
- Handling repos where marketplace.json is missing or empty (existing flow covers this)

## Technical Notes

### Dependencies
- GitHub Contents API (`GET /repos/{owner}/{repo}/contents/plugins/`) for directory listing
- Existing `submitSkill()` from `src/api/client.ts` for re-submission
- Existing `installRepoPlugin()` from `src/commands/add.ts` for extraction pipeline
- Existing lockfile infrastructure for `tier: "UNSCANNED"` entries

### Constraints
- Discovery is a single API call with no retry/fallback (best-effort)
- The `plugins/` directory convention is standard for all vskill marketplace repos
- Plugin name in marketplace.json always matches directory name under `plugins/`
- `UNSCANNED` lockfile tier is new but the `tier` field is already a free-form string

### Architecture Decisions
- `discoverUnregisteredPlugins()` lives in `src/marketplace/marketplace.ts` alongside existing manifest parsing functions
- `triggerResubmission()` helper wraps `submitSkill()` with UX messaging
- `installRepoPlugin()` gains an optional `overrideSource` parameter for unregistered plugin paths
- No new command or subcommand; changes integrate into the existing `install` flow in `src/commands/add.ts`

## Success Metrics

- Unregistered plugins are correctly detected in 100% of marketplace repos where filesystem and manifest diverge
- Zero regressions in existing install flow when no unregistered plugins exist
- Discovery API failures produce no user-visible errors or install interruptions
