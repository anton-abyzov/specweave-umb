---
id: US-001
feature: FS-265
title: Smart Project Root Detection
status: complete
priority: P1
created: 2026-02-21
project: vskill
external:
  github:
    issue: 1192
    url: https://github.com/anton-abyzov/specweave/issues/1192
---
# US-001: Smart Project Root Detection

**Feature**: [FS-265](./FEATURE.md)

developer running `vskill install` from a subdirectory
**I want** the CLI to automatically find my project root
**So that** skills are installed in the correct location (e.g., `.claude/commands/` at the project root) instead of relative to my current working directory

---

## Acceptance Criteria

- [x] **AC-US1-01**: When running `vskill install` from a subdirectory (e.g., `src/components/`), the CLI walks up the directory tree to find the project root by looking for marker files (`.git/`, `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `.specweave/`, `vskill.lock`)
- [x] **AC-US1-02**: When a project root is found, local skills install to `<project-root>/<agent.localSkillsDir>` instead of `<cwd>/<agent.localSkillsDir>`
- [x] **AC-US1-03**: When no project root is found (walking up to filesystem root), fall back to `cwd` (current behavior) and print a warning
- [x] **AC-US1-04**: A `--cwd` flag allows the user to override the auto-detected root and force install relative to cwd
- [x] **AC-US1-05**: The detected project root is printed in the install output so the user can see where files were installed

---

## Implementation

**Increment**: [0265-vskill-install-ux](../../../../../increments/0265-vskill-install-ux/spec.md)

