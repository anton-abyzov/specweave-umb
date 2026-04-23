---
increment: 0681-studio-update-notifications
title: Studio Update Notifications — Technical Plan
type: plan
status: draft
created: 2026-04-23
architect: sw-architect
design_authority: sw:architect
---

# Plan: Studio Update Notifications

> **Scope clarification.** UI-only integration of the existing update-detection backend into the main `vskill studio` chrome. No backend route changes, no CLI changes. All four UI surfaces share a single polling hook. The standalone `UpdatesPanel` page is reused unchanged — this increment plumbs the same data into the rest of the chrome.

---

## 0. Design Direction (inherited from 0674)

- Warm-neutral visual language (`--color-paper`, `--color-own` amber for "Own" / update signals, `--color-installed` quiet green, `--color-accent` tan ≤5% surface).
- No shimmers, no celebration language, no emoji in product strings.
- Voice: short declarative sentences, period-terminated toasts, "Refreshing…" not "Please wait…".
- Motion budget: 120–180ms cubic-bezier(0.2, 0, 0, 1); respects `prefers-reduced-motion`.

This increment inherits and applies all of 0674's design tokens and voice rules without adding new ones.

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│ StudioContext (providers mount once)                                 │
│   useSkillUpdates()  ──┐                                             │
│                        ├─► updatesMap: Map<skillName, SkillUpdateInfo>│
│                        ├─► updateCount: number                       │
│                        ├─► outdatedPerOrigin: { source, installed }  │
│                        ├─► refresh: () => Promise<void>              │
│                        └─► lastFetchAt, isRefreshing                 │
└──────────────────────────────────────────────────────────────────────┘
          │                                  │
          │                                  │
          ▼                                  ▼
┌───────────────────────┐       ┌───────────────────────────────────────┐
│ SkillRow              │       │ TopRail                               │
│  ↑ glyph (if outdated)│       │   <UpdateBell count={updateCount} />  │
│  (merged via          │       │     └─► <UpdateBellDropdown>          │
│   mergeUpdatesInto-   │       │           list of outdated + refresh  │
│   Skills before store)│       └───────────────────────────────────────┘
└───────────────────────┘
          │
          ▼
