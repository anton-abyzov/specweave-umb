---
increment: 0812-studio-video-refresh-and-docs-section
title: "Refresh /studio video using scene-kit + Sarah VO; create /docs/studio section"
type: feature
priority: P1
status: planned
created: 2026-04-30
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Refresh /studio video using scene-kit + Sarah VO; create /docs/studio section

## Overview

INC-B of the verified-skill.com video overhaul (master plan: `~/.claude/plans/curried-beaming-summit.md`). The current `/studio` video (last rendered 2026-03-18 from `src/remotion/SkillStudioDemo.tsx`) is materially stale — it predates 8+ shipped Studio features: Tests-as-tab (1.0.9), Publish-to-GitHub flow + Generate-with-AI (0784), Install Scope picker User/Project/Global (0784), Update Toast (0781), and Command Palette ⌘K (29c313c). At the same time the `/docs` site has no Studio section at all — `src/app/docs/docs-nav.ts` jumps from "Workflows" to "Integrations" with nothing in between, and there is no `src/app/docs/studio/page.tsx`.

This increment delivers three coordinated changes:

1. **Refactor `src/remotion/SkillStudioDemo.tsx`** to consume the scene-kit primitives shipped in INC-A (0810): `TerminalFrame`, `BigText`, `CommandTypewriter`, `CaptionBar`, `PillTag`, `MetricBar`, `BrowserChrome` from `src/remotion/scene-kit/`. Adopt the script-as-data pattern: write `src/remotion/scenes/studio/script.ts` following `src/remotion/scenes/hackathon/script.ts` as the template. Add 5 NEW scenes covering the post-2026-03-18 features: `TestsTabIntro`, `PublishToGitHub`, `InstallScopePicker`, `UpdateToast`, `CommandPalette` under `src/remotion/scenes/studio/`. Composition target: 3:00–3:30 minutes at 30fps.

2. **Render and ship the new media**: generate Sarah voiceover via `scripts/generate-voiceover.mjs` (ELEVENLABS_API_KEY now in `.env.local`, voice id `EXAVITQu4vr4xnSDxMaL`). Render mp4 + webm in parallel from the same composition (current renders drift — webm is 8 days older than mp4). Generate `.vtt` sidecar from `script.ts` captions. Replace `public/video/skill-studio.mp4` + `public/video/skill-studio.webm` and add `public/video/skill-studio.vtt`. Wire the `<track kind="captions">` in `src/app/components/shared/VideoPlayer.tsx` (currently has the element but no `src`). Update the `DEMO_CHAPTERS` array in `src/app/studio/page.tsx` to match the new scene boundaries from `script.ts`.

3. **Create the `/docs/studio` section**: new `src/app/docs/studio/page.tsx` (or `.mdx`) with the new video embedded at the top + body covering Plain-English Evals, A/B Compare, Any Model, Local-first, Publish-to-GitHub, Install Scopes, and Update Notifications. Add a "Studio" entry to `src/app/docs/docs-nav.ts` between "Workflows" and "Integrations". Add `/docs/studio` to `src/app/sitemap.ts`.

Source storyboard: `repositories/anton-abyzov/vskill-platform/.specweave/scratch/skill-studio-hackathon-video.md` (already truth-checked, covers all 5 new scenes). INC-A foundation 0810 is merged: scene-kit at `src/remotion/scene-kit/` with 12 components + `BRAND_COLORS` + `STUDIO_LIGHT`/`VERIFIED_DARK`/`TERMINAL_UI` tokens; generic voiceover script at `scripts/generate-voiceover.mjs` (Sarah default voice). Proof-of-life Sarah render: `public/video/proof-of-life/hackathon-sarah.mp4` (3:04, 21.7MB). Live preview servers: `http://localhost:3010` (INC-A baseline), `http://localhost:3030` (current dev), `http://localhost:3031` (Remotion studio). Brand decisions locked per memory `project_video_brand_decisions_2026_04.md`. Local-preview verification rule per memory `feedback_video_local_preview.md`.

## User Stories

