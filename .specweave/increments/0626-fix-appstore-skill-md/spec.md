---
increment: 0626-fix-appstore-skill-md
title: "Fix appstore SKILL.md - broken CLI commands, security gaps, missing workflows"
type: feature
priority: P1
status: planned
created: 2026-03-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix appstore SKILL.md

## Overview

Fix 27 issues identified by 5-agent review in the appstore SKILL.md — broken CLI flags, missing variable captures, security gaps, phantom related skills, and missing workflows.

## User Stories

### US-001: Fix Broken CLI Commands (P1)
**Project**: vskill

**As a** developer using the appstore skill
**I want** correct `asc` CLI commands and flags
**So that** the generated commands actually work

**Acceptance Criteria**:
- [ ] **AC-US1-01**: All `--app-id` flags replaced with `--app`
- [ ] **AC-US1-02**: All `--build-id` flags replaced with `--build`
- [ ] **AC-US1-03**: All `--file` flags in upload contexts replaced with `--ipa`
- [ ] **AC-US1-04**: `asc apps` replaced with `asc apps list`
- [ ] **AC-US1-05**: `--workflow-name` replaced with `--workflow-id` for Xcode Cloud
- [ ] **AC-US1-06**: Install commands fixed: `brew install asc` (no tap), install script URL `https://asccli.sh/install`
- [ ] **AC-US1-07**: Troubleshooting section install command fixed

---

### US-002: Add Variable Capture Patterns (P1)
**Project**: vskill

**As a** developer following the skill's instructions
**I want** `$BUILD_ID` and `$VERSION_ID` to be captured before use
**So that** subsequent commands using these variables actually work

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `$BUILD_ID` capture pattern added using `jq -r '.id'` after build list/latest
- [ ] **AC-US2-02**: `$VERSION_ID` capture pattern added after version create/list
- [ ] **AC-US2-03**: Submit mode captures `$VERSION_ID` before using it

---

### US-003: Add Security Warnings and Safety Guards (P1)
**Project**: vskill

**As a** developer deploying to the App Store
**I want** security warnings for sensitive operations
**So that** I don't accidentally leak credentials or make irreversible changes

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `--confirm` flag added to all destructive operations (submit, revoke, expire, phased-release complete)
- [ ] **AC-US3-02**: Certificate revocation blast radius warning added
- [ ] **AC-US3-03**: Phased release COMPLETE irreversibility warning added
- [ ] **AC-US3-04**: .p8 key security warnings (chmod 600, .gitignore, shell history)
- [ ] **AC-US3-05**: `ASC_DEBUG=api` CI security warning added
- [ ] **AC-US3-06**: API key role guidance recommends App Manager minimum
- [ ] **AC-US3-07**: App Privacy declaration requirement warning added
- [ ] **AC-US3-08**: Export compliance note added

---

### US-004: Add Missing Workflows (P2)
**Project**: vskill

**As a** developer managing App Store submissions
**I want** rejection handling, rollback, and emergency removal workflows
**So that** I can handle common real-world scenarios

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Rejection handling workflow added with steps to check rejection reason, fix, resubmit
- [ ] **AC-US4-02**: Rollback workflow added to revert to previous version
- [ ] **AC-US4-03**: Emergency app removal workflow added

---

### US-005: Fix Quality and Completeness Issues (P2)
**Project**: vskill

**As a** developer using the appstore skill
**I want** complete menus, correct namespaces, and proper shell quoting
**So that** the skill is production-quality

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Default interactive menu shows all 10 modes (not just 4)
- [ ] **AC-US5-02**: Metadata bulk localization uses correct namespace
- [ ] **AC-US5-03**: METADATA MODE includes version selection step
- [ ] **AC-US5-04**: Submit mode checks for existing draft versions before creating new
- [ ] **AC-US5-05**: Phantom related skills removed or replaced with real ones
- [ ] **AC-US5-06**: Env var table split into secrets vs config sections
- [ ] **AC-US5-07**: All shell variables properly quoted (`"$APP_ID"` not `$APP_ID`)
- [ ] **AC-US5-08**: vskill install section added with correct `npx vskill i` command

## Out of Scope

- Rewriting the entire SKILL.md from scratch
- Adding new modes beyond the existing 10
- Testing against actual `asc` CLI (skill is documentation)
