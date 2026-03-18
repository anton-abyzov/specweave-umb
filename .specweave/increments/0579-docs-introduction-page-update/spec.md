---
increment: 0579-docs-introduction-page-update
title: Update introduction page with recent features
type: feature
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Update Introduction Page with Recent Features

## Overview

Update the SpecWeave introduction page (`docs-site/docs/overview/introduction.md`) to reflect recently added critical features: Team Lead parallel agents, Brainstorming, Brownfield `specweave get`, and production tool integrations. Consolidate the best content from README.md into the intro page while keeping it focused and scannable.

**Project**: specweave
**Type**: Documentation (single-file modification)
**Target file**: `repositories/anton-abyzov/specweave/docs-site/docs/overview/introduction.md`

---

## User Stories

### US-001: Visitor Learns About Team Lead / Parallel Agents (P1)
**Project**: specweave

**As a** visitor reading the introduction page,
**I want to** understand that SpecWeave supports parallel multi-agent work via `/sw:team-lead`,
**So that** I know SpecWeave can orchestrate agent swarms across iTerm/tmux panes for complex features.

**Acceptance Criteria:**
- [x] **AC-US1-01**: Introduction page includes an "Agent Swarms" or equivalent section describing `/sw:team-lead` and its 6 operating modes (brainstorm, plan, implement, review, research, test)
- [x] **AC-US1-02**: The iTerm/tmux ASCII art diagram from README (lines 206-212) appears on the intro page
- [x] **AC-US1-03**: The section explains that Team Lead uses Claude Code's native TeamCreate for true parallelism

---

### US-002: Visitor Learns About Brainstorming (P1)
**Project**: specweave

**As a** visitor reading the introduction page,
**I want to** learn that SpecWeave has a structured brainstorming capability,
**So that** I understand I can use multi-perspective ideation before committing to a plan.

**Acceptance Criteria:**
- [x] **AC-US2-01**: The natural language routing table includes brainstorming triggers (e.g., "Brainstorm approaches for X")
- [x] **AC-US2-02**: Brainstorming is mentioned in the workflow narratives or the complexity diagram showing it as a step for medium-complexity features

---

### US-003: Visitor Understands Brownfield Support (P1)
**Project**: specweave

**As a** visitor with an existing codebase,
**I want to** see that SpecWeave supports brownfield adoption via `specweave get`,
**So that** I know I can bring existing repos into SpecWeave without refactoring.

**Acceptance Criteria:**
- [x] **AC-US3-01**: A brownfield workflow narrative appears on the intro page (from README lines 125-130)
- [x] **AC-US3-02**: The "Who Should Use SpecWeave" or equivalent section highlights brownfield support with `specweave get` capabilities (single repo, bulk clone, org-wide)

---

### US-004: Visitor Sees Production Tool Integrations (P1)
**Project**: specweave

**As a** visitor evaluating SpecWeave for their team,
**I want to** see which external tools SpecWeave integrates with and what syncs,
**So that** I can assess compatibility with my existing workflow.

**Acceptance Criteria:**
- [x] **AC-US4-01**: An integrations table appears on the intro page showing GitHub, JIRA, Azure DevOps, and Verified Skills with what syncs for each (from README lines 345-358)
- [x] **AC-US4-02**: The circuit breaker resilience pattern is mentioned (per-provider, 3-failure threshold, 5-min auto-reset)

---

### US-005: Content Consolidation from README (P1)
**Project**: specweave

**As a** visitor landing on the introduction page,
**I want to** see the most compelling content from the README consolidated here,
**So that** the intro page serves as a comprehensive overview without requiring me to find the README.

**Acceptance Criteria:**
- [x] **AC-US5-01**: The "No Commands to Memorize" natural language routing table from README (lines 38-55) is added to the intro page
- [x] **AC-US5-02**: Three workflow narratives (solo, agent team, brownfield) from README (lines 85-131) appear on the intro page
- [x] **AC-US5-03**: The "Harder problems" complexity diagram from README (lines 162-180) is included
- [x] **AC-US5-04**: Existing intro page sections are preserved or enhanced — no content regression
- [x] **AC-US5-05**: The page remains scannable — clear headings, short paragraphs, tables over prose

---

## Out of Scope

- Changes to any file other than `introduction.md`
- New Docusaurus components or custom React components
- Changes to sidebar configuration
- Changes to the README.md itself
- Adding new images or SVGs (reuse existing references only)

## Technical Notes

- The file uses Docusaurus MDX with the `CommandTabs` component (already imported)
- All external links should use existing URL patterns from the current page
- Keep the existing `<p align="center">` image reference for the flow diagram
- The page is ~196 lines currently; target ~280-320 lines after additions (stay well under the 1500 line limit)

## Dependencies

None — docs-only change with no code or infrastructure dependencies.
