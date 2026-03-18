---
increment: 0574-docs-skills-page-accuracy
title: "Fix Skills Are Structured Expertise docs page"
type: docs
status: planned
created: 2026-03-18
---

# Architecture Plan: Fix Skills Docs Page

## Overview

Single-file documentation fix. No code changes, no new files, no ADRs needed.

## Target File

`repositories/anton-abyzov/specweave/docs-site/docs/overview/skills-as-structured-expertise.md`

## Changes Required

### 1. Fix skill count (line 71)

- **Current**: "100+ Skills Cover the Full Lifecycle"
- **Fix**: "44 Skills Cover the Full Lifecycle"
- **Rationale**: Core plugin has exactly 44 SKILL.md files. The "100+" claim is inaccurate.

### 2. Remove stale skill references (lines 78-82)

The following skills listed on the page do not exist:

| Listed Reference | Status |
|---|---|
| `/backend:nodejs`, `backend:python`, `backend:go` | Never existed in core — these were planned domain plugins that were never built |
| `/testing:qa` | Does not exist |
| `/sw:security` | Not a standalone skill (exists only as a team-lead agent role at `skills/team-lead/agents/security.md`) |
| `/backend:database-optimizer` (labeled "DevOps") | Does not exist |
| `/sw:code-review` | Wrong name — actual skill is `/sw:code-reviewer` |

### 3. Replace with accurate skill list

Replace the stale bullet list with skills that actually exist in the core plugin, organized by role:

- **PM** (`/sw:pm`) — writes user stories with acceptance criteria
- **Architect** (`/sw:architect`) — designs systems, writes ADRs
- **Code Review** (`/sw:code-reviewer`) — parallel review with confidence scoring
- **QA** (`/sw:grill`) — quality gate verification
- **TDD** (`/sw:tdd-cycle`) — red-green-refactor test-driven development
- **Release** (`/sw:release-expert`) — release management

## Architecture Decisions

None required — this is a documentation-only change with zero impact on code, tests, or system behavior.

## Risk Assessment

**Risk**: None. This is a markdown content fix in a docs-site page.

## Dependencies

None.
