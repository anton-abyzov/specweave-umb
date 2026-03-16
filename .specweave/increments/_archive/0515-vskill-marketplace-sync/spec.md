---
increment: 0515-vskill-marketplace-sync
title: vskill marketplace sync command
type: feature
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill marketplace sync command

## Problem Statement

When new plugin directories are added to `plugins/` in the vskill repo, `.claude-plugin/marketplace.json` drifts out of sync. The `/plugin Discover` tab in Claude Code only renders plugins listed in `marketplace.json`, making new plugins invisible until the registry is manually edited. Observed: `google-workspace`, `marketing`, `productivity` were in `plugins/` but missing from `marketplace.json` -- appearing as "new -- not in marketplace.json" during `npx vskill i`.

## Goals

- Automate synchronization between `plugins/*/` directories and `.claude-plugin/marketplace.json`
- Detect new plugins, update drifted metadata, and report changes clearly
- Support safe preview via `--dry-run` before committing changes
- Register as `vskill marketplace sync` with `mp` alias for ergonomics

## User Stories

### US-001: Auto-add new plugins to marketplace.json (P1)
**Project**: vskill

**As a** vskill plugin author
**I want** to run `vskill marketplace sync` to automatically add my new plugin to marketplace.json
**So that** it appears in Claude Code's `/plugin Discover` tab without manual file editing

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a plugin directory `plugins/foo/` with a valid `.claude-plugin/plugin.json` that is not listed in marketplace.json, when the user runs `vskill marketplace sync`, then a new entry is added to the `plugins` array in marketplace.json with `name`, `source` (`./plugins/foo`), `version`, and `description` from plugin.json
- [x] **AC-US1-02**: Given a plugin directory `plugins/bar/` with no `.claude-plugin/plugin.json`, when the user runs `vskill marketplace sync`, then the directory is skipped and a warning is printed to stderr naming the skipped directory
- [x] **AC-US1-03**: Given marketplace.json does not exist at `.claude-plugin/marketplace.json`, when the user runs `vskill marketplace sync`, then the command prints an error message and exits with code 1

---

### US-002: Update drifted plugin metadata (P1)
**Project**: vskill

**As a** vskill plugin author
**I want** marketplace sync to update existing entries when version or description has changed in plugin.json
**So that** marketplace.json stays accurate without manual edits

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given plugin `mobile` exists in marketplace.json with version `2.3.0` and its `.claude-plugin/plugin.json` now has version `2.4.0`, when the user runs `vskill marketplace sync`, then the marketplace.json entry for `mobile` is updated to version `2.4.0`
- [x] **AC-US2-02**: Given plugin `skills` exists in marketplace.json with description `"old desc"` and its `.claude-plugin/plugin.json` now has description `"new desc"`, when the user runs `vskill marketplace sync`, then the marketplace.json entry for `skills` is updated to `"new desc"`
- [x] **AC-US2-03**: Given a plugin exists in marketplace.json and its `.claude-plugin/plugin.json` has identical name, version, and description, when the user runs `vskill marketplace sync`, then the entry is left unchanged and reported as unchanged in the output

---

### US-003: Dry-run preview mode (P1)
**Project**: vskill

**As a** developer
**I want** a `--dry-run` flag to preview what would change without actually writing the file
**So that** I can verify before committing

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given there are pending additions and updates, when the user runs `vskill marketplace sync --dry-run`, then the summary table is printed but marketplace.json is not modified on disk
- [x] **AC-US3-02**: Given `--dry-run` is active, when the command completes, then the output includes a line indicating no files were written (e.g., "dry run -- no changes written")

---

### US-004: Informative summary output and alias (P1)
**Project**: vskill

**As a** developer
**I want** informative output showing added/updated/unchanged counts and a table per plugin
**So that** I know exactly what changed

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the sync finds 2 added, 1 updated, and 2 unchanged plugins, when the command completes, then it prints a summary table with columns for status indicator (`+` added, `~` updated, ` ` unchanged) and plugin name, one row per plugin
- [x] **AC-US4-02**: Given there are skipped directories, when the command completes, then each skipped directory is reported with a warning line before the summary table
- [x] **AC-US4-03**: Given the user runs `vskill mp sync`, when the command executes, then it behaves identically to `vskill marketplace sync`
- [x] **AC-US4-04**: Given all plugins are already in sync, when the command completes, then it prints the summary table showing all entries as unchanged and exits with code 0

## Functional Requirements

### FR-001: Plugin directory scanning
The command scans all immediate subdirectories of `plugins/` relative to the repo root. For each subdirectory, it attempts to read `.claude-plugin/plugin.json`. Directories without this file are collected as "skipped" and reported with a warning.

### FR-002: Marketplace entry matching
Plugins are matched by `name` field from plugin.json against existing entries in marketplace.json. The `source` field is always `./plugins/<dirname>`.

### FR-003: Field comparison
The sync compares `version` and `description` fields between plugin.json and the marketplace entry. If either field differs, the entry is marked as "updated" and the marketplace entry is patched.

### FR-004: JSON formatting
marketplace.json is written with 2-space indentation and a trailing newline, matching existing formatting conventions.

### FR-005: Command registration
The command is registered in Commander.js as `marketplace <subcommand>` with alias `mp`. The `sync` subcommand is the first (and initially only) subcommand. This structure allows future marketplace subcommands (e.g., `marketplace validate`, `marketplace list`).

## Out of Scope

- Removing plugins from marketplace.json that no longer have directories (no orphan cleanup)
- Syncing fields other than `name`, `version`, `description`, and `source` (e.g., `category`, `author`)
- Remote/GitHub-based sync (this is local filesystem only)
- Auto-generating plugin.json from directory contents
- Updating the top-level `metadata.version` in marketplace.json

## Non-Functional Requirements

- **Testing**: All new code has unit tests with Vitest; TDD cycle (red-green-refactor)
- **Compatibility**: ESM imports with `.js` extensions per vskill conventions
- **Code style**: Follows existing vskill patterns (Commander.js, console output, vi.hoisted mocking)

## Edge Cases

- **Empty plugins/ directory**: Command runs successfully, prints "0 plugins found", exits 0
- **Malformed plugin.json**: Skip directory with warning (treat as missing plugin.json)
- **Plugin.json missing `name` field**: Skip directory with warning
- **marketplace.json is malformed JSON**: Print error and exit 1
- **Plugin directory is a file, not a directory**: Skip silently (only process directories)
- **Duplicate plugin names across directories**: First encountered wins; warn about the duplicate

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| marketplace.json format changes upstream | 0.1 | 3 | 0.3 | Use existing MarketplaceManifest types |
| Plugin.json schema varies across plugins | 0.2 | 2 | 0.4 | Validate required fields, skip on missing |

## Technical Notes

- **Existing code**: `src/marketplace/marketplace.ts` has types (`MarketplaceManifest`, `MarketplacePlugin`) and parsers that should be reused
- **Plugin.json location**: `.claude-plugin/plugin.json` inside each plugin directory (confirmed by codebase inspection)
- **Commander.js pattern**: Use `.command("marketplace").alias("mp")` with subcommand `.command("sync")` following existing patterns in `src/index.ts`
- **New files**: `src/commands/marketplace-sync.ts` (command logic), `src/commands/marketplace-sync.test.ts` (tests)
- **File I/O**: Use `node:fs/promises` for reading plugin.json files and writing marketplace.json

## Success Metrics

- Running `vskill marketplace sync` after adding a new plugin directory results in marketplace.json being updated in under 1 second
- Zero manual edits to marketplace.json needed after running sync
- All new code covered by unit tests at 90%+ coverage
