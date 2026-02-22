# Implementation Plan: Trust Center fixes

## Overview

Four targeted changes to the Trust Center page (`/trust`). No new tables, no new API routes, no new packages. All work is in existing files.

## Architecture

### Component Map (files touched)

| Change | Files | Type |
|--------|-------|------|
| US-001: Tier stats | `src/app/api/v1/stats/route.ts`, `src/lib/data.ts` | Backend fix |
| US-002: Blocklist retry | `src/app/trust/BlockedSkillsTab.tsx` | Frontend fix |
| US-003: Reports modal | `src/app/trust/page.tsx`, `src/app/trust/ReportsTab.tsx` | Frontend refactor |
| US-004: Auto-refresh | `src/app/trust/TrustTierDistribution.tsx` | Frontend feature |

### US-001: Fix Trust Tier Computation

**Root cause**: `getTrustStats()` in the stats route reads `skill.trustTier`, but `mapDbSkillToSkillData()` never sets `trustTier` on Prisma-sourced skills. All DB skills fall into the `else` branch and get counted as T1.

**Fix approach -- option A (chosen): Compute tiers directly in the stats route**

Rewrite `getTrustStats()` in `src/app/api/v1/stats/route.ts` to:

1. Accept `allSkills` (merged seed + Prisma from `getSkills()`) which already have seed skills with `trustTier` set.
2. For each skill: if `trustTier` is set and valid (T0-T4), use it. Otherwise, derive from `certTier`: SCANNED->T2, VERIFIED->T3, CERTIFIED->T4. Fallback: T1.
3. Separately query `db.blocklistEntry.count({ where: { isActive: true } })` and assign to T0.

**Why not option B (set trustTier in mapDbSkillToSkillData)**:
- `mapDbSkillToSkillData` serves the general data layer. Adding `trustTier` there would leak trust-center-specific logic into the shared mapper. The stats route is the single consumer of trust tier counts, so the derivation belongs there.
- The blocklist T0 count requires a separate Prisma query regardless, so the stats route must already do custom work.

**Data flow**:

```
GET /api/v1/stats
  ├── getSkills()         → merged seed + Prisma skills (with certTier)
  ├── getDb()             → blocklistEntry.count({ isActive: true }) → T0
  └── getTrustStats(skills, blocklistCount)
        for each skill:
          if skill.trustTier in {T0..T4} → use it
          else derive from skill.certTier:
            SCANNED → T2, VERIFIED → T3, CERTIFIED → T4
            default → T1
        counts.T0 += blocklistCount  (additive — blocklist entries are separate entities)
```

**Key detail**: Blocklist entries are NOT skills in the skills array. They live in a separate `blocklistEntry` table. So T0 is purely from the blocklist count, not from skill iteration. Skills with `trustTier: "T0"` in seed data (if any) would also be counted, but currently no seed skills have T0.

### US-002: Blocklist Retry with Exponential Backoff

**Current state**: `BlockedSkillsTab.fetchBlocklist()` is a plain fetch with `.catch(() => setError(...))`. No retry, no recovery button.

**Approach**: Replace `fetchBlocklist` with a `fetchWithRetry` function inline in the component.

```
fetchWithRetry(attemptsRemaining = 3, delay = 0):
  if delay > 0: await sleep(delay)
  try:
    response = await fetch("/api/v1/blocklist")
    if !response.ok: throw
    parse + setEntries + setCount
    setError("") // clear
  catch:
    if attemptsRemaining > 1:
      nextDelay = delay === 0 ? 1000 : delay * 2
      jitter = nextDelay * 0.2 * (Math.random() * 2 - 1)
      fetchWithRetry(attemptsRemaining - 1, nextDelay + jitter)
    else:
      setError("Failed to load blocklist")
      setLoading(false)
```

The Retry button calls `fetchWithRetry(3, 0)` -- a fresh cycle every time. During retry, `loading=true` hides the error and shows "Loading blocklist...". When all attempts exhaust, error + Retry button reappears.

**No new dependencies**. The `sleep` utility is a simple `new Promise(r => setTimeout(r, ms))` inline.

### US-003: Reports Tab to Modal

