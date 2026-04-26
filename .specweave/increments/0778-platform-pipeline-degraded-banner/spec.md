---
increment: 0778-platform-pipeline-degraded-banner
title: "Studio Bell — Surface Platform Pipeline Degraded State"
type: bug
priority: P2
status: active
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Bell — Surface Platform Pipeline Degraded State

## Overview

When the upstream `vskill-platform` pipeline degrades (tier-1 scanner stalled, VM heartbeat stale, submissions stuck in `TIER1_SCANNING` for days), the Studio's update bell still shows green/neutral "No updates available" — misleading authors into thinking Studio is broken when the platform is. The platform already exposes a degraded signal (`/api/v1/submissions/stats.degraded` + `/api/v1/queue/health`); this increment surfaces it.

**Out of scope**: fixing the platform-side stuck submissions (operational/admin work). This increment ONLY surfaces the existing degraded signal so authors understand why their submissions aren't appearing as updates.

## User Stories

### US-001: Bell shows amber state when platform is degraded
**Project**: vskill

**As a** skill author who just submitted a new version
**I want** the Studio update bell to indicate when the platform's crawler/queue is degraded
**So that** I understand why my submission isn't showing as an available update — and that the issue is on the platform, not on my install

**Acceptance Criteria**:
- [x] **AC-US1-01**: New endpoint `GET /api/platform/health` on the eval-server returns `{ degraded: boolean, reason: string | null, statsAgeMs: number, oldestActiveAgeMs: number }`. Computed by fetching `https://verified-skill.com/api/v1/submissions/stats` and `https://verified-skill.com/api/v1/queue/health` in parallel with a 1500 ms hard timeout.
- [x] **AC-US1-02**: `degraded === true` iff ANY of these fire: (a) `stats.degraded === true` from the platform, (b) `queueHealth.statsAge.ageMs > 1_800_000` (heartbeat stale > 30 min), (c) `queueHealth.oldestActive.ageMs > 86_400_000` (oldest submission active > 24 h). The `reason` field composes a short human string naming whichever signal(s) fired.
- [x] **AC-US1-03**: Upstream timeout, network error, or malformed JSON → endpoint returns `{ degraded: false, reason: "platform-unreachable", statsAgeMs: 0, oldestActiveAgeMs: 0 }`. The studio MUST NOT false-positive on a flaky local connection.
- [x] **AC-US1-04**: The endpoint caches its response in-memory for 60 s so per-studio polling does not amplify upstream load.

### US-002: Bell glyph + tooltip shift to amber when degraded
**Project**: vskill

**As a** user looking at the bell glyph in the studio top rail
**I want** an at-a-glance signal that something is wrong upstream
**So that** I don't have to open the dropdown to find out

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `usePlatformHealth().degraded === true`, the bell glyph fill becomes `var(--color-own)` (the existing amber/warn token).
- [x] **AC-US2-02**: The bell button's `aria-label` reads `"Notifications — platform crawler degraded"` (vs the default).
- [x] **AC-US2-03**: The bell button's `title` attribute reads `"Update checks paused — verified-skill.com crawler is degraded. Your submissions are queued."`.
- [x] **AC-US2-04**: When `degraded === false` (or hook is loading), bell rendering is unchanged.

### US-003: Dropdown shows an amber banner with the reason
**Project**: vskill

**As a** user who clicked the bell
**I want** the dropdown to explain why no updates are showing
**So that** I know whether to wait, retry, or check verified-skill.com status

**Acceptance Criteria**:
- [x] **AC-US3-01**: When `degraded === true`, the dropdown renders an amber banner above the existing list: a ⚠ glyph, a bold "Platform crawler degraded", and a dim line containing `reason`.
- [x] **AC-US3-02**: The existing "No updates available" / "X updates" content still renders below the banner — additive, not replacement.
- [x] **AC-US3-03**: When `degraded === false`, no banner is rendered.
- [x] **AC-US3-04**: Banner uses `role="status"` and `aria-live="polite"` for screen readers.

## Non-Functional Requirements

- **Performance**: 60 s server cache + 60 s client SWR TTL. ≤1 extra GET/min per studio session.
- **Reliability**: 1500 ms upstream timeout. Endpoint NEVER throws; failure paths return the safe fallback.
- **Cross-platform**: Standard `fetch` + `AbortSignal.timeout`.
- **Accessibility**: Banner is screen-reader live region; bell aria-label updates with state.

## Out of Scope

- Fixing platform-side stuck submissions / VM heartbeat.
- SSE for real-time degraded → healthy transitions.
- Submission status dashboard.

## References

- `src/eval-server/api-routes.ts` — new route adjacent to `/api/skills/updates`
- `src/eval-ui/src/components/UpdateBell.tsx` — bell + dropdown
- `src/eval-ui/src/hooks/useSWR.ts` — existing SWR primitive
- `https://verified-skill.com/api/v1/submissions/stats` + `/api/v1/queue/health` — upstream signals
