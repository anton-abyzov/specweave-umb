---
increment: 0391-askuserquestion-markdown-previews
title: AskUserQuestion Markdown Previews for SpecWeave Skills
type: feature
priority: P1
status: completed
created: 2026-03-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Feature: AskUserQuestion Markdown Previews for SpecWeave Skills

## Overview

Add ASCII diagram utility functions and integrate markdown preview support into SpecWeave skills (`/sw:architect`, `/sw:plan`, `/sw:increment`) so that architectural decisions, task dependencies, and schema choices are presented visually via Claude Code's `AskUserQuestion` markdown preview feature.

Skills are SKILL.md prompt files — integration means updating prompts with instructions and examples for generating ASCII diagrams in the `markdown` field of `AskUserQuestion` options.

## User Stories

### US-001: ASCII Diagram Utility Functions (P1)
**Project**: specweave

**As a** SpecWeave skill author
**I want** reusable ASCII diagram generator functions
**So that** skills produce consistent, well-formatted diagrams for AskUserQuestion previews

**Acceptance Criteria**:
- [x] **AC-US1-01**: `renderBoxDiagram(nodes, connections)` generates ASCII box diagrams with Unicode box-drawing characters, max 80 chars wide
- [x] **AC-US1-02**: `renderDAG(tasks, dependencies)` generates ASCII directed acyclic graph showing parallel lanes and critical path
- [x] **AC-US1-03**: `renderTable(headers, rows, options?)` generates ASCII tables with aligned columns and optional header separators
- [x] **AC-US1-04**: `renderTree(items)` generates ASCII tree diagrams with proper branch characters
- [x] **AC-US1-05**: All functions handle edge cases: empty input, single node, overflow truncation at 80 chars

---

### US-002: Architect Skill Markdown Previews (P1)
**Project**: specweave

**As a** developer using `/sw:architect`
**I want** to see ASCII architecture diagrams and schema tables in side-by-side previews when choosing between approaches
**So that** I can visually compare structural trade-offs before committing to a decision

**Acceptance Criteria**:
- [x] **AC-US2-01**: `/sw:architect` SKILL.md includes instructions to use `AskUserQuestion` with `markdown` previews when presenting 2+ architectural approaches
- [x] **AC-US2-02**: Architecture decisions show box diagrams (service/component layouts) in preview panels
- [x] **AC-US2-03**: Schema decisions show ASCII table format (columns, types, relationships) in preview panels
- [x] **AC-US2-04**: SKILL.md includes at least 2 complete examples of AskUserQuestion calls with markdown previews

---

### US-003: Plan Skill Markdown Previews (P1)
**Project**: specweave

**As a** developer using `/sw:plan`
**I want** to see task dependency DAGs in side-by-side previews when choosing between execution strategies
**So that** I can visualize the critical path and parallelism before approving the plan

**Acceptance Criteria**:
- [x] **AC-US3-01**: `/sw:plan` SKILL.md includes instructions to use `AskUserQuestion` with `markdown` DAG previews for task ordering decisions
- [x] **AC-US3-02**: DAG previews show task IDs, names, dependencies, parallel lanes, and critical path annotation
- [x] **AC-US3-03**: SKILL.md includes at least 1 complete example of AskUserQuestion with DAG preview

---

### US-004: Increment Skill Markdown Previews (P2)
**Project**: specweave

**As a** developer using `/sw:increment`
**I want** to see folder structure trees and AC coverage tables when choosing between increment approaches
**So that** I can quickly assess the scope and structure of proposed work

**Acceptance Criteria**:
- [x] **AC-US4-01**: `/sw:increment` SKILL.md includes instructions to use `AskUserQuestion` with `markdown` previews for scope/structure decisions
- [x] **AC-US4-02**: Tree previews show proposed folder structures with proper indentation
- [x] **AC-US4-03**: Table previews show AC coverage mapping (tasks to ACs)

---

## Functional Requirements

### FR-001: ASCII Diagram Module
TypeScript module at `src/utils/ascii-diagrams.ts` exporting four pure functions. Each function takes structured input and returns a string. No side effects, no file I/O.

### FR-002: SKILL.md Integration Pattern
Each updated SKILL.md includes a dedicated section with:
- When to use markdown previews (decision points with 2+ options)
- How to format the AskUserQuestion call
- Complete copy-paste examples with realistic content
- Constraint: previews only at decision points, not every question

### FR-003: Width Constraint
All diagram output fits within 80 characters per line. Functions truncate or wrap gracefully when content exceeds width.

## Success Criteria

- All 4 diagram functions have 95%+ unit test coverage
- 3 SKILL.md files updated with preview instructions and examples
- Manual verification: running each skill shows previews in Claude Code terminal

## Out of Scope

- Mermaid rendering in AskUserQuestion (doesn't render in terminal)
- Terminal width detection (fixed 80 chars)
- config.json toggle for enabling/disabling previews
- Diagram generation in non-AskUserQuestion contexts (living docs, etc.)
- Updating skills beyond architect, plan, increment

## Dependencies

- Claude Code AskUserQuestion `markdown` field support (already shipped)
- SpecWeave skill system (SKILL.md prompt files)
