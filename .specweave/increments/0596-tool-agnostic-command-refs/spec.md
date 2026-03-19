---
increment: 0596-tool-agnostic-command-refs
title: Tool-agnostic command references in templates
type: change-request
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Tool-Agnostic Command References in Templates

## Overview

Replace Claude-specific `/sw:do` slash-command format with tool-agnostic `sw:do` identifier format across templates and agents-md-compiler. Add "How to Invoke" section for per-tool guidance.

## User Stories

### US-001: Tool-Agnostic AGENTS.md Template (P1)
**Project**: specweave

**As a** developer using any AI tool (Cursor, Copilot, Windsurf, etc.)
**I want** AGENTS.md to use tool-agnostic command references
**So that** I understand the commands without assuming Claude Code's slash-command syntax

**Acceptance Criteria**:
- [x] **AC-US1-01**: All `/sw:` references in AGENTS.md.template are replaced with `sw:` (no leading slash)
- [x] **AC-US1-02**: A "How to Invoke" section is added showing per-tool invocation mapping
- [x] **AC-US1-03**: Claude-specific comparison columns retain `/sw:` format where they explicitly describe Claude behavior

### US-002: Tool-Agnostic README Template (P1)
**Project**: specweave

**As a** new user reading the project README
**I want** command references to be tool-agnostic
**So that** I can follow the quickstart regardless of which AI tool I use

**Acceptance Criteria**:
- [x] **AC-US2-01**: All `/sw:` references in README.md.template are replaced with `sw:` format
- [x] **AC-US2-02**: "slash commands" prose is changed to "commands"
- [x] **AC-US2-03**: A brief invocation note is added explaining commands vary by tool

### US-003: Unified Compiler Format (P1)
**Project**: specweave

**As a** non-Claude tool user reading the compiled AGENTS.md
**I want** commands to use the canonical `sw:` format instead of `/specweave.` dot-notation
**So that** the format is consistent with templates and documentation

**Acceptance Criteria**:
- [x] **AC-US3-01**: All `/specweave.*` references in agents-md-compiler.ts are replaced with `sw:` canonical format

### US-004: Tasks Template and CLAUDE.md Note (P2)
**Project**: specweave

**As a** developer working across tools
**I want** tasks.md template to use tool-agnostic format and CLAUDE.md to explain the mapping
**So that** generated task files work for any tool and Claude users understand the relationship

**Acceptance Criteria**:
- [x] **AC-US4-01**: `/sw:validate` and `/sw:done` in tasks.md.template replaced with `sw:validate` and `sw:done`
- [x] **AC-US4-02**: CLAUDE.md.template includes a note explaining `/sw:do` (Claude) vs `sw:do` (tool-agnostic) mapping

## Out of Scope

- SKILL.md files (44 files — future increment)
- docs-site pages (199 files — future increment)
- TypeScript source runtime messages (103 files — future increment)
- vskill SKILL.md files (already tool-agnostic)
