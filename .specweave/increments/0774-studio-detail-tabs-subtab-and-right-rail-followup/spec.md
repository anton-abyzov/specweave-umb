---
increment: 0774-studio-detail-tabs-subtab-and-right-rail-followup
title: >-
  Studio detail page: SubTabBar (Run/Trigger sub-modes) + Overview right-rail
  (Setup/Credentials)
type: feature
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio detail page — SubTabBar (Run/Trigger sub-modes) + Overview right-rail (Setup/Credentials)

## Overview

Direct follow-up to **0769**. Picks up the four items 0769 deferred:

1. **SubTabBar** UX descoped from 0769 (T-021/T-022) — Run tab gets `Run | History | Models` sub-modes; Trigger tab gets `Run | History`.
2. **Deps content → SkillOverview right-rail** (0769 T-025) — `Setup` (MCP/skill deps) + `Credentials` sections in a 280px right column at viewports ≥ 900px.
3. **F-004 safeActive correctness fix** from 0769 code-review (one-render ARIA mismatch when consumer deep-links to a hidden author tab).
4. (Out of scope, deferred again) `@testing-library/react` infra — heavy dep, separate increment.

## Background

0769 shipped the persona-conditional 6/3 tab bar, the Activation→Trigger label rename, the path-chip + install-method fixes, the file-tree allowlist, and the CheckNow gate. It explicitly descoped the SubTabBar UX and the Deps→right-rail relocation so 0769 could ship in a single increment without merge churn.

The HistoryPanel, LeaderboardPanel, and ActivationPanel already exist as standalone panels (605 / 526 / 586 lines respectively). They need no rewrites — only mounting as children inside a SubTabBar.

The DepsPanel today is 47 lines: `McpDependencies` + `CredentialManager`. Both components are reusable; relocating them into SkillOverview is composition, not rewriting.

## Scope

