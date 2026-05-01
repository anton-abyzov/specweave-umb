---
increment: 0817-watch-library-rename-and-render-101-series
title: "Rename /learn to /watch, promote to nav, render the 4 broken Learn101 videos with Sarah VO"
---

# Tasks

## T-001: Rename /learn to /watch — folder move + identifier renames + dynamic slug route

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Scope**:
- `git mv src/app/learn src/app/watch`
- `git mv src/app/watch/LearnPageClient.tsx src/app/watch/WatchPageClient.tsx`
- `git mv src/app/components/learn/LazyVideoPlayer.tsx src/app/components/learn/WatchVideoPlayer.tsx`
- Rename identifiers inside moved files (`LearnPageClient` → `WatchPageClient`, `LearnPage` → `WatchPage`, `/learn` strings → `/watch`)
- Scaffold `src/app/watch/[slug]/page.tsx` (~30 LOC): `getVideo(slug)` lookup; if found render `WatchVideoPlayer`; else `notFound()`
- `next.config.ts`: add 2 redirect entries — `/learn` → `/watch` (permanent: true) and `/learn/:slug*` → `/watch/:slug*` (permanent: true) in `redirects()`
- Update `src/app/watch/page.tsx` `Metadata.title` to `"Watch"`

**Test Plan** (BDD):
```
Given next.config.ts has permanent redirects for /learn and /learn/:slug*
When curl -I http://localhost:3000/learn
Then response status is 301 or 308 with Location: /watch

Given src/app/learn/ is git-moved to src/app/watch/
When the dev server renders /watch
Then HTTP 200 is returned and no /learn directory exists in the working tree

Given src/app/watch/[slug]/page.tsx exists
When a request hits /watch/getting-started-101
Then the page renders (not 404) and WatchVideoPlayer is mounted

Given /learn/:slug* redirects are configured
When curl -I http://localhost:3000/learn/getting-started-101
Then status is 301 or 308 with Location: /watch/getting-started-101
```

---

## T-002: Sitemap rewrite + nav/mobile/footer test assertions

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Scope**:
- Update `src/app/sitemap.ts`: replace `/learn` entry with `/watch` (zero `/learn` occurrences remain)
- Create `src/app/watch/__tests__/redirects.test.ts` Playwright spec: `request.get(url, { maxRedirects: 0 })` for `/learn`, `/learn/getting-started-101`, `/learn/cli-commands-101`, `/learn/security-scan-101`, `/learn/plugin-marketplace-101`; assert `[301, 308].includes(status)` for each
- Add or update `src/app/__tests__/sitemap.test.ts` to assert `<loc>https://verified-skill.com/watch</loc>` is present and no `/learn` entry exists
- Create or update `src/app/__tests__/layout.test.tsx` asserting desktop nav + footer contain Watch link between Studio and Submit
- Create or update `src/app/__tests__/MobileNav.test.tsx` asserting Watch entry present in mobile menu

**Test Plan** (BDD):
```
Given /learn and /learn/:slug* redirects are live
When Playwright calls request.get for each of the 5 /learn URLs with maxRedirects:0
Then all 5 return status in [301, 308]

Given sitemap.ts emits /watch
When /sitemap.xml is served
Then it contains <loc>https://verified-skill.com/watch</loc> and zero /learn occurrences

Given layout.tsx desktop nav renders Watch between Studio and Submit
When Vitest renders the nav snapshot
Then the snapshot contains "Watch" at position between "Studio" and "Submit"

Given MobileNav.tsx renders Watch
When Vitest renders the MobileNav component
Then Watch entry is present without horizontal overflow
```

---

## T-003: Watch in global navigation — desktop nav + mobile nav + footer

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Scope**:
- `src/app/layout.tsx` desktop nav (~lines 92-108): insert `<a href="/watch">Watch</a>` between Studio and Submit entries; total nav item count becomes 9 (Skills | Studio | Watch | Submit | Publishers | Trust | Queue | Docs | Insights)
- `src/app/layout.tsx` footer (~lines 123-129): add Watch `footer-link` entry alongside existing links
- `src/app/components/MobileNav.tsx` (~line 44 boundary): insert Watch entry between Studio and Submit

