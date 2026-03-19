---
increment: 0620-docs-sw-closer-agent
title: "Document sw-closer agent in skills/agents docs"
type: change-request
priority: P1
status: planned
created: 2026-03-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Document sw-closer Agent Across All Docs

## Overview

Update all agent/skill documentation to reflect the sw-closer subagent type (`sw:sw-closer`) that runs the full sw:done closure pipeline in a fresh context to prevent context overflow during team-led development.

## User Stories

### US-001: Document sw-closer in User-Facing Docs (P1)
**Project**: specweave

**As a** SpecWeave user reading the documentation
**I want** to find clear documentation about the sw-closer agent and when to use it
**So that** I understand the closure workflow for multi-agent teams

**Acceptance Criteria**:
- [x] **AC-US1-01**: AGENTS.md (umbrella) has a "Subagent Types" section listing sw:sw-closer with purpose and usage
- [x] **AC-US1-02**: AGENTS.md (specweave repo) has matching subagent types section
- [x] **AC-US1-03**: done/SKILL.md mentions sw-closer as alternative for context overflow prevention
- [x] **AC-US1-04**: team-lead/SKILL.md documents the team-lead → sw-closer closure workflow (already partially present, verify/update)
- [x] **AC-US1-05**: PLUGIN.md has a "Subagents" section listing sw:sw-closer, sw:sw-pm, sw:sw-architect, sw:sw-planner

### US-002: Document sw-closer in Public Docs Site (P2)
**Project**: specweave

**As a** developer learning SpecWeave from the docs site
**I want** the agent teams guide and increment lifecycle docs to explain closure patterns
**So that** I understand how multi-agent closure works

**Acceptance Criteria**:
- [x] **AC-US2-01**: docs-site/docs/guides/agent-teams-and-swarms.md has a "Closure" section explaining sw-closer
- [x] **AC-US2-02**: docs-site/docs/academy/specweave-essentials/13-increment-lifecycle.md mentions closure subagent pattern

## Out of Scope

- Code changes to sw-closer itself
- CLAUDE.md changes (auto-generated, not manually edited)
