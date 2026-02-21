---
id: US-001
feature: FS-219
title: Single-to-Umbrella Migration Command
status: complete
priority: P0
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1194
    url: https://github.com/anton-abyzov/specweave/issues/1194
---
# US-001: Single-to-Umbrella Migration Command

**Feature**: [FS-219](./FEATURE.md)

developer with an existing single-repo SpecWeave project
**I want to** run a CLI command that creates a sibling umbrella workspace and moves SpecWeave-managed files to it
**So that** I can organize multiple repositories without disrupting my existing project

---

## Acceptance Criteria

- [x] **AC-US1-01**: `specweave migrate-to-umbrella` detects the current project as a single-repo SpecWeave project (has `.specweave/config.json`, no `umbrella.enabled`)
- [x] **AC-US1-02**: Running without `--execute` shows a dry-run plan listing all operations (create directories, move files, update config) without modifying anything
- [x] **AC-US1-03**: Running with `--execute` creates the umbrella as a sibling folder next to the current project
- [x] **AC-US1-04**: The current project folder stays completely untouched — no rename, no git remote changes, folder name preserved
- [x] **AC-US1-05**: `.specweave/` directory is moved to the umbrella root with all contents preserved
- [x] **AC-US1-06**: `CLAUDE.md` and `AGENTS.md` are moved to the umbrella root (if they exist)
- [x] **AC-US1-07**: `docs-site/` is moved to the umbrella root (if it exists)
- [x] **AC-US1-08**: `config.json` at umbrella level has `umbrella.enabled = true` and the original project registered as first `childRepos[]` entry with relative path (e.g., `../specweave`)
- [x] **AC-US1-09**: The command suggests an umbrella folder name (e.g., `{project}-umb`) and lets user override
- [x] **AC-US1-10**: Migration refuses to proceed if the working directory has uncommitted changes
- [x] **AC-US1-11**: A backup of the original `.specweave/` is created before any changes

---

## Implementation

**Increment**: [0219-multi-repo-migrate](../../../../../increments/0219-multi-repo-migrate/spec.md)