**Test Plan** (BDD):
```
Given layout.tsx desktop nav is updated
When a page renders the global header
Then nav renders 9 items: Skills | Studio | Watch | Submit | Publishers | Trust | Queue | Docs | Insights

Given MobileNav.tsx has Watch entry
When mobile nav is rendered on 375px viewport equivalent
Then Watch appears between Studio and Submit with no horizontal scroll

Given layout.tsx footer is updated
When the footer renders
Then a Watch footer-link anchor with href="/watch" is present
```

---

## T-004: Catalog rename — video-data.ts → video-catalog.ts + captionsSrc field + overview category

**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US4-05
**Status**: [x] completed

**Scope**:
- `git mv src/lib/learn/video-data.ts src/lib/learn/video-catalog.ts`
- Update `src/lib/learn/videos.ts` import path to `./video-catalog`; add `"overview"` to `VideoCategory` union; add optional `captionsSrc?: string` field to `Video` type
- Rewrite all path strings in `video-catalog.ts`:
  - `thumbnail`: `/learn/thumbnails/<slug>.webp` → `/watch/thumbnails/<slug>.webp`
  - `sources.mp4`: `/video/learn/<slug>.mp4` → `/video/watch/<slug>.mp4`
  - Add optional `sources.webm` for the 4 published slugs
  - Add `captionsSrc` field → `/video/watch/<slug>.vtt` for each published slug
- Update all consumer imports across `src/app/watch/page.tsx`, components, tests to import from new module
- Add `skills-manager-overview` entry as first array element: `featured: true`, `status: "published"`, `category: "overview"`, paths under `/video/watch/` and `/watch/thumbnails/`, `relatedDocs: ["/docs/getting-started"]`
- Create `src/lib/learn/__tests__/video-catalog.test.ts`: imports `VIDEOS` from `video-catalog`; asserts each published entry has `/video/watch/` paths and `captionsSrc` set; asserts `skills-manager-overview` is first with `featured: true`

**Test Plan** (BDD):
```
Given video-catalog.ts is the renamed file with updated paths
When Vitest imports VIDEOS from video-catalog
Then all 5 published entries have sources.mp4 under /video/watch/, thumbnail under /watch/thumbnails/, and captionsSrc set

Given skills-manager-overview is inserted as first element
When VIDEOS[0] is inspected
Then slug === "skills-manager-overview" and featured === true and category === "overview"

Given videos.ts re-exports from video-catalog
When downstream consumers import VIDEOS from videos.ts
Then TypeScript (tsc --noEmit) has zero errors
```

---

## T-005: Extend voiceover + VTT scripts + add 26 package.json scripts + thumbnail script update

**User Story**: US-003, US-004, US-005 | **Satisfies ACs**: AC-US3-04, AC-US3-05, AC-US3-06, AC-US4-03, AC-US4-04, AC-US5-02
**Status**: [x] completed

**Scope**:
- `scripts/generate-voiceover.mjs`: extend `VIDEO_SOURCES` map with all 5 watch slugs pointing to `src/remotion/scenes/watch/<slug>/script.ts`; extend `VIDEO_OUTPUTS` override map so each slug writes to `public/voiceover/watch/<slug>.mp3`
- `scripts/generate-vtt.mjs`: extend `VIDEO_SOURCES` and `VTT_OUTPUTS` for all 5 watch slugs pointing to `public/video/watch/<slug>.vtt`
- `scripts/generate-thumbnails.ts`: update `OUTPUT_DIR` to `public/watch/thumbnails`; update `THUMBNAIL_TARGETS` to reference `Watch101GettingStarted-still`, `Watch101CliCommands-still`, `Watch101SecurityScan-still`, `Watch101PluginMarketplace-still`, `SkillsManagerOverview-still`; add `--frame=60` for `cli-commands-101` (post-typewriter frame)
- `package.json`: delete 4 legacy `video:render:learn:*` scripts; add 26 new scripts (5 slugs × {mp4, webm, vtt, all, voiceover} + `thumbs:watch` + `video:render:watch:all` chain)

**Test Plan** (BDD):
```
Given generate-voiceover.mjs has VIDEO_SOURCES for all 5 watch slugs
When the file is parsed for VIDEO_SOURCES entries
Then entries exist for getting-started-101, cli-commands-101, security-scan-101, plugin-marketplace-101, skills-manager-overview

Given generate-vtt.mjs has VTT_OUTPUTS for all 5 watch slugs
When VTT_OUTPUTS is inspected
Then each slug maps to public/video/watch/<slug>.vtt

Given package.json has 26 new scripts
When npm run lists available scripts
Then video:render:watch:getting-started, video:render:watch:all, thumbs:watch appear; no video:render:learn:* remain

Given generate-thumbnails.ts has updated targets
When THUMBNAIL_TARGETS is parsed
Then 5 entries reference Watch101* and SkillsManagerOverview-still IDs with OUTPUT_DIR public/watch/thumbnails
```

