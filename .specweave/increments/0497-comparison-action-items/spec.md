---
increment: 0497-comparison-action-items
title: Comparison Action Items Engine
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Comparison Action Items Engine

## Overview

After A/B comparison completes in vskill studio, the verdict (EFFECTIVE/MARGINAL/INEFFECTIVE/DEGRADING) provides no actionable guidance. This increment adds an action items engine that analyzes comparison results + SKILL.md via LLM and produces concrete recommendations, plus a UI panel with an "Apply AI Fix" button connecting to the existing improve infrastructure.

## User Stories

### US-001: Actionable comparison results (P1)
**Project**: vskill

**As a** skill author
**I want** concrete action items after A/B comparison
**So that** I know exactly what to do: keep, improve, rewrite, or remove my skill

**Acceptance Criteria**:
- [x] **AC-US1-01**: After verdict computation, system generates structured action items via LLM call
- [x] **AC-US1-02**: Action items include recommendation (keep/improve/rewrite/remove), summary, weaknesses, strengths, suggestedFocus
- [x] **AC-US1-03**: Action items are persisted in history alongside verdict and comparison data
- [x] **AC-US1-04**: Action items generation is non-fatal — comparison is still valid without it

---

### US-002: Action items UI panel (P1)
**Project**: vskill

**As a** skill author
**I want** to see action items rendered below the verdict card
**So that** I can quickly understand what to do without reading raw data

**Acceptance Criteria**:
- [x] **AC-US2-01**: ActionItemsPanel renders below verdict card with color-coded recommendation badge
- [x] **AC-US2-02**: Panel shows weaknesses (red) and strengths (green) in a 2-column grid
- [x] **AC-US2-03**: Suggested focus area is highlighted in a separate box
- [x] **AC-US2-04**: "Apply AI Fix" button appears for improve/rewrite recommendations

---

### US-003: Apply AI Fix integration (P1)
**Project**: vskill

**As a** skill author
**I want** to click "Apply AI Fix" and have the system improve my skill
**So that** I don't have to manually figure out how to fix weaknesses

**Acceptance Criteria**:
- [x] **AC-US3-01**: "Apply AI Fix" navigates to workspace editor with comparison context as notes
- [x] **AC-US3-02**: Reuses existing /improve endpoint — zero duplication of improve infrastructure

---

### US-004: Fix 404 console noise (P2)
**Project**: vskill

**As a** developer
**I want** no console errors when loading skills without benchmarks
**So that** the console stays clean for real errors

**Acceptance Criteria**:
- [x] **AC-US4-01**: getLatestBenchmark returns null on 404 instead of throwing
- [x] **AC-US4-02**: All callers handle null gracefully

## Out of Scope

- Inline improve flow within ComparisonPage (uses existing workspace editor)
- Auto-fixing without user confirmation
- Action items for non-comparison benchmark runs
