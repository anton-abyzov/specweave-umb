---
increment: 0575-docs-no-docs-needed-rewrite
title: "Rework no-docs-needed page to lead with SpecWeave value"
type: change-request
priority: P1
status: planned
created: 2026-03-18
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Rework no-docs-needed page to lead with SpecWeave value

## Overview

Rewrite `repositories/anton-abyzov/specweave/docs-site/docs/overview/no-docs-needed.md` — a single documentation page in the SpecWeave docs site.

**Problem**: The current page titled "You Don't Need to Learn Claude Code" positions SpecWeave as a Claude Code wrapper — making Claude Code the protagonist and SpecWeave a mere convenience layer. This contradicts product positioning across all other pages:

- **Homepage**: "Ship Features While You Sleep" — autonomous AI dev platform
- **Introduction** (`introduction.md`): "spec-first AI development framework" — tool-agnostic, works with Claude Code, Cursor, Copilot, Codex
- **Why SpecWeave** (`why-specweave.md`): Frames problem as "vibe coding" vs spec-driven development
- **Philosophy** (`philosophy.md`): "The plan is the source of truth. Code is a derivative."

The rewritten page must align with this established positioning by leading with SpecWeave's own value proposition rather than defining itself relative to Claude Code.

**Scope**: Single markdown file rewrite. No new files. No architecture changes.

**Target file**: `repositories/anton-abyzov/specweave/docs-site/docs/overview/no-docs-needed.md`

## User Stories

### US-001: Page title and framing communicate SpecWeave's value (P1)
**Project**: specweave

**As a** prospective SpecWeave user reading the docs
**I want** the page to lead with what SpecWeave enables me to do
**So that** I understand SpecWeave as a powerful development framework, not just a wrapper around another tool

**Acceptance Criteria**:
- [x] **AC-US1-01**: Page title is "Start Building in Minutes" (replaces "You Don't Need to Learn Claude Code")
- [x] **AC-US1-02**: Page `description` frontmatter references SpecWeave's spec-first methodology and immediate productivity — not Claude Code abstraction
- [x] **AC-US1-03**: Opening section leads with SpecWeave's own value: spec-first development, autonomous execution, quality gates, living documentation
- [x] **AC-US1-04**: Claude Code is NOT the organizing principle of the page — it appears only as supporting detail (one of several supported tools)

---

### US-002: Table reframed around capabilities (P1)
**Project**: specweave

**As a** prospective user scanning the page
**I want** a capabilities table that shows what I get immediately with SpecWeave
**So that** I understand the breadth of the framework without needing to read detailed docs

**Acceptance Criteria**:
- [x] **AC-US2-01**: Table header changes from "Claude Code concepts we hide" pattern to "What you get immediately" or equivalent capabilities framing
- [x] **AC-US2-02**: Table rows describe SpecWeave capabilities (spec-first planning, autonomous execution, quality gates, living docs, built-in skills, external sync) — not Claude Code concepts being abstracted
- [x] **AC-US2-03**: Table does not use Claude Code as the left/anchor column

---

### US-003: Before/After reframed as vibe coding vs spec-driven (P1)
**Project**: specweave

**As a** developer evaluating whether SpecWeave solves my problems
**I want** a comparison that contrasts unstructured AI coding with spec-driven development
**So that** I see the value of SpecWeave's methodology regardless of which AI tool I use

**Acceptance Criteria**:
- [x] **AC-US3-01**: "Without SpecWeave" section describes vibe coding problems (lost context, no specs, manual testing, no docs) — NOT "read Claude Code docs"
- [x] **AC-US3-02**: "With SpecWeave" section shows the same install + increment + auto flow but framed as spec-driven methodology, not Claude Code abstraction
- [x] **AC-US3-03**: Comparison is tool-agnostic — works regardless of whether user uses Claude Code, Cursor, or Copilot

---

### US-004: Tool-agnostic framing consistent with introduction page (P1)
**Project**: specweave

**As a** user who may use Cursor, Copilot, or other AI tools
**I want** the page to present SpecWeave as tool-agnostic
**So that** I don't think SpecWeave only works with Claude Code

**Acceptance Criteria**:
- [x] **AC-US4-01**: Page mentions that SpecWeave works with Claude Code, Cursor, Copilot, and other AI coding tools — consistent with introduction.md positioning
- [x] **AC-US4-02**: Claude Code mentions are reduced to supporting detail (mentioned 0-3 times max, never as the organizing principle)
- [x] **AC-US4-03**: No section titles reference Claude Code

---

### US-005: Sidebar position and internal links preserved (P1)
**Project**: specweave

**As a** docs site maintainer
**I want** the rewritten page to maintain its position in the sidebar and keep internal links functional
**So that** the docs site navigation is not broken

**Acceptance Criteria**:
- [x] **AC-US5-01**: `sidebar_position: 3` frontmatter is preserved
- [x] **AC-US5-02**: All internal links (to skill development, extensible skills, troubleshooting) remain valid or are updated to equivalent targets
- [x] **AC-US5-03**: Page slug remains compatible — file stays at `docs/overview/no-docs-needed.md` (URL may change via frontmatter slug if needed)

## Functional Requirements

### FR-001: Content structure
The rewritten page should follow this structure:
1. **Title**: "Start Building in Minutes"
2. **Opening paragraph**: SpecWeave's value prop — spec-first, autonomous, quality-gated
3. **Capabilities table**: What you get immediately (not what CC concepts are hidden)
4. **Before/After comparison**: Vibe coding vs spec-driven development
5. **How it works section**: Brief overview of the 3-command workflow (increment, do, done)
6. **When to go deeper**: Links to advanced topics (skill creation, customization, troubleshooting)

### FR-002: Tone and voice
- Confident and direct — SpecWeave is the protagonist
- Consistent with introduction.md and why-specweave.md tone
- No apologetic or subordinate framing ("we just wrap X")
- Practical — show the workflow, not just describe it

### FR-003: Claude Code mention budget
- Claude Code may be mentioned as one of several supported tools
- Maximum 3 mentions, all as supporting detail
- Never in a section title or as the organizing principle of a section

## Success Criteria

- Page title is "Start Building in Minutes"
- Claude Code is not the organizing principle of ANY section
- Before/After comparison uses vibe coding vs spec-driven framing (consistent with why-specweave.md)
- Capabilities table lists SpecWeave features, not Claude Code concepts
- Tool-agnostic positioning matches introduction.md
- All internal links remain functional
- sidebar_position preserved at 3

## Out of Scope

- Changes to any other documentation page
- Changes to sidebar configuration files
- New documentation files
- Architecture or code changes
- URL redirects (file path stays the same)

## Dependencies

- None — standalone single-file rewrite
