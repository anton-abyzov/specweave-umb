---
increment: 0395-init-location-guard-rails
title: Init Location Guard Rails
type: feature
priority: P1
status: completed
created: 2026-03-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Feature: Init Location Guard Rails

## Overview

Add guard rails to `specweave init` to prevent creating `.specweave/` folders in wrong locations. Two new checks run early in the init flow:

1. **Umbrella sub-repo detection**: Refuse to init inside a sub-repository of an already-initialized umbrella project (walk up directory tree to find parent `.specweave/` with `config.json` that has `repository.umbrellaRepo` or a `repositories/` sibling directory).
2. **Suspicious path detection**: Refuse to init in paths that look like they are deep inside a project (e.g., `src/stories/`, `Resources/Audio/`, `node_modules/`, `.git/`, `dist/`, `build/`, `vendor/`, `__pycache__/`, etc.). Warn the user and require `--force` to override.

**Motivation**: We discovered 103 orphaned `.specweave/` folders in a scan, with 6 clearly in wrong locations. This feature prevents future proliferation.

**Tech Stack**: TypeScript, Node.js (ESM), Vitest

---

## User Stories

### US-001: Prevent Init Inside Umbrella Sub-Repos (P0)
**Project**: specweave

**As a** developer working in a multi-repo umbrella project
**I want** `specweave init` to refuse to initialize inside a sub-repository that belongs to an already-initialized umbrella
**So that** I don't create orphaned `.specweave/` folders that conflict with the umbrella's management

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `specweave init` is run inside a directory that has a parent `.specweave/config.json` with umbrella indicators (repository.umbrellaRepo set, or sibling `repositories/` dir exists), init MUST refuse and show an error message explaining the umbrella relationship
  - Priority: P0 (Critical)
  - Testable: Yes
- [x] **AC-US1-02**: The error message MUST suggest running init in the umbrella root or using `--force` to override
  - Priority: P0 (Critical)
  - Testable: Yes
- [x] **AC-US1-03**: When `--force` flag is passed, the umbrella sub-repo check MUST be bypassed with a warning
  - Priority: P1 (High)
  - Testable: Yes
- [x] **AC-US1-04**: The existing `detectNestedSpecweave()` parent-walking logic MUST be reused (no duplication)
  - Priority: P1 (High)
  - Testable: Yes (code review)

---

### US-002: Prevent Init in Suspicious Paths (P0)
**Project**: specweave

**As a** developer
**I want** `specweave init` to warn me when I'm trying to initialize in a path that looks like it's deep inside a project (e.g., `src/`, `node_modules/`, `dist/`)
**So that** I don't accidentally create orphaned `.specweave/` folders in wrong locations

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `specweave init` target directory path contains any suspicious segment (node_modules, src, dist, build, .git, vendor, __pycache__, .next, .nuxt, .output, coverage, tmp, temp, Resources/Audio, test, tests, __tests__, stories, storybook), init MUST refuse and show a warning
  - Priority: P0 (Critical)
  - Testable: Yes
- [x] **AC-US2-02**: The warning message MUST explain why the path looks suspicious and suggest the likely project root
  - Priority: P1 (High)
  - Testable: Yes
- [x] **AC-US2-03**: When `--force` flag is passed, the suspicious path check MUST be bypassed with a warning
  - Priority: P1 (High)
  - Testable: Yes
- [x] **AC-US2-04**: In CI/quick mode (`--quick`), suspicious path check MUST still block (not auto-skip) unless `--force` is also passed
  - Priority: P1 (High)
  - Testable: Yes
- [x] **AC-US2-05**: The suspicious segments list MUST be configurable/extensible (exported constant, not hardcoded inline)
  - Priority: P2 (Medium)
  - Testable: Yes (code review)

---

## Functional Requirements

### FR-001: Umbrella Sub-Repo Detection
Walk up from the target directory. For each parent that has `.specweave/config.json`:
- Check if it has `repository.umbrellaRepo` set
- Check if a `repositories/` directory exists as a sibling
- If either condition is true, this is an umbrella project and the target dir is inside it
- Block init with descriptive error unless `--force` is passed

### FR-002: Suspicious Path Segment Detection
Check the resolved absolute path of the target directory for known suspicious segments:
- Package manager: `node_modules`, `vendor`, `__pycache__`, `.venv`, `venv`
- Build output: `dist`, `build`, `.next`, `.nuxt`, `.output`, `out`, `coverage`
- Source dirs: `src`, `lib` (only when 2+ levels deep from a project root indicator)
- Test dirs: `test`, `tests`, `__tests__`, `stories`, `storybook`
- VCS internals: `.git`, `.svn`, `.hg`
- Temp: `tmp`, `temp`
- Platform-specific: `Resources/Audio`, `Assets/Plugins`

### FR-003: Guard Rail Ordering
Both checks run BEFORE any file creation or user prompts (after language selection, before directory structure creation). Order: umbrella check first, then suspicious path check.

## Success Criteria

- Zero false positives on common project roots (home dir already guarded separately)
- All 6 known bad locations from the audit would be caught
- `--force` provides escape hatch for legitimate edge cases
- No regression in existing init flow for normal usage

## Out of Scope

- Retroactive cleanup of existing orphaned `.specweave/` folders (separate tooling)
- Downward scanning (checking if target dir contains sub-repos with `.specweave/`)
- Changes to the `detectNestedSpecweave()` upward-walk for parent detection (already works)

## Dependencies

- Existing `detectNestedSpecweave()` in `src/cli/helpers/init/path-utils.ts`
- Existing `--force` flag in `InitOptions` type
- Existing home directory guard in `init.ts`
