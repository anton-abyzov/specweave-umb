---
increment: 0414-smooth-queue-stats
title: "Smooth Queue Stats Display"
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005, T-006]
tasks_total: 6
tasks_completed: 6
---

# Tasks: Smooth Queue Stats Display

## User Story: US-001 - Animated Number Transitions

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed

---

### T-001: Implement `useAnimatedNumber` hook

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a component using `useAnimatedNumber(target, 400)`
- **When** the target value changes
- **Then** the hook interpolates from old to new value over 400ms using easeOutCubic via requestAnimationFrame

**Test Cases**:
1. **Unit**: `src/app/hooks/__tests__/useAnimatedNumber.test.tsx`
   - `testAnimatesFromOldToNewValue()`: Drive rAF frames totaling 400ms; assert returned value equals target at completion (AC-US1-01)
   - `testIntermediateValueIsInterpolated()`: At 200ms mark, returned value is between start and target following easeOutCubic (AC-US1-01)
   - `testReducedMotionSkipsRaf()`: Mock matchMedia returns `matches: true`; assert value equals target immediately with no rAF loop entered (AC-US1-02)
   - `testInterruptAndRestartFromCurrentValue()`: Change target mid-animation at 200ms; assert new animation starts from current animated value, not original start (AC-US1-03)
   - `testCancelAnimationFrameOnUnmount()`: Unmount component mid-animation; assert `cancelAnimationFrame` called with the active rAF ID (AC-US1-04)
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/hooks/useAnimatedNumber.ts` with `"use client"` directive
2. Implement `useAnimatedNumber(target: number, duration = 400): number` using `useState`, `useEffect`, `useRef`
3. Read `prefers-reduced-motion` via `window.matchMedia` guarded with `typeof window !== "undefined"` check; if true, skip rAF and return target directly
4. Use `startRef` (snapshot at animation start) and `currentRef` (live animated float) to avoid stale closure
5. easeOutCubic: `1 - Math.pow(1 - t, 3)` where `t = Math.min(elapsed / duration, 1)`
6. Cleanup: cancel in-flight rAF via `cancelAnimationFrame(rafRef.current)` in `useEffect` return
7. On target dependency change, effect cleanup cancels the old loop; new effect reads `currentRef.current` as start value

---

### T-002: Write unit tests for `useAnimatedNumber`

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `useAnimatedNumber` hook and mocked `requestAnimationFrame` / `matchMedia` globals
- **When** tests drive frames manually by capturing and invoking the registered callback
- **Then** all four ACs are verified with numeric assertions on the returned value

**Test Cases**:
1. **Unit**: `src/app/hooks/__tests__/useAnimatedNumber.test.tsx`
   - rAF mock pattern: `vi.stubGlobal("requestAnimationFrame", cb => { rafCallback = cb; return 1; })`
   - matchMedia mock: `vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: false }))`
   - `driveFrame(elapsed)`: helper calls `rafCallback?.(elapsed)` to advance animation
   - All five test cases from T-001 implemented and passing
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/hooks/__tests__/useAnimatedNumber.test.tsx`
2. Set up `vi.stubGlobal` mocks for `requestAnimationFrame`, `cancelAnimationFrame`, `matchMedia` in `beforeEach`
3. Implement `driveFrame(elapsed: number)` helper
4. Write all five test cases from T-001 test plan
5. Run `npx vitest run src/app/hooks/__tests__/useAnimatedNumber.test.tsx` and confirm all pass

---

## User Story: US-002 - Direction Indicators on Value Change

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 2 total, 2 completed

---

### T-003: Add direction indicator to `StatCard`

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** a `StatCard` rendering a numeric value
- **When** the value prop increases or decreases
- **Then** a colored arrow span appears next to the number and disappears after 1500ms

**Test Cases**:
1. **Integration**: `src/app/queue/__tests__/StatCard.test.tsx`
   - `testUpArrowAppearsOnIncrease()`: Re-render with higher value; assert `↑` span present with `color: #16A34A` (AC-US2-01)
   - `testDownArrowAppearsOnDecrease()`: Re-render with lower value; assert `↓` span present with `color: #DC2626` (AC-US2-02)
   - `testNoArrowWhenValueUnchanged()`: Re-render with same value; assert neither `↑` nor `↓` in DOM (AC-US2-01/02)
   - `testArrowFadesAfter1500ms()`: Use `vi.useFakeTimers()`; advance 1500ms; assert direction span removed (AC-US2-01/02)
   - `testNoFadeTransitionWhenReducedMotion()`: Mock matchMedia `matches: true`; assert direction span has `transition: none` (AC-US2-03)
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/app/queue/QueuePageClient.tsx`, locate the `StatCard` function (around line 1148)
2. Add `useRef`, `useState`, `useEffect` imports if not already present
3. Inside `StatCard`, add: `prevRef = useRef(value)`, `direction` state (`"up" | "down" | null`), `timerRef` for the setTimeout handle
4. Add `useEffect` watching `value`: on change, set direction, schedule `setTimeout(() => setDirection(null), 1500)`, clear timer on cleanup
5. Render `<span>` next to value displaying `↑` or `↓`; color `#16A34A` for up, `#DC2626` for down
6. Apply `transition: reducedMotion ? "none" : "opacity 200ms ease"` on the span's inline style
7. Read `reducedMotion` via `window.matchMedia` with the `typeof window !== "undefined"` guard

