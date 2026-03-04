---
increment: 0414-smooth-queue-stats
title: "Smooth Queue Stats Display"
type: feature
priority: P1
status: completed
created: 2026-03-03
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Smooth Queue Stats Display

## Problem Statement

The `/queue` page displays 6 stat cards (Total, Active, Published, Rejected, Blocked, Avg Score). These numbers update in three situations: SSE `state_changed` events trigger optimistic counter changes, a periodic `/api/v1/submissions/stats` fetch refreshes all counts, and a reconciliation effect corrects drift between the live submission list and the KV-cached stats endpoint. Each of these triggers a hard instant jump in the displayed number, which is jarring — particularly for the "Active" card which changes most frequently.

## Goals

- Smooth all number changes on stat cards with a 400ms easeOutCubic animation using requestAnimationFrame
- Show a brief directional indicator (up/down arrow) when a value changes, color-coded green/red
- Visually distinguish cached stats from freshly fetched live stats via a subtle left border accent
- Respect the `prefers-reduced-motion` OS-level accessibility setting by skipping animation entirely
- Introduce zero new npm dependencies (pure rAF approach)

## User Stories

### US-001: Animated Number Transitions
**Project**: vskill-platform
**As a** queue operator
**I want** stat card numbers to animate smoothly when they change
**So that** I can follow value changes without disorienting visual jumps

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given any stat card value changes, when the new value arrives, then the displayed number interpolates from the old value to the new value over 400ms using an easeOutCubic curve, updating via requestAnimationFrame on each frame
- [ ] **AC-US1-02**: Given a user has `prefers-reduced-motion: reduce` set at the OS level, when a stat card value changes, then the new value is shown immediately with no animation (the hook skips the rAF loop)
- [ ] **AC-US1-03**: Given the animation is in progress and a new target value arrives before the current animation completes, when the hook receives the updated target, then the animation restarts from the current animated value to the new target (no queuing, no gap)
- [ ] **AC-US1-04**: Given the `useAnimatedNumber` hook, when the component unmounts mid-animation, then the in-flight `requestAnimationFrame` callback is cancelled via `cancelAnimationFrame` to prevent memory leaks and state updates on unmounted components

### US-002: Direction Indicators on Value Change
**Project**: vskill-platform
**As a** queue operator
**I want** to see a brief directional arrow when a stat number changes
**So that** I can instantly perceive whether the count went up or down without comparing old and new values

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given a stat card value increases, when the animation starts, then a green upward arrow (↑) appears next to the number and fades out after approximately 1500ms
- [ ] **AC-US2-02**: Given a stat card value decreases, when the animation starts, then a red downward arrow (↓) appears next to the number and fades out after approximately 1500ms
- [ ] **AC-US2-03**: Given `prefers-reduced-motion` is active, when a value changes, then direction indicators are shown without fade animation (appear then disappear at 1500ms with no CSS transition)

### US-003: Cached Data Visual Distinction
**Project**: vskill-platform
**As a** queue operator
**I want** to know when stat cards are showing KV-cached data versus freshly fetched data
**So that** I can trust the numbers I see and understand when they might be up to 5 minutes stale

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given the stats were last updated from the KV-cached endpoint (initial load or fetch without live reconciliation), when `StatCard` receives `isCached={true}`, then the card renders with a 3px left border accent in a muted amber/yellow tone (`#B45309` at 40% opacity or equivalent)
- [ ] **AC-US3-02**: Given live data has arrived (reconciliation has run or a fresh `/api/v1/submissions/stats` fetch succeeded), when `StatCard` receives `isCached={false}`, then the left border accent transitions away over 600ms CSS transition and the card returns to its default border style
- [ ] **AC-US3-03**: Given the stat cards grid, when any card shows a cached border accent, then no tooltip or text label is added — the accent is the sole indicator (non-intrusive)

## Out of Scope

- Animating anything other than the six stat card numbers (table rows, submission scores, etc.)
- Server-side changes — this is purely a client-side visual enhancement
- Adding a dedicated "last updated" timestamp to stat cards
- Persisting animation preferences in localStorage or user settings
- Loading skeleton states or shimmer effects

## Technical Notes

### File Targets
- New hook: `src/app/hooks/useAnimatedNumber.ts`
- Modified component: `StatCard` function (inline in `src/app/queue/QueuePageClient.tsx`, around line 1148)
- New prop on `StatCard`: `isCached?: boolean`

### Animation Implementation
- `useAnimatedNumber(target: number, duration = 400)` returns the current animated value as a number
- Uses `performance.now()` for high-resolution timestamps
- easeOutCubic: `1 - Math.pow(1 - t, 3)` where `t` is elapsed/duration clamped to [0, 1]
- Interpolation: `start + (end - start) * eased`
- Detect reduced motion via `window.matchMedia("(prefers-reduced-motion: reduce)").matches` at hook init; if true, return `target` directly without rAF

### Direction Indicator Implementation
- Track previous target in a `useRef` to compute direction on each target change
- Render `↑` or `↓` as a `<span>` next to the value number inside `StatCard`
- CSS `opacity` transition: 0→1 immediately, then 1→0 after 1500ms via `setTimeout` clearing the direction state
- Colors: `#16A34A` (green-600) for up, `#DC2626` (red-600) for down

### Cached State Tracking in QueuePageClient
- Introduce a `statsAreCached` boolean state, initialized to `true`
- Set to `false` after the first successful non-degraded fetch from `/api/v1/submissions/stats`
- Pass `isCached={statsAreCached}` to all six `StatCard` instances
- The reconciliation `setStats` calls do not change `statsAreCached` (they operate on live list data)

### Constraints
- No new npm packages
- The `useAnimatedNumber` hook must be unit-testable with Vitest (fake timers + rAF mock)
- `StatCard` props interface remains backward-compatible (all new props optional)

## Success Metrics

- Zero "jarring jump" observations reported from queue operators after deployment
- Animation frame rate stays at 60fps on M-series Mac and mid-range Chrome on Linux (no dropped frames measured in DevTools)
- `useAnimatedNumber` unit test coverage at 90%+ per increment target