┌──────────────────────────────────┐     ┌─────────────────────────────┐
│ SidebarSection header            │     │ RightPanel Overview tab     │
│  "Installed · Claude · 3 updates"│     │   <UpdateAction skill={..}> │
│  (clickable → #/updates)          │     │     Update to 1.4.0         │
└──────────────────────────────────┘     │     Preview changelog ▸     │
                                         │     (SSE progress inline)   │
                                         └─────────────────────────────┘
```

### 1.1 Data flow

1. `StudioContext` invokes `useSkillUpdates()` at app root (once). The hook owns the poll timer, in-flight request dedup, and visibility listener.
2. The hook's result (array of `SkillUpdateInfo`) is normalized into a `Map<skillName, info>` plus per-origin counts.
3. `StudioContext` runs `mergeUpdatesIntoSkills(skills, updates)` (existing helper, `src/eval-ui/src/api.ts:409`) so every downstream consumer reads a `SkillInfo` with `updateAvailable`, `currentVersion`, `latestVersion` already populated.
4. `<UpdateBell />`, `<SidebarSection>` header chips, `<UpdateAction />` all read from context — no duplicate fetches.

### 1.2 Why polling (ADR-0681-01)

See ADR in §6.

---

## 2. Component Inventory

### 2.1 New components

| File | Purpose | Approx LoC |
|---|---|---|
| `src/eval-ui/src/hooks/useSkillUpdates.ts` | Polling hook with visibility-pause, debounce, dedup | ~110 |
| `src/eval-ui/src/components/UpdateBell.tsx` | Bell icon + count badge in TopRail right cluster | ~80 |
| `src/eval-ui/src/components/UpdateBellDropdown.tsx` | Popover listing outdated skills, refresh, view-all | ~200 |
| `src/eval-ui/src/components/UpdateAction.tsx` | RightPanel block: button + SSE progress + changelog toggle | ~160 |

### 2.2 Modified components

| File | Change |
|---|---|
| `src/eval-ui/src/components/SkillRow.tsx` | Lines 118–143: replace `update` pill with 10×10px `↑` glyph + `title` tooltip + `data-testid="skill-row-update-glyph"`. Wrap `SkillRow` with `React.memo`. |
| `src/eval-ui/src/components/SidebarSection.tsx` | Add `updateCount?: number` prop; render `{N} updates ▾` chip after count when `updateCount > 0`, wired to `window.location.hash = "#/updates"`. `event.stopPropagation()` in chip onClick to avoid toggling collapse. |
| `src/eval-ui/src/components/TopRail.tsx` | Mount `<UpdateBell />` between `<ModelSelector />` (line 155) and the `⌘K` button (line 158). |
| `src/eval-ui/src/components/RightPanel.tsx` | In the Overview tab body (where `MetadataTab` is rendered), render `<UpdateAction skill={selectedSkillInfo} />` before `MetadataTab` so the CTA is visually above the metadata. Import `UpdateAction`. |
| `src/eval-ui/src/StudioContext.tsx` | Call `useSkillUpdates()` once in the provider; add `updates`, `updateCount`, `outdatedByOrigin`, `refreshUpdates` to the exposed context value. Merge updates into `state.skills` before it leaves the provider so every SkillRow sees `updateAvailable`. |

### 2.3 Components explicitly **not** touched

- `src/eval-ui/src/pages/UpdatesPanel.tsx` — reused as-is.
- `src/eval-ui/src/components/ChangelogViewer.tsx` — consumed, not modified.
- `src/eval-ui/src/hooks/useOptimisticAction.ts` — consumed, not modified.
- Anything under `src/eval-server/**`.

---

## 3. The `useSkillUpdates()` Hook — Contract

```ts
interface SkillUpdatesState {
  updates: SkillUpdateInfo[];          // raw list from /api/skills/updates
  updatesMap: Map<string, SkillUpdateInfo>; // keyed by short skill name
  updateCount: number;                 // outdated skills only
  outdatedByOrigin: { source: number; installed: number };
  isRefreshing: boolean;
  lastFetchAt: number | null;
  error: Error | null;
}

interface UseSkillUpdatesReturn extends SkillUpdatesState {
  refresh: () => Promise<void>;        // dedup'd — concurrent calls share promise
}

export function useSkillUpdates(opts?: {
  intervalMs?: number;       // default 300_000 (5 min)
  debounceMs?: number;       // default 500
  timeoutMs?: number;        // default 15_000 per fetch
}): UseSkillUpdatesReturn;
```

### 3.1 State machine

```
           mount (visible)
                │
                ▼
        ┌─────────────┐   visibilitychange → hidden
        │  RUNNING    │───────────────────────────────┐
        │ (timer on)  │                                │
        └─────────────┘                                ▼
                │                               ┌───────────────┐
                │  timer tick / refresh()       │   PAUSED      │
                ▼                               │ (timer off)   │
        ┌─────────────┐                         └───────────────┘
        │  FETCHING   │                                │
        │ (dedup'd)   │                                │ visibilitychange → visible
        └─────────────┘                                │ + 500ms debounce
                │                                      ▼
                ▼                               ┌───────────────┐
        ┌─────────────┐ ◄──────────────────────│ RESUMING      │
        │  IDLE-WAIT  │                        │ (fetch if     │
        │ (timer on)  │                        │  >60s stale)  │
        └─────────────┘                        └───────────────┘
```

### 3.2 Dedup rule

```ts
let inFlight: Promise<void> | null = null;
async function refresh() {
  if (inFlight) return inFlight;
  inFlight = doFetch().finally(() => { inFlight = null; });
  return inFlight;
}
```

### 3.3 Timeout

Each fetch wraps `api.getSkillUpdates()` with an `AbortController` + `setTimeout(timeoutMs, abort)`. On timeout, `error` is set to `new Error("TIMEOUT")`, the previous `updates` stay in place (stale data beats blank state), and the next scheduled poll runs normally.

### 3.4 Initial fetch

On mount: if `lastFetchAt === null` OR `Date.now() - lastFetchAt > 60_000`, call `refresh()` inside `requestIdleCallback` (fallback: `setTimeout(0)`).

---

## 4. SkillRow Glyph — Markup Contract

Before (current, lines 118–143):
```jsx
{skill.updateAvailable && (
  <span /* large chip with icon + "update" text */>…</span>
)}
```

After:
```jsx
{skill.updateAvailable && (
  <span
    data-testid="skill-row-update-glyph"
    title={
      skill.latestVersion
        ? `Update available: ${skill.currentVersion ?? ""} → ${skill.latestVersion}`
        : "Update available"
    }
    aria-label="Update available"
    style={{ color: "var(--color-own)", display: "inline-flex", flexShrink: 0 }}
  >
    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 19V5" />
      <path d="M5 12l7-7 7 7" />
    </svg>
  </span>
)}
```

Notable: `currentColor` + `var(--color-own)` means theme switch is free (both themes already define `--color-own`).

---

## 5. UpdateBell + Dropdown — Markup Contract

```jsx
<button
  type="button"
  aria-label={count === 0 ? "No updates available" : `${count} updates available, open summary`}
  aria-haspopup="dialog"
  aria-expanded={open}
  onClick={toggle}