### US-001: Refreshed /studio video reflects current Studio features (P1)
**Project**: vskill-platform

**As a** Studio prospect landing on `/studio`
**I want** the embedded video to demonstrate the features actually shipped in the product today (Tests-as-tab, Publish-to-GitHub with Generate-with-AI, Install Scope picker, Update Toast, Command Palette)
**So that** I can evaluate the real product instead of the 2026-03-18 version that omits eight subsequently-shipped features

**Acceptance Criteria**:
- [x] **AC-US1-01**: `src/remotion/SkillStudioDemo.tsx` consumes at minimum these scene-kit primitives from `src/remotion/scene-kit/`: `TerminalFrame`, `BigText`, `CommandTypewriter`, `CaptionBar`, `PillTag`, `MetricBar`, `BrowserChrome`, `TransitionWipe` — verified by `import` statements pointing only to `../scene-kit` (or `./scene-kit`) for these 8 components, with no remaining direct imports from `src/remotion/components/` for primitives covered by scene-kit.
- [x] **AC-US1-02**: Five NEW scene files exist under `src/remotion/scenes/studio/`: `TestsTabIntro.tsx`, `PublishToGitHub.tsx`, `InstallScopePicker.tsx`, `UpdateToast.tsx`, `CommandPalette.tsx`. Each is registered in `SkillStudioDemo.tsx` via `<Sequence>` and exports a default React component accepting `script[i]` props.
- [x] **AC-US1-03**: `TestsTabIntro` scene renders Tests as a top-level tab in the Studio tab strip (not nested under Eval Cases), matching the 1.0.9 IA — verified by the scene component rendering 4 tab labels in order: `Eval Cases`, `Eval Runs`, `Tests`, `History` (or current 4-tab order shipped in 1.0.9).
- [x] **AC-US1-04**: `PublishToGitHub` scene shows the Publish modal with both "Push to GitHub" and "Generate with AI" affordances (per 0784) — verified by scene markup including a button labelled "Generate with AI" and a destination field showing a `github.com/<owner>/<repo>` placeholder.
- [x] **AC-US1-05**: `InstallScopePicker` scene shows three install scope options labelled `User`, `Project`, `Global` (per 0784) — verified by the scene rendering all three labels in a single radio/segment control with `Project` highlighted as the default selected scope.
- [x] **AC-US1-06**: `UpdateToast` scene shows a toast notification matching the 0781 updater popup (text mentioning "Update available" and a CTA button) — verified by the scene rendering both the version diff (e.g. `1.0.13 → 1.0.14`) and an "Update" CTA button.
- [x] **AC-US1-07**: `CommandPalette` scene shows a ⌘K-triggered palette with at least 3 listed commands and a search input — verified by the scene rendering an input element and a list of command rows with keyboard-shortcut hints (per 29c313c).
- [x] **AC-US1-08**: Total composition duration is between 5400 and 6300 frames at 30fps (3:00 to 3:30) — verified by summing `durationFrames` across all entries in `STUDIO_SCRIPT` in `src/remotion/scenes/studio/script.ts`.

---

### US-002: Sarah voiceover matches Hackathon polish tier (P1)
**Project**: vskill-platform

