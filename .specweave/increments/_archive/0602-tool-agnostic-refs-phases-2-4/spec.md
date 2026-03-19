---
increment: 0602-tool-agnostic-refs-phases-2-4
title: 'Tool-agnostic command refs: SKILL.md, docs-site, TS source'
type: change-request
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Tool-Agnostic Command References — Phases 2-4

## Overview

Continuation of increment 0596 (Phase 1 — templates). Drop the leading `/` from `sw:` command references across SKILL.md files, docs-site, and TypeScript source. Canonical format: `sw:do` (established in 0596).

## User Stories

### US-001: Tool-Agnostic SKILL.md Files (P1)
**Project**: specweave

**As a** skill author or AI tool reading SKILL.md content
**I want** command references to use `sw:do` format without the Claude-specific `/` prefix
**So that** skill instructions are tool-agnostic across all 49 supported AI platforms

**Acceptance Criteria**:
- [x] **AC-US1-01**: All `/sw:` prose references in SKILL.md files replaced with `sw:`
- [x] **AC-US1-02**: All `/sw-` references (plugin namespaces) replaced with `sw-`
- [x] **AC-US1-03**: `Skill({ skill: "sw:..."})` calls remain unchanged (already correct)

### US-002: Tool-Agnostic Docs-Site (P1)
**Project**: specweave

**As a** developer reading the SpecWeave documentation site
**I want** command references to be tool-agnostic
**So that** docs work regardless of which AI tool I use

**Acceptance Criteria**:
- [x] **AC-US2-01**: All `/sw:` references in docs-site markdown files replaced with `sw:`
- [x] **AC-US2-02**: All `/sw-` references replaced with `sw-`

### US-003: Tool-Agnostic TypeScript Source (P1)
**Project**: specweave

**As a** developer reading error messages and CLI output
**I want** command suggestions to use tool-agnostic format
**So that** output is correct regardless of which AI tool invoked it

**Acceptance Criteria**:
- [x] **AC-US3-01**: `/sw:` references in error messages, suggestions, and log output replaced with `sw:`
- [x] **AC-US3-02**: Functional code in phase-detector.ts and project-scope-guard.ts preserved (these parse `/sw:` as routing prefixes)
- [x] **AC-US3-03**: All existing tests pass after changes

## Out of Scope

- CLAUDE.md template (already handled in 0596, keeps `/sw:` format)
- vskill SKILL.md files (already tool-agnostic)
