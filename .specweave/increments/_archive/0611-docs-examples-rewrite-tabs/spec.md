---
increment: 0611-docs-examples-rewrite-tabs
title: Docs examples rewrite and three-tab pattern consistency
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Docs Examples Rewrite & Three-Tab Pattern Consistency

## Overview

Replace fabricated examples on docs/examples/index.md with real SpecWeave projects. Add CommandTabs three-tab pattern to 6 docs files that have plain `sw:` bash blocks.

## User Stories

### US-001: Real Examples Page (P0)
**Project**: specweave

**As a** developer evaluating SpecWeave
**I want** the examples page to show real, verifiable projects
**So that** I can trust the tool's claims and see authentic usage patterns

**Acceptance Criteria**:
- [x] **AC-US1-01**: Examples page showcases sw-url-shortener (beginner), sw-meeting-cost (intermediate), sw-wc26-travel (advanced), specweave-umb (showcase) with real data
- [x] **AC-US1-02**: All fabricated content removed (BizZone scanner, fake community examples, non-existent GitHub links)
- [x] **AC-US1-03**: Every code example on the examples page uses CommandTabs component
- [x] **AC-US1-04**: Comparison matrix updated with real project data

### US-002: Three-Tab Pattern Consistency (P1)
**Project**: specweave

**As a** docs reader
**I want** all user-facing command examples to show three invocation methods
**So that** I know how to invoke commands regardless of my AI tool

**Acceptance Criteria**:
- [x] **AC-US2-01**: CommandTabs added to 6 files: use-case-guide, command-decision-tree, fundamentals, self-improving-skills, cost-tracking, skills-vs-agents
- [x] **AC-US2-02**: Only user-facing invocations converted (reference tables and technical blocks left as-is)
- [x] **AC-US2-03**: Docusaurus build passes with zero errors after all changes

## Out of Scope

- Changes to CommandTabs component source code
- Changes to Docusaurus config or sidebar structure
- Files that already have CommandTabs (120 existing files)
