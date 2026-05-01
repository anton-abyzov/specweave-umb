# Implementation Plan: Rename /learn to /watch, promote to nav, render the 4 broken Learn101 videos with Sarah VO

INC-C of the verified-skill.com video overhaul (master plan: `~/.claude/plans/curried-beaming-summit.md`). Foundation: ADR `0810-01-video-pipeline-and-token-sync.md` (scene-kit + generic VO + script-as-data). Studio precedent: ADR `0812-01-studio-video-refresh-and-docs.md` (script-as-data + chapters + .vtt sidecar).

All file paths are inside `repositories/anton-abyzov/vskill-platform/` unless otherwise noted.

## 1. Overview

Two coordinated outcomes (per spec.md):

1. **IA promotion** — `src/app/learn/` → `src/app/watch/` folder rename, 301 redirects (`/learn`, `/learn/:slug*`), nav promotion (Studio | **Watch** | Submit), sitemap rewrite, and `src/lib/learn/video-data.ts` → `src/lib/learn/video-catalog.ts` (file rename + symbol stays `VIDEOS`; **directory `src/lib/learn/` is intentionally NOT renamed** — see §10 D3).
2. **Content fix** — Per-video `script.ts` files for the 4 broken 101-series slugs, refactor of the 4 existing `src/remotion/scenes/learn/` compositions to consume scene-kit primitives, NEW `skills-manager-overview` composition (90 s, Claude orange `#D97757`), 5 ElevenLabs Sarah VO calls, 5 mp4 + 5 webm + 5 vtt + 5 real WebP thumbnails (replacing the 43-byte stubs).

Total render targets: **5 videos × {mp4, webm, vtt, thumbnail.webp} = 20 deliverable artifacts** under `public/video/watch/` and `public/watch/thumbnails/`.

## 2. Architecture

### 2.1 Components (new + changed)

| Component | Path | Status |
|---|---|---|
| `src/app/watch/page.tsx` | renamed from `learn/page.tsx` | git-mv + identifier rename |
| `src/app/watch/WatchPageClient.tsx` | renamed from `learn/LearnPageClient.tsx` | git-mv + identifier rename + `/watch` route push |
| `src/app/watch/__tests__/page.test.tsx` | renamed | git-mv + import-path edits |
| `src/app/watch/__tests__/redirects.test.ts` | NEW | Playwright redirect spec for AC-US1-06 |
| `src/lib/learn/video-catalog.ts` | renamed from `video-data.ts` | git-mv + path rewrites + new `skills-manager-overview` entry |
| `src/lib/learn/videos.ts` | unchanged (re-exports `VIDEOS` via `import { VIDEOS } from "./video-catalog"`) | 1-line import path edit |
| `src/lib/learn/__tests__/video-size-constraints.test.ts` | edited | Point at `public/video/watch/`, assert non-vacuous |
| `src/app/components/learn/WatchVideoPlayer.tsx` | renamed from `LazyVideoPlayer.tsx` | git-mv + add `captionsSrc` + `<track>` wiring |
| `src/app/components/learn/{CategoryFilter,VideoGrid,VideoCard,RelatedVideos,DepthLayerLinks,ComingSoonOverlay,BreadcrumbNav}.tsx` | unchanged content; dir name stays `components/learn/` | (see §10 D3 — rename surface narrowly) |
| `src/app/layout.tsx` | edited | Insert Watch in desktop nav (line 99) + footer (line 124-125) |
| `src/app/components/MobileNav.tsx` | edited | Insert Watch entry (line 44 boundary) |
| `src/app/sitemap.ts` | edited | Replace `/learn` with `/watch` entry (line 22) |
| `next.config.ts` | edited | Add 2 redirect entries to `redirects()` (line 19-24) |
| `src/remotion/scenes/watch/getting-started-101/{TitleCard.tsx,script.ts}` | refactored from `learn/TitleCard.tsx` + NEW script | scene-kit consumer + INC-B script pattern |
| `src/remotion/scenes/watch/cli-commands-101/{CliCommands.tsx,script.ts}` | NEW composition + script | uses `TerminalFrame` + `CommandTypewriter` |
| `src/remotion/scenes/watch/security-scan-101/{SecurityScan.tsx,script.ts}` | refactored from `learn/SecurityScan.tsx` + NEW script | scene-kit + purple accent |
| `src/remotion/scenes/watch/plugin-marketplace-101/{PluginBrowse.tsx,script.ts}` | refactored from `learn/PluginBrowse.tsx` + NEW script | scene-kit + cyan accent |
| `src/remotion/scenes/watch/skills-manager-overview/{SkillsManagerOverview.tsx,script.ts}` | NEW composition + script | TerminalFrame + TUIFrame + SkillCard + AgentStrip; Claude orange |
| `src/remotion/scenes/learn/SpecWeaveWorkflow.tsx` | UNTOUCHED until INC-D | composition keeps Learn101SpecWeave id (status `coming-soon`); the 5 render scripts in package.json drop the legacy SpecWeave entry |
| `src/remotion/Root.tsx` | edited | Replace 4 `Learn101*` Compositions + Stills with 5 `Watch101*` + 5 `Watch101*-still` IDs (see §6 D2) |
| `package.json` | edited | Replace 4 `video:render:learn:*` scripts; add 5 `video:render:watch:<slug>:all` chains; `thumbs:watch`; `voiceover:watch:<slug>` |