---

### T-004: Integrate `useAnimatedNumber` into `StatCard`

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** `StatCard` rendering with `useAnimatedNumber`
- **When** the value prop changes
- **Then** the displayed number is the animated (interpolated) value rounded to an integer

**Test Cases**:
1. **Integration**: `src/app/queue/__tests__/StatCard.test.tsx`
   - `testDisplaysRoundedAnimatedValue()`: With rAF mocked, value starts at 0 and target is 100; after partial frame, displayed value is between 0 and 100 (AC-US1-01 integration)
   - **Coverage Target**: 85%

**Implementation**:
1. Import `useAnimatedNumber` from `../../hooks/useAnimatedNumber` inside `QueuePageClient.tsx`
2. Inside `StatCard`, call `const animatedValue = useAnimatedNumber(value, 400)`
3. Replace `{value.toLocaleString()}` with `{Math.round(animatedValue).toLocaleString()}`
4. Ensure direction indicator still compares raw `value` prop (not `animatedValue`) for direction logic

---

## User Story: US-003 - Cached Data Visual Distinction

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 2 total, 2 completed

---

### T-005: Add `isCached` prop and border accent to `StatCard`

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** a `StatCard` with `isCached` prop
- **When** `isCached={true}` or `isCached={false}`
- **Then** the card's left border accent shows amber when cached and is transparent when live

**Test Cases**:
1. **Integration**: `src/app/queue/__tests__/StatCard.test.tsx`
   - `testCachedBorderAppearsWhenCached()`: Render with `isCached={true}`; assert container `borderLeft` contains `rgba(180, 83, 9, 0.4)` (AC-US3-01)
   - `testCachedBorderClearsWhenLive()`: Render with `isCached={false}`; assert container `borderLeft` is `3px solid transparent` (AC-US3-02)
   - `testNoTooltipOrLabelForCachedState()`: Render with `isCached={true}`; assert no `title` attribute and no text "cached" or "stale" in the component (AC-US3-03)
   - **Coverage Target**: 85%

**Implementation**:
1. Add `isCached?: boolean` to the `StatCard` props interface (backward-compatible — optional)
2. In the outer container `<div>` style object, add:
   - `borderLeft: isCached ? "3px solid rgba(180, 83, 9, 0.4)" : "3px solid transparent"`
   - `transition: "all 200ms ease, border-left 600ms ease"` (appended to existing transition string)
3. Place `borderLeft` after any existing `border` shorthand in the style object so it wins (inline style last-write-wins rule)
4. Do not add tooltip, title attribute, or any text label (AC-US3-03)

---

### T-006: Add `statsAreCached` state to `QueuePageClient` and wire to `StatCard` instances

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** `QueuePageClient` with `statsAreCached` state initialized to `true`
- **When** a successful non-degraded stats fetch completes
- **Then** `statsAreCached` flips to `false` and all six `StatCard` instances lose the amber border

**Test Cases**:
1. **Integration**: `src/app/queue/__tests__/QueuePageClient.test.tsx`
   - `testStatCardsReceiveIsCachedTrue()`: On initial render before any fetch completes, assert `isCached={true}` passed to StatCard (AC-US3-01)
   - `testStatCardsReceiveIsCachedFalseAfterLiveFetch()`: Mock `fetch` returning `{ degraded: false, ... }`; trigger fetchStats; assert `isCached={false}` passed to StatCard (AC-US3-02)
   - `testDegradedFetchDoesNotClearCachedFlag()`: Mock `fetch` returning `{ degraded: true, ... }`; trigger fetchStats; assert `isCached` remains `true` (AC-US3-01)
   - **Coverage Target**: 85%

**Implementation**:
1. In `QueuePageClient.tsx`, add `const [statsAreCached, setStatsAreCached] = useState(true)` near the other stats state declarations (around line 83)
2. In the `fetchStats` callback, after `setStats(json)`, add: `if (!json.degraded) { setStatsAreCached(false); }`
3. Reconciliation `setStats` calls must NOT call `setStatsAreCached` — leave them untouched
4. Pass `isCached={statsAreCached}` to all 6 `<StatCard>` instances (lines ~586-626)
5. Run `npx vitest run` to confirm all tests pass; run `npx playwright test` if E2E suite covers the queue page