---

## T-006: Refactor getting-started-101 composition + script.ts + Root.tsx registration

**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed

**Scope**:
- Create `src/remotion/scenes/watch/getting-started-101/script.ts`: export `GETTING_STARTED_SCRIPT: Scene[]` (5 scenes: TitleCard → InstallTerminal → FirstScanTerminal → ResultsBrowser → CTA outro); `accentColor: BRAND_COLORS.green`; target 1800 frames raw; export `GETTING_STARTED_EFFECTIVE_FRAMES`
- Refactor (move + rewrite) `src/remotion/scenes/learn/TitleCard.tsx` → `src/remotion/scenes/watch/getting-started-101/GettingStarted.tsx`: consumes `TerminalFrame`, `BigText`, `CommandTypewriter`, `CaptionBar`, `PillTag`, `TransitionWipe` from scene-kit; zero inline hex (only `BRAND_COLORS` import); composition ID `Watch101GettingStarted`
- Update `src/remotion/Root.tsx`: import `GettingStarted` from new path; add `<Composition id="Watch101GettingStarted" durationInFrames={GETTING_STARTED_EFFECTIVE_FRAMES}>` and `<Still id="Watch101GettingStarted-still">`; remove legacy `Learn101TitleCard` entries

**Test Plan** (BDD):
```
Given src/remotion/scenes/watch/getting-started-101/script.ts exports GETTING_STARTED_SCRIPT
When Vitest imports it
Then script array length >= 5 and GETTING_STARTED_EFFECTIVE_FRAMES is within 1700-1900
And every scene has voiceText, caption, durationFrames defined

Given GettingStarted.tsx uses only scene-kit imports for colors
When the file is searched for inline hex colors (#[0-9A-Fa-f]{6})
Then zero hex literals appear outside BRAND_COLORS usage

Given Root.tsx registers Watch101GettingStarted
When tsc --noEmit runs
Then Composition and Still IDs are present; Learn101TitleCard is absent
```

---

## T-007: Build cli-commands-101 NEW composition + script.ts + Root.tsx wiring

**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed

**Scope**:
- Create `src/remotion/scenes/watch/cli-commands-101/script.ts`: export `CLI_COMMANDS_SCRIPT: Scene[]` (6 scenes: TitleCard → vskill install typewriter → vskill scan + result → vskill list SkillCard cascade → vskill publish + queued pill → CTA); `accentColor: BRAND_COLORS.cyan`; target 2700 frames raw; export `CLI_COMMANDS_EFFECTIVE_FRAMES`
- Create `src/remotion/scenes/watch/cli-commands-101/CliCommands.tsx`: NEW composition using `TerminalFrame`, `CommandTypewriter`, `BigText`, `CaptionBar`, `PillTag` from scene-kit; composition ID `Watch101CliCommands`; no inline hex
- Update `src/remotion/Root.tsx`: add `Watch101CliCommands` Composition (durationInFrames={CLI_COMMANDS_EFFECTIVE_FRAMES}) + `Watch101CliCommands-still` Still; remove any legacy CLI Learn101 entry if present

**Test Plan** (BDD):
```
Given src/remotion/scenes/watch/cli-commands-101/script.ts
When Vitest imports it
Then CLI_COMMANDS_SCRIPT has length >= 6 and CLI_COMMANDS_EFFECTIVE_FRAMES is within 2500-2850

Given CliCommands.tsx imports from scene-kit only for colors
When file is grepped for inline hex
Then zero raw hex literals found

Given Root.tsx has Watch101CliCommands registered
When tsc --noEmit runs
Then Composition and Watch101CliCommands-still Still are present
```

---

## T-008: Refactor security-scan-101 composition + script.ts + Root.tsx wiring

**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed

