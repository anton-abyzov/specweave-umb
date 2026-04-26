# 0766 — Studio: UI cache-invalidation + loading-state bugs

## Problem

After 0765 shipped (`vskill@0.5.135`) the on-disk frontmatter and the lockfile correctly bump to the new version when the user clicks "Update to <X>". The header chip refreshes, but two stale-state bugs remain in the Studio UI:

### A. Versions tab is stuck on shimmer

`http://localhost:3162/#/skills/.claude/greet-anton` (Versions tab) shows skeleton loaders that never resolve, even though `GET /api/skills/.claude/greet-anton/versions` returns valid JSON (2 rows: 1.0.3 + 1.0.2 with `isInstalled: true`).

### B. "Update to <X>" button keeps showing after a successful update

The user clicks Update. Backend updates the file. Header chip refreshes to the new version. But the "Update to 1.0.3" button keeps rendering and the bell still says "1 update available" until polling cycles 5 minutes later.

## Root causes (verified by `sw:code-reviewer`)

### F-001 (CRITICAL) — `useSWR.ts:144` — infinite loading after fetch rejection
`return { loading: loading || (enabled && !entry), ... }` is permanently `true` when the fetcher rejected: the inFlight is cleared, no cache entry is set, no error is captured (the `error` field is hardcoded to `undefined`), and the rejection handler at lines 123–130 just `throw err` into an unhandled promise rejection. The loading skeleton never goes away.

### F-002 (CRITICAL) — Asymmetric cross-component invalidation
`UpdateAction.handleUpdate` calls only `refreshUpdates()`. `VersionHistoryPanel.handleUpdate` calls only `refreshSkills() + mutate(swrKey)`. Neither path invalidates the other's data. Whichever entry point the user uses, the other half of the UI stays stale until the 5-minute polling cycle.

### F-004 (HIGH) — `mergeUpdatesIntoSkills` re-stamps `updateAvailable` even after refresh
`mergedSkills` (`StudioContext.tsx:466`) re-runs whenever `state.skills` OR `skillUpdates.updates` changes. After `refreshSkills()` lands, the just-loaded skill data is merged with the still-stale polling list and `updateAvailable: true` is re-stamped — so the button keeps rendering until BOTH `refreshSkills` AND `refreshUpdates` complete.

(F-003, F-005, F-007 are noise reduction — addressed alongside F-001/F-002.)

## User Stories

### US-001: Versions tab surfaces errors instead of looping shimmer
**As** a Studio user with a failing /versions fetch
**I want** to see an error message (or empty state) instead of an infinite skeleton
**So that** I can tell the difference between "loading" and "broken".

**Acceptance Criteria:**
- [x] AC-US1-01: When `useSWR`'s fetcher rejects, the returned `loading` becomes `false` and the returned `error` carries the rejected `Error`.
- [x] AC-US1-02: When the fetcher rejects, no unhandled promise rejection is thrown to the host (no `throw err` in the rejection handler).
- [x] AC-US1-03: `revalidate()` clears any captured `errorState` so the next attempt can succeed cleanly.

### US-002: "Update to <X>" button + bell clear after a successful update from any entry point
**As** a Studio user clicking Update from the detail page OR the Versions tab OR the bell dropdown
**I want** the button, bell, sidebar arrow, and version chip to clear together
**So that** the UI reflects the new state without waiting up to 5 minutes for polling.

**Acceptance Criteria:**
- [x] AC-US2-01: A single `studio.onSkillUpdated(plugin, skill)` helper exists and runs `refreshUpdates()` + `refreshSkills()` + `mutate("versions/${plugin}/${skill}")` + `dismissPushUpdate(...)`.
- [x] AC-US2-02: `UpdateAction.handleUpdate` calls `onSkillUpdated` instead of the partial `refreshUpdates + dismissPushUpdate` pair.
- [x] AC-US2-03: `VersionHistoryPanel.handleUpdate` calls `onSkillUpdated` instead of the partial `refreshSkills + mutate(swrKey)` pair.
- [x] AC-US2-04: `UpdateDropdown` (the bell's per-row Update button) also routes through `onSkillUpdated` for the same skill.
- [x] AC-US2-05: `mergeUpdatesIntoSkills` skips stamping `updateAvailable` on a row when its `currentVersion` is `>=` the polling result's `latestVersion` (defense-in-depth so the button doesn't re-flicker between `refreshSkills` and `refreshUpdates` landing).

## Out of scope

- Changing polling cadence.
- Replacing the SWR module with the official `swr` package.
- The `UpdateDropdown` inline-update flow (separate increment 0747 in flight).
