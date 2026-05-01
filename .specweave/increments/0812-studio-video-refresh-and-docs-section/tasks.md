---
increment: 0812-studio-video-refresh-and-docs-section
title: "Refresh /studio video using scene-kit + Sarah VO; create /docs/studio section"
status: planned
---

# Tasks — 0812 Studio Video Refresh + /docs/studio

## Task List

### T-001: Author src/remotion/scenes/studio/script.ts
**User Story**: US-001, US-002, US-005 | **Satisfies ACs**: AC-US1-08, AC-US2-01, AC-US5-01, AC-US5-05
**Status**: [x] completed

Full 11-scene `STUDIO_SCRIPT` array (6 existing re-timed + 5 new). Exports: `StudioScene` type, `STUDIO_SCRIPT`, `STUDIO_FPS`, `STUDIO_TRANSITION_FRAMES`, `STUDIO_TOTAL_FRAMES`, `STUDIO_EFFECTIVE_FRAMES`, `STUDIO_DURATION_SECONDS`, `STUDIO_VOICE_TEXT`, `STUDIO_VOICE`. Each entry has: `id`, `durationFrames`, `transitionType`, `voiceText`, `caption?`, `visualNotes`. Scene timing table from plan §3.1 (total raw 4980 frames, effective ~4830). Snapshot test at `src/remotion/scenes/studio/__tests__/script.test.ts`: unique ids, positive durationFrames, non-empty voiceText, last scene transitionType null, all 5 new ids present.

**Test Plan** (BDD):
  Given the file `src/remotion/scenes/studio/script.ts` is created
  When Vitest runs `script.test.ts`
  Then: (a) all 11 scenes have required fields; (b) `STUDIO_SCRIPT.reduce((s,x)=>s+x.durationFrames,0)` equals 4980 (raw total per plan §3.1); (c) last scene `transitionType` is null; (d) all 5 new scene ids are present in the array

---

### T-002: Refactor SkillStudioDemo.tsx to script-as-data + scene-kit
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

Port `src/remotion/SkillStudioDemo.tsx` to mirror `HackathonDemo.tsx:60-104` topology: flat-map `STUDIO_SCRIPT` into `<TransitionSeries>` entries, derive `durationInFrames` and `transition` from script entries. Import all scene components from a `Record<string, React.FC>` registry. All primitive imports come only from `../scene-kit` (no direct `../components/` for anything scene-kit covers). Wire audio: single `<Audio src={staticFile("studio/voiceover-raw.mp3")} volume={1.0}>` (placeholder path — T-008 generates the file) + BGM `<Audio src={staticFile("product-demo/bgm.mp3")} volume={0.20}>` inside `<Sequence from={30}>` cold-open. Update `src/remotion/Root.tsx`: set `durationInFrames={STUDIO_EFFECTIVE_FRAMES}`.

**Test Plan** (BDD):
  Given `script.ts` (T-001) and scene-kit are in place
  When grep runs on `src/remotion/SkillStudioDemo.tsx`
  Then: (a) no import from `../components/` for primitives that scene-kit exports; (b) exactly one `<Audio` whose src ends in `studio/voiceover-raw.mp3`; (c) exactly one `<Audio` whose src ends in `product-demo/bgm.mp3` with `volume` ≤ 0.3; (d) `Root.tsx` references `STUDIO_EFFECTIVE_FRAMES` for `durationInFrames`

---

### T-003: Implement TestsTabIntro.tsx (new scene 1/5)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03
**Status**: [x] completed

Create `src/remotion/scenes/studio/TestsTabIntro.tsx`. Visual: Studio chrome (STUDIO_LIGHT), Tests tab active in 4-tab strip (`Eval Cases`, `Eval Runs`, `Tests`, `History`), 3 test case rows, "Run all" click → spinner cascade → green ticks at frames 90/150/210 → `3/3 passed · 100%` pill springs in at frame 220. Primitives: `BrowserChrome`, `PillTag`, `MetricBar`. Duration: 540 frames. Accent: `BRAND_COLORS.green`. Component reads voiceText/caption from `STUDIO_SCRIPT.find(s => s.id === "TestsTabIntro")` via props.