**As a** viewer of the `/studio` video
**I want** narration delivered in the Sarah ElevenLabs voice (the same voice used in the gold-standard `HackathonDemo`)
**So that** the brand audio is consistent across `/studio` and `/learn|/watch` videos and the production polish matches the bar set by Hackathon

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/remotion/scenes/studio/script.ts` exports a `STUDIO_SCRIPT` array with one entry per scene; each entry has the fields `id`, `durationFrames`, `transitionType`, `voiceText`, `caption?`, `visualNotes` (matching the `HackathonScene` shape in `src/remotion/scenes/hackathon/script.ts`).
- [x] **AC-US2-02**: Running `node scripts/generate-voiceover.mjs studio` (or equivalent invocation per the script's CLI signature) reads `STUDIO_SCRIPT[*].voiceText`, calls ElevenLabs with voice id `EXAVITQu4vr4xnSDxMaL` (Sarah), and writes `public/studio/voiceover.mp3` — verified by the generated file existing, being non-empty, and being referenced by an `<Audio src="/studio/voiceover.mp3">` element inside `SkillStudioDemo.tsx`.
- [x] **AC-US2-03**: `SkillStudioDemo.tsx` mounts a single `<Audio>` element loading the Sarah voiceover (no other voice tracks); verified by AST/grep showing exactly one `<Audio` element whose `src` ends in `/studio/voiceover.mp3`.
- [x] **AC-US2-04**: A second `<Audio>` mounts the Skybound BGM bed at `public/hackathon-demo/bgm.mp3` (reused per master plan §Reuse) at low volume — verified by an `<Audio src="/hackathon-demo/bgm.mp3" volume={...}>` element in `SkillStudioDemo.tsx` with a numeric `volume` prop ≤ 0.3.
- [x] **AC-US2-05**: The rendered `public/video/skill-studio.mp4` is non-empty (>5MB) and has duration matching the composition (3:00–3:30 ±2s) — verified by `ffprobe public/video/skill-studio.mp4` reporting duration in `[178, 212]` seconds.
- [x] **AC-US2-06**: The rendered `public/video/skill-studio.webm` exists and was modified within 5 minutes of `public/video/skill-studio.mp4` (no drift like the current 8-day gap) — verified by `stat -f %m` on both files differing by <300 seconds.

---

### US-003: Working closed-captions track on /studio video (P1)
**Project**: vskill-platform

**As a** captions user (deaf/hard-of-hearing, non-native English speaker, or sound-off viewer)
**I want** a working `<track kind="captions">` on the `/studio` video that loads a real `.vtt` file
**So that** I can read along with the narration — currently the `<track>` element exists in `VideoPlayer.tsx` but no `.vtt` sidecar has ever been generated, so captions silently fail

**Acceptance Criteria**:
- [x] **AC-US3-01**: `public/video/skill-studio.vtt` exists and conforms to WebVTT 1.0: starts with the literal first line `WEBVTT`, contains one cue per scene in `STUDIO_SCRIPT`, each cue has a `HH:MM:SS.mmm --> HH:MM:SS.mmm` timing line and one or more text lines.
- [x] **AC-US3-02**: VTT cue timings are derived programmatically from `STUDIO_SCRIPT[*].durationFrames` at 30fps (cumulative offsets), not hand-edited — verified by either (a) a generator script `scripts/generate-vtt.mjs` (or similar) committed in this increment that emits `skill-studio.vtt` from `script.ts`, OR (b) the vtt's cue boundaries matching the script's cumulative-frame offsets within ±2 frames per cue.
- [x] **AC-US3-03**: `src/app/components/shared/VideoPlayer.tsx` renders `<track kind="captions" label="English" default src={...}>` with a non-empty `src` (currently the element has `default` but no `src` attribute) — accepted via either a new `vtt?: string` prop wired from the caller, or a derived path (e.g. replace `.mp4` with `.vtt`).
- [x] **AC-US3-04**: When `/studio` is loaded in a browser via the local dev server, the network panel shows `/video/skill-studio.vtt` returning HTTP 200 — verified via Playwright assertion or Claude Preview MCP `preview_network` snapshot included in the closure summary.
- [x] **AC-US3-05**: Captions render visibly on the `/studio` video element when CC is toggled on — verified by Playwright scenario: navigate to `/studio`, click the in-page video, enable captions track, assert that a `::cue` text node appears within 5 seconds of playback.
- [x] **AC-US3-06**: The `DEMO_CHAPTERS` array in `src/app/studio/page.tsx` (currently lines ~20-31) is replaced so that every chapter's `seconds` value matches a scene boundary computed from `STUDIO_SCRIPT` cumulative durations — verified by a unit test in `src/app/studio/__tests__/chapters.test.ts` (or sibling) asserting `DEMO_CHAPTERS[i].seconds === Math.floor(sumFrames(0..i) / 30)`.

---

### US-004: /docs/studio section exists in global docs nav (P1)
**Project**: vskill-platform

**As a** docs reader looking for written reference material on Skill Studio
**I want** a `/docs/studio` section listed in the docs sidebar between "Workflows" and "Integrations"
**So that** I can find detailed text documentation about Skill Studio (currently zero Studio documentation exists in `/docs`)

**Acceptance Criteria**:
- [x] **AC-US4-01**: `src/app/docs/studio/page.tsx` (or `src/app/docs/studio/page.mdx`) exists, is a valid Next.js App Router page, exports a `metadata` object with `title` containing "Studio", and renders without runtime errors when navigating to `/docs/studio` on the local dev server.
- [x] **AC-US4-02**: The `/docs/studio` page embeds the new `skill-studio.mp4` near the top of the body — verified by the page importing and rendering the same `VideoPlayer` (or `ProductDemoCard`) component used on `/studio` with `mp4="/video/skill-studio.mp4"` and `webm="/video/skill-studio.webm"`.
- [x] **AC-US4-03**: The `/docs/studio` body covers all 7 documented topics — Plain-English Evals, A/B Compare, Any Model, Local-first (100% Local), Publish-to-GitHub, Install Scopes (User/Project/Global), Update Notifications — verified by a snapshot test or grep asserting each of these 7 strings (or a documented synonym from a single-source-of-truth list) appears as an `<h2>` or `<h3>` heading on the rendered page.
- [x] **AC-US4-04**: `src/app/docs/docs-nav.ts` includes a top-level entry whose `label` is exactly `"Studio"` and `href` is `"/docs/studio"`, positioned in the `DOCS_NAV` array AFTER the "Workflows" entry and BEFORE the "Integrations" entry — verified by an array-index assertion in `docs-nav.test.ts`.
- [x] **AC-US4-05**: `src/app/sitemap.ts` emits `/docs/studio` in its returned `MetadataRoute.Sitemap` array — verified by importing the sitemap function in a unit test and asserting one entry has `url` ending in `/docs/studio`.
- [x] **AC-US4-06**: When the docs Quickstart sidebar renders on `/docs/getting-started`, the "Studio" item is visible and clickable, and clicking it navigates to `/docs/studio` — verified by Playwright scenario.

---

### US-005: /studio video composition is defined as data (P2)
**Project**: vskill-platform

**As a** video producer maintaining the `/studio` video over time
**I want** the composition driven by a single `script.ts` data file (script-as-data pattern, mirroring `hackathon/script.ts`)
**So that** future re-renders, voiceover regeneration, caption regeneration, and chapter regeneration are mechanical — change the script, re-run pipeline, ship — instead of touching multiple files

**Acceptance Criteria**:
- [x] **AC-US5-01**: `src/remotion/scenes/studio/script.ts` is the single source of truth for scene IDs, durations, transitions, voiceover text, captions, and visual notes — verified by grep showing no duplicate hardcoded `voiceText` strings or `durationFrames` literals inside scene `.tsx` files (each scene reads its values from `STUDIO_SCRIPT.find(s => s.id === ...)` or props).
- [x] **AC-US5-02**: The voiceover generator at `scripts/generate-voiceover.mjs` consumes `script.ts` as input (not hardcoded strings) — verified by the script importing or reading from `src/remotion/scenes/studio/script.ts` and concatenating `voiceText` fields when invoked with the `studio` argument.
- [x] **AC-US5-03**: The VTT generator (whether new `scripts/generate-vtt.mjs` or extension of an existing pipeline) consumes the same `script.ts` — verified by the generator importing `STUDIO_SCRIPT` and writing cue text from `voiceText` (or `caption` where present).
- [x] **AC-US5-04**: The `DEMO_CHAPTERS` array in `src/app/studio/page.tsx` is generated from `STUDIO_SCRIPT` rather than hand-typed — verified either by `studio/page.tsx` importing a helper that derives chapters from the script at build time, OR by a committed unit test that fails if `DEMO_CHAPTERS` drifts from the script's scene boundaries.
- [x] **AC-US5-05**: A snapshot test under `src/remotion/scenes/studio/__tests__/script.test.ts` (or similar) locks the script structure: every scene has a unique `id`, every `durationFrames` is a positive integer, every `voiceText` is a non-empty string, the `transitionType` of the LAST scene is `null`, and at least one scene id is present from each of `["TestsTabIntro", "PublishToGitHub", "InstallScopePicker", "UpdateToast", "CommandPalette"]`.

## Functional Requirements

### FR-001: Scene-kit consumption replaces direct primitive imports
`SkillStudioDemo.tsx` and all scenes under `src/remotion/scenes/studio/` import primitives ONLY from `src/remotion/scene-kit/` (the public API surface). Direct imports from `src/remotion/components/` for primitives that exist in scene-kit are forbidden in this directory after the refactor. Tokens (`STUDIO_LIGHT`, `BRAND_COLORS`) come from `scene-kit/tokens.ts`.

### FR-002: Sarah voiceover pipeline produces `public/studio/voiceover.mp3`
The generic `scripts/generate-voiceover.mjs <video-name>` (shipped in INC-A 0810) is invoked with `studio` as the argument. It reads `STUDIO_SCRIPT`, posts `voiceText` to ElevenLabs (model `eleven_v3`, voice id `EXAVITQu4vr4xnSDxMaL` Sarah, env `ELEVENLABS_API_KEY` from `.env.local`), and writes `public/studio/voiceover.mp3`. The composition mounts this file plus the reused Skybound BGM at `public/hackathon-demo/bgm.mp3`.

### FR-003: mp4 + webm rendered together; no drift
A single render invocation (e.g. an npm script `render:studio` that calls Remotion render twice or once with multi-codec output) produces `public/video/skill-studio.mp4` and `public/video/skill-studio.webm` from the same composition revision. The two files' modification timestamps differ by <300 seconds.

### FR-004: WebVTT sidecar generated from script.ts
A generator (committed in this increment, location at the planner's discretion under `scripts/`) reads `STUDIO_SCRIPT` and writes a WebVTT-1.0-conformant file to `public/video/skill-studio.vtt`. Cue boundaries are computed from cumulative `durationFrames` at 30fps. Cue text is taken from the scene's `caption` if present, else from `voiceText` (truncated to ≤80 chars per cue if needed).

### FR-005: VideoPlayer wires the captions src
`src/app/components/shared/VideoPlayer.tsx` accepts a new optional `vtt?: string` prop. When provided, the rendered `<track>` includes `src={vtt}`. Callers on `/studio` and `/docs/studio` pass `vtt="/video/skill-studio.vtt"`. The existing `default` and `kind="captions"` and `label="English"` attributes are preserved.

### FR-006: Chapters array regenerated from script timings
`src/app/studio/page.tsx`'s `DEMO_CHAPTERS` array is updated so each chapter's `seconds` value equals the cumulative-frame offset of the corresponding scene boundary divided by 30 (rounded down). The chapter titles are short human-readable scene labels derived from `STUDIO_SCRIPT[i].id` or a sibling `chapterTitle` field.

### FR-007: /docs/studio page + nav entry + sitemap
- Create `src/app/docs/studio/page.tsx` (or `.mdx`) with embedded video at top + body covering the 7 documented topics.
- Add `{ label: "Studio", href: "/docs/studio", children: [...] }` to `DOCS_NAV` in `src/app/docs/docs-nav.ts` between "Workflows" and "Integrations".
- Add `/docs/studio` to `src/app/sitemap.ts`.

## Success Criteria

- The refreshed `/studio` video plays end-to-end on `http://localhost:3030/studio` (or the next available dev port) with Sarah narration, BGM bed, and visible captions when CC is toggled.
- All 5 newly-shipped Studio features (Tests-as-tab, Publish-to-GitHub, Install Scope picker, Update Toast, Command Palette) appear visually in the rendered video at the timestamps declared in `STUDIO_SCRIPT`.
- `/docs/studio` is reachable from the docs sidebar and renders the same video at the top of the page.
- A senior engineer reviewing the diff can re-render the entire video by editing `script.ts`, running the voiceover script, and running the render script — no other files need to be touched for content changes.
- Composition duration: 3:00–3:30. mp4 size: 15–35MB. webm size: 8–25MB.
- All AC-tagged tests pass: `npx vitest run` and `npx playwright test` (when applicable to the Playwright scenarios in US-003 and US-004) both succeed.
- Local-preview verification rule (memory `feedback_video_local_preview.md`) followed: closure summary includes Claude Preview screenshots of `/studio` and `/docs/studio` from a running local server, not "please go check it."

