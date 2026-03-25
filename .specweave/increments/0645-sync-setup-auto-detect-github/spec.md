---
increment: 0645-sync-setup-auto-detect-github
title: Auto-detect GitHub owner/repo in sync-setup
type: bug
priority: P1
status: completed
created: 2026-03-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: Auto-detect GitHub owner/repo in sync-setup wizard

## Overview

After authenticating with GitHub in `specweave sync-setup`, the repo mapping wizard asks 3 redundant questions (map? owner? repo?) when the answers are already available from the sync profile config and git remotes.

## User Stories

### US-001: Auto-detect GitHub owner/repo from context (P1)
**Project**: specweave

**As a** developer mapping workspace repos during sync-setup
**I want** the wizard to auto-detect GitHub owner and repo name
**So that** I don't re-enter information that's already known

**Acceptance Criteria**:
- [x] **AC-US1-01**: When git remote points to GitHub, wizard auto-detects owner/repo and shows single confirmation instead of 3 prompts
- [x] **AC-US1-02**: When no git remote, wizard uses sync profile owner + repo name as defaults
- [x] **AC-US1-03**: When user rejects auto-detected mapping, wizard falls back to manual entry
- [x] **AC-US1-04**: JIRA/ADO providers are unaffected — keep current flow

## Out of Scope

- Changing `setupIssueTracker()` return type (read from config instead)
- Auto-detecting JIRA/ADO project mappings