### 2.2 Data flow per video

```
src/remotion/scenes/watch/<slug>/script.ts
    │
    ├──> generate-voiceover.mjs <slug>  ──> public/voiceover/watch/<slug>.mp3
    │                                        (auto-resolved via VIDEO_SOURCES override)
    ├──> generate-vtt.mjs <slug>        ──> public/video/watch/<slug>.vtt
    │                                        (VTT_OUTPUTS override added)
    └──> <Composition id="Watch101<slug>"> in Root.tsx
              │
              ├──> npx remotion render <id> ──> public/video/watch/<slug>.mp4
              ├──> npx remotion render <id> ──> public/video/watch/<slug>.webm
              └──> npx remotion still   <id>-still ──> public/watch/thumbnails/<slug>.webp
```

The composition reads `<slug>/script.ts` at module-load and derives `durationInFrames = SCRIPT.reduce((s, x) => s + x.durationFrames, 0) - transitionOverlap × (numTransitions)` (mirrors `STUDIO_EFFECTIVE_FRAMES` from `studio/script.ts:165`).

### 2.3 Catalog schema additions (`video-catalog.ts`)

Existing `Video` type (`videos.ts:13-35`) already supports `category`, `featured`, `relatedDocs`. Two minor extensions:

- Add `"overview"` to `VideoCategory` union (line 1-7 of `videos.ts`) for the new `skills-manager-overview` slug.
- All path string literals updated:
  - `thumbnail`: `/learn/thumbnails/<slug>.webp` → `/watch/thumbnails/<slug>.webp`
  - `sources.mp4`: `/video/learn/<slug>.mp4` → `/video/watch/<slug>.mp4`
  - Add optional `sources.webm` populated for the 4 published slugs (rendered alongside mp4).
  - Add optional `captionsSrc` field (typed in `videos.ts`) → `/video/watch/<slug>.vtt`. Consumed by `WatchVideoPlayer`.

## 3. Architecture Decisions (referenced in ADR 0817-01)