## Out of Scope

- **`/learn` → `/watch` IA changes** — the rename, the global nav entry, the 301 redirects, and the four broken `/learn` videos all live in INC-C. This increment does NOT touch `src/app/learn/`, `src/lib/learn/video-data.ts`, or `next.config.ts` redirects.
- **Inline video embeds on `/docs/getting-started`, `/docs/cli-reference`, `/docs/security-guidelines`, `/docs/plugins`, `/docs/submitting`** — these are INC-D scope. Only `/docs/studio` gets a video embed in this increment.
- **Dead-code deletion** (`src/app/components/homepage/VideoHero.tsx`, orphan `public/video/ship-while-you-sleep.mp4`, `specweave-promo.mp4`/`.webm`) — INC-D scope.
- **Homepage hero video refresh** — deferred per master plan, not in any current increment.
- **YouTube re-upload of the new mp4** — out of scope; the YouTube id `yEg46Ybh4Yk` referenced in `studio/page.tsx` continues to point to the old upload until separate manual re-upload. The inline `<video>` fallback served from `/video/skill-studio.mp4` IS replaced in this increment, so users who hit the local mp4 path see the refreshed content.
- **CSS token sync** (`globals.css` `--accent-cyan`, `--code-green`, `--bg-code` updates, `--accent-purple` add) — already shipped in INC-A 0810. Not this increment.
- **scene-kit additions or modifications** — INC-A is the foundation increment; this increment only consumes scene-kit, does not extend it. If a needed primitive is missing, raise it as a blocker rather than adding it inline.
- **Voiceover for any video other than `/studio`** — `/learn` voiceovers belong to INC-C.
- **Release/publish ceremony** for the renders (CDN upload, R2 sync, cache busting beyond what Next.js handles automatically) — closure ships the new files into `public/video/`; CDN/R2 promotion is a separate ops step the user runs after merge.

