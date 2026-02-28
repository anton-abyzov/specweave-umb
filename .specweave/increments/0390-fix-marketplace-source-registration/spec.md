---
increment: 0390-fix-marketplace-source-registration
title: "Fix marketplace temp dir registered as source"
type: bugfix
priority: P1
status: planned
created: 2026-02-28
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Bugfix: Fix marketplace temp dir registered as source

## Overview

When `vskill install owner/repo` installs from a Claude Code plugin marketplace, `installMarketplaceRepo()` clones the repo to a temp directory and calls `registerMarketplace(tmpDir)`. This registers the ephemeral temp path as the marketplace source with Claude Code. After the temp dir is cleaned up, the marketplace reference becomes stale -- `claude plugin list`, marketplace updates, and plugin management silently fail until the user manually runs `claude plugin marketplace remove`.

**Root cause**: `registerMarketplace()` is called with `tmpDir` (a temporary local path) instead of the GitHub `owner/repo` identifier. The `claude plugin marketplace add` command accepts paths, URLs, and GitHub repo shorthand (`owner/repo`), so passing the GitHub source directly avoids the stale-path problem entirely.

**Fix scope**: Change the single `registerMarketplace(tmpDir)` call in `installMarketplaceRepo()` to `registerMarketplace(`${owner}/${repo}`)`. Update `registerMarketplace()` JSDoc to clarify it accepts any valid marketplace source. Update tests.

## User Stories

### US-001: Persistent marketplace registration after plugin install (P1)
**Project**: vskill

**As a** developer installing plugins from a marketplace repo
**I want** the marketplace to be registered using its GitHub source identifier
**So that** Claude Code can resolve the marketplace for future operations (list, update, uninstall) without relying on a temp directory that gets deleted

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `installMarketplaceRepo()` calls `registerMarketplace()` with `${owner}/${repo}` (GitHub shorthand) instead of `tmpDir`
- [ ] **AC-US1-02**: `registerMarketplace()` JSDoc `@param` is updated from "Absolute path to the repo root" to document it accepts any valid marketplace source (path, URL, or GitHub `owner/repo`)
- [ ] **AC-US1-03**: The shallow clone to tmpDir is still performed (needed for fallback extraction), but tmpDir is no longer passed to `registerMarketplace()`
- [ ] **AC-US1-04**: `tryNativeClaudeInstall()` continues to use `resolve(basePath)` (local persistent path) -- no change needed there

### US-002: Test coverage for GitHub source registration (P1)
**Project**: vskill

**As a** maintainer
**I want** tests to verify the correct marketplace source is registered
**So that** regressions are caught before release

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `claude-cli.test.ts` tests for `registerMarketplace()` include a case with GitHub `owner/repo` format input
- [ ] **AC-US2-02**: `add.test.ts` marketplace integration tests assert that `registerMarketplace` is called with `owner/repo` (not a temp dir path) when installing from a GitHub marketplace repo
- [ ] **AC-US2-03**: Existing `registerMarketplace` tests for local paths and paths-with-spaces continue to pass (no regression)

## Functional Requirements

### FR-001: Use GitHub source for marketplace registration in installMarketplaceRepo
In `src/commands/add.ts`, line 256: change `registerMarketplace(tmpDir)` to `registerMarketplace(`${owner}/${repo}`)`. The `owner` and `repo` parameters are already available as function arguments.

### FR-002: Update registerMarketplace JSDoc
In `src/utils/claude-cli.ts`, update the `@param` documentation for `registerMarketplace()` to reflect that the parameter accepts any valid Claude Code marketplace source (absolute path, URL, or GitHub `owner/repo` shorthand), not just a local path.

## Success Criteria

- After `vskill install owner/repo`, `claude plugin marketplace list` shows the GitHub `owner/repo` source (not a `/tmp/vskill-marketplace-*` path)
- All existing tests pass with no regressions
- New tests cover the GitHub shorthand registration path

## Out of Scope

- Migration or cleanup of previously stale marketplace registrations (users fix with `claude plugin marketplace remove`)
- Changes to `tryNativeClaudeInstall()` which correctly uses `resolve(basePath)` (persistent local path)
- Changes to `claude plugin marketplace add` CLI behavior itself

## Dependencies

- Claude Code CLI must support `claude plugin marketplace add owner/repo` (confirmed: accepts paths, URLs, and GitHub repos)