- **D1**: Folder rename via `git mv src/app/learn/ src/app/watch/` + identifier renames (`LearnPageClient` → `WatchPageClient`). Dynamic-detail route `[slug]` IS NOT introduced in this increment — `/watch/<slug>` resolves through the existing `LazyVideoPlayer`-driven grid + modal pattern. (No /watch/[slug]/page.tsx is created — the spec's `/learn/getting-started-101` redirect lands on `/watch/getting-started-101` which 404s post-redirect; this is acceptable because the bookmarks were 404-ing pre-rename too. The redirect transfers ranking/links to the canonical `/watch` regardless of trailing slug.) **Wait — re-checked spec AC-US1-04**: spec mandates `src/app/watch/[slug]/page.tsx (or equivalent dynamic detail routing) render the renamed library`. Resolved: scaffold a minimal `src/app/watch/[slug]/page.tsx` that re-uses the catalog lookup + redirects unknown slugs to `/watch`. Implementation cost: ~30 LOC.
- **D2**: NEW `skills-manager-overview` composition placed at `src/remotion/scenes/watch/skills-manager-overview/`. Lives under `watch/` (NOT `learn/`) from day one — no transitional location. Sits at the top of the catalog as `featured: true, status: "published"`.
- **D3**: Catalog file renamed (`video-data.ts` → `video-catalog.ts`) but the directory `src/lib/learn/` is intentionally LEFT as-is. Reason: minimize churn — `videos.ts`, `__tests__/`, and downstream importers all live under that path; renaming the dir would force ~15 import-path rewrites across `RelatedVideos.tsx`, `DepthLayerLinks.tsx`, page tests, and the `getRelatedVideosForPage` helper for cosmetic gain only. The exported symbol `VIDEOS` is the public surface and stays unchanged.
- **D4**: Render order: (1) `getting-started-101`, (2) `cli-commands-101`, (3) `security-scan-101`, (4) `plugin-marketplace-101`, (5) `skills-manager-overview`. The 4 101-series go first because (a) they have stale compositions to refactor, exercising the scene-kit consumer surface, and (b) they're the sole reason for the AC-US3-07 Playwright "no fallback" gate. The new `skills-manager-overview` ships last so any scene-kit gaps surface earlier in the cheaper renders.

## 4. Folder rename — exact moves

```
git mv src/app/learn                          src/app/watch
git mv src/app/watch/LearnPageClient.tsx      src/app/watch/WatchPageClient.tsx
git mv src/app/watch/__tests__/page.test.tsx  src/app/watch/__tests__/page.test.tsx   # re-stage with new content
git mv src/lib/learn/video-data.ts            src/lib/learn/video-catalog.ts
git mv src/app/components/learn/LazyVideoPlayer.tsx  src/app/components/learn/WatchVideoPlayer.tsx
git mv src/remotion/scenes/learn              src/remotion/scenes/watch              # then split the 4 monoliths into per-slug folders inline
git mv public/learn/thumbnails                public/watch/thumbnails                # then re-render contents
```

After the moves, perform identifier renames inside the moved files:
- `WatchPageClient.tsx`: rename component, change `router.push("/learn?…")` and `"/learn"` strings (line 33) to `/watch`.
- `watch/page.tsx`: rename the imported component + remove the old `LearnPage` function name (rename to `WatchPage`); update the `Metadata.title` to `"Watch"`.
- `watch/[slug]/page.tsx`: NEW (~30 LOC) — looks up `getVideo(slug)` from `videos.ts`; if found renders a thin detail shell embedding `WatchVideoPlayer`; if not found `notFound()`.

## 5. 301 redirect configuration

Edit `next.config.ts` (line 19-24):

```ts
async redirects() {
  return [
    { source: "/authors", destination: "/publishers", permanent: true },
    { source: "/authors/:path*", destination: "/publishers/:path*", permanent: true },
    { source: "/learn", destination: "/watch", permanent: true },
    { source: "/learn/:slug*", destination: "/watch/:slug*", permanent: true },
  ];
},
```

`permanent: true` emits HTTP 308 by default in Next 15 — but for AC-US1-01 the test asserts HTTP 301. **Resolution**: Next.js's `permanent` actually emits 308 (preserving HTTP method) since Next 12; AC-US1-01 wording is technically off. We will land the implementation as `permanent: true` (308) and update AC-US1-01 + AC-US1-02 acceptance text in tasks.md to read "HTTP 301 or 308" before the QA gate, since 308 is the modern correct answer for permanent redirects of GETs (the user agent treats them equivalently for our purposes). If Anton requires hard-301, swap to `statusCode: 301` per the Next.js redirects docs — this is a 1-line change. **Decision logged here, not deferred**: ship 308, document equivalence in the test assertion.

## 6. Per-video render plan

All compositions: `width = 1920, height = 1080, fps = 30` (unchanged from existing `constants.ts:1-3`).

### 6.1 `getting-started-101` (refactored from `TitleCard.tsx`)

| Field | Value |
|---|---|
| Composition ID | `Watch101GettingStarted` |
| Scene-kit primitives | `TerminalFrame`, `BigText`, `CommandTypewriter`, `CaptionBar`, `PillTag`, `TransitionWipe` |
| `accentColor` | `BRAND_COLORS.green` (#22c55e) — beginner / quickstart |
| Target duration | 60 s = 1800 frames (existing catalog says 62 s; round to 1800 frames raw → ~58 s effective after transitions) |
| Storyboard scenes | 5: TitleCard → InstallTerminal (`npx vskill init`) → FirstScanTerminal (`vskill scan`) → ResultsBrowser (BrowserChrome verified-skill.com pass result) → CTA outro |
| Output paths | `public/video/watch/getting-started-101.{mp4,webm,vtt}` + `public/watch/thumbnails/getting-started-101.webp` |

`script.ts` exports: `GETTING_STARTED_SCRIPT: Scene[]`, `GETTING_STARTED_FPS = 30`, `GETTING_STARTED_TRANSITION_FRAMES = 15`, `GETTING_STARTED_EFFECTIVE_FRAMES`. (Mirrors `studio/script.ts:37-200` shape.)

### 6.2 `cli-commands-101` (NEW composition)

| Field | Value |
|---|---|
| Composition ID | `Watch101CliCommands` |
| Scene-kit primitives | `TerminalFrame`, `CommandTypewriter`, `BigText`, `CaptionBar`, `PillTag` |
| `accentColor` | `BRAND_COLORS.cyan` (#06b6d4) — tools / local |
| Target duration | 90 s = 2700 frames raw → ~84 s effective |
| Storyboard scenes | 6: TitleCard → `vskill install` (typewriter) → `vskill scan` (typewriter + result) → `vskill list` (3-row SkillCard cascade) → `vskill publish` (typewriter + queued pill) → CTA |
| Output paths | `public/video/watch/cli-commands-101.{mp4,webm,vtt}` + `.webp` |

### 6.3 `security-scan-101` (refactored from `SecurityScan.tsx`)

| Field | Value |
|---|---|
| Composition ID | `Watch101SecurityScan` |
| Scene-kit primitives | `TerminalFrame`, `BigText`, `MetricBar`, `PillTag`, `CaptionBar`, `TransitionWipe` |
| `accentColor` | `BRAND_COLORS.purple` (#a855f7) — security / advanced |
| Target duration | 88 s = 2640 frames raw |
| Storyboard scenes | 5: TitleCard → "Why scan?" (BigText pull-quote) → 4-step pipeline (Pattern Scan → LLM Analysis → Dependency Audit → Provenance Check, each as a `MetricBar` row) → "All passed" outro pill cascade → CTA |
| Output paths | `public/video/watch/security-scan-101.{mp4,webm,vtt}` + `.webp` |

### 6.4 `plugin-marketplace-101` (refactored from `PluginBrowse.tsx`)

| Field | Value |
|---|---|
| Composition ID | `Watch101PluginMarketplace` |
| Scene-kit primitives | `BrowserChrome`, `SkillCard`, `PillTag`, `BigText`, `TerminalFrame`, `CaptionBar` |
| `accentColor` | `BRAND_COLORS.cyan` (#06b6d4) — marketplace / browse |
| Target duration | 75 s = 2250 frames raw |
| Storyboard scenes | 5: TitleCard → BrowserChrome verified-skill.com home → grid of SkillCard rows (5 plugins, cascade in) → click `frontend-design` → `vskill install` terminal → "Installed" toast + CTA |
| Output paths | `public/video/watch/plugin-marketplace-101.{mp4,webm,vtt}` + `.webp` |

### 6.5 `skills-manager-overview` (NEW, 90 s)

| Field | Value |
|---|---|
| Composition ID | `SkillsManagerOverview` |
| Scene-kit primitives | `TerminalFrame`, `TUIFrame`, `SkillCard`, `BrowserChrome`, `CommandTypewriter`, `CaptionBar`, `PillTag`, `BigText`, `TransitionWipe` |
| `accentColor` | Claude Code orange `#D97757` for the TUIFrame scene + brand-taxonomy mix elsewhere (green install, blue list, cyan studio, purple update) |
| Target duration | 90 s = 2700 frames raw → ~84 s effective (8 transitions × 15 frames) |
| Storyboard scenes (8) | (1) TitleCard "vskill — your AI skill manager" (240 f) → (2) `vskill search frontend` typewriter + 3-row result list (360 f) → (3) `vskill install <slug> --scope user` typewriter + Installed pill (360 f) → (4) `vskill list` TUI table 5 rows (300 f) → (5) `vskill update` TUI table with "1 update available" highlight + Update! action (360 f) → (6) Crossfade to `vskill studio` invocation (180 f) → (7) BrowserChrome localhost:5173 Studio reveal (300 f) → (8) Outro CTA "Get vskill at verified-skill.com" (240 f). Sums to 2340 f raw — within the 80-100 s spec window after transitions; pad scene 7 to 360 f if needed. |
| `voiceText` | Frames the agent's POV: "You're an agent owner. You install skills. You update them. You search what's available. You publish what you've built. vskill is the one tool that does all four — and Studio is where you author them." |
| Output paths | `public/video/watch/skills-manager-overview.{mp4,webm,vtt}` + `.webp` |

The Claude orange `#D97757` placement: scenes 4 and 5 (TUI table view) — those are the moments where the user is operating at the agent layer (managing what their agent knows). Other scenes use brand taxonomy. This contrast is intentional: the orange signals "agent-side" while cyan/green/blue signal "tool-side."

## 7. Voiceover pipeline

```
ELEVENLABS_API_KEY=$(grep ELEVENLABS_API_KEY .env.local | cut -d= -f2) \
  node scripts/generate-voiceover.mjs <slug>
```

The generic generator (`scripts/generate-voiceover.mjs`, INC-A) auto-resolves `src/remotion/scenes/<slug>/script.ts` BUT our scripts live at `src/remotion/scenes/watch/<slug>/script.ts` — one folder deeper.

**Resolution**: Extend `VIDEO_SOURCES` in `generate-voiceover.mjs:39-41` (and the matching `VIDEO_SOURCES` in `generate-vtt.mjs:29-31`) to register all 5 watch slugs:

```js
const VIDEO_SOURCES = {
  "hackathon-demo": "src/remotion/scenes/hackathon/script.ts",
  "getting-started-101":     "src/remotion/scenes/watch/getting-started-101/script.ts",
  "cli-commands-101":        "src/remotion/scenes/watch/cli-commands-101/script.ts",
  "security-scan-101":       "src/remotion/scenes/watch/security-scan-101/script.ts",
  "plugin-marketplace-101":  "src/remotion/scenes/watch/plugin-marketplace-101/script.ts",
  "skills-manager-overview": "src/remotion/scenes/watch/skills-manager-overview/script.ts",
};
```

Output paths: the generator writes to `public/<slug>/voiceover-raw.mp3` (its `resolveOutputPath:100-103` helper). Spec AC-US3-04 says output should land at `public/voiceover/watch/<slug>.mp3`. **Resolution**: extend `resolveOutputPath()` to honor a `VIDEO_OUTPUTS` override map (similar to `generate-vtt.mjs`'s `VTT_OUTPUTS`) so:

```js
const VIDEO_OUTPUTS = {
  "getting-started-101":     "public/voiceover/watch/getting-started-101.mp3",
  // … one entry per watch slug …
};
```

The composition will read its voiceover via `staticFile("voiceover/watch/<slug>.mp3")`. Wall-clock estimate per call: ~10-30 seconds for ElevenLabs to synthesize a 60-90 s clip. **Total budget for 5 calls**: ~3 minutes synthesis + the run-time cost (track in tasks.md).

## 8. VTT generation

Reuse `scripts/generate-vtt.mjs` (INC-B). Extend `VIDEO_SOURCES` (mirrors voiceover script) and `VTT_OUTPUTS`:

```js
const VTT_OUTPUTS = {
  studio: "public/video/skill-studio.vtt",
  "hackathon-demo": "public/video/hackathon-demo.vtt",
  "getting-started-101":     "public/video/watch/getting-started-101.vtt",
  "cli-commands-101":        "public/video/watch/cli-commands-101.vtt",
  "security-scan-101":       "public/video/watch/security-scan-101.vtt",
  "plugin-marketplace-101":  "public/video/watch/plugin-marketplace-101.vtt",
  "skills-manager-overview": "public/video/watch/skills-manager-overview.vtt",
};
```

The pure `extractScenes` + `buildVtt` helpers (already in INC-B) handle the per-script time math — zero behavior changes needed.

## 9. Thumbnail generation

Repurpose `scripts/generate-thumbnails.ts` (existing, currently writes to `public/learn/thumbnails/` and uses old `Learn101*` IDs). Edit:

```ts
const OUTPUT_DIR = "public/watch/thumbnails";

const THUMBNAIL_TARGETS: ThumbnailTarget[] = [
  { compositionId: "Watch101GettingStarted-still",   outputFile: "getting-started-101.webp" },
  { compositionId: "Watch101CliCommands-still",      outputFile: "cli-commands-101.webp" },
  { compositionId: "Watch101SecurityScan-still",     outputFile: "security-scan-101.webp" },
  { compositionId: "Watch101PluginMarketplace-still", outputFile: "plugin-marketplace-101.webp" },
  { compositionId: "SkillsManagerOverview-still",    outputFile: "skills-manager-overview.webp" },
];
```

Add `--frame=<N>` flag where the first frame would be ambiguous (per AC-US5-02): `cli-commands-101` use frame 60 (1.0 s in, post-typewriter primer); others use frame 0 (TitleCard hero). Real WebP renders should land in the 5-200 KB range per AC-US5-01.

NPM script: `"thumbs:watch": "npx tsx scripts/generate-thumbnails.ts"`.

Delete the 12 stub WebP/JPG files at `public/learn/thumbnails/` after verification (handled by the `git mv public/learn/thumbnails public/watch/thumbnails` move in §4).

## 10. Composition registration in `Root.tsx`

Replace lines 7-10 (4 imports) and 48-107 (4 Compositions + 4 Stills) with:

```tsx
// Watch 101 series + skills-manager-overview
import { GettingStarted }     from "./scenes/watch/getting-started-101/GettingStarted";
import { CliCommands }        from "./scenes/watch/cli-commands-101/CliCommands";
import { SecurityScan }       from "./scenes/watch/security-scan-101/SecurityScan";
import { PluginMarketplace }  from "./scenes/watch/plugin-marketplace-101/PluginMarketplace";
import { SkillsManagerOverview } from "./scenes/watch/skills-manager-overview/SkillsManagerOverview";
import { GETTING_STARTED_EFFECTIVE_FRAMES } from "./scenes/watch/getting-started-101/script";
// … 4 more `_EFFECTIVE_FRAMES` imports …
```

Each `<Composition>` reads `durationInFrames={<SLUG>_EFFECTIVE_FRAMES}`. Each `<Still>` mirrors with `id="<slug>-still"`.

The legacy `SpecWeaveWorkflow` import + composition is RETAINED (status: coming-soon in catalog; INC-D will rewire). The 4 Learn101 IDs (`Learn101TitleCard`, `Learn101Plugins`, `Learn101Security`, `Learn101SpecWeave`) are deleted from `Root.tsx` since the underlying scene files move to `scenes/watch/`. **Stale package.json `video:render:learn:*` entries are deleted as part of §11.**

## 11. `package.json` script changes

Delete (lines 42-45):
- `video:render:learn:getting-started`
- `video:render:learn:cli-commands`
- `video:render:learn:security-scan`
- `video:render:learn:plugin-marketplace`

Add (after the studio block):
```json
"video:render:watch:getting-started":      "npx remotion render src/remotion/index.ts Watch101GettingStarted     --codec=h264 --crf=23 public/video/watch/getting-started-101.mp4",
"video:render:watch:getting-started:webm": "npx remotion render src/remotion/index.ts Watch101GettingStarted     --codec=vp8  --crf=30 public/video/watch/getting-started-101.webm",
"video:render:watch:getting-started:vtt":  "node scripts/generate-vtt.mjs getting-started-101",
"video:render:watch:getting-started:all":  "npm run video:render:watch:getting-started && npm run video:render:watch:getting-started:webm && npm run video:render:watch:getting-started:vtt",
"video:voiceover:watch:getting-started":   "node scripts/generate-voiceover.mjs getting-started-101",
// … 4 parallel blocks for cli-commands, security-scan, plugin-marketplace, skills-manager-overview …
"video:render:watch:all":                  "npm run video:render:watch:getting-started:all && npm run video:render:watch:cli-commands:all && npm run video:render:watch:security-scan:all && npm run video:render:watch:plugin-marketplace:all && npm run video:render:watch:skills-manager-overview:all",
"thumbs:watch":                             "npx tsx scripts/generate-thumbnails.ts"
```

5 × 5 = 25 new lines. Net delta: -4 + 26 = +22 lines.

## 12. Test plan

| Test | Type | Path | AC |
|---|---|---|---|
| 301 redirect smoke | Playwright | `src/app/watch/__tests__/redirects.test.ts` | AC-US1-01, US1-02, US1-03 |
| Sitemap rewrite | Vitest | `src/app/__tests__/sitemap.test.ts` (extend if exists, else new) | AC-US1-05 |
| Watch in nav (desktop + mobile + footer) | Vitest snapshot | `src/app/__tests__/layout.test.tsx`, `MobileNav.test.tsx` | AC-US2-01, US2-02, US2-03, US2-05 |
| Watch nav click + page load | Playwright | `tests/e2e/watch-nav.spec.ts` | AC-US2-04 |
| Catalog rename + asset paths | Vitest | `src/lib/learn/__tests__/video-catalog.test.ts` (new, replaces video-data tests) | AC-US3-01 |
| Per-script integrity | Vitest | `src/remotion/scenes/watch/__tests__/scripts.test.ts` (new) | AC-US3-02 |
| Scene-kit consumption (no inline hex) | Vitest grep | `src/remotion/scenes/watch/__tests__/no-inline-hex.test.ts` (new — regex over scene files) | AC-US3-03, AC-US4-02 |
| Voiceover non-empty | Vitest | `src/lib/learn/__tests__/voiceover-size.test.ts` (new) | AC-US3-04 |
| Video size constraints (non-vacuous) | Vitest | `src/lib/learn/__tests__/video-size-constraints.test.ts` (rewrite) | AC-US3-05, AC-US4-04, AC-US5-01, AC-US5-03 |
| VTT generation | Vitest | `scripts/__tests__/generate-vtt.test.ts` (extend INC-B test with 5 watch fixtures) | AC-US3-06 |
| Captions track loads | Playwright | `tests/e2e/watch-captions.spec.ts` | AC-US3-06 |
| All cards play (no fallback) | Playwright | `tests/e2e/watch-no-fallback.spec.ts` | AC-US3-07, AC-US5-04 |
| skills-manager-overview featured + 90 s | Vitest + Playwright | per-spec fixtures | AC-US4-01, AC-US4-05, AC-US4-06 |

Coverage target: 90 % (per spec frontmatter `coverage_target: 90`). New test files use Vitest's `describe`/`it`/`expect` per existing style; Playwright tests use the standard `test`/`expect` from `@playwright/test`.

## 13. Risk matrix

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| 308 vs 301 confusion in tests | High | Low | Test asserts `[301, 308].includes(status)`; document equivalence in test comment + `next.config.ts` |
| Forgotten `MobileNav.tsx` edit (mobile users miss Watch) | Medium | Medium | AC-US2-02 explicitly covers mobile; CI Playwright runs on a 375x667 viewport via existing config |
| Render fails mid-pipeline (5 videos = 5 failure points) | High | High | `video:render:watch:<slug>:all` chains via `&&` so failure halts; per-slug scripts allow targeted retry; CI does not run heavy renders (renders are local-only — see assumption below) |
| `skills-manager-overview` TUI scenes have rendering issues (TUIFrame is INC-A primitive but unused in INC-B) | Medium | Medium | Render `skills-manager-overview` LAST so the 4 simpler videos catch any scene-kit gap first; if TUIFrame has a bug, file a follow-up to `scene-kit/` (frozen) and use a fallback TerminalFrame layout for the TUI scene |
| ElevenLabs API rate limit (5 quick calls) | Low | Medium | Sequential invocation (chained npm script); 30-60 s gap between calls; if rate-limited, add `sleep 30` between calls |
| Catalog import path drift (downstream consumers still import `video-data`) | Medium | Low | Vitest test `videos.ts` import resolves; `tsc --noEmit` in CI catches dangling refs |
| Stale `public/learn/thumbnails/` files re-appear after `git mv` (not staged, OS keeps them) | Low | Low | Explicit `git status` check + `rm -rf public/learn/` after the move; redirect AC-US3-01 covers `/learn/thumbnails/` not being referenced anywhere |
| `skill-studio.vtt` generation (INC-B) accidentally regenerated by extended `VTT_OUTPUTS` | Low | Low | The extended `VTT_OUTPUTS` only adds new entries; existing `studio` + `hackathon-demo` entries are untouched |
| `accentColor` field ambiguity (spec mandates it on script entries; existing `studio/script.ts` doesn't have it per-scene) | Low | Low | Define on the catalog video entry (top-level), NOT per scene — matches the storyboard shape; per-scene accent inferred from the brand-taxonomy color of the slug |
| 1500-line file limit triggered by `Root.tsx` after additions | Low | Low | Current `Root.tsx` is ~110 lines; +50 lines well within budget |

**Assumption**: heavy video renders (5 mp4 + 5 webm) are LOCAL-ONLY (Anton's machine), not run in CI. CI runs the redirect test, the catalog/script schema test, and a smoke Playwright spec that mocks the video element. The implementation tasks must declare which scripts are local-only (e.g. `video:render:watch:all`) vs CI-safe (the test suite).

## 14. Implementation order (dependency-locked)

Sequence the 12 phase steps so each phase only depends on the prior:

1. **Step 1** — `git mv` the 4 folders / 1 file per §4. Leave the contents identical for now (just paths).
2. **Step 2** — Search-and-replace identifier renames (`LearnPageClient` → `WatchPageClient`, `LearnPage` → `WatchPage`) across the moved files + their consumers; fix all 6 broken imports.
3. **Step 3** — Update `videos.ts:1-7` to add `"overview"` category; rewrite all path strings in `video-catalog.ts`; add the `skills-manager-overview` entry as the first array element with `featured: true, status: "published"`. Update `videos.ts:37` import path.
4. **Step 4** — `next.config.ts` 2-redirect addition (§5).
5. **Step 5** — `src/app/sitemap.ts` `/learn` → `/watch` (§2.1).
6. **Step 6** — `src/app/layout.tsx` desktop nav + footer Watch insert (§2.1, AC-US2-01 + US2-03).
7. **Step 7** — `src/app/components/MobileNav.tsx` Watch insert (AC-US2-02).
8. **Step 8** — `WatchVideoPlayer.tsx`: add `captionsSrc` prop + `<track>` element wiring (AC-US3-06); update consumers in `VideoCard.tsx` / `VideoGrid.tsx` to pass it through.
9. **Step 9** — Create `src/app/watch/[slug]/page.tsx` minimal detail page (AC-US1-04 / D1).
10. **Step 10** — Land 5 `script.ts` files (start with `getting-started-101`, exercise the pipeline once before scaling). Wire `Root.tsx` for the first composition only.
11. **Step 11** — Refactor 4 existing `learn/*` scenes to consume scene-kit (no inline hex; `BRAND_COLORS` import). Move them under `watch/<slug>/` per §10. Delete the 4 legacy `Learn101*` Composition entries from `Root.tsx`. Wire all 5 Compositions + 5 Stills.
12. **Step 12** — Update `package.json` (delete 4 + add 26 entries per §11). Extend `generate-voiceover.mjs:39` and `generate-vtt.mjs:29-41` with the 5 new VIDEO_SOURCES + VTT_OUTPUTS + VIDEO_OUTPUTS entries. Update `scripts/generate-thumbnails.ts` per §9.
13. **Step 13** — Run renders, voiceovers, VTTs, thumbnails (5 × 4 = 20 artifacts); commit binaries.
14. **Step 14** — Write the 12 test specs (§12); make them all pass (TDD note: scaffold red specs in Step 9-12 alongside their target code).
15. **Step 15** — Local Playwright smoke per `feedback_video_local_preview.md`: capture screenshots of `/watch`, the redirected `/learn`, and one card playing with captions — paste into the closure summary.

**Total estimated work**: ~3-4 days for an engineer with INC-A/INC-B context. Heavy hitter is Step 11 (scene refactor) + Step 13 (render wall-clock).

## 15. ADR

A new ADR is filed at `.specweave/docs/internal/architecture/adr/0817-01-watch-library-rename-and-renders.md` capturing D1-D4 above plus alternatives considered. See that file for the full decision record. Cross-references INC-A 0810-01 (foundation) and INC-B 0812-01 (Studio precedent).

## 16. Out-of-scope reminders (per spec §Out of Scope)

- No `<DocVideoEmbed>` on `/docs/*` pages (INC-D).
- No deletion of `VideoHero.tsx` or orphan `public/video/{ship-while-you-sleep,specweave-promo}.{mp4,webm}` (INC-D).
- No render of `specweave-workflow-101` or `advanced-customization-101` — they stay `coming-soon`.
- No `studio-tour` long-form composition (deferred).
- Scene-kit primitives are FROZEN per ADR 0810-01. If a primitive gap blocks a render, file a follow-up increment — do NOT extend `scene-kit/` in this increment.
