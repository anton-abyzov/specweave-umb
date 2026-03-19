---
increment: 0630-global-agent-teams-env
title: Enable agent teams env var in global Claude settings
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Enable agent teams env var in global Claude settings

## Overview

`enableAgentTeamsEnvVar` only writes to project-level `.claude/settings.json`. When Claude Code is launched outside a specweave project (or via VSCode extension from GUI), the global `~/.claude/settings.json` lacks the env var and agent teams tools are unavailable.

## User Stories

### US-001: Global agent teams env var on init and team (P1)
**Project**: specweave

**As a** developer using specweave
**I want** `specweave init` and `specweave team` to also set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in my global `~/.claude/settings.json`
**So that** agent teams tools (TeamCreate/SendMessage) are available in all Claude Code sessions, not just within the specweave project

**Acceptance Criteria**:
- [x] **AC-US1-01**: `specweave team` calls `enableAgentTeamsEnvVar` with `os.homedir()` in addition to the project directory
- [x] **AC-US1-02**: `specweave init` calls `enableAgentTeamsEnvVar` with `os.homedir()` in addition to the project directory
- [x] **AC-US1-03**: Global settings write is idempotent — running multiple times does not duplicate or corrupt existing settings
- [x] **AC-US1-04**: Existing global settings (permissions, plugins, etc.) are preserved when env var is added

## Out of Scope

- Removing the project-level env var write (still needed for portable project settings)
- Adding other env vars to global settings
- Windows-specific registry/setx configuration
