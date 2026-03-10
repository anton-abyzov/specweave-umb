---
id: US-001
feature: FS-456
title: "Fix safeProjectRoot to resolve actual project root"
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** CLI user running `vskill add` from a subdirectory or parent directory."
project: vskill
---

# US-001: Fix safeProjectRoot to resolve actual project root

**Feature**: [FS-456](./FEATURE.md)

**As a** CLI user running `vskill add` from a subdirectory or parent directory
**I want** the CLI to find my actual project root using project markers
**So that** agent dot-folders are created in the correct project, not in whatever directory I happen to be in

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a directory tree where `findProjectRoot()` returns a valid project root, when `safeProjectRoot()` is called without `--cwd`, then it returns the `findProjectRoot()` result
- [x] **AC-US1-02**: Given `findProjectRoot()` returns the HOME directory (HOME has a `.git` or `package.json`), when `safeProjectRoot()` is called without `--cwd`, then it silently falls back to `process.cwd()`
- [x] **AC-US1-03**: Given `findProjectRoot()` returns `null` (no markers found), when `safeProjectRoot()` is called, then it silently falls back to `process.cwd()`
- [x] **AC-US1-04**: Given `--cwd` is set, when `safeProjectRoot()` is called, then it returns `process.cwd()` directly without HOME guard or `findProjectRoot()` lookup

---

## Implementation

**Increment**: [0456-prevent-unwanted-agent-dotfolders](../../../../../increments/0456-prevent-unwanted-agent-dotfolders/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Fix safeProjectRoot() in add.ts and add findProjectRoot import
