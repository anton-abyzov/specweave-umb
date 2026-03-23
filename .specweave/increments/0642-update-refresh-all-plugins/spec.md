---
increment: 0642-update-refresh-all-plugins
title: Fix specweave update to refresh all plugin skills
type: bug
priority: P1
status: completed
created: 2026-03-23T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: specweave update must refresh all plugin skills

## Overview

After `specweave update`, slash commands like `/help` show Claude Code's built-in commands instead of SpecWeave's skills. This is because `refreshPluginsCommand()` only installs the core `sw` plugin by default, leaving non-core skills stale or missing. Running `specweave init .` fixes it because `installAllPlugins()` copies ALL skill directories.

## User Stories

### US-001: All plugin skills refreshed on update (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** `specweave update` to refresh all plugin skills (not just core `sw`)
**So that** slash commands like `/help` work correctly after updating

**Acceptance Criteria**:
- [x] **AC-US1-01**: `specweave update` (without `--all` flag) refreshes all marketplace plugins, not just the core `sw` plugin
- [x] **AC-US1-02**: Existing `--all` flag continues to work (backward compat, now a no-op)
- [x] **AC-US1-03**: `--no-plugins` flag still skips plugin refresh entirely

## Out of Scope

- Changes to `specweave refresh-plugins` standalone behavior (core-only default is fine there)
- Changes to `specweave init` flow
