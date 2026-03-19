---
increment: 0606-non-claude-skill-refresh
title: 'Non-Claude Skill Refresh: Frontmatter Normalization + vskill update'
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Non-Claude Skill Refresh: Frontmatter Normalization + vskill update

## Overview

Skills copied to non-Claude tool directories (`.opencode/skills/`, `.cursor/skills/`, etc.) lack proper frontmatter (`name:`, `description:`), making them undiscoverable. Additionally, `vskill update` skips `local:specweave` skills, preventing users from refreshing core specweave skills.

## User Stories

### US-001: Proper Skill Frontmatter for Non-Claude Tools (P1)
**Project**: specweave

**As a** developer using OpenCode, Cursor, or other non-Claude AI tools
**I want** skills copied by `specweave refresh-plugins` to have proper frontmatter (name, description)
**So that** my AI tool can discover and invoke skills correctly

**Acceptance Criteria**:
- [x] **AC-US1-01**: SKILL.md files copied to non-Claude directories include `name:` field derived from directory name
- [x] **AC-US1-02**: SKILL.md files copied to non-Claude directories include `description:` field (extracted from body if missing)
- [x] **AC-US1-03**: Claude-specific fields (`user-invocable`, `allowed-tools`, `model`, `argument-hint`, `context`, `hooks`) are stripped from non-Claude copies
- [x] **AC-US1-04**: Non-SKILL.md files (agents/*.md, etc.) are copied unchanged (raw copy)

---

### US-002: vskill update Handles Local Specweave Skills (P1)
**Project**: vskill

**As a** developer using vskill to manage project-level skills
**I want** `vskill update` to refresh `local:specweave` skills from the plugin cache
**So that** I can keep core specweave skills up to date without running `specweave refresh-plugins` separately

**Acceptance Criteria**:
- [x] **AC-US2-01**: `vskill update` (no args) defaults to updating ALL installed skills (previously required `--all`)
- [x] **AC-US2-02**: Skills with `source: "local:specweave"` in lockfile are updated from specweave plugin cache
- [x] **AC-US2-03**: SHA comparison skips unchanged skills (no unnecessary re-installs)
- [x] **AC-US2-04**: Updated skills go through `ensureFrontmatter()` (name + description guaranteed)
- [x] **AC-US2-05**: Lockfile entry updated with new SHA + timestamp after successful update

---

### US-003: Documentation Updates (P2)
**Project**: specweave

**As a** developer reading SpecWeave or vskill documentation
**I want** docs to reflect the new frontmatter normalization and vskill update behavior
**So that** I know how skills work across different AI tools

**Acceptance Criteria**:
- [x] **AC-US3-01**: specweave.com docs describe frontmatter normalization for non-Claude adapters
- [x] **AC-US3-02**: verified-skill.com docs describe `vskill update` default behavior change and local:specweave support

## Out of Scope

- MCP-based hot-reload for non-Claude tools
- File watchers for auto-refresh
- New CLI flags or commands beyond existing `vskill update`