**Scope**:
- Create `src/remotion/scenes/watch/security-scan-101/script.ts`: export `SECURITY_SCAN_SCRIPT: Scene[]` (5 scenes: TitleCard → "Why scan?" BigText → 4-step pipeline MetricBar rows → "All passed" pill cascade → CTA); `accentColor: BRAND_COLORS.purple`; target 2640 frames raw; export `SECURITY_SCAN_EFFECTIVE_FRAMES`
- Refactor `src/remotion/scenes/learn/SecurityScan.tsx` → `src/remotion/scenes/watch/security-scan-101/SecurityScan.tsx`: use `TerminalFrame`, `BigText`, `MetricBar`, `PillTag`, `CaptionBar`, `TransitionWipe` from scene-kit; composition ID `Watch101SecurityScan`; no inline hex
- Update `src/remotion/Root.tsx`: add `Watch101SecurityScan` Composition + `Watch101SecurityScan-still`; remove legacy `Learn101Security` entries

**Test Plan** (BDD):
```
Given src/remotion/scenes/watch/security-scan-101/script.ts
When Vitest imports it
Then SECURITY_SCAN_SCRIPT has length >= 5 and SECURITY_SCAN_EFFECTIVE_FRAMES is within 2500-2750

Given SecurityScan.tsx uses BRAND_COLORS.purple for accent
When file content is checked for inline hex
Then zero raw hex literals; purple accent via BRAND_COLORS import

Given Root.tsx has Watch101SecurityScan registered
When tsc --noEmit runs
Then Composition and Still IDs are present; Learn101Security is absent
```

---

## T-009: Refactor plugin-marketplace-101 composition + script.ts + Root.tsx wiring

**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed

**Scope**:
- Create `src/remotion/scenes/watch/plugin-marketplace-101/script.ts`: export `PLUGIN_MARKETPLACE_SCRIPT: Scene[]` (5 scenes: TitleCard → BrowserChrome home → SkillCard grid cascade → click frontend-design → vskill install terminal → "Installed" toast + CTA); `accentColor: BRAND_COLORS.cyan`; target 2250 frames raw; export `PLUGIN_MARKETPLACE_EFFECTIVE_FRAMES`
- Refactor `src/remotion/scenes/learn/PluginBrowse.tsx` → `src/remotion/scenes/watch/plugin-marketplace-101/PluginMarketplace.tsx`: use `BrowserChrome`, `SkillCard`, `PillTag`, `BigText`, `TerminalFrame`, `CaptionBar` from scene-kit; composition ID `Watch101PluginMarketplace`; no inline hex
- Update `src/remotion/Root.tsx`: add `Watch101PluginMarketplace` Composition + `Watch101PluginMarketplace-still`; remove legacy `Learn101Plugins` entries

**Test Plan** (BDD):
```
Given src/remotion/scenes/watch/plugin-marketplace-101/script.ts
When Vitest imports it
Then PLUGIN_MARKETPLACE_SCRIPT has length >= 5 and PLUGIN_MARKETPLACE_EFFECTIVE_FRAMES is within 2100-2400

Given PluginMarketplace.tsx uses scene-kit primitives only
When file content is grepped for inline hex
Then zero raw hex literals found

Given Root.tsx has Watch101PluginMarketplace registered
When tsc --noEmit runs
Then Composition and Still IDs are present; Learn101Plugins is absent
```

---

## T-010: Build skills-manager-overview NEW composition + script.ts + Root.tsx final wiring

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

**Scope**:
- Create `src/remotion/scenes/watch/skills-manager-overview/script.ts`: export `SKILLS_MANAGER_SCRIPT: Scene[]` (8 scenes per plan §6.5: TitleCard 240f → vskill search 360f → vskill install 360f → vskill list TUI 300f → vskill update TUI 360f → vskill studio 180f → BrowserChrome Studio 360f → CTA 240f); export `SKILLS_MANAGER_EFFECTIVE_FRAMES` (target 2400-3000 for 80-100 s at 30fps); scenes 4 and 5 (index 3, 4) use `accentColor: "#D97757"` (Claude orange TUI scenes); all others use BRAND_COLORS taxonomy
- Create `src/remotion/scenes/watch/skills-manager-overview/SkillsManagerOverview.tsx`: uses `TerminalFrame`, `TUIFrame`, `SkillCard`, `BrowserChrome`, `CommandTypewriter`, `CaptionBar`, `PillTag`, `BigText`, `TransitionWipe`; composition ID `SkillsManagerOverview`; Claude orange `#D97757` only on TUI scenes 4-5 via direct prop; all other scenes use BRAND_COLORS
- Update `src/remotion/Root.tsx`: add `SkillsManagerOverview` Composition (durationInFrames={SKILLS_MANAGER_EFFECTIVE_FRAMES}) + `SkillsManagerOverview-still` Still; confirm all 4 legacy `Learn101*` entries removed; `SpecWeaveWorkflow` (coming-soon) retained