>
  <img src={updateBellIcon} width={14} height={14} alt="" />
  {count > 0 && (
    <span data-testid="update-bell-badge">{count > 9 ? "9+" : count}</span>
  )}
</button>

{open && (
  <UpdateBellDropdown
    updates={updates}
    onRefresh={refresh}
    isRefreshing={isRefreshing}
    onSelectSkill={(s) => { selectSkill(s); close(); }}
    onViewAll={() => { window.location.hash = "#/updates"; close(); }}
    onClose={close}
  />
)}
```

`UpdateBellDropdown` is **dynamically imported** via `React.lazy()`:
```ts
const UpdateBellDropdown = React.lazy(() => import("./UpdateBellDropdown"));
```
— so the closed bell is ≤2 KB gzipped and the dropdown code only loads on first open.

### 5.1 Semver bump classification

```ts
function classifyBump(installed: string, latest: string): "major" | "minor" | "patch" {
  const [iMaj, iMin] = installed.split(".").map(Number);
  const [lMaj, lMin] = latest.split(".").map(Number);
  if (!Number.isFinite(iMaj) || !Number.isFinite(lMaj)) return "patch";
  if (lMaj > iMaj) return "major";
  if (lMin > iMin) return "minor";
  return "patch";
}
```

(Borrowed directly from `UpdatesPanel.tsx` to keep one implementation. Extract to `src/eval-ui/src/utils/semverBump.ts` as part of T-006 so both surfaces share it.)

---

## 6. UpdateAction — SSE + Optimistic Action Flow

```ts
const updateAction = useOptimisticAction<[], ActionSnapshot>({
  snapshot: () => ({ wasUpdating: false }),
  apply: () => setLocalStatus("updating"),
  commit: () => runSingleUpdateSSE(skill),       // resolves on `done`, rejects on `error`/timeout
  rollback: () => setLocalStatus("idle"),
  failureMessage: (err) => `Couldn't update ${skill.skill} — ${(err as Error).message}`,
  timeoutMs: 60_000,   // overrides the 5s default for long-running updates
});