**Test Plan** (BDD):
  Given `TestsTabIntro.tsx` is mounted in jsdom via @testing-library/react
  When rendered at frame 0
  Then: (a) no throw; (b) rendered output contains all 4 tab labels including "Tests"; (c) component file imports only from `../scene-kit` for its primitives (grep assertion in test)

---

### T-004: Implement PublishToGitHub.tsx (new scene 2/5)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04
**Status**: [x] completed

Create `src/remotion/scenes/studio/PublishToGitHub.tsx`. Visual: Publish modal slide-in with "Push to GitHub" affordance + "Generate with AI" button and `github.com/<owner>/<repo>` destination field. Terminal strip typing `gh repo create …` via `CommandTypewriter` (frames 90–150). Green `repo created` pill at 160. Cross-fade at 280 to `BrowserChrome` showing verified-skill.com with status pill cycling Queued→Scanning→Processed ✓ · v1.0.0. Duration: 720 frames. Accent: `BRAND_COLORS.blue`. Primitives: `BrowserChrome`, `TerminalFrame`, `CommandTypewriter`, `PillTag`.

**Test Plan** (BDD):
  Given `PublishToGitHub.tsx` is mounted
  When rendered at frame 0
  Then: (a) no throw; (b) markup contains a button/element labelled "Generate with AI"; (c) markup contains a `github.com/` string for the destination field placeholder

---

### T-005: Implement InstallScopePicker.tsx (new scene 3/5)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-05
**Status**: [x] completed

Create `src/remotion/scenes/studio/InstallScopePicker.tsx`. Visual: Studio chrome with URL bar `localhost:5173/skills/…`. Three scope rows (User, Project, Global) as `PillTag` rows with radio dot + label + helper text. At frame 90 cursor lands on Project row → radio fills cyan. At frame 180 Install click → green `✓ Installed` toast slides up. Duration: 420 frames. Accent: `BRAND_COLORS.cyan`. Primitives: `BrowserChrome`, `PillTag`.

**Test Plan** (BDD):
  Given `InstallScopePicker.tsx` is mounted
  When rendered at frame 0
  Then: (a) no throw; (b) markup contains all three scope labels: "User", "Project", "Global"; (c) "Project" row is visually distinguished as default selected scope

---

### T-006: Implement UpdateToast.tsx (new scene 4/5)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-06
**Status**: [x] completed

Create `src/remotion/scenes/studio/UpdateToast.tsx`. Visual: Bell icon with red `1` badge. At frame 30 popup appears: "1 update available · Refresh", single skill row showing `1.0.0 → 1.0.1` version diff, "Update" CTA button, "View all" footer. Cursor moves to Update at frame 180 → click at frame 240 → row flips to green `✓ Updated to 1.0.1`. Hold 360 frames, then 4 feature-recap pills cascade. Duration: 600 frames. Accent: `BRAND_COLORS.purple`. Primitives: `BrowserChrome`, `PillTag`.

**Test Plan** (BDD):
  Given `UpdateToast.tsx` is mounted
  When rendered at frame 35 (after popup appears)
  Then: (a) no throw; (b) markup contains "Update available" text; (c) markup contains version diff strings ("1.0.0" and "1.0.1"); (d) markup contains an "Update" CTA button

---

### T-007: Implement CommandPalette.tsx (new scene 5/5)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-07
**Status**: [x] completed

Create `src/remotion/scenes/studio/CommandPalette.tsx`. Visual: Studio chrome dimmed at 60% behind centered ⌘K palette overlay. Frame 30: ⌘K key-press graphic (rendered as `PillTag`). Frame 45: palette springs in. `CommandTypewriter` types `frontend-design` in search input. Three `SkillCard` result rows. Cursor → first row highlight → click at frame 180 → palette dismisses (200ms fade) → main pane crossfades to skill detail. Duration: 360 frames. Accent: `BRAND_COLORS.cyan`. Primitives: `BrowserChrome`, `CommandTypewriter`, `SkillCard`, `PillTag`.

**Test Plan** (BDD):
  Given `CommandPalette.tsx` is mounted
  When rendered at frame 50 (palette fully visible)
  Then: (a) no throw; (b) markup contains a search input element; (c) markup contains at least 3 skill/command result rows; (d) at least one row shows a keyboard-shortcut hint element

---

