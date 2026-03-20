---
increment: 0638-fix-appstore-skill-md
title: Fix appstore skill security scan false positives
type: bug
priority: P1
status: completed
created: 2026-03-20T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix appstore skill security scan false positives

## Overview

The appstore skill fails `vskill install` with Tier 1 score 22/100 (3 critical false positives). Fix the scanner patterns and SKILL.md content so the skill installs cleanly and passes platform verification.

## User Stories

### US-001: Scanner accurately handles keychain documentation (P1)
**Project**: vskill

**As a** skill author
**I want** the CT-004 pattern to only flag actual keychain access code
**So that** documentation mentioning "keychain" doesn't trigger false critical findings

**Acceptance Criteria**:
- [x] **AC-US1-01**: CT-004 matches `security find-generic-password`, `security default-keychain`, `SecKeychainFindGenericPassword`, `keychain.get(`
- [x] **AC-US1-02**: CT-004 does NOT match bare "keychain" in env var names (`ASC_BYPASS_KEYCHAIN`) or explanatory text ("macOS Keychain is unavailable")
- [x] **AC-US1-03**: CT-004 is in DOCUMENTATION_SAFE_PATTERNS for defense-in-depth downgrade inside fenced code blocks

---

### US-002: Appstore SKILL.md passes security scan (P1)
**Project**: vskill

**As a** user installing the appstore skill
**I want** the skill to pass the Tier 1 security scan without `--force`
**So that** I can install it normally and trust its security rating

**Acceptance Criteria**:
- [x] **AC-US2-01**: SKILL.md has no nested fenced code blocks that break scanner fence detection
- [x] **AC-US2-02**: Tier 1 scan of appstore SKILL.md scores >= 80 (PASS verdict)
- [x] **AC-US2-03**: All existing scanner tests continue to pass

## Out of Scope

- Fixing the scanner's toggle-based fence detection to handle nested blocks (general fix)
- Platform-side rejection clearing (handled by resubmission after code fix)