**Test Plan** (BDD):
```
Given src/remotion/scenes/watch/skills-manager-overview/script.ts
When Vitest imports it
Then SKILLS_MANAGER_SCRIPT has length >= 8; SKILLS_MANAGER_EFFECTIVE_FRAMES is in range 2400-3000
And scenes at index 3 and 4 have accentColor "#D97757"

Given SkillsManagerOverview.tsx uses scene-kit primitives
When file is grepped for hex literals other than #D97757
Then zero additional inline hex colors are present

Given Root.tsx has SkillsManagerOverview and all 5 Watch101 Compositions registered
When tsc --noEmit runs
Then all 5 Compositions + 5 Stills are present; all 4 Learn101* IDs are absent; SpecWeaveWorkflow is present
```

---

## T-011: WatchVideoPlayer.tsx — captionsSrc prop + track wiring + consumer pass-through

**User Story**: US-003 | **Satisfies ACs**: AC-US3-06
**Status**: [x] completed

**Scope**:
- In `src/app/components/learn/WatchVideoPlayer.tsx` (renamed from LazyVideoPlayer in T-001): add `captionsSrc?: string` prop to the component interface
- Wire `<track kind="captions" default src={captionsSrc} />` inside the `<video>` element when `captionsSrc` is provided
- Update `VideoCard.tsx` and `VideoGrid.tsx` (and any other consumers) to pass `captionsSrc` through from the `VIDEOS` catalog entry
- Extend `scripts/__tests__/generate-vtt.test.ts` (INC-B test) with 5 watch fixture assertions: each VTT output path for watch slugs matches `public/video/watch/<slug>.vtt`

**Test Plan** (BDD):
```
Given WatchVideoPlayer receives captionsSrc="/video/watch/getting-started-101.vtt"
When the component renders
Then <track kind="captions" default src="/video/watch/getting-started-101.vtt"> is in the DOM

Given VideoCard passes captionsSrc from catalog entry
When VIDEOS entry has captionsSrc set
Then VideoCard renders WatchVideoPlayer with that captionsSrc prop

Given generate-vtt.mjs VTT_OUTPUTS has all 5 watch slugs
When the Vitest fixture test parses VTT_OUTPUTS
Then each watch slug maps to public/video/watch/<slug>.vtt
```

---

## T-012: Render voiceovers + videos + VTTs + thumbnails (25 local artifacts)

**User Story**: US-003, US-004, US-005 | **Satisfies ACs**: AC-US3-04, AC-US3-05, AC-US4-04, AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Scope** (local-only, not run in CI):
- Run ElevenLabs voiceover for all 5 slugs sequentially: `node scripts/generate-voiceover.mjs getting-started-101`, then cli-commands-101, security-scan-101, plugin-marketplace-101, skills-manager-overview
- Verify each `public/voiceover/watch/<slug>.mp3` is non-empty (>= 50 KB)
- Run Remotion renders in D4 order (getting-started-101 first, skills-manager-overview last): `npm run video:render:watch:<slug>:all` (mp4 + webm + vtt) for each
- Run thumbnail renders: `npm run thumbs:watch` (5 WebP stills via `npx remotion still`)
- `git mv public/learn/thumbnails public/watch/thumbnails`; remove 43-byte stub files; verify real renders landed
- Remove `public/learn/` directory if empty after moves

**Test Plan** (BDD):
```
Given voiceover pipeline runs for all 5 slugs
When each public/voiceover/watch/<slug>.mp3 is stat'd
Then size >= 50 KB for all 5

Given Remotion renders complete for all 5 slugs
When each public/video/watch/<slug>.mp4 is stat'd
Then size >= 1 MB and <= 25 MB for 101-series; >= 5 MB and <= 40 MB for skills-manager-overview

Given npm run thumbs:watch runs
When each public/watch/thumbnails/<slug>.webp is stat'd
Then size >= 5 KB and <= 200 KB for all 5; dimensions 1280x720 per webp metadata

Given public/learn/thumbnails/ is moved and stubs replaced
When public/learn/thumbnails/ is checked
Then directory does not exist; public/watch/thumbnails/ has 5 real WebP files
```

---

## T-013: Test suite — video-size-constraints + no-inline-hex + voiceover-size + scripts integrity

