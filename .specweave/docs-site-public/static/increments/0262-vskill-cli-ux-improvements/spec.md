---
increment: 0262-vskill-cli-ux-improvements
title: "vskill CLI UX Improvements"
type: feature
priority: P1
status: planned
created: 2026-02-20
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: vskill CLI UX Improvements

## Overview

Improve the vskill CLI developer experience with three targeted UX changes:
1. Rename `init` command to `install` (with alias `i`) to match npm/yarn conventions
2. Add `search` as an alias for the `find` command
3. Update `submit` to accept full GitHub URLs (e.g., `https://github.com/owner/repo`) in addition to `owner/repo` shorthand
4. Update README.md and all docs to reflect these changes

## User Stories

### US-001: Rename init to install (P1)
**Project**: vskill

**As a** developer installing vskill for the first time
**I want** to run `vskill install` (or `vskill i`) to set up my environment
**So that** the command matches the familiar npm/yarn convention and feels intuitive

**Acceptance Criteria**:
- [x] **AC-US1-01**: `vskill install` works as an alias for `vskill install` (skill installation from GitHub/registry)
- [x] **AC-US1-02**: `vskill i` works as a short alias for `install`/`add`
- [x] **AC-US1-03**: `vskill init` retained as the agent detection command (separate from skill installation)
- [x] **AC-US1-04**: `install` and `add` are interchangeable for skill installation; `init` handles agent bootstrapping

---

### US-002: Add search alias for find (P1)
**Project**: vskill

**As a** developer looking for skills in the registry
**I want** to use `vskill search <query>` as an alternative to `vskill find <query>`
**So that** I can use whichever verb feels more natural

**Acceptance Criteria**:
- [x] **AC-US2-01**: `vskill search <query>` executes the same logic as `vskill find <query>`
- [x] **AC-US2-02**: `vskill find <query>` continues to work (both commands are available)
- [x] **AC-US2-03**: `vskill search` appears in `--help` output

---

### US-003: Submit accepts full GitHub URLs (P1)
**Project**: vskill

**As a** developer submitting a skill for verification
**I want** to paste a full GitHub URL like `https://github.com/owner/repo`
**So that** I don't have to manually extract the owner/repo from the URL

**Acceptance Criteria**:
- [x] **AC-US3-01**: `vskill submit https://github.com/owner/repo` extracts owner/repo and works identically to `vskill submit owner/repo`
- [x] **AC-US3-02**: `vskill submit owner/repo` continues to work (backward compatible)
- [x] **AC-US3-03**: Invalid GitHub URLs (wrong host, missing segments) are rejected with a clear error message
- [x] **AC-US3-04**: Edge cases handled: trailing slashes, `.git` suffix, URLs with extra path segments (tree/branch) are normalized to owner/repo

---

### US-004: Update documentation (P1)
**Project**: vskill

**As a** new user reading vskill documentation
**I want** the README and help text to reflect the current command names
**So that** I'm not confused by outdated references

**Acceptance Criteria**:
- [x] **AC-US4-01**: README.md Commands section shows `install` instead of `init`, includes `search`, and shows URL support for `submit`
- [x] **AC-US4-02**: Console output messages correctly reference `vskill init` for agent detection and `vskill install` for skill installation

## Functional Requirements

### FR-001: Command renaming via Commander.js
The `init` command definition in `src/index.ts` must be changed to `install` with alias `i`. Commander.js supports `.alias()` for this.

### FR-002: Search alias via Commander.js
Add a second command registration for `search` that shares the `findCommand` handler, or use Commander's `.alias()` on the `find` command.

### FR-003: GitHub URL parsing in submit
Add a URL parsing function that detects `https://github.com/owner/repo` patterns and extracts the owner/repo segments. Must handle:
- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`
- `https://github.com/owner/repo/` (trailing slash)
- `https://github.com/owner/repo/tree/main/...` (extra path segments)

## Success Criteria

- All existing tests pass
- New tests added for URL parsing in submit
- README reflects all changes
- `vskill --help` shows updated commands

## Out of Scope

- Deprecation warnings for `init` (clean break)
- Changes to any other commands (add, remove, scan, list, update, audit, blocklist)
- Changes to the underlying command logic (agent detection, lockfile, scanning)

## Dependencies

- Commander.js (already a dependency, supports aliases natively)
