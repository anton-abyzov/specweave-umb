---
increment: 0428-plugin-install-reliability
title: 'Plugin install reliability: temp dirs, interactive selection, error messages'
type: bug
priority: P2
status: completed
created: 2026-03-05T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Plugin Install Reliability

## Problem Statement

`vskill install` fails with confusing errors when installing marketplace plugins. Three root causes have been identified:

1. **Stale temp directory registration** -- `registerMarketplace()` in `src/utils/claude-cli.ts` passes paths that may originate from `os.tmpdir()`. When the temp directory is cleaned up, the marketplace registration becomes stale and all subsequent plugin installs fail silently.

2. **Missing interactive selection** -- Single-plugin marketplaces proceed without showing the user what will be installed. `installPluginDir()` begins scanning immediately with no pre-install overview showing plugin name and source.

3. **Silent failures and confusing errors** -- `registerMarketplace()` returns a bare `boolean` with no stderr capture. Plugin-not-found errors do not list available alternatives. There is no structured validation function for diagnosing marketplace issues.

## Goals

- Eliminate stale temp directory paths from marketplace registration
- Give users clear visibility into what gets installed before it happens
- Surface actionable diagnostics when install fails

## User Stories

### US-001: Reliable marketplace registration
**Project**: vskill
**As a** plugin developer
**I want** marketplace registration to never use temp directory paths
**So that** my plugins don't break after install

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a source path matching the `os.tmpdir()` prefix, when `registerMarketplace()` is called, then the temp path is detected and skipped with a clear warning message logged to stderr
- [x] **AC-US1-02**: Given any call to `registerMarketplace()`, when the underlying `claude plugin marketplace add` command runs, then stderr is captured and the return type is `{ success: boolean; stderr?: string }` instead of bare `boolean`
- [x] **AC-US1-03**: Given a failed registration, when `registerMarketplace()` detects the failure, then it retries once after deregistering the stale entry via `claude plugin marketplace remove`, returning success only if the retry succeeds

---

### US-002: Interactive plugin selection
**Project**: vskill
**As a** plugin user
**I want** to see what will be installed and confirm before proceeding
**So that** I'm never surprised by what gets installed

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a single-plugin marketplace in TTY mode without `--yes`, when the user runs `vskill install`, then plugin name, version, and description are displayed and the user is prompted for confirmation before proceeding
- [x] **AC-US2-02**: Given the `--yes` flag is passed, when `vskill install` runs in any environment (TTY or CI), then confirmation is bypassed and install proceeds automatically
- [x] **AC-US2-03**: Given a call to `installPluginDir()`, when scanning begins, then a pre-install overview line showing the plugin name and source path/URL is printed before the "Collecting plugin files" message

---

### US-003: Clear error messages
**Project**: vskill
**As a** plugin user
**I want** actionable error messages when install fails
**So that** I know what went wrong and how to fix it

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a plugin name that does not exist in marketplace.json, when the user runs `vskill install`, then the error message lists all available plugin names from marketplace.json
- [x] **AC-US3-02**: Given a marketplace registration failure, when the error is displayed to the user, then captured stderr from the `claude` CLI is shown in dim text below the primary error message
- [x] **AC-US3-03**: Given any marketplace validation call, when `validateMarketplace()` is invoked, then it returns a structured object with `{ valid: boolean; errors: Array<{ code: string; message: string }> }` covering specific error reasons (missing manifest, empty plugin list, invalid JSON, unreachable source)

## Out of Scope

- Refactoring the extraction-based fallback install path
- Changes to the Claude Code CLI itself (`claude plugin` commands)
- Multi-marketplace conflict resolution
- Offline/cached marketplace support

## Technical Notes

### Files to modify
- `src/utils/claude-cli.ts` -- `registerMarketplace()` signature change (US-001)
- `src/commands/add.ts` -- `installMarketplaceRepo()` for interactive selection (US-002), `installPluginDir()` for pre-install overview (US-002), plugin-not-found error handling (US-003)
- `src/marketplace/` -- new `validateMarketplace()` function (US-003)

### Constraints
- Must remain backward-compatible: callers of `registerMarketplace()` need updating for the new return type
- `--yes` flag already exists; US-002 adds confirmation behavior when it is absent
- TTY detection via existing `isTTY()` utility in `src/utils/prompts.ts`

### Dependencies
- `os.tmpdir()` from Node.js `os` module for temp path detection
- Existing `createPrompter()` for interactive confirmation prompts

## Success Metrics

- Zero stale-temp-dir registration failures in marketplace installs
- All install error messages include at least one actionable suggestion
- Single-plugin marketplace installs show confirmation prompt in TTY mode