**User Story**: US-003, US-004, US-005 | **Satisfies ACs**: AC-US3-05, AC-US4-04, AC-US5-01, AC-US5-03
**Status**: [x] completed

**Scope**:
- Rewrite `src/lib/learn/__tests__/video-size-constraints.test.ts`: point at `public/video/watch/`; assert each of the 5 published slugs has an mp4 where `fs.statSync` confirms it exists and is within bounds (1-25 MB for 101-series; 5-40 MB for skills-manager-overview); assert each webp thumbnail in `public/watch/thumbnails/` is 5-200 KB; test is non-vacuous (file list is not empty)
- Create `src/lib/learn/__tests__/voiceover-size.test.ts`: for each of the 5 slugs assert `public/voiceover/watch/<slug>.mp3` exists and size >= 50 KB
- Create `src/remotion/scenes/watch/__tests__/no-inline-hex.test.ts`: read all `.tsx` files under `src/remotion/scenes/watch/` recursively; regex for raw hex literals (`#[0-9A-Fa-f]{6}`) excluding `#D97757`; assert zero matches
- Create `src/remotion/scenes/watch/__tests__/scripts.test.ts`: for each of the 5 slugs import their `script.ts` and assert: array length >= 5 (>= 8 for skills-manager-overview), every scene has `voiceText`, `caption`, `durationFrames`; effective frames constant is within expected range

**Test Plan** (BDD):
```
Given public/video/watch/ contains 5 rendered mp4 files
When video-size-constraints.test.ts runs
Then each file exists, size is within bounds, and the test is non-vacuous

Given public/voiceover/watch/ contains 5 mp3 files
When voiceover-size.test.ts runs
Then each file is >= 50 KB

Given all watch scene tsx files are scanned for hex literals
When no-inline-hex.test.ts runs
Then zero hex literals (excluding #D97757) are found

Given all 5 script.ts files exist
When scripts.test.ts imports each
Then all scenes have required fields and effective frames constants are in valid ranges
```

---

## T-014: Playwright E2E — all cards play + no fallback + captions + nav click + no broken images

**User Story**: US-003, US-004, US-005 | **Satisfies ACs**: AC-US2-04, AC-US3-07, AC-US4-06, AC-US5-04
**Status**: [x] completed

**Scope**:
- Create `tests/e2e/watch-no-fallback.spec.ts`: navigate to `/watch`; for each of the 5 published card play buttons, click and assert `<video>` element reaches `readyState >= 3` within 5 s and no "Video unavailable" text rendered
- Create `tests/e2e/watch-captions.spec.ts`: navigate to `/watch`, click first card; assert `<track kind="captions">` element is mounted and `src` resolves to `/video/watch/<slug>.vtt`
- Create or update `tests/e2e/watch-nav.spec.ts`: click desktop "Watch" nav link from homepage; assert navigation to `/watch` with HTTP 200 and video grid visible; take Playwright screenshot for closure summary
- Add to watch-no-fallback or separate spec: assert no visible broken image icon for any of the 5 published cards (`img.naturalWidth > 0` for all 5 card thumbnails)

**Test Plan** (BDD):
```
Given /watch renders with 5 published cards
When Playwright clicks each play button
Then <video>.readyState >= 3 within 5 s and no "Video unavailable" text for all 5

Given WatchVideoPlayer wires <track kind="captions">
When Playwright inspects the DOM after clicking a card
Then a <track kind="captions" src="/video/watch/<slug>.vtt"> element is found

Given Watch appears in desktop nav
When Playwright clicks the Watch nav link from homepage
Then URL is /watch and HTTP 200 and video grid has at least 5 card elements

Given real WebP thumbnails are in place
When Playwright screenshots the /watch grid
Then img.naturalWidth > 0 for all 5 published card thumbnails (no broken-image icons)
```

---

## T-015: Verification gates — tsc + vitest + ffprobe duration parity + local dev preview screenshots

**User Story**: US-001 through US-005 | **Satisfies ACs**: AC-US1-06, AC-US3-07, AC-US4-06
**Status**: [x] completed

**Scope**:
- Run `npx tsc --noEmit` in `repositories/anton-abyzov/vskill-platform/` — zero errors required
- Run `npx vitest run` — all unit/integration tests pass
- Run `npx playwright test` — all E2E specs pass (redirects, nav, no-fallback, captions, no-broken-images)
- Run ffprobe duration parity check: for each of the 5 slugs compare mp4 duration vs webm duration; assert difference < 300 ms
- Run local dev server (`npm run dev`, port 3000); screenshot `/watch` (full grid visible); screenshot `/learn` (confirms 301/308 redirect to /watch); screenshot one card playing with captions toggled on
- Paste screenshots into closure summary; confirm all success criteria from spec are visually verifiable