### T-008: Generate Sarah voiceover — run generate-voiceover.mjs studio
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US5-02
**Status**: [x] completed

Add npm script `video:voiceover:studio` to `package.json`. Run `npm run video:voiceover:studio` (reads `STUDIO_SCRIPT[*].voiceText`, calls ElevenLabs voice `EXAVITQu4vr4xnSDxMaL` Sarah, model `eleven_v3`, writes `public/studio/voiceover-raw.mp3`). Verify output: file exists, >50 KB, `ffprobe` duration ~105–130s (Sarah's pace at the locked script length lands ~113s; the composition's remaining ~48s are an intentional BGM cinematic outro per `project_video_brand_decisions_2026_04`).

**Test Plan** (BDD):
  Given `script.ts` (T-001) is authored and `ELEVENLABS_API_KEY` is set in `.env.local`
  When `npm run video:voiceover:studio` completes
  Then: (a) `public/studio/voiceover-raw.mp3` exists and size > 50 KB; (b) `ffprobe` reports duration in range [105, 130] seconds (architect-locked target); (c) `SkillStudioDemo.tsx` has `<Audio` with src ending in `studio/voiceover-raw.mp3` (verified by grep)

---

### T-009: Author scripts/generate-vtt.mjs + unit tests
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US5-03
**Status**: [x] completed

Create `scripts/generate-vtt.mjs <video-name>` that imports `STUDIO_SCRIPT` from `src/remotion/scenes/studio/script.ts`, computes cumulative cue offsets (start = cumulative effective frames before scene / 30fps, end = start + durationFrames/30), takes cue text from `scene.caption ?? scene.voiceText.split('.')[0]` (truncated to ≤80 chars), writes a WebVTT-1.0-conformant file to `public/video/skill-studio.vtt`. Add npm script `video:vtt:studio` to `package.json`. Unit test at `scripts/__tests__/generate-vtt.test.ts`: fixture = 3-scene mock script (durations 300/240/180, transitions fade/slide-right/null), asserts: WEBVTT header on line 1, exactly 3 cue blocks, monotonically increasing times, `end > start` for every cue, cue text ≤ 80 chars.

**Test Plan** (BDD):
  Given a 3-scene mock fixture with known frame counts
  When `generate-vtt.mjs` processes the fixture
  Then: (a) output starts with `WEBVTT`; (b) exactly 3 cue blocks produced; (c) all start times are monotonically non-decreasing; (d) every `end > start`; (e) every cue text line ≤ 80 characters

---

### T-010: Render skill-studio.mp4 + .webm + .vtt (full render pipeline)
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-05, AC-US2-06, AC-US3-01, AC-US3-02
**Status**: [x] completed

Add npm script `video:render:studio:all` to `package.json` chaining: `npm run video:render:studio && npm run video:render:studio:webm && npm run video:vtt:studio`. Run it. Verify artifacts: `public/video/skill-studio.mp4` >5 MB, `ffprobe` duration in [178, 212] seconds; `public/video/skill-studio.webm` exists; `stat -f %m` on mp4 and webm differ by <300 seconds; `public/video/skill-studio.vtt` starts with `WEBVTT` and has ≥ 11 cue blocks.

**Test Plan** (BDD):
  Given all scenes (T-001–T-007) and voiceover (T-008) and VTT generator (T-009) are in place
  When `npm run video:render:studio:all` completes
  Then: (a) mp4 size > 5 MB; (b) `ffprobe` mp4 duration in [178, 212]s; (c) mp4 and webm mtime diff < 300s (no drift); (d) `public/video/skill-studio.vtt` begins with `WEBVTT` and has ≥ 11 cue blocks

---

### T-011: VideoPlayer.tsx — captionsSrc prop + conditional track render
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed

Update `src/app/components/shared/VideoPlayer.tsx`: add optional `captionsSrc?: string` prop to the `VideoPlayerProps` interface. Render `<track kind="captions" srcLang="en" label="English" src={captionsSrc} default>` ONLY when `captionsSrc` is provided (omit the track entirely when absent — empty track is invalid HTML and confuses Chrome). Existing callers remain unchanged (no captions for them). Add Vitest unit test asserting: with `captionsSrc` → `<track>` present with correct `src`, `kind`, `label`; without `captionsSrc` → no `<track>` element.

