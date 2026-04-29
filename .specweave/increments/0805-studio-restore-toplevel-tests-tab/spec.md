---
increment: 0805-studio-restore-toplevel-tests-tab
title: Restore top-level Tests tab in Studio
type: feature
priority: P1
status: completed
created: 2026-04-29T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Restore top-level Tests tab in Studio

## Context

Increment 0792 collapsed the dedicated **Tests** tab into Run > Benchmark + Edit > eval-cases disclosure. Increment 0800 restored the per-case 2x2 pass/fail visualization on the Run tab and made authoring discoverable from Edit + Overview chip.

After 0800 shipped, the user confirmed the inline path works ("I could see tests now, kind of below in the edit button") but explicitly asked for the **dedicated top-level Tests tab back** because the prior IA "deserves a separate tab like it was before." This increment restores that tab.

## Goals

- Add a 5th top-level tab "Tests" between Edit and Run
- Mount the existing `<TestsPanel />` in **non-embedded** mode on this tab — full authoring + execution history surface (filter tabs, parameter store, eval-case forms, AI generation, per-case 2x2 grid)
- Keep the Edit-tab eval-cases disclosure (no regression — convenient inline authoring)
- Update legacy redirect: `?tab=tests` now mounts the Tests tab directly (was redirecting to `?tab=run&mode=benchmark`)

## Non-Goals

- Removing the Edit-tab eval-cases section (kept; both surfaces stay in sync via WorkspaceContext)
- Removing the Run-tab `PerCaseHistory` block from 0800 (kept; useful when running and watching results)
- Backend changes
- Re-architecting the eval execution path

## User Stories

### US-001: Top-level Tests tab visible alongside other tabs
**Project**: vskill

**As a** Studio user
**I want** a dedicated top-level "Tests" tab in the Skill Detail page
**So that** I can find authoring + execution history in the place I expect — alongside Overview / Edit / Run / History

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given I open any skill detail page, when the right panel renders, then exactly five tabs are visible in this order: Overview, Edit, Tests, Run, History
- [x] **AC-US1-02**: Given I click the Tests tab, when navigation completes, then the URL becomes `?tab=tests` AND the tab content area mounts `<TestsPanel />` in non-embedded mode (full authoring surface)
- [x] **AC-US1-03**: Given I land on the Tests tab, when the panel mounts, then the eval-case filter tabs (All / Unit / Integration), per-case rows with Run buttons, parameter store, and Execution History split-lane grid are all visible
- [x] **AC-US1-04**: Given I am viewing an installed skill (`origin === "installed"`), when I open the Tests tab, then `canEdit` gating from 0800 is in effect — Add/Edit/Delete hidden, Run buttons visible, read-only banner rendered
- [x] **AC-US1-05**: Given I navigate via the legacy URL `?tab=tests`, when the page loads, then the Tests tab is the active tab (no redirect to Run)
- [x] **AC-US1-06**: Given I am on the Edit tab, when I expand the eval-cases disclosure (`editor-eval-cases-section`), then the existing 0800 inline authoring + Run-all CTA still work (no regression — kept for convenience)
- [x] **AC-US1-07**: Given the Run tab is open in Benchmark mode, when cases render, then the 0800 `PerCaseHistory` block under each case still renders (no regression)

## Out of Scope

- Removing or hiding the Edit-tab eval-cases disclosure
- Removing the Run-tab per-case history grid
- Restoring the historical Trigger or Versions top-level tabs (those remain consolidated per 0792)
- Migrating data shape or backend handlers

## Non-Functional Requirements

- **Compatibility**: One file changed — `src/eval-ui/src/components/RightPanel.tsx`. Imports `TestsPanel` from existing module.
- **Performance**: Same as today (TestsPanel already mounts in embedded mode in Edit tab). No new network calls. Bundle delta < 0.5 KB.
- **Accessibility**: Tab uses existing `data-testid="detail-tab-tests"` pattern.

## Edge Cases

- **Legacy `?tab=tests`**: Now mounts Tests tab directly. Pre-0792 redirect at RightPanel.tsx ~92 must be removed or no-op'd.
- **0792 E2E specs that assert exactly 4 tabs**: Need migration to assert 5. Likely `e2e/qa-click-audit.spec.ts` or similar.
- **Sub-tab descriptors for Tests**: Tests tab has no sub-modes (unlike Run). `SUB_TAB_DESCRIPTORS["tests"]` is empty or omitted.
- **Empty state**: Source skill with zero cases shows existing TestsPanel empty state (Create Test Case + Generate buttons) — same UX as today's Edit-tab disclosure.

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Tab order conflict with existing 4-tab E2E specs | 0.5 | 2 | 1.0 | Migrate any spec that hardcodes "exactly 4 tabs" to "exactly 5 tabs"; fix the assertion |
| Legacy redirect from 0792 still firing on `?tab=tests` | 0.4 | 1 | 0.4 | Remove the redirect block in RightPanel.tsx |

## Success Metrics

- All ACs pass via vitest + playwright
- Manual smoke: open Studio, click Tests tab, confirm full TestsPanel content visible (filter tabs, cases, history grid)
- vskill 1.0.x patch ships and the user sees Tests tab back at the top level
