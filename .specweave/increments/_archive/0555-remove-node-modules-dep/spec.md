---
increment: 0555-remove-node-modules-dep
title: Remove node_modules Specweave Dependency
type: refactor
priority: P2
status: completed
created: 2026-03-17T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Remove node_modules Specweave Dependency

## Problem Statement

The umbrella repo's `package.json` lists `specweave` as a dependency (v1.0.411) but never imports it at runtime. Hooks run from the global install via the plugin cache. Multiple hook scripts contain hardcoded `$PROJECT_ROOT/node_modules/specweave/dist/...` fallback paths that resolve to stale code when `node_modules/` exists. One path in `scheduler-startup.sh:100` has a latent bug (missing `/src/` segment). This creates an `npx` footgun where stale local code runs instead of the current global install.

## Goals

- Eliminate all hardcoded `node_modules/specweave` path references from plugin hook source
- Fix the latent path bug in `scheduler-startup.sh`
- Remove the unused `specweave` dependency from umbrella `package.json`
- Ensure all hooks resolve the specweave package via `resolve-package.sh` or JS-native candidate lists

## User Stories

### US-001: Replace hardcoded node_modules paths with dynamic resolution
**Project**: specweave
**As a** specweave maintainer
**I want** all hook scripts to resolve specweave paths dynamically
**So that** hooks never silently use stale code from a local `node_modules/` install

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `scheduler-startup.sh`, when the session-sync-executor path is resolved, then it uses `resolve-package.sh` to set `SPECWEAVE_ROOT` before the inline `node -e` block and the path includes the correct `/src/` segment (`dist/src/core/scheduler/session-sync-executor.js`)
- [x] **AC-US1-02**: Given `post-task-completion.sh`, when `SYNC_CLI` and `DETECT_CLI` fallback paths are resolved (lines 141, 185), then each uses `find_specweave_script` from `resolve-package.sh` instead of hardcoded `$PROJECT_ROOT/node_modules/specweave/...`
- [x] **AC-US1-03**: Given `ac-sync-dispatcher.sh`, when the ac-progress-sync candidate path is resolved (line 245), then it uses `find_specweave_script` from `resolve-package.sh` instead of hardcoded `$PROJECT_ROOT/node_modules/specweave/...`
- [x] **AC-US1-04**: Given `dispatcher.mjs`, when `findHooksDir()` builds its candidate list, then the `node_modules/specweave/dist/src/hooks` candidate is removed and no `node_modules/specweave` references remain in the file
- [x] **AC-US1-05**: Given `universal-auto-create-dispatcher.sh`, when handler and auto-create script paths are resolved (lines 151, 192), then each uses `find_specweave_script` from `resolve-package.sh` instead of hardcoded `$PROJECT_ROOT/node_modules/specweave/...`

---

### US-002: Remove specweave from umbrella package.json
**Project**: specweave-umb
**As a** specweave maintainer
**I want** the `specweave` entry removed from the umbrella `package.json` dependencies
**So that** `npx specweave` no longer resolves to a stale local install

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the umbrella `package.json`, when inspected, then no `specweave` entry exists in `dependencies` or `devDependencies`
- [x] **AC-US2-02**: Given a fresh clone of the umbrella repo, when `npm install` completes, then `node_modules/specweave` does not exist
- [x] **AC-US2-03**: Given the global specweave CLI is installed, when `specweave --version` is run from the umbrella root, then it resolves to the global install (not a local one)

## Out of Scope

- Adding staleness warnings or version-mismatch detection
- Auto-update mechanisms for the global install
- Source-first resolution (resolving from repo source before dist)
- Modifying `package-lock.json` manually
- Cleaning up `node_modules/` directory (handled by next `npm install`)
- Archive files (`_archive/` directory) -- legacy, not actively used
- References in `chunk-prompt.js` and `github-project-sync.ts` (these use `node_modules/specweave` as a project-local resolution candidate, which is a valid fallback pattern for non-hook contexts)

## Technical Notes

### Dependencies
- `resolve-package.sh` already exists at `plugins/specweave/hooks/lib/resolve-package.sh` with `find_specweave_script()` and `resolve_specweave_package()` helpers
- Bash hooks can `source` resolve-package.sh; ES module files use JS-native `fs.existsSync` candidates

### Constraints
- Bash hooks must source `resolve-package.sh` relative to their own location
- `dispatcher.mjs` cannot source bash -- must use JS-native resolution (already has `findHooksDir()` with candidate list)
- `scheduler-startup.sh` uses inline `node -e` -- bash resolves the path, then passes it into the JS block

### Architecture Decisions
- Bash hooks: source `resolve-package.sh`, use `$SPECWEAVE_PKG` or `find_specweave_script()` to locate files
- ES modules: remove the `node_modules` candidate from existing candidate arrays
- No new resolution mechanisms introduced -- reuse existing patterns

## Non-Functional Requirements

- **Compatibility**: All hooks must continue to work on macOS and Linux with both global npm and Volta installs
- **Performance**: No measurable impact -- `resolve-package.sh` is already sourced by other hooks in the same execution
- **Security**: No change to security surface

## Edge Cases

- **resolve-package.sh not found**: Hooks that newly source it should fail gracefully with a clear error, same as existing hooks that already source it
- **SPECWEAVE_PKG unset after resolution**: If resolution fails, the hook should skip the operation with a logged warning rather than using a broken path
- **No global install**: If specweave is not installed globally and `node_modules` is also removed, hooks will log resolution failure -- this is expected and correct behavior

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Hook breaks because resolve-package.sh returns empty | 0.2 | 6 | 1.2 | Test each hook with `SPECWEAVE_PKG` unset; verify fallback chain |
| Relative path to resolve-package.sh wrong for some hook depths | 0.3 | 5 | 1.5 | Verify `source` paths match actual directory depth for each hook file |

## Success Metrics

- Zero `node_modules/specweave` references in non-archive plugin source files (verified by grep)
- No `specweave` entry in umbrella `package.json`
- All modified hooks pass existing test suites