## Dependencies

- **INC-A 0810 (MERGED)**: scene-kit at `src/remotion/scene-kit/` with 12 components + tokens; generic `scripts/generate-voiceover.mjs`; `ELEVENLABS_API_KEY` and Sarah voice id documented; reusable BGM at `public/hackathon-demo/bgm.mp3`.
- **Source storyboard**: `repositories/anton-abyzov/vskill-platform/.specweave/scratch/skill-studio-hackathon-video.md` — already truth-checked, covers the 5 new feature scenes plus Tests-as-tab framing.
- **Existing scenes that stay** (refactor only, do not delete): `StudioIntro.tsx`, `StudioOutro.tsx`, `StudioAICreate.tsx`, `StudioBenchmark.tsx`, `StudioHistory.tsx`, `StudioMultiModel.tsx`, `StudioTestCases.tsx` under `src/remotion/scenes/studio/` — these get refactored to consume scene-kit + read from `script.ts`, but their visual identity is preserved.
- **Live preview servers** (already running per teammate brief): `http://localhost:3010` (INC-A baseline), `http://localhost:3030` (current dev), `http://localhost:3031` (Remotion studio).
- **Brand decisions locked**: memory `project_video_brand_decisions_2026_04.md` — Sarah voiceover, Studio Remotion colors source-of-truth, no YouTube embed dependence for the inline video.
- **Sequencing**: this increment unblocks INC-D `/docs/studio` inline-video reuse (INC-D will not duplicate the embed; it will reuse this increment's page and assets).
