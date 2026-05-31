# 0862 — Lifecycle demo video

## Goal
Produce a screen-recorded video walkthrough of the full Skill Studio lifecycle, the way a user does it, on the macOS app UI: **bump a skill's version → submit it in-app via Skill Studio → see the review decision notification → click it → update the locally-installed copy.** Subject skill: a dedicated `anton-grid` demo skill.

## User Stories
### US-001 — The video
- **AC-US1-01**: A single continuous recording shows: select `anton-grid` (v1.0.0) → edit + bump version to v1.0.1 → Publish drawer → Commit & Push → **in-app submit** (inline outcome, no browser redirect).
- **AC-US1-02**: The submission appears in **My Queue** (RECEIVED), then transitions to **APPROVED/PUBLISHED**.
- **AC-US1-03**: The **top-right bell** shows the notification; clicking it opens the update dropdown; clicking **Update** updates the local copy to v1.0.1.
- **AC-US1-04**: On-screen captions narrate each step; output is an mp4 (h264) with an intro title card, delivered to Anton.

### US-002 — Real + clean
- **AC-US2-01**: Drives the REAL studio UI (not a mockup animation). Deterministic via stubs (no real registry pollution). Any UI bug hit is fixed minimally so the flow is clean.

## Approach
Reuse the 0860 Playwright E2E flow + selectors with `video: 'on'`, a 1440x900 viewport, slowed pacing, and a per-step caption overlay. Post-process the `.webm` → `.mp4` with ffmpeg (+ title card).
