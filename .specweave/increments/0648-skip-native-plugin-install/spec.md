---
increment: 0648-skip-native-plugin-install
title: Skip local skill copy when SW plugin is natively installed in Claude Code
type: bug
priority: P1
status: completed
created: 2026-03-27T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skip local skill copy when SW plugin is natively installed in Claude Code

## Overview

When `specweave init` detects Claude Code and the SW plugin is already installed natively via Claude Code's plugin system, skip the `installAllPlugins()` call that redundantly copies skills to `.claude/skills/`. Uses `claude plugin list` CLI for cross-platform detection.

## User Stories

### US-001: Skip redundant skill copy when native plugin exists (P1)
**Project**: specweave

**As a** developer using Claude Code with the SW plugin already installed
**I want** `specweave init` to detect my native plugin and skip local skill copying
**So that** init is faster and my project folder isn't cluttered with redundant skill files

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `claude plugin list` shows `sw@specweave` with status enabled, `installAllPlugins()` is skipped
- [x] **AC-US1-02**: A clear message "SW plugin already installed natively" is displayed when skipping
- [x] **AC-US1-03**: The `--force-refresh` flag bypasses the native check and runs `installAllPlugins()` anyway
- [x] **AC-US1-04**: When `claude plugin list` fails or sw@specweave is not found, falls through to `installAllPlugins()` as before

---

### US-002: Cross-platform native plugin detection (P1)
**Project**: specweave

**As a** developer on any OS (macOS, Linux, Windows)
**I want** the native plugin detection to use `claude plugin list` CLI instead of reading internal files
**So that** the check works regardless of OS or Claude Code's internal file format changes

**Acceptance Criteria**:
- [x] **AC-US2-01**: Detection uses `claude plugin list` CLI command, not file path assumptions
- [x] **AC-US2-02**: Handles CLI failures gracefully (command not found, non-zero exit, timeout)
- [x] **AC-US2-03**: Correctly distinguishes enabled vs disabled plugins in CLI output

## Out of Scope

- Refactoring existing `isPluginInstalled()` in issue-tracker/utils.ts
- Changing the `installAllPlugins()` function itself
- Non-Claude adapter paths
