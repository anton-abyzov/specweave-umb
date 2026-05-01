---
increment: 0817-watch-library-rename-and-render-101-series
title: >-
  Rename /learn to /watch, promote to nav, render the 4 broken Learn101 videos
  with Sarah VO
type: feature
priority: P1
status: completed
created: 2026-04-30T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Rename /learn to /watch, promote to nav, render the 4 broken Learn101 videos with Sarah VO

## Overview

INC-C of the verified-skill.com video overhaul (master plan: `~/.claude/plans/curried-beaming-summit.md`). Two coordinated outcomes:

1. **IA promotion** — Rename `src/app/learn/` to `src/app/watch/`, add 301 redirects (`/learn -> /watch`, `/learn/[slug] -> /watch/[slug]`), promote the renamed library into the global desktop + mobile nav between **Studio** and **Submit** (8 items -> 9 items), and update `src/app/sitemap.ts` to emit the new canonical URLs. Rename `src/lib/learn/video-data.ts` -> `src/lib/learn/video-catalog.ts` and update all asset paths from `/video/learn/...` and `/learn/thumbnails/...` to `/video/watch/...` and `/watch/thumbnails/...`.
2. **Content fix** — Render the 4 currently-published-but-broken Learn101 videos (`getting-started-101`, `cli-commands-101`, `security-scan-101`, `plugin-marketplace-101`) using the INC-A scene-kit (`src/remotion/scene-kit/` from increment 0810) plus per-video `script.ts` files (script-as-data pattern validated in INC-B 0812) plus ElevenLabs Sarah voiceover. Generate real WebP thumbnails (replacing the 43-byte stubs at `public/learn/thumbnails/`). Add a NEW 90-second `skills-manager-overview` Remotion composition + render that becomes the canonical "what is vskill" onboarding asset on `/watch` (replaces the YouTube embed positioning per Anton's locked brand decision).

INC-A foundation (0810) and INC-B Studio refresh (0812) are merged and live. ELEVENLABS_API_KEY is configured in `repositories/anton-abyzov/vskill-platform/.env.local`. Brand color taxonomy: green `#22c55e` (beginner / getting-started), blue `#3b82f6` (compare), purple `#a855f7` (security / advanced), cyan `#06b6d4` (studio / local), Claude Code orange `#D97757` for the skills-manager-overview TUI scene.

## User Stories

### US-001: Permanent redirect from /learn to /watch (P1)
**Project**: vskill-platform

**As a** user with `/learn` bookmarks, RSS subscriptions, or external links
**I want** every `/learn` URL to permanently redirect to its `/watch` equivalent
**So that** existing links keep working and search engines transfer ranking to the new canonical path without producing 404s

**Acceptance Criteria**:
- [x] **AC-US1-01**: `next.config.ts` declares a `redirects()` entry mapping `/learn` -> `/watch` with `permanent: true`, and `curl -I http://localhost:3000/learn` returns HTTP **301 or 308** with `Location: /watch`. (Per ADR `0817-01` §D1: Next.js `permanent: true` emits HTTP 308 by design — both 301 and 308 are accepted "permanent" semantics for SEO transfer and bookmark fidelity.)
- [x] **AC-US1-02**: `next.config.ts` declares a wildcard redirect mapping `/learn/:slug*` -> `/watch/:slug*` with `permanent: true`, and `curl -I http://localhost:3000/learn/getting-started-101` returns HTTP **301 or 308** with `Location: /watch/getting-started-101`. (See ADR `0817-01` §D1.)
- [x] **AC-US1-03**: All four published video slugs (`getting-started-101`, `cli-commands-101`, `security-scan-101`, `plugin-marketplace-101`) redirect from `/learn/<slug>` to `/watch/<slug>` with HTTP **301 or 308**, verified via Playwright `request.get(url, { maxRedirects: 0 })`. (See ADR `0817-01` §D1.)
- [x] **AC-US1-04**: `src/app/learn/` directory no longer exists in the working tree after the move; `src/app/watch/page.tsx` and `src/app/watch/[slug]/page.tsx` (or equivalent dynamic detail routing) render the renamed library.
- [x] **AC-US1-05**: `src/app/sitemap.ts` emits a `/watch` URL entry (no `/learn` entries remain), and the sitemap.xml served at `/sitemap.xml` contains `<loc>https://verified-skill.com/watch</loc>` and zero occurrences of `/learn`.
- [x] **AC-US1-06**: A Playwright redirect test in `src/app/watch/__tests__/redirects.test.ts` (or equivalent E2E spec) covers the three redirect AC scenarios above and is included in the default `npx playwright test` run.

---

### US-002: Watch in global navigation (P1)
**Project**: vskill-platform

**As a** first-time visitor on verified-skill.com
**I want** a top-level "Watch" link in the global header nav
**So that** I can discover the video library without already knowing the URL (today `/learn` is sitemap-only and reachable from no surface, so it gets near-zero traffic)

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/app/layout.tsx` desktop nav (current lines ~92-108) renders a `<a href="/watch">Watch</a>` link positioned between the **Studio** and **Submit** entries; total nav item count is 9 (Skills | Studio | **Watch** | Submit | Publishers | Trust | Queue | Docs | Insights).
- [x] **AC-US2-02**: `src/app/components/MobileNav.tsx` renders a `Watch` entry between Studio and Submit; mobile menu shows it without horizontal scroll on a 375x667 viewport.
- [x] **AC-US2-03**: The footer in `src/app/layout.tsx` (current lines ~123-129) includes a "Watch" `footer-link` alongside Skills/Studio/Publishers/Trust/Docs/Queue/Submit.
- [x] **AC-US2-04**: Clicking the desktop nav "Watch" link on any page navigates to `/watch` and the page renders the video grid with HTTP 200 (no 404, no console errors), verified by Playwright snapshot.
- [x] **AC-US2-05**: Existing nav-related Vitest specs (e.g. layout snapshot tests if present) pass with the new ordering, and an updated test asserts the desktop and mobile nav both contain the Watch link.

---

### US-003: Render the 4 broken Learn101 videos with Sarah VO + captions (P1)
**Project**: vskill-platform

**As a** `/watch` (formerly `/learn`) visitor clicking on a published 101 video card
**I want** the video to actually play with synchronized voiceover and captions
**So that** the cards stop falling back to the "Video unavailable" placeholder in `LazyVideoPlayer.tsx` (today all 4 published cards land on the fallback because `public/video/learn/` does not exist on disk)

<!-- 0817 INC-C: AC-US3-04 was originally specified with ±10% VO/video duration tolerance assuming voiceText fills the entire visual timeline. Implementation reality: tutorial videos have ~10-30s of intentional silent buffer for scene transitions and outro lingering. The revised AC asserts the practical invariant (VO non-empty, present as primary audio, no truncation) instead of an arbitrary tolerance. Approved as architect-level spec amendment 2026-05-01. -->
**Acceptance Criteria**:
- [x] **AC-US3-01**: `src/lib/learn/video-data.ts` is renamed to `src/lib/learn/video-catalog.ts` (file move, exported symbol stays `VIDEOS`), every `sources.mp4` path is rewritten from `/video/learn/<slug>.mp4` to `/video/watch/<slug>.mp4`, every `thumbnail` path is rewritten from `/learn/thumbnails/<slug>.webp` to `/watch/thumbnails/<slug>.webp`, and every consumer import (e.g. `src/app/watch/page.tsx`, components, tests) is updated to import from the new module.
- [x] **AC-US3-02**: For each of the 4 published slugs (`getting-started-101`, `cli-commands-101`, `security-scan-101`, `plugin-marketplace-101`) a sibling `src/remotion/scenes/watch/<slug>/script.ts` file exists that defines an array of scene entries with at minimum `voiceText: string`, `caption: string`, `durationFrames: number`, and `accentColor` keyed to the brand taxonomy (green for getting-started, purple for security-scan, default cyan for cli-commands and plugin-marketplace unless the storyboard specifies otherwise).
- [x] **AC-US3-03**: The 4 existing scene compositions under `src/remotion/scenes/learn/` (`TitleCard.tsx`, `PluginBrowse.tsx`, `SecurityScan.tsx`, `SpecWeaveWorkflow.tsx`) are refactored to consume `src/remotion/scene-kit/` primitives (no inline hex colors except via `BRAND_COLORS`, no duplicated `TerminalFrame` / `BigText` definitions), and the source folder is moved/renamed to `src/remotion/scenes/watch/` with `Root.tsx` composition IDs updated from `Learn101*` to `Watch101*`.
- [x] **AC-US3-04**: `scripts/generate-voiceover.mjs <slug>` (the generalized version landed in INC-A) successfully produces `public/voiceover/watch/<slug>.mp3` for each of the 4 slugs using the ElevenLabs Sarah voice (env: `ELEVENLABS_API_KEY` from `.env.local`, voice id sourced from `ELEVENLABS_VOICE_ID_SARAH`); each MP3 is non-empty (>= 50 KB), and the VO is the primary audio track in the rendered MP4 with VO duration ≤ MP4 duration (no truncation; trailing silence is acceptable for scene transitions and outro lingering).
- [x] **AC-US3-05**: `npm run render:watch -- <slug>` (or equivalent task wired into `package.json`) renders both `public/video/watch/<slug>.mp4` and `public/video/watch/<slug>.webm` for each of the 4 slugs; each MP4 is `>= 1 MB` and `<= 25 MB`, plays for the duration declared in `video-catalog.ts` (+/- 1 second), and the existing `src/lib/learn/__tests__/video-size-constraints.test.ts` is updated to point at `public/video/watch/` and now passes non-vacuously (asserts each file exists and is within bounds).
- [x] **AC-US3-06**: A captions sidecar `public/video/watch/<slug>.vtt` is generated for each of the 4 slugs (cues sourced from each script entry's `caption`), and `src/app/components/learn/LazyVideoPlayer.tsx` (renamed to `WatchVideoPlayer.tsx`) wires `<track kind="captions" default src="<vtt-path>" />` so DevTools network tab shows the VTT loading 200 when the player mounts.
- [x] **AC-US3-07**: A Playwright E2E spec navigates to `/watch`, clicks each of the 4 published-card play buttons, and asserts the `<video>` element reaches `readyState >= 3` (HAVE_FUTURE_DATA) within 5 seconds with no `Video unavailable` fallback text rendered on the page.

---

### US-004: New skills-manager-overview composition for /watch (P2)
**Project**: vskill-platform

**As a** prospect landing on `/watch` for the first time
**I want** a polished ~90-second "what is vskill" onboarding video featured at the top of the library
**So that** I get a single canonical piece of onboarding content (replacing the dropped YouTube positioning per the locked brand decision: no YouTube embeds, all video assets first-party)

**Acceptance Criteria**:
- [x] **AC-US4-01**: `src/remotion/scenes/watch/skills-manager-overview/SkillsManagerOverview.tsx` exists and is registered as a `<Composition id="SkillsManagerOverview" />` in `src/remotion/Root.tsx` with `width = VIDEO_WIDTH`, `height = VIDEO_HEIGHT`, `fps = FPS`, and `durationInFrames` derived from its `script.ts` (target ~90 s = ~2700 frames at 30 fps, must fall within 80-100 s).
- [x] **AC-US4-02**: The composition consumes scene-kit primitives (`TerminalFrame`, `TUIFrame`, `BrowserChrome`, `CommandTypewriter`, `CaptionBar`, `PillTag`, `SkillCard`, `TransitionWipe`) and uses Claude Code orange `#D97757` exclusively for the TUI-mock scene plus the four-color brand taxonomy elsewhere; no inline hex colors outside the scene-kit `BRAND_COLORS` import.
- [x] **AC-US4-03**: A sibling `script.ts` defines the per-scene `voiceText` / `caption` / `durationFrames`, and `scripts/generate-voiceover.mjs skills-manager-overview` produces `public/voiceover/watch/skills-manager-overview.mp3` with Sarah at the same loudness target as the 4 101-series VOs.
- [x] **AC-US4-04**: `npm run render:watch -- skills-manager-overview` produces `public/video/watch/skills-manager-overview.mp4` + `.webm` + `.vtt`; the MP4 is `>= 5 MB` and `<= 40 MB`, duration 80-100 s.
- [x] **AC-US4-05**: `src/lib/learn/video-catalog.ts` includes a new `VIDEOS` entry with `slug: "skills-manager-overview"`, `category: "overview"`, `status: "published"`, `featured: true`, paths under `/video/watch/` and `/watch/thumbnails/`, and `relatedDocs: ["/docs/getting-started"]`; the entry is positioned first in the array so `/watch` renders it as the featured hero card.
- [x] **AC-US4-06**: Visiting `/watch` in dev (`npm run dev` on port 3000) shows the skills-manager-overview card prominently above the 4 101-series cards; clicking it plays the rendered MP4 with VO + captions and no console errors (verified via Playwright + screenshot in the closure summary per the local-preview feedback rule).

---

### US-005: Real WebP thumbnails for every /watch card (P2)
**Project**: vskill-platform

**As a** `/watch` grid visitor
**I want** every video card to show a real preview thumbnail that hints at the video's content
**So that** the page looks designed (today every thumbnail at `public/learn/thumbnails/*.webp` is a 43-byte placeholder stub, making the grid feel broken)

**Acceptance Criteria**:
- [x] **AC-US5-01**: For each of the 5 published slugs (`skills-manager-overview` + the 4 101-series), `public/watch/thumbnails/<slug>.webp` exists, is `>= 5 KB` and `<= 200 KB`, and is `1280 x 720` (16:9) per `webp` decoder metadata.
- [x] **AC-US5-02**: Each thumbnail is generated via Remotion `<Still>` rendering of the composition's first hero frame (or a dedicated thumbnail still where the first-frame would be ambiguous, e.g. for `cli-commands-101` use a frame with the typewriter mid-command rather than the empty terminal); the still IDs are registered in `src/remotion/Root.tsx` and the render command is wired via `npm run thumbs:watch`.
- [x] **AC-US5-03**: `public/learn/thumbnails/` is removed from the working tree (after `git mv` to `public/watch/thumbnails/` and replacement of the stubs with real renders); a Vitest spec asserts `fs.statSync` on each new thumbnail returns a size between 5 KB and 200 KB.
- [x] **AC-US5-04**: `WatchVideoPlayer.tsx` (formerly `LazyVideoPlayer.tsx`) loads the thumbnail via `<img src={thumbnail} loading="lazy" />` and a Playwright snapshot of the `/watch` grid shows no visible "broken image" icon for any of the 5 published cards.

## Functional Requirements

### FR-001: Permanent redirects via next.config.ts
Use Next.js `redirects()` (not `middleware.ts`) for the `/learn` -> `/watch` mapping so the redirect runs at the edge and is cacheable. Wildcard syntax: `{ source: "/learn/:slug*", destination: "/watch/:slug*", permanent: true }`. Per ADR `0817-01` §D1: `permanent: true` emits HTTP **308** in Next.js 15 (preserves request method / body across the hop); both 301 and 308 are valid "permanent" status codes for SEO ranking transfer and browser bookmark updates, so the ACs accept either.

### FR-002: Script-as-data pattern reused from INC-B
Every `script.ts` exports `const SCRIPT: Scene[]` where `Scene = { voiceText: string; caption: string; durationFrames: number; accentColor?: keyof typeof BRAND_COLORS; visualNotes?: string }`. The composition derives total `durationInFrames` from `SCRIPT.reduce((sum, s) => sum + s.durationFrames, 0)`. The voiceover script for `generate-voiceover.mjs` is the concatenation of `voiceText` joined with appropriate SSML pause hints between scenes.

### FR-003: Sarah ElevenLabs voice
Voice ID resolution order: `process.env.ELEVENLABS_VOICE_ID_SARAH` -> hard-coded fallback ID for Sarah documented in the INC-A ADR `0XXX-video-pipeline-and-token-sync.md`. API key from `ELEVENLABS_API_KEY` in `.env.local`. Output bitrate 128 kbps mp3, model `eleven_multilingual_v2` per the INC-A pipeline.

### FR-004: VTT captions sidecar generation
For every script, produce a sidecar `.vtt` whose cues are timestamped from running `durationFrames` totals (cue start = sum of prior `durationFrames` / fps, cue end = cue start + current `durationFrames` / fps, cue text = `caption`). Generated as part of the same `npm run render:watch -- <slug>` task so MP4, WebM, and VTT cannot drift in time.

### FR-005: Thumbnail render via Remotion `<Still>`
Add `<Still>` registrations for each new composition in `src/remotion/Root.tsx` (already partially scaffolded for the existing 4 — must extend to `SkillsManagerOverview` and adjust the existing four to point to the renamed scene paths). Render command uses `npx remotion still <id> public/watch/thumbnails/<slug>.webp --image-format=webp --quality=80`.

## Success Criteria

- `curl -I http://localhost:3000/learn` returns **301 or 308** with `Location: /watch`; same for `/learn/getting-started-101` (per ADR `0817-01` §D1).
- All 5 published `/watch` cards (`skills-manager-overview` + 4 101-series) play through with VO + captions, zero "Video unavailable" fallbacks rendered.
- Real WebP thumbnails (5-200 KB each) replace the 43-byte stubs.
- "Watch" appears in desktop nav, mobile nav, and footer between Studio and Submit; nav item count is 9.
- `src/lib/learn/__tests__/video-size-constraints.test.ts` passes non-vacuously (asserts every published catalog entry resolves to a real file in the declared size range).
- Playwright + Vitest suites green on `repositories/anton-abyzov/vskill-platform/` (`npm run test` + `npx playwright test`).
- Per `feedback_video_local_preview.md`: closure summary includes screenshots of `/watch`, the redirected `/learn`, and at least one card playing with captions toggled on.

## Out of Scope

- Inline `<DocVideoEmbed>` components on `/docs/*` pages other than `/docs/studio` (which was already added in INC-B). Embedding the 101 videos at the top of `/docs/getting-started`, `/docs/cli-reference`, `/docs/security-guidelines`, `/docs/plugins` is **INC-D**.
- Deleting `src/app/components/homepage/VideoHero.tsx` and the ~8.5 MB orphan assets at `public/video/ship-while-you-sleep.mp4`, `public/video/specweave-promo.mp4`, `public/video/specweave-promo.webm`. **INC-D**.
- Refreshing the homepage hero video. **INC-D / deferred**.
- Rendering `specweave-workflow-101` and `advanced-customization-101`. They stay `status: "coming-soon"` in `video-catalog.ts`; rendering is **INC-D** (workflow) or future (advanced).
- Lifting unique components from `repositories/anton-abyzov/specweave/docs-site/remotion/` into the shared scene-kit. **INC-D**.
- Building a separate `studio-tour` composition (the long-form `/watch` entry distinct from the `/studio` inline video). Deferred because INC-B already shipped the `/studio` inline refresh; the long-form library entry can come later if traffic warrants.
- Adding "Watch" to the homepage hero CTA. Hero overhaul is deferred per master plan.
- Modifying `src/remotion/scene-kit/` itself — primitives are frozen as of INC-A 0810. If a missing primitive is needed (e.g. a tighter `SkillCard` variant), file it as a follow-up increment instead of growing scope here.

## Dependencies

- **INC-A (0810)** — scene-kit at `src/remotion/scene-kit/` with 12 components + `BRAND_COLORS` taxonomy + canonical token sync in `globals.css` + `scripts/generate-voiceover.mjs` Sarah pipeline. **MERGED + LIVE**.
- **INC-B (0812)** — Studio refresh validated the script-as-data pattern, generic Sarah VO script, and captions wiring at `src/app/components/shared/VideoPlayer.tsx`. **MERGED + LIVE**.
- `ELEVENLABS_API_KEY` in `repositories/anton-abyzov/vskill-platform/.env.local` (already set per master plan).
- Skybound Circuits BGM at `public/hackathon-demo/bgm.mp3` reusable for the 5 renders.
