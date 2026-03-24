---
increment: 0644-fix-vskill-lock-in-user-projects
title: Fix vskill.lock created in user project folders
type: bug
priority: P1
status: completed
created: 2026-03-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: vskill.lock created in user project folders

## Overview

`specweave init` creates `vskill.lock` in user project folders. The migration to global lock (`~/.specweave/plugins-lock.json`) only runs from `refresh-plugins`, not from `init`.

## User Stories

### US-001: vskill.lock must not remain in user project after init (P1)
**Project**: specweave

**As a** developer running `specweave init`
**I want** no `vskill.lock` file left in my project folder
**So that** my project isn't polluted with framework-internal cache files

**Acceptance Criteria**:
- [x] **AC-US1-01**: `installAllPlugins()` calls `migrateBundledToGlobalLock(projectRoot)` after plugin installation completes
- [x] **AC-US1-02**: If migration throws, init continues without error (non-blocking)

---

### US-002: .gitignore safety net for vskill.lock (P1)
**Project**: specweave

**As a** developer whose project may have a stale `vskill.lock`
**I want** `vskill.lock` in the generated `.gitignore`
**So that** even if migration fails, the file doesn't pollute git status

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GITIGNORE_ENTRIES.specweave` array includes `vskill.lock`

## Out of Scope

- Changing `copyPluginSkillsToProject()` internals (it still uses project-local lock as working cache)
- Cleanup in `specweave doctor` (separate increment)
