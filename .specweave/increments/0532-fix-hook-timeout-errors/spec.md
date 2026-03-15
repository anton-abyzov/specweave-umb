---
increment: 0532-fix-hook-timeout-errors
title: Fix PostToolUse/PreToolUse Edit Hook Errors
type: bug
priority: P2
status: completed
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix PostToolUse/PreToolUse Edit Hook Errors

## Overview

Every Edit/Write to `.specweave/increments/` files produces "PreToolUse:Edit hook error" and "PostToolUse:Edit hook error" warnings. While edits succeed (hooks are non-blocking by design), the errors are noisy, indicate wasted computation, and degrade the developer experience.

## Root Causes

1. **`pre-tool-use.sh` uses `set -e`** — violates the "CRITICAL: Never exit on error" principle, crashes on jq/stdin failures
2. **`post-tool-use.sh` exceeds 5s timeout** — runs `task-ac-sync-guard.sh` synchronously (awk/sed/jq) within fail-fast-wrapper's default 5s timeout
3. **Triple hook chains** — 3 plugins (SpecWeave, Security-Guidance, Hookify) all register Edit hooks

## User Stories

### US-001: Eliminate PreToolUse Edit Hook Errors (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** PreToolUse hooks to not crash on Edit operations
**So that** I don't see noisy "PreToolUse:Edit hook error" warnings on every edit

**Acceptance Criteria**:
- [x] **AC-US1-01**: `pre-tool-use.sh` uses `set +e` instead of `set -e`, matching all other hook scripts
- [x] **AC-US1-02**: Editing a `.specweave/increments/*/tasks.md` file produces no PreToolUse error warnings

---

### US-002: Eliminate PostToolUse Edit Hook Timeout Errors (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** PostToolUse hooks to complete within their timeout budget
**So that** I don't see "PostToolUse:Edit hook error" warnings on every edit

**Acceptance Criteria**:
- [x] **AC-US2-01**: `fail-fast-wrapper.sh` has a 15s timeout override for `post-tool-use.sh`
- [x] **AC-US2-02**: `task-ac-sync-guard.sh` runs in background (non-blocking) instead of synchronously
- [x] **AC-US2-03**: Editing a `.specweave/increments/*/tasks.md` file produces no PostToolUse timeout warnings
- [x] **AC-US2-04**: AC sync from tasks.md to spec.md still works correctly after backgrounding

## Out of Scope

- Removing/disabling third-party plugin hooks (Hookify, Security-Guidance) — those are user-managed
- Rewriting the hook architecture — this is a targeted fix for the timeout/crash bugs

## Dependencies

- `specweave refresh-plugins` must be run after source changes to update plugin cache
