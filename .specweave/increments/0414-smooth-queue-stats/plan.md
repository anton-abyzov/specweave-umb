---
increment: 0414-smooth-queue-stats
architect: sw-sw-architect
created: 2026-03-03
---

# Architecture Plan: Smooth Queue Stats Display

## Overview

Pure client-side visual enhancement to the `/queue` page stat cards. Three
concerns are addressed: animated number transitions (new reusable hook),
directional change indicators (inside `StatCard`), and a cached-data border
accent (new prop on `StatCard`). No server changes, no new npm dependencies.

---

## Component Map

```
QueuePageClient.tsx
│
├── fetchStats()               (existing — adds statsAreCached tracking)
│
├── statsAreCached: boolean    (NEW state — true until first live fetch)
│
└── <StatCard isCached={statsAreCached} ... />   (6 instances, new prop)
         │
         ├── useAnimatedNumber(value, 400)        (NEW hook)
         │         └── rAF loop, easeOutCubic, reduced-motion guard
         │
         ├── direction indicator <span>           (NEW — ↑/↓ with fade-out)
         │
         └── left-border accent (inline style)   (NEW — conditional on isCached)
```

---

## Architecture Decisions

### 1. Hook owns animation math only; direction logic lives in StatCard

`useAnimatedNumber` returns a single interpolated `number`. Direction
tracking, the indicator `<span>`, and the fade-out `setTimeout` live inside
`StatCard` because:
- Direction is a UI concern, not an animation math concern.
- A value-only hook is unit-testable with simple numeric assertions — no DOM
  or indicator timer involved.
- Future consumers can choose different direction UX without changing the hook.

### 2. Reduced-motion detection at effect init (not render)

`window.matchMedia("(prefers-reduced-motion: reduce)").matches` is read once
inside the `useEffect` that starts the rAF loop. This matches the existing
`ScrollFadeIn.tsx` pattern in the codebase. No event listener is needed —
the page is expected to be hard-refreshed if the OS setting changes, and the
visual stakes are low.

### 3. Interrupt-and-restart (no queue)

When a new target arrives mid-animation, the running rAF loop is cancelled
via `cancelAnimationFrame` (happens automatically when the `useEffect`
cleanup fires on dependency change). A new loop starts from the current
animated value. The current value is tracked in a `currentRef` (separate
from React state) to avoid stale-closure issues when reading the start point.

### 4. `statsAreCached` state placement

`QueuePageClient` already owns `stats` state and `fetchStats`. Adding
`statsAreCached` alongside is the minimal change. It initializes to `true`
(first render always shows KV-cached data). It flips to `false` on the first
successful non-degraded stats fetch. Reconciliation `setStats` calls (from
the live-list reconciliation effect) do NOT touch `statsAreCached`.

### 5. No CSS modules — inline styles match codebase convention

`StatCard` and all adjacent components use inline `style` objects throughout
`QueuePageClient.tsx`. The cached border accent is expressed as a conditional
inline style, not a class. The `borderLeft` 600ms transition is added to the
existing `transition` string.

---

## File Targets

### New: `src/app/hooks/useAnimatedNumber.ts`

```typescript
"use client";

import { useState, useEffect, useRef } from "react";

export function useAnimatedNumber(target: number, duration = 400): number {
  const [displayed, setDisplayed] = useState(target);
  const rafRef = useRef<number | null>(null);
  const currentRef = useRef(target);   // tracks latest animated value
  const startRef = useRef(target);     // start value for current animation

  useEffect(() => {
    const reducedMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reducedMotion) {
      currentRef.current = target;
      setDisplayed(target);
      return;
    }

    startRef.current = currentRef.current; // snapshot current value as start
    let startTime: number | null = null;

    const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

    const animate = (now: number) => {
      if (startTime === null) startTime = now;
      const elapsed = now - startTime;
      const t = Math.min(elapsed / duration, 1);
      const value = startRef.current + (target - startRef.current) * easeOutCubic(t);
      currentRef.current = value;
      setDisplayed(value);
      if (t < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    };
  }, [target, duration]);

  return displayed;
}
```

`currentRef` tracks the in-flight animated value between frames without
re-triggering the effect on every frame. On the next target change, the
effect cleanup cancels the old loop and the new effect reads `currentRef`
for its start value — no stale closure.

### Modified: `src/app/queue/QueuePageClient.tsx`

**Change 1 — `statsAreCached` state (near line 83):**
```typescript
const [statsAreCached, setStatsAreCached] = useState(true);
```

**Change 2 — `fetchStats` callback (after `setStats(json)`):**
```typescript
if (!json.degraded) {
  setStatsAreCached(false);
}
```

**Change 3 — `StatCard` props interface:**
```typescript
function StatCard({ label, value, color, highlight, active, onClick, isCached }: {
  label: string;
  value: number;
  color?: string;
  highlight?: boolean;
  active?: boolean;
  onClick?: () => void;
  isCached?: boolean;   // NEW
})
```

**Change 4 — `StatCard` function body additions:**

```typescript
// animated display value
const animatedValue = useAnimatedNumber(value, 400);

// reduced-motion detection (shared for direction indicator)
const reducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// direction indicator
const prevRef = useRef(value);
const [direction, setDirection] = useState<"up" | "down" | null>(null);
const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

useEffect(() => {
  if (value !== prevRef.current) {
    if (timerRef.current) clearTimeout(timerRef.current);
    setDirection(value > prevRef.current ? "up" : "down");
    timerRef.current = setTimeout(() => setDirection(null), 1500);
    prevRef.current = value;
  }
  return () => {
    if (timerRef.current) clearTimeout(timerRef.current);
  };
}, [value]);
```

