---
increment: 0657E-dark-theme-followup
title: "Dark-theme token migration followup — admin/queue subtree + QueueStatusBar"
type: refactor
priority: P1
status: planned
parent: 0657-dark-theme-semantic-tokens
created: 2026-04-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Complete dark-theme semantic-token migration for admin/queue subtree + QueueStatusBar

## Overview

Followup to 0657-dark-theme-semantic-tokens. The parent increment successfully migrated `src/app/trust/`, `src/app/admin/*` (except queue subtree), `src/app/queue/QueuePageClient.tsx`, `src/app/components/`, and the shared `src/lib/` modules. A third-round closure review of 0657 surfaced four files that were not in the original file inventory but are in the AC-scoped surface ("all admin pages pass WCAG AA in dark mode", AC-US5-02 queue health badge, AC-US6-09 admin WCAG):

- `src/app/admin/queue/page.tsx` — 15 residual hex literals in tab indicators and StatCards (lines ~446–710)
- `src/app/admin/queue/components.tsx` — 40+ hex literals across SseIndicator, HealthBadge, PauseToggle, and chart primitives
- `src/app/admin/queue/styles.ts` — `pausedBanner`, `errorStyle`, button styles
- `src/app/queue/QueueStatusBar.tsx` — SSE dot (line 82) and `HEALTH_COLORS` fallback (lines 97–98)

The `components.tsx` and `styles.ts` files were extracted from the original `admin/queue/page.tsx` during 0668 (queue page dedup refactor). The extraction preserved pre-existing hex; it did not introduce new literals.

## User Stories

### US-001: Complete dark-theme token coverage for admin/queue (P1)
**Project**: vskill-platform

**As an** admin user operating the vskill-platform queue in dark mode
**I want** all status colors on admin/queue pages to adapt to my theme
**So that** no chart legend, health badge, SSE indicator, or StatCard renders as a light-mode-only color in dark mode.

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `src/app/admin/queue/page.tsx` contains zero hardcoded status hex literals — all status colors use `var(--status-*)` tokens or values sourced from `STATUS_VARS` / `STATE_CONFIG`.
- [ ] **AC-US1-02**: `src/app/admin/queue/components.tsx` contains zero hardcoded status hex literals. SseIndicator, HealthBadge, PauseToggle, StuckRow, StatCard, ThroughputChart, ProcessingTimeChart, DLQRow all use tokens.
- [ ] **AC-US1-03**: `src/app/admin/queue/styles.ts` migrates `pausedBanner`, `errorStyle`, and all destructive/action button styles to tokens.
- [ ] **AC-US1-04**: `src/app/queue/QueueStatusBar.tsx` SSE dot and `HEALTH_COLORS` fallback use tokens.
- [ ] **AC-US1-05**: `grep -rEn '#[0-9A-Fa-f]{6}' src/app/admin/queue/ src/app/queue/QueueStatusBar.tsx | grep -v 'var(--' | grep -v '__tests__'` returns zero hits (except `#FFFFFF` foreground paired with `--status-*-solid` backgrounds, which is intentional).
- [ ] **AC-US1-06**: Admin queue page renders with WCAG AA contrast (≥ 4.5:1) on destructive action buttons in both light and dark themes.

## Functional Requirements

### FR-001: Token usage consistent with 0657
Use the same tokens already defined in `src/app/globals.css` and exposed via `STATUS_VARS` in `src/lib/status-intent.ts`. Do not introduce new CSS variables in this increment.

### FR-002: Preserve observable behavior
The migrated components must render the same visual hierarchy (health = green/amber/red, SSE = green when connected / gray when not, charts use semantic colors for success/failure/retry). No layout shifts.

## Success Criteria

- Global grep across `src/app/admin/queue/` and `src/app/queue/QueueStatusBar.tsx` returns zero residual status hex (excluding intentional `#FFFFFF` on solid backgrounds).
- `npx vitest run` (Node 20) passes at or above 2806-test baseline.
- `npx tsc --noEmit` introduces zero new errors.

## Out of Scope

- New token definitions (use existing `--status-*` tokens).
- Structural refactors (keep the 0668 extraction layout).
- Public queue page (already migrated in 0657).
- Writing per-component snapshot tests (deferred per 0657 F-002 note).

## Dependencies

- 0657-dark-theme-semantic-tokens (parent — must be closed first so `STATUS_VARS` tokens are stable)
- 0668-vskill-platform-audit-fixes (defines the file extraction layout for admin/queue)