**Test Plan** (BDD):
  Given `VideoPlayer.tsx` is rendered via @testing-library/react
  When rendered WITH `captionsSrc="/video/skill-studio.vtt"`
  Then `<track>` element exists with `src="/video/skill-studio.vtt"`, `kind="captions"`, `label="English"`
  When rendered WITHOUT `captionsSrc`
  Then no `<track>` element is in the rendered output

---

### T-012: buildChapters.ts + studio/page.tsx chapters auto-gen + captions wiring
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US3-06, AC-US5-04
**Status**: [x] completed

Create `src/app/studio/buildChapters.ts`: pure function `buildStudioChapters()` reading `STUDIO_SCRIPT`, computing cumulative seconds with 15-frame transition overlap per plan §7.3, returning `{ time: string; seconds: number; title: string }[]`. Update `src/app/studio/page.tsx`: (a) replace hand-typed `DEMO_CHAPTERS` array with `const DEMO_CHAPTERS = buildStudioChapters()`; (b) switch `mp4=` prop from R2 URL to `"/video/skill-studio.mp4"`; (c) add `captionsSrc="/video/skill-studio.vtt"` to `ProductDemoCard` (or wire through if it wraps `VideoPlayer`); (d) replace hardcoded `hasPart` SEO array with `DEMO_CHAPTERS.map(c => ({ "@type": "Clip", name: c.title, startOffset: c.seconds, ... }))`. Unit test at `src/app/studio/__tests__/chapters.test.ts`: given known `STUDIO_SCRIPT`, asserts `DEMO_CHAPTERS[i].seconds === Math.floor(cumFrames/30)` and `DEMO_CHAPTERS.length === STUDIO_SCRIPT.length`.

**Test Plan** (BDD):
  Given `STUDIO_SCRIPT` with known cumulative frame offsets (scene 0 at 0s, scene 1 at 8s per plan §3.1)
  When `buildStudioChapters()` is called
  Then: (a) `DEMO_CHAPTERS[0].seconds === 0`; (b) `DEMO_CHAPTERS[1].seconds === 8`; (c) `DEMO_CHAPTERS.length === STUDIO_SCRIPT.length`; (d) `page.tsx` no longer contains hardcoded chapter timestamp strings

---

### T-013: Create src/app/docs/studio/page.tsx (full content)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

Create `src/app/docs/studio/page.tsx` as a Next.js App Router `.tsx` page (marketing-shaped, not MDX). Export `metadata` object with `title` containing "Studio". Embed `<VideoPlayer mp4="/video/skill-studio.mp4" webm="/video/skill-studio.webm" captionsSrc="/video/skill-studio.vtt" ariaLabel="Skill Studio product walkthrough" accentColor="#06b6d4" />` near the top. Body: 7 sections with `<h2>` headings — Plain-English Evals (`id="evals"`), A/B Compare (`id="ab-compare"`), Any Model (`id="any-model"`), Local-first 100% Local (`id="local-first"`), Publish-to-GitHub (`id="publish-to-github"`), Install Scopes (`id="install-scopes"`), Update Notifications (`id="updates"`). Each section: 60–120 word paragraph. Related section with internal links to `/docs/security-guidelines`, `/docs/plugins`, `/docs/submitting`.

**Test Plan** (BDD):
  Given `src/app/docs/studio/page.tsx` is created
  When the file is compiled and its content grepped
  Then: (a) `metadata.title` contains "Studio"; (b) `VideoPlayer` rendered with `mp4="/video/skill-studio.mp4"` and non-empty `captionsSrc`; (c) all 7 heading strings present as `<h2>` or `<h3>` (Plain-English Evals, A/B Compare, Any Model, Local-first, Publish-to-GitHub, Install Scopes, Update Notifications); (d) `npx tsc --noEmit` reports 0 errors

---

### T-014: docs-nav.ts Studio entry + sitemap.ts + nav test update
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05, AC-US4-06
**Status**: [x] completed