function runSingleUpdateSSE(skill: SkillInfo): Promise<void> {
  return new Promise((resolve, reject) => {
    const es = api.startSingleUpdate(skill.plugin, skill.skill); // existing helper
    const timer = setTimeout(() => { es.close(); reject(new Error("TIMEOUT")); }, 60_000);
    es.addEventListener("progress", (e: MessageEvent) => {
      const { status } = JSON.parse(e.data);
      setProgressStatus(status);
    });
    es.addEventListener("done", () => { clearTimeout(timer); es.close(); refreshUpdates(); resolve(); });
    es.addEventListener("error", (e: MessageEvent) => {
      clearTimeout(timer); es.close();
      const payload = typeof e.data === "string" ? JSON.parse(e.data) : { error: "Stream error" };
      reject(new Error(payload.error ?? "Unknown error"));
    });
  });
}
```

On success, `refreshUpdates()` (from context) invalidates the update map, so the row glyph / section chip / bell badge all update in the same tick.

---

## 7. ADRs

### ADR-0681-01 — Polling over push-SSE for update discovery

**Status**: Accepted.

**Context**: We need the studio to reflect "is there an update?" state without the user clicking refresh. Two options:
- (A) Poll `GET /api/skills/updates` on a timer.
- (B) Open a server-push SSE stream that broadcasts `update-available` events as the backend discovers them.

**Decision**: Poll.

**Rationale**:
1. **Low frequency signal**. `vskill outdated` runs upstream-lookup against the registry; new versions are published hours-to-days apart, not seconds. A 5-minute poll is well-matched to the real-world update cadence.
2. **Browser resource cost**. An always-open SSE stream per tab would keep a connection alive and require backend fan-out for no observable benefit at this cadence.
3. **Visibility-aware pause is trivial with polling** (`visibilitychange` + clear interval). Equivalent SSE pause requires explicit client disconnect-and-reconnect.
4. **Backend simplicity**. The existing `GET /api/skills/updates` is synchronous and trivially idempotent. A push stream would need a background watcher, an in-memory change-detector, and a broadcast channel — scope creep for the gain.
5. **Dedup and cancellation semantics** are straightforward with fetch + AbortController; much fuzzier with long-lived SSE.

**Consequences**:
- Up to 5 minutes of latency between a new version appearing in the registry and the badge showing up. Acceptable.
- Manual `Refresh` action in the dropdown covers the "I just ran `vskill install` in a terminal, want the UI to catch up now" case.
- If future requirements demand sub-minute latency we revisit (keyword: "real-time update notifications") — but not in 0681.

### ADR-0681-02 — Mount the polling hook at the provider root, not per-consumer

**Status**: Accepted.

**Context**: Four surfaces need update state. Options:
- (A) Each component calls `useSkillUpdates()` independently — 4× timers, 4× fetches.
- (B) Mount once at the provider and share via context.

**Decision**: Mount at `StudioContext` and share via context (FR-001, FR-005).

**Rationale**: Option A violates FR-005 (no duplicate polling) and compounds network/battery cost linearly with surface count. Option B is idiomatic for "singleton side-effect driven by React lifecycle" and aligns with how `StudioContext` already owns `skills`, `selection`, `preferences`.

**Consequences**: Components become simpler (they just read from `useStudio()`), and adding a fifth surface (e.g., a Command Palette entry) costs no extra fetch.

### ADR-0681-03 — Lazy-load `UpdateBellDropdown`

**Status**: Accepted.

**Context**: NFR-004 caps bundle growth at 8 KB gzipped. The dropdown brings ~200 LoC of markup + focus-trap + semver-classify logic.

**Decision**: `React.lazy()` the dropdown; keep the closed bell ≤2 KB.

**Rationale**: Most sessions won't click the bell. Shipping the dropdown code in the initial chunk would waste bytes on cold loads.

**Consequences**: First open has a ~50ms chunk-fetch delay on slow networks. Acceptable — the dropdown is non-critical and we render a small `Loading…` placeholder inside `<Suspense fallback>` for the 2-frame delay.

### ADR-0681-04 — Reuse `useOptimisticAction` rather than roll a new SSE-specific hook

**Status**: Accepted.

**Context**: `useOptimisticAction` (0674 T-053) handles snapshot/apply/commit/rollback/retry. It was designed for promise-shaped commits. Our commit here is an SSE stream.

**Decision**: Wrap the SSE stream in a Promise (resolves on `done`, rejects on `error`/`TIMEOUT`) and feed that promise to `useOptimisticAction`.

**Rationale**: One optimistic-action pattern across the app (already used for install/uninstall/edit elsewhere). The SSE-to-Promise adapter is 20 lines; a parallel hook would duplicate toast / retry / snapshot logic.

**Consequences**: SSE `progress` events (interim status) are surfaced via a separate local `progressStatus` state — they're not part of the optimistic-action contract. That's fine: optimistic-action cares only about final success/failure.

---

## 8. File Tree (delta)

```
src/eval-ui/src/
├── hooks/
│   ├── useSkillUpdates.ts             (new)
│   └── useOptimisticAction.ts         (existing, unchanged)
├── components/
│   ├── UpdateBell.tsx                 (new)
│   ├── UpdateBellDropdown.tsx         (new, lazy-chunked)
│   ├── UpdateAction.tsx               (new)
│   ├── SkillRow.tsx                   (modified — glyph replaces pill)
│   ├── SidebarSection.tsx             (modified — updateCount prop + chip)
│   ├── TopRail.tsx                    (modified — mount <UpdateBell/>)
│   ├── RightPanel.tsx                 (modified — mount <UpdateAction/>)
│   └── ChangelogViewer.tsx            (existing, consumed)
├── utils/
│   └── semverBump.ts                  (new — extracted from UpdatesPanel)
├── StudioContext.tsx                  (modified — calls useSkillUpdates, merges into skills)
├── assets/icons/                      (existing — bell/arrow SVGs generated in parallel)
└── __tests__/
    ├── useSkillUpdates.test.ts        (new)
    ├── UpdateBell.test.tsx            (new)
    ├── UpdateAction.test.tsx          (new)
    └── SidebarSection.updateCount.test.tsx (new)