**Step 1**: In `page.tsx`:
- Remove `"reports"` from `TABS` array (2 tabs remain: verified, blocked).
- Remove `{activeTab === "reports" && <ReportsTab />}` from tab content.
- Add `reportModalOpen` state (`useState(false)`).
- Add "Report a Skill" button in header area (right of subtitle paragraph).
- Add overlay modal (when `reportModalOpen=true`): fixed full-page backdrop + centered card with X close button + `<ReportsTab />` inside.

**Step 2**: In `ReportsTab.tsx`:
- No changes to component internals. It already handles its own fetch/state.
- The component is simply re-parented from tab content to modal content.

**Modal pattern**: Replicate the existing block dialog in VerifiedSkillsTab (lines 313-369):
- `position: fixed`, full viewport backdrop with `rgba(0,0,0,0.5)`
- Centered card with `maxWidth: 640px` (wider than block dialog's 420px to fit the form + table)
- Backdrop click dismisses; card `onClick={e => e.stopPropagation()}`
- X button: absolute positioned top-right of card

### US-004: Relative Time + Refresh Button

**Approach**: Extend `TrustTierDistribution.tsx`:

1. Track `fetchedAt` timestamp (`Date.now()` when fetch completes).
2. Add a `relativeTime` string state, updated via `setInterval` every 15 seconds.
3. Add a `refresh()` callback that re-fetches `/api/v1/stats` and resets `fetchedAt`.
4. Add `refreshing` state for spinner/disabled button during fetch.

**Relative time formatting**: Simple inline function, no library needed.
```
function formatRelativeTime(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `updated ${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `updated ${minutes}m ago`;
  return `updated ${Math.floor(minutes / 60)}h ago`;
}
```

**Refresh icon**: Small inline SVG (circular arrow), 16x16, wrapped in a `<button>` with `border-radius: 50%`. During refresh, apply CSS `animation: spin 1s linear infinite` via inline style or a `@keyframes` block.

**Layout**: Below the tier cards row, a `div` with `display: flex; justifyContent: flex-end; alignItems: center; gap: 0.5rem`. Contains the muted text label + the refresh icon button.

## Technology Stack

No new dependencies. All changes use:
- **React** (useState, useEffect, useCallback, useRef)
- **Next.js** (API route, client components)
- **Prisma** (existing `getDb()` for blocklistEntry count)
- **Inline styles** (consistent with existing Trust Center components)

## Implementation Phases

### Phase 1: Backend Fix (US-001)
1. Rewrite `getTrustStats()` in stats route to derive trust tier from `certTier`
2. Add blocklist count query to GET handler
3. Update the response to include blocklist-derived T0

### Phase 2: Frontend Fixes (US-002, US-003, US-004) -- parallelizable
4. Add retry logic to `BlockedSkillsTab`
5. Restructure `page.tsx` (remove reports tab, add modal + button)
6. Extend `TrustTierDistribution` with refresh + relative time

### Phase 3: Testing
7. Unit tests for the updated `getTrustStats` logic
8. Component tests for retry behavior, modal open/close, refresh tick

## Testing Strategy

- **Stats route**: Unit test `getTrustStats()` with mock skills (mix of seed with `trustTier` set, DB skills with only `certTier`, and blocklist count). Verify correct T0-T4 distribution.
- **BlockedSkillsTab**: Test retry button appears on error. Mock fetch to fail N times then succeed. Verify exponential delay timing with fake timers.
- **Page.tsx modal**: Test that clicking "Report a Skill" opens modal, clicking backdrop closes it, X button closes it.
- **TrustTierDistribution**: Test relative time label ticks. Test refresh button triggers re-fetch. Use `vi.useFakeTimers()` for interval assertions.

## Technical Challenges

### Challenge 1: Blocklist T0 count is additive, not from skills array
**Solution**: Query `blocklistEntry.count` separately in the stats route. Add to `counts.T0` after iterating skills. Wrap in try/catch so if blocklist table is unreachable, T0 defaults to 0 (graceful degradation).

### Challenge 2: setInterval cleanup for relative time ticker
**Solution**: Use `useEffect` with cleanup return. Store interval ID via `useRef` to avoid stale closure issues. Clear on unmount and on re-fetch.