Update `src/app/docs/docs-nav.ts`: insert Studio nav section with `label: "Studio"`, `href: "/docs/studio"`, and 7 anchor-linked children (Overview → `/docs/studio`, Plain-English Evals → `#evals`, A/B Compare → `#ab-compare`, Any Model → `#any-model`, Publish to GitHub → `#publish-to-github`, Install Scopes → `#install-scopes`, Updates → `#updates`) positioned AFTER the Quickstart entry and BEFORE the Core Concepts entry. Update `src/app/sitemap.ts`: add `{ url: \`\${base}/docs/studio\`, changeFrequency: "weekly", priority: 0.7 }` grouped with other `/docs/*` entries. Update `docs-nav.test.ts` (or its allow-list): extend section hierarchy allow-list to include "Studio" so the position-enforcer test continues to pass.

**Test Plan** (BDD):
  Given the updated `docs-nav.ts`, `sitemap.ts`, and `docs-nav.test.ts`
  When unit tests run
  Then: (a) test asserting `label: "Studio"` entry present at correct array position passes; (b) `DOCS_NAV` index of Studio > index of Quickstart, < index of Core Concepts; (c) sitemap test finds one entry with url ending `/docs/studio`; (d) `npx vitest run` passes including docs-nav position-enforcer test

---

### T-015: Verification gates (E2E + type-check + unit sweep)
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: AC-US3-04, AC-US3-05, AC-US4-06, AC-US2-05, AC-US2-06
**Status**: [x] completed

Run all closure gates:
1. `npx tsc --noEmit` → 0 errors across all modified and created files
2. `npx vitest run` → all existing tests pass + new tests pass: `script.test.ts`, `chapters.test.ts`, `generate-vtt.test.ts`, `VideoPlayer` caption conditional test, 5 scene smoke tests (T-003 through T-007)
3. ffprobe assertions: mp4 duration in [178, 212]s, mp4/webm mtime diff < 300s (reconfirm from T-010)
4. Playwright E2E scenario A: navigate to `/studio`, assert `<video>` element present, assert `<track src="/video/skill-studio.vtt">` in DOM, assert `/video/skill-studio.vtt` returns HTTP 200 via `preview_network`
5. Playwright E2E scenario B: navigate to `/docs/studio`, assert `<video>` element present, assert sidebar shows "Studio" item
6. Playwright E2E scenario C: navigate to `/docs/getting-started`, assert "Studio" sidebar item visible, click it, assert navigation to `/docs/studio`
7. Playwright E2E CC toggle: navigate to `/studio`, play video, enable CC track, assert `::cue` text node appears within 5 seconds of playback
8. Closure summary includes Claude Preview screenshots of `/studio` and `/docs/studio` from running local server (feedback_video_local_preview rule)

**Test Plan** (BDD):
  Given all T-001 through T-014 are complete and local dev server is running on `localhost:3030`
  When the full verification suite runs
  Then: (a) 0 TypeScript errors; (b) all Vitest tests pass; (c) all 4 Playwright E2E scenarios pass including CC toggle; (d) ffprobe confirms render durations within spec; (e) local preview screenshots of `/studio` and `/docs/studio` included in closure summary

---

## Bidirectional AC Coverage

| AC | Covered By |
|----|-----------|
| AC-US1-01 | T-002 |
| AC-US1-02 | T-002, T-003, T-004, T-005, T-006, T-007 |
| AC-US1-03 | T-003 |
| AC-US1-04 | T-004 |
| AC-US1-05 | T-005 |
| AC-US1-06 | T-006 |
| AC-US1-07 | T-007 |
| AC-US1-08 | T-001 |
| AC-US2-01 | T-001 |
| AC-US2-02 | T-008 |
| AC-US2-03 | T-002 |
| AC-US2-04 | T-002 |
| AC-US2-05 | T-010, T-015 |
| AC-US2-06 | T-010, T-015 |
| AC-US3-01 | T-009, T-010 |
| AC-US3-02 | T-009 |
| AC-US3-03 | T-011 |
| AC-US3-04 | T-015 |
| AC-US3-05 | T-015 |
| AC-US3-06 | T-012 |
| AC-US4-01 | T-013 |
| AC-US4-02 | T-013 |
| AC-US4-03 | T-013 |
| AC-US4-04 | T-014 |
| AC-US4-05 | T-014 |
| AC-US4-06 | T-014, T-015 |
| AC-US5-01 | T-001 |
| AC-US5-02 | T-008 |
| AC-US5-03 | T-009 |
| AC-US5-04 | T-012 |
| AC-US5-05 | T-001 |