src/eval-ui/e2e/
└── update-notifications.spec.ts       (new)
```

---

## 9. Testing Strategy

### 9.1 Unit

- `useSkillUpdates.test.ts` — fake timers + `vi.spyOn(document, "visibilityState", "get")`; covers initial fetch, periodic poll, visibility pause/resume, debounce window, dedup, 15s timeout.
- `UpdateBell.test.tsx` — rendered with count 0 (no badge), 1..9 (exact number), 10+ (`9+`); dropdown open on click; Escape closes; outside-click closes.
- `UpdateBellDropdown` — bump-type dot colors; row click invokes `onSelectSkill`; `Refresh` button disabled while refreshing.
- `UpdateAction.test.tsx` — renders when `updateAvailable && latestVersion`; returns null otherwise; optimistic state transitions (idle → updating → success / error / timeout); `Preview changelog` toggles `ChangelogViewer`.
- `SidebarSection.updateCount.test.tsx` — chip renders only when `updateCount > 0`; click navigates to `#/updates` without collapsing; keyboard focus order.

### 9.2 Integration

- `StudioContext` integration: mock `api.getSkillUpdates()` to return a 3-skill outdated list; mount a tree containing `SkillRow`, `SidebarSection`, `UpdateBell`, `UpdateAction`; assert all four reflect `count === 3` and all derive from a **single** fetch (spy assertion: `apiMock.getSkillUpdates` called exactly once on mount).

### 9.3 E2E (Playwright)

`e2e/update-notifications.spec.ts`:
1. Launch studio with a fixture workspace that has 2 outdated installed skills.
2. Assert bell badge reads `2`.
3. Assert sidebar `Installed` section header reads `… 2 updates ▾`.
4. Assert first outdated row shows the `↑` glyph (selector: `data-testid="skill-row-update-glyph"`).
5. Click bell → dropdown opens, shows 2 rows.
6. Click `View all` → URL hash becomes `#/updates`.
7. Back-nav, select an outdated skill in sidebar → `RightPanel` shows `Update to X.Y.Z` button.
8. Click it → button becomes `Updating…`, SSE mock emits `progress` then `done`.
9. Assert success toast `Updated <skill>.` and badge count drops to `1`.

---

## 10. Rollout

- Behind no feature flag. Ship directly.
- Release notes snippet: "Studio now shows update badges in the sidebar, section headers, and top rail — click the new bell icon for a quick summary, or use the new `Update to X.Y.Z` button in any skill's detail panel."
- Monitoring: existing telemetry key `studio.shortcut_used` not touched. If telemetry is enabled (NFR-006 from 0674), add three new keys — `studio.update.bell_opened`, `studio.update.single_invoked`, `studio.update.refresh_manual` — behind the existing opt-in.

---

## 11. Open Questions

- None blocking. Decision-points recorded in §7 ADRs.
- **Future (post-0681)**: if we want sub-minute discovery latency, the backend can add a lightweight SSE channel that multiplexes `updates-available` events; client swaps polling for subscription without API surface changes.
