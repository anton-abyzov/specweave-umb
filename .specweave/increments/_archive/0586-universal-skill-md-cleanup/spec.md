---
increment: 0586-universal-skill-md-cleanup
title: Universal SKILL.md + Dead Code Cleanup
type: refactor
priority: P2
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Universal SKILL.md + Dead Code Cleanup

## Overview

Make the increment SKILL.md universal (CLI-first, works with all AI tools) instead of Claude Code-specific, remove dead ID pre-generation code, and update next-id help text.

## User Stories

### US-001: CLI-first SKILL.md Structure (P1)
**Project**: specweave

**As a** developer using any AI tool (Cursor, Copilot, OpenCode, etc.)
**I want** the increment SKILL.md to present direct spec writing as the default path
**So that** I can use SpecWeave increment planning regardless of which AI tool I use

**Acceptance Criteria**:
- [x] **AC-US1-01**: Step 3b uses `create-increment --auto-id` as the sole creation path (legacy two-step section removed)
- [x] **AC-US1-02**: Step 4 is "Direct Specification Writing" -- universal, CLI-first, works with all tools
- [x] **AC-US1-03**: Step 4a is "Enhanced: Team-Based Delegation" -- framed as optional Claude Code enhancement
- [x] **AC-US1-04**: Critical Rules updated to prefer team delegation when available, not mandate it

---

### US-002: Remove Dead ID Pre-Generation (P1)
**Project**: specweave

**As a** maintainer of the specweave CLI
**I want** dead code in create-increment.ts removed
**So that** the codebase accurately reflects the atomic ID generation flow

**Acceptance Criteria**:
- [x] **AC-US2-01**: `getNextIncrementNumber()` call removed from create-increment.ts when autoId=true
- [x] **AC-US2-02**: resolvedId set to empty string when autoId=true (template-creator handles real ID)
- [x] **AC-US2-03**: Unused IncrementNumberManager import removed

---

### US-003: Update next-id Help Text (P2)
**Project**: specweave

**As a** CLI user
**I want** the next-id command description to point toward the preferred --auto-id approach
**So that** I use the atomic path by default

**Acceptance Criteria**:
- [x] **AC-US3-01**: next-id description updated to recommend create-increment --auto-id

## Out of Scope

- Removing the `next-id` command entirely (still useful for diagnostics)
- Changing template-creator.ts behavior
- Modifying other SKILL.md files