**In scope:**
- New `src/eval-ui/src/components/SubTabBar.tsx` — descriptor-driven sub-tab bar.
- `RightPanel.tsx` reads/writes `?sub=` URL param; `WorkspacePanel` dispatches on `(active, sub)`.
- Run tab sub-modes: `Run | History | Models` (default: `Run`).
- Trigger tab sub-modes: `Run | History` (default: `Run`).
- `SkillOverview.tsx` becomes a 2-column grid at ≥ 900px (main + 280px right-rail).
- New `SkillOverviewRightRail.tsx` — `Setup` (MCP + skill deps) + `Credentials` sections.
- F-004 fix: `safeActive` (post-redirect) replaces pre-redirect `active` in `WorkspaceTabSync` and `WorkspacePanel`.
- DepsPanel and the standalone `?panel=deps` deep-link kept for back-compat (existing bookmarks don't 404).

**Out of scope:**
- `Compare` sub-mode UI under Run (separate UX task).
- `@testing-library/react` infra.
- Any backend route changes.

## Glossary

- **SubTabBar** — secondary tab bar nested inside a top-level tab. Renders below the top-level tab bar, uses smaller font (12px) and tighter padding to visually nest.
- **safeActive** — `applyPersonaRedirect(active, isReadOnly)` result. The "real" tab the user sees, after the consumer redirect (0769 T-024).

## User Stories

### US-001: Run tab exposes History and Models as sub-modes (P2)
**Project**: vskill

**As an** author working in the Run tab
**I want** History and Models (cross-model leaderboard) accessible as sub-tabs of Run
**So that** I have one mental model for "what does this skill produce" — execute it, see past runs, compare across models — without switching top-level tabs

**Acceptance Criteria:**
- [x] **AC-US1-01**: Run tab renders a SubTabBar with three sub-tabs: `Run` (default), `History`, `Models`.
- [x] **AC-US1-02**: Selecting `History` mounts the existing `HistoryPanel` content; `Models` mounts the existing `LeaderboardPanel`; `Run` mounts the existing `RunPanel`. No rewrites.
- [x] **AC-US1-03**: URL encoding: `?panel=run&sub=history` round-trips. Switching top-level tab drops `?sub=` from URL.
- [x] **AC-US1-04**: Unknown `?sub=` value falls back to the tab's default sub-mode and the URL is canonicalized on next render.

### US-002: Trigger tab exposes activation history as a sub-mode (P2)
**Project**: vskill

**As a** user working in the Trigger tab
**I want** past activation runs in a `History` sub-tab beside the live `Run` view
**So that** I can switch between "test a new prompt" and "see what fired before" without scrolling through one combined panel

**Acceptance Criteria:**
- [x] **AC-US2-01**: Trigger tab renders a SubTabBar with two sub-tabs: `Run` (default), `History`.
- [x] **AC-US2-02**: `History` mounts the activation-history list (extracted from ActivationPanel's existing in-panel history) or the full ActivationPanel if extraction is non-trivial.
- [x] **AC-US2-03**: URL: `?panel=trigger&sub=history` round-trips.

### US-003: Overview gains a right-rail with Setup + Credentials (P2)
**Project**: vskill

**As a** user landing on the Overview tab
**I want** dependency and credential information visible without clicking into a separate Deps tab
**So that** the page reads as a complete model card — what it is, how it performs, what it needs to run

**Acceptance Criteria:**
- [x] **AC-US3-01**: At viewports ≥ 900px, SkillOverview renders a 2-column grid with main content (header + metric grid + publish status) on the left and a 280px right-rail on the right.
- [x] **AC-US3-02**: Right-rail has two sections: `Setup` (renders `McpDependencies` content) and `Credentials` (renders `CredentialManager`).
- [x] **AC-US3-03**: Below 900px the right-rail collapses below the metric grid (single-column responsive).
- [x] **AC-US3-04**: The standalone Deps tab via `?panel=deps` deep-link continues to work for back-compat.

### US-004: One-render ARIA correctness on consumer deep-link (P3)
**Project**: vskill

**As a** consumer who deep-links to a workbench tab (`?tab=editor`)
**I want** WorkspaceTabSync and WorkspacePanel to receive the post-redirect tab id
**So that** the panel content matches the bar selection on the very first render — no one-frame ARIA mismatch

**Acceptance Criteria:**
- [x] **AC-US4-01**: `WorkspaceTabSync` and `WorkspacePanel` are passed `safeActive` (post `applyPersonaRedirect`) instead of pre-redirect `active`.
- [x] **AC-US4-02**: No regression in author-tab behavior (where `safeActive === active`).

### US-005: Build + smoke verification (P2)
**Project**: vskill

**As a** developer landing this increment
**I want** `npx tsc --noEmit`, `npm run build`, and `npm run build:eval-ui` to all pass cleanly
**So that** the studio bundle is ship-ready

**Acceptance Criteria:**
- [x] **AC-US5-01**: `npx tsc --noEmit` PASS.
- [x] **AC-US5-02**: `npm run build` PASS.
- [x] **AC-US5-03**: `npm run build:eval-ui` PASS (Vite bundle).
- [x] **AC-US5-04**: Full vitest suite shows no NEW failures vs the pre-0774 baseline (pre-existing flakes documented in 0769 closure remain unchanged).

## Risks

- **Sub-tab URL state collision** — if two `useEffect` writes to the URL race (top-level tab change + sub-tab change), the URL could end up with a stale `?sub=`. Mitigation: single effect that reads (active, sub) and writes both params atomically.
- **Right-rail fetch overhead** — McpDependencies and CredentialManager each fetch on mount. If both fetch immediately on Overview render, that's 2 extra round-trips users who don't care about Setup never wanted. Mitigation: lazy-mount the right-rail (only when viewport ≥ 900px) and accept the trade-off for now; future optimization is to move detail fetches behind a toggle.
- **HistoryPanel/LeaderboardPanel mount cost** — both panels fetch their data on mount. Switching sub-tabs causes a re-fetch. Acceptable trade-off; both panels have their own loading skeletons.