**Grill Findings Resolution (2026-05-01)**:
- CRITICAL #3 (`video-size-constraints.test.ts` RED): RESOLVED — test now passes after webm re-renders for `skills-manager-overview`, `security-scan-101`, `plugin-marketplace-101` completed.
- CRITICAL #4 (Watch101 scene tests broken): FALSE POSITIVE — `vi.mock('remotion', ...)` factories already include `Audio` + `staticFile`. 6/6 tests pass on `src/remotion/scenes/watch/`.
- HIGH #2 (skills-manager VO 7s longer than video): RESOLVED via Option B — extended `EndCard` from 240→480 frames in `src/remotion/scenes/watch/skills-manager-overview/script.ts`. New raw frames 2940 / effective 2835 = 94.5s composition (vs 93.4s VO). Catalog `duration` updated 87→95s. Test fixture expectedRawFrames updated 2700→2940. MP4 + WebM + VTT + thumbnail re-rendered.
- HIGH #3 (test bounds looser than spec): FALSE POSITIVE — `video-size-constraints.test.ts:28-41` already has slug-specific bounds (1-25 MB for 101-series, 5-40 MB for skills-manager) matching AC-US3-05 / AC-US4-04. Grill cited stale pre-T-013 numbers.
- HIGH #1 (MP4 durations miss ±1s): RESOLVED — catalog DURATION values were already aligned to actual MP4 durations within ±1s. Grill compared against raw-frame expectations, not catalog declarations. After skills-manager re-render the catalog now reads `duration: 95` and the MP4 is 94.55s — within ±1s tolerance.
- Spec ADR D1 reconciliation: AC-US1-01/02/03 + FR-001 + Success Criteria amended to accept "HTTP 301 or 308" per ADR `0817-01` §D1 (Next.js `permanent: true` emits 308 by design).

**Test Plan** (BDD):
```
Given all code changes are complete
When npx tsc --noEmit runs
Then exit code 0, zero type errors

Given all Vitest tests are implemented and artifacts rendered
When npx vitest run runs
Then all tests pass including video-size-constraints non-vacuous, no-inline-hex, scripts integrity, voiceover-size, catalog, VTT

Given all Playwright specs implemented and dev server running
When npx playwright test runs
Then all specs pass: redirects, nav click, no-fallback, captions, no-broken-images

Given mp4 and webm renders completed for all 5 slugs
When ffprobe checks duration for each pair
Then |mp4_duration - webm_duration| < 0.3 s for all 5

Given local dev server is running on port 3000
When /watch is loaded and screenshots taken
Then grid shows 5 cards with real thumbnails; /learn redirects to /watch; captions track loads for a playing card
```

---

## Bidirectional AC Coverage

| AC | Task |
|----|------|
| AC-US1-01 | T-001, T-002 |
| AC-US1-02 | T-001, T-002 |
| AC-US1-03 | T-002 |
| AC-US1-04 | T-001 |
| AC-US1-05 | T-002 |
| AC-US1-06 | T-002, T-015 |
| AC-US2-01 | T-003 |
| AC-US2-02 | T-003 |
| AC-US2-03 | T-003 |
| AC-US2-04 | T-002, T-014 |
| AC-US2-05 | T-002 |
| AC-US3-01 | T-004 |
| AC-US3-02 | T-006, T-007, T-008, T-009 |
| AC-US3-03 | T-006, T-007, T-008, T-009 |
| AC-US3-04 | T-005, T-012 |
| AC-US3-05 | T-005, T-012, T-013 |
| AC-US3-06 | T-005, T-011 |
| AC-US3-07 | T-014, T-015 |
| AC-US4-01 | T-010 |
| AC-US4-02 | T-010 |
| AC-US4-03 | T-005, T-010 |
| AC-US4-04 | T-005, T-012, T-013 |
| AC-US4-05 | T-004 |
| AC-US4-06 | T-014, T-015 |
| AC-US5-01 | T-012, T-013 |
| AC-US5-02 | T-005, T-012 |
| AC-US5-03 | T-012, T-013 |
| AC-US5-04 | T-014 |
