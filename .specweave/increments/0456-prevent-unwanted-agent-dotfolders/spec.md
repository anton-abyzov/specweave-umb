---
increment: 0456-prevent-unwanted-agent-dotfolders
title: "Prevent unwanted agent dot-folder creation"
status: active
priority: P1
type: bugfix
created: 2026-03-09
---

# Prevent Unwanted Agent Dot-Folders in Wrong Location

## Problem Statement

Running `vskill add` from a parent or umbrella directory creates agent dot-folders (`.aider/`, `.kiro/`, `.pi/`, `.codex/`, `.cursor/`, `.agent/`, `.windsurf/`, etc.) in the wrong location. The root cause is twofold: `safeProjectRoot()` in `src/commands/add.ts` is a stub that always returns `process.cwd()` instead of walking up to find the actual project root, and the installer in `canonical.ts` lacks boundary guards to prevent directory creation above the project root or at HOME.

## Goals

- Fix `safeProjectRoot()` to use the existing `findProjectRoot()` utility with HOME guard and `--cwd` escape hatch
- Add path traversal and HOME directory boundary guards in the canonical installer
- Update and expand tests to cover the corrected behavior

## User Stories

### US-001: Fix safeProjectRoot to resolve actual project root
**Project**: vskill

**As a** CLI user running `vskill add` from a subdirectory or parent directory
**I want** the CLI to find my actual project root using project markers
**So that** agent dot-folders are created in the correct project, not in whatever directory I happen to be in

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a directory tree where `findProjectRoot()` returns a valid project root, when `safeProjectRoot()` is called without `--cwd`, then it returns the `findProjectRoot()` result
- [x] **AC-US1-02**: Given `findProjectRoot()` returns the HOME directory (HOME has a `.git` or `package.json`), when `safeProjectRoot()` is called without `--cwd`, then it silently falls back to `process.cwd()`
- [x] **AC-US1-03**: Given `findProjectRoot()` returns `null` (no markers found), when `safeProjectRoot()` is called, then it silently falls back to `process.cwd()`
- [x] **AC-US1-04**: Given `--cwd` is set, when `safeProjectRoot()` is called, then it returns `process.cwd()` directly without HOME guard or `findProjectRoot()` lookup

---

### US-002: Add boundary guards in canonical installer
**Project**: vskill

**As a** CLI maintainer
**I want** the installer to reject path traversal in agent definitions and HOME directory installs
**So that** malformed registry data or misconfigured roots cannot pollute the filesystem outside the project

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given an agent definition with `localSkillsDir` containing `../` that would resolve above `projectRoot`, when `resolveAgentSkillsDir()` is called for a non-global install, then it throws an error
- [x] **AC-US2-02**: Given `base` equals `os.homedir()` exactly, when `ensureCanonicalDir()` is called with `global: false`, then it throws an error with a clear message
- [x] **AC-US2-03**: Given `base` is a subdirectory of HOME (not HOME itself), when `ensureCanonicalDir()` is called with `global: false`, then it creates the directory normally

---

### US-003: Update and expand test coverage
**Project**: vskill

**As a** developer maintaining the vskill CLI
**I want** tests that verify the corrected `safeProjectRoot()` and new boundary guards
**So that** regressions are caught immediately

**Acceptance Criteria**:
- [x] **AC-US3-01**: TC-012 in `add.test.ts` is updated to assert `safeProjectRoot()` calls `findProjectRoot()` instead of asserting the old stub behavior
- [x] **AC-US3-02**: New tests in `add.test.ts` cover: findProjectRoot integration, null fallback to cwd, HOME guard fallback, and `--cwd` bypass
- [x] **AC-US3-03**: New tests in `canonical.test.ts` cover: `resolveAgentSkillsDir` rejects `../` traversal, `ensureCanonicalDir` throws on HOME for non-global, and `ensureCanonicalDir` allows subdirectories of HOME

## Out of Scope

- Changing `findProjectRoot()` logic or its marker list in `project-root.ts`
- Adding new CLI flags beyond the existing `--cwd`
- Modifying global install paths or `lockfileRoot()` behavior
- Warning/error UX beyond the throw in `ensureCanonicalDir` (safeProjectRoot is intentionally silent)

## Technical Notes

### Dependencies
- `findProjectRoot()` from `src/utils/project-root.ts` (existing, no changes needed)
- `os.homedir()` from Node.js standard library

### Constraints
- ESM with `--moduleResolution nodenext` -- all imports must have `.js` extensions
- `safeProjectRoot()` must remain a silent fallback (no throws, no console output)
- `ensureCanonicalDir()` and `resolveAgentSkillsDir()` are the hard boundary -- they throw

### Architecture Decisions
- Two-layer defense: `safeProjectRoot()` is the soft first layer (best-effort root resolution with silent fallback), `canonical.ts` guards are the hard second layer (throws on violations)
- `--cwd` is a trust override -- no guards applied when explicitly set
- HOME guard on `findProjectRoot` result only triggers when HOME is returned as a found root (has markers), not when `findProjectRoot` returns null and cwd happens to be HOME
- `ensureCanonicalDir` HOME check uses exact `===` match against `os.homedir()`

### Files Modified
- `src/commands/add.ts` -- fix `safeProjectRoot()` (~line 845-847)
- `src/installer/canonical.ts` -- add guards to `resolveAgentSkillsDir()` and `ensureCanonicalDir()`
- `src/commands/add.test.ts` -- update TC-012, add new test cases
- `src/installer/canonical.test.ts` -- add boundary guard tests

## Success Metrics

- All existing tests pass after changes
- New tests cover all acceptance criteria scenarios
- Running `vskill add` from an umbrella directory no longer creates dot-folders at the umbrella root when a child project root exists