Rendered value line (replaces `{value.toLocaleString()}`):
```tsx
<div style={{ fontSize: "1.25rem", fontWeight: 700, color: ... }}>
  {Math.round(animatedValue).toLocaleString()}
  {direction && (
    <span style={{
      color: direction === "up" ? "#16A34A" : "#DC2626",
      fontSize: "0.75rem",
      marginLeft: "4px",
      opacity: 1,
      transition: reducedMotion ? "none" : "opacity 200ms ease",
    }}>
      {direction === "up" ? "↑" : "↓"}
    </span>
  )}
</div>
```

Outer `<div>` style additions (cached border):
```typescript
borderLeft: isCached ? "3px solid rgba(180, 83, 9, 0.4)" : "3px solid transparent",
transition: "all 200ms ease, border-left 600ms ease",
```

Using `transparent` avoids layout shift — the 3px space is always reserved.

**Change 5 — 6 `<StatCard>` call sites (lines ~586-626):**
```tsx
<StatCard ... isCached={statsAreCached} />
```

---

## Data Flow

```
SSE event        → optimistic setStats()           ─┐
Periodic fetch   → setStats() + setStatsAreCached() ├─► stats + cached state
Reconciliation   → setStats()                      ─┘

stats.{total,active,...}  ──►  StatCard value prop
                                      │
                         useAnimatedNumber(value, 400)
                                      │
                              currentRef tracks float
                                      │
                         Math.round(animated).toLocaleString()
                                      │
                                  rendered

statsAreCached ──► isCached prop ──► borderLeft style
```

---

## Testing Strategy

### `useAnimatedNumber` — Vitest unit tests

Mock `requestAnimationFrame` globally; drive frames manually by capturing and
calling the registered callback. Use `vi.useFakeTimers()` where needed.

```typescript
// rAF mock pattern
let rafCallback: FrameRequestCallback | null = null;
vi.stubGlobal("requestAnimationFrame", (cb: FrameRequestCallback) => {
  rafCallback = cb;
  return 1;
});
vi.stubGlobal("cancelAnimationFrame", vi.fn());

const driveFrame = (elapsed: number) => rafCallback?.(elapsed);
```

AC coverage:
- **AC-US1-01**: After driving frames totaling 400ms, returned value equals target.
- **AC-US1-02**: `matchMedia` returns `matches: true` → value equals target immediately, no rAF loop entered.
- **AC-US1-03**: Change target mid-animation → new animation starts from current animated value, not from original start.
- **AC-US1-04**: Unmount → `cancelAnimationFrame` called with the active rAF ID.

`matchMedia` mock:
```typescript
vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({
  matches: false,
  addListener: vi.fn(),
  removeListener: vi.fn(),
}));
```

### `StatCard` changes — React Testing Library component tests

- Direction `↑` appears with `color: #16A34A` when value increases.
- Direction `↓` appears with `color: #DC2626` when value decreases.
- No direction span when value is unchanged.
- `isCached={true}` → `borderLeft` contains `rgba(180, 83, 9, 0.4)`.
- `isCached={false}` → `borderLeft` is `3px solid transparent`.
- After 1500ms (fake timer), direction span is removed.

---

## Technical Challenges

### Challenge 1: Stale closure for animation start value
**Problem**: Reading React state inside a `useEffect` captures the value at
closure time. If `displayed` is listed as a dependency, the effect re-runs
every frame — defeating the rAF loop pattern.
**Solution**: `currentRef` tracks the live animated value outside React state.
Effect reads `currentRef.current` for the start snapshot without needing
`displayed` as a dependency.

### Challenge 2: `borderLeft` overriding `border` shorthand
**Problem**: CSS shorthand `border` sets all four sides. Adding `borderLeft`
after `border` in an inline style object will be overridden by the shorthand
in the next render.
**Solution**: Place `borderLeft` in the style object AFTER `border` — inline
styles are applied as object properties and the last value wins. Alternatively,
use `borderLeftWidth` and `borderLeftColor` as separate properties.
**Mitigation**: Test visually; write a component test asserting computed style.

### Challenge 3: `window.matchMedia` in SSR/test environments
**Problem**: `window` is undefined in Node.js (SSR build, Vitest with jsdom
misconfigured).
**Solution**: Guard with `typeof window !== "undefined"` before calling.
Treat absence as `matches: false` (animation enabled). Vitest provides jsdom
where `matchMedia` exists but must be mocked.

---

## Technology Stack

- **Language**: TypeScript (strict, ESM)
- **Framework**: React 18 (hooks), Next.js 15 app router
- **Animation**: browser `requestAnimationFrame` — no library
- **Testing**: Vitest + React Testing Library (existing stack)
- **New dependencies**: none

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Stale closure on interrupt-restart | Medium | `currentRef` pattern — documented above |
| `borderLeft` overridden by `border` shorthand | Low | Inline style object property order; component test |
| `matchMedia` undefined in test env | Low | `typeof window` guard; Vitest jsdom mock |
| `setTimeout` not cleared on unmount | Low | Return `clearTimeout` in `useEffect` cleanup |
| `Math.round` causes ±1 flicker near integer boundary | Low | Acceptable; standard for counter animation |

---

## Out of Scope

- No change to the stats API endpoint.
- No change to `useSubmissionStream` or SSE infrastructure.
- No animation outside the 6 `StatCard` instances (no table rows, no scores).
- No localStorage persistence of animation preferences.
- No new npm packages.
