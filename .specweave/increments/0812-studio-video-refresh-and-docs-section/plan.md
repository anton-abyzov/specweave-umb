# Plan — 0812 Studio Video Refresh + /docs/studio

## 0. Reading order

1. spec.md (this increment) — user stories + ACs
2. ADR `0810-01-video-pipeline-and-token-sync.md` — INC-A foundation contract this plan builds on (scene-kit at `src/remotion/scene-kit/`, BRAND_COLORS canonical, `scripts/generate-voiceover.mjs <video-name>`, `script.ts` schema, mandate "every new video MUST" rules in §D3+§Consequences)
3. ADR `0812-01-studio-video-refresh-and-docs.md` — written alongside this plan
4. Truth-checked storyboard `.specweave/scratch/skill-studio-hackathon-video.md` — note: that file is the YouTube hackathon storyboard (3:30 with face-cam + b-roll). INC-B targets a tighter Remotion-only render (~2:46–3:00) covering the Studio product surface; we lift the *feature beats* but not the face-cam / b-roll clips.

## 1. Strategy: refactor in one shot, not two phases

The temptation is "Phase 1 = new scenes only, Phase 2 = port existing scenes." We reject that. Three reasons:

1. **The current `SkillStudioDemo.tsx` already wires 6 scenes via `<TransitionSeries>`** (see `SkillStudioDemo.tsx:34-94`) — adopting `script.ts` is a localized change: lift the inline `<TransitionSeries.Sequence durationInFrames={N}>` triples into an array, mirror the `HackathonDemo.tsx:60-104` flat-map pattern, register components in a `Record<string, React.FC>`. ~50 LOC swap.
2. **A two-phase approach leaves the composition in a hybrid state** where new scenes are data-driven and old scenes are inline-JSX. Future contributors who need to re-time a beat have to remember which side of the composition they're editing. ADR 0810-01 §D3 mandates script-as-data for *every* video — partial adoption would itself be drift.
3. **Existing 6 scenes need re-timing anyway.** New runtime budget is ~2:46–3:00 across 11 scenes (6 existing + 5 new). Touching every `durationFrames` in one pass is cleaner than touching them twice.

So: Phase 1 = full data-driven port + 5 new scenes + Sarah VO + `.vtt` + render + page wiring + `/docs/studio`.

## 2. New scene specs (5 scenes)

Each scene is a new file under `src/remotion/scenes/studio/`. All consume `scene-kit/` primitives (no raw hex codes — pull from `BRAND_COLORS`). Each accepts the same prop contract as the existing studio scenes: zero props (the scene reads its own `id` slot from `STUDIO_SCRIPT` for caption text via a `useScriptScene(id)` helper introduced in §3 below).

### 2.1 `TestsTabIntro.tsx` — 540 frames (18s) — accent green `BRAND_COLORS.green`

**Visual:** Studio chrome in light theme (`STUDIO_LIGHT.bg`). Sidebar collapsed, main pane shows a skill detail page with the Tests tab active. Three test cases listed (data: rule strings — "When asked for a Buy Now button, output must not contain `font-inter`", "Output palette ≤ 2 colors", "No `bg-purple-500` gradient"). Cursor moves to "Run all" → click → spinner per row → green ticks cascade (90 → 150 → 210 frames, staggered 60). At 220 a pill `3/3 passed · 100%` springs in. Hold to 540.

**Primitives used:** `BrowserChrome` (Studio chrome), `PillTag` (each test row + final pass-rate pill), `MetricBar` (small "100%" green bar that fills 220→230). Cursor + click animation = inline (matches existing studio scenes).

**Why it leads:** Tests-as-tab is the headline feature shipped post-2026-03-18; it must come before `PublishToGitHub` because the Publish flow depends on a green-test posture in the storyboard.

### 2.2 `PublishToGitHub.tsx` — 720 frames (24s) — accent blue `BRAND_COLORS.blue`

**Visual:** Studio chrome, skill detail page, "Publish" button top-right. Cursor click → inline panel slides in: "No GitHub repo — create with `gh` CLI?" with a `Yes, create` button. Click → terminal strip at bottom: `$ gh repo create anton-abyzov/frontend-design --public --source . --push` types itself (frame 90→150). At 160 a green `repo created` pill appears. Cross-fade at 280 to a verified-skill.com browser tab (`BrowserChrome` with `https://verified-skill.com/queue` URL bar) showing a status pill cycling `Queued` (300→400) → `Scanning…` (400→520, with shimmer) → `Processed ✓ · v1.0.0` (520→640). Hold to 720.

**Primitives used:** `BrowserChrome` (Studio + verified-skill.com), `TerminalFrame` (the `gh repo create` strip), `CommandTypewriter` (types the gh command), `PillTag` (status pill cycle).

**Why this scene exists:** the gh-CLI auto-repo flow is the Hyperframes-flagged "recently-shipped" beat. The storyboard explicitly calls out a 300ms zoom-ring + "new" badge — we map that to a 1.05× spring on the inline panel between frames 30–45.

### 2.3 `InstallScopePicker.tsx` — 420 frames (14s) — accent cyan `BRAND_COLORS.cyan`

**Visual:** Studio in "consumer" mode — same chrome, but the URL bar reads `localhost:5173/skills/anton-abyzov/frontend-design`. Search box pre-filled with `frontend-design`. Below: a 3-row scope picker (matches the real product surface). Each row = a `PillTag` row with a radio dot + label + helper text:

- ⚪ **Project** — `.claude/skills/` in this folder
- ⚪ **User** — `~/.claude/skills/` (every project)
- ⚪ **Global** — `/usr/local/share/claude/skills/` (every machine)

Cursor lands on Project at frame 90 → radio fills cyan → Install button pulses → click at frame 180 → green `✓ Installed` toast slides up from the bottom. Sidebar refreshes in-place: PROJECT (0) → (1) row, halo pulse. Hold to 420.

**Primitives used:** `BrowserChrome` (Studio), `PillTag` (3 scope rows + the `Installed` toast).

### 2.4 `UpdateToast.tsx` — 600 frames (20s) — accent purple `BRAND_COLORS.purple`

**Visual:** Studio chrome, viewing `frontend-design` Overview tab (cooked from existing `StudioHistory` aesthetic). Bell icon top-right has a red `1` badge. At frame 30 a popup pops in from the bell (mirrors the user's reference screenshot from the hackathon script): header `1 update available · Refresh`, single skill row with blue selection ring `anton-abyzov/frontend-design  1.0.0 → 1.0.1  [Update]`, footer `View all`. Cursor moves to `Update` button at frame 180 → click at frame 240 → row flips to green `✓ Updated to 1.0.1`. Hold 360 frames. Closing pill row cascades the four feature pills (matches `/studio` page FEATURES order, brand-canonical: green / blue / purple / cyan).

**Primitives used:** `BrowserChrome`, `PillTag` (version-from/to pill + Update button + final ✓ Updated pill + 4 feature pills).

**Note on color:** purple maps 1:1 to the `Any Model` feature on the Studio FEATURES array (`src/app/studio/page.tsx:158`). We keep the mapping consistent so the closing "feature recap" beat lights up four chips in the brand-canonical order.

### 2.5 `CommandPalette.tsx` — 360 frames (12s) — accent cyan `BRAND_COLORS.cyan`

**Visual:** Studio chrome dimmed at 60% opacity behind a centered ⌘K palette overlay (max-width 560 px, `STUDIO_LIGHT.bgCard`). At frame 0 the page is plain; at frame 30 a key-press graphic (⌘ + K) flashes in the upper-left. At frame 45 the palette springs in. Search input shows `frontend-design` typing (uses `CommandTypewriter`). Below: 3 result rows (each a small `SkillCard`) — `frontend-design`, `pptx-generator`, `social-media-posting`. Cursor moves to first row at frame 150 → row highlights → click at frame 180 → palette dismisses (200ms fade) → main pane crossfades to the skill detail page. Hold 60 frames.

**Primitives used:** `BrowserChrome`, `CommandTypewriter`, `SkillCard` (×3), `PillTag` (the ⌘K key-cap graphic if rendered as a pill).

**Why this scene exists:** the ⌘K palette is the second largest discoverability surface in Studio; the storyboard's Marketplace browse beat is too video-library-shaped for INC-B and properly belongs in INC-C's `studio-tour` composition. The palette is the Studio-internal analogue.

## 3. `script.ts` schema for `/studio`

Lives at `src/remotion/scenes/studio/script.ts`. Mirrors `scenes/hackathon/script.ts` exactly — same exported names so `scripts/generate-voiceover.mjs studio` (slug `studio` → resolved via `resolveScriptPath()` per `scripts/generate-voiceover.mjs:93-98`) works without overrides.

```ts
export type StudioScene = {
  id: string;
  durationFrames: number;
  transitionType: "fade" | "slide-right" | "slide-left" | null;
  voiceText: string;
  caption?: string;
  visualNotes: string;
};

export const STUDIO_FPS = 30;
export const STUDIO_TRANSITION_FRAMES = 15;
export const STUDIO_SCRIPT: StudioScene[] = [ /* see §3.1 */ ];

export const STUDIO_VOICE = {
  primary: { voiceId: "EXAVITQu4vr4xnSDxMaL", name: "Sarah", modelId: "eleven_v3" },
} as const;

// Computed totals (mirror hackathon/script.ts:180-213)
export const STUDIO_TOTAL_FRAMES = STUDIO_SCRIPT.reduce((s, x) => s + x.durationFrames, 0);
export const STUDIO_NUM_TRANSITIONS = STUDIO_SCRIPT.filter(s => s.transitionType !== null).length;
export const STUDIO_EFFECTIVE_FRAMES = STUDIO_TOTAL_FRAMES - STUDIO_NUM_TRANSITIONS * STUDIO_TRANSITION_FRAMES;
export const STUDIO_DURATION_SECONDS = STUDIO_EFFECTIVE_FRAMES / STUDIO_FPS;
export const STUDIO_VOICE_TEXT = STUDIO_SCRIPT.map(s => s.voiceText).join("\n\n");
```

### 3.1 Scene roster (11 scenes — re-timed)

| # | id | durationFrames | secs | transition out | accent |
|---|---|---|---|---|---|
| 01 | `StudioIntro` | 240 | 8.0 | fade | cyan |
| 02 | `StudioAICreate` | 480 | 16.0 | slide-right | purple |
| 03 | `TestsTabIntro` (NEW) | 540 | 18.0 | fade | green |
| 04 | `StudioTestCases` | 360 | 12.0 | slide-left | green |
| 05 | `StudioBenchmark` | 540 | 18.0 | fade | blue |
| 06 | `StudioMultiModel` | 360 | 12.0 | slide-right | purple |
| 07 | `CommandPalette` (NEW) | 360 | 12.0 | fade | cyan |
| 08 | `PublishToGitHub` (NEW) | 720 | 24.0 | slide-left | blue |
| 09 | `InstallScopePicker` (NEW) | 420 | 14.0 | fade | cyan |
| 10 | `UpdateToast` (NEW) | 600 | 20.0 | fade | purple |
| 11 | `StudioOutro` | 360 | 12.0 | null | (logo) |

**Total raw**: 4980 frames. **Effective after 10 × 15-frame overlaps**: 4830 frames = **2:41**.

If post-render Anton wants 3:00+, the safest extension knob is `StudioOutro` (feature pills + CTA hold). `PublishToGitHub` is also extensible (more of the verified-skill.com pill cycle).

### 3.2 voiceText / caption sketches (architect-level — PM owns final copy)

The voice texts are placeholder spans for ElevenLabs pacing budgeting; the PM owns final wording in spec.md US-001 ACs. For pacing math: Sarah at the locked voice settings (stability 0.5, similarity 0.75) reads at ~155 wpm (measured against `HACKATHON_VOICE_TEXT`'s 446 words / ~173s). For 2:41 we budget ~415 words across 11 scenes (~37 words/scene avg).

Each `voiceText` ends with an em-dash or full stop so ElevenLabs renders a natural pause at the scene boundary. `\n\n` between scenes (the script extractor in `generate-voiceover.mjs:233` already handles this) gives a paragraph-level pause.

## 4. Voiceover pipeline

### 4.1 Single command — slug = `studio`

```bash
ELEVENLABS_API_KEY=$(grep ELEVENLABS_API_KEY .env.local | cut -d= -f2 | tr -d '"') \
  node scripts/generate-voiceover.mjs studio
```

`scripts/generate-voiceover.mjs:93-98` resolves slug `studio` → `src/remotion/scenes/studio/script.ts` (no override needed in `VIDEO_SOURCES`). Output: `public/studio/voiceover-raw.mp3`.

### 4.2 npm script alias

Add to `package.json` (next to `video:voiceover:hackathon`):

```jsonc
"video:voiceover:studio": "node scripts/generate-voiceover.mjs studio",
```

Justification: the alias preserves the call-pattern users see for `video:voiceover:hackathon` (per ADR 0810-01 §Consequences mandate "every new video MUST add a `video:render:<group>:<slug>` entry"). The voiceover counterpart is already implicitly required.

### 4.3 Output directory: `public/studio/`

We use a NEW directory `public/studio/voiceover-raw.mp3` rather than overloading `public/product-demo/`. Two reasons:

1. `public/product-demo/` is the hackathon-demo asset bag (`bgm.mp3`, `voiceover.mp3`, `voiceover-rachel-backup.mp3`, logo PNGs, site-good/site-excellent PNGs). Reusing it for the studio render mixes concerns and the `voiceover.mp3` filename collides with `HackathonDemo.tsx:68` which loads `staticFile("product-demo/voiceover.mp3")`.
2. The slug-based convention (`public/<slug>/`) is the contract from `scripts/generate-voiceover.mjs:101`. Using `public/studio/` keeps the convention clean for INC-C's `/watch` videos which will produce `public/getting-started-101/`, `public/cli-commands-101/` etc.

**Caveat:** `voiceover-raw.mp3` is the unmastered ElevenLabs output. The hackathon flow has a separate mastered `voiceover.mp3` (loudness-normalized via ffmpeg). For INC-B we deliberately scope OUT mastering — Phase-2 follow-up if Anton hears clipping. The `<Audio src="...">` in the composition reads `voiceover-raw.mp3` directly.

### 4.4 BGM — reuse Skybound Circuits

`public/product-demo/bgm.mp3` (Skybound Circuits, mixed at 0.20 volume per `HackathonDemo.tsx:66`) is universal per ADR 0810-01 §Reuse. Same `<Audio src={staticFile("product-demo/bgm.mp3")} volume={0.20}>` block in the new `SkillStudioDemo.tsx`. Same `<Sequence from={30}>` 1-second cold-open before the voice enters.

## 5. `.vtt` captions sidecar

### 5.1 Generation strategy: dedicated script, not inline build step

We add `scripts/generate-vtt.mjs <video-name>` (parallel to `generate-voiceover.mjs`). Justification:

- It needs to run AFTER the voiceover is generated and AFTER the composition's `effectiveFrames` are known (cue end-times depend on per-scene `durationFrames`).
- It's a short pure transformation (script → cue blocks); no need to bundle it into a Vite plugin or Remotion preprocessor.
- A dedicated script is testable in isolation (mirrors the testing pattern at `scripts/__tests__/generate-voiceover.test.ts`).

### 5.2 Cue format

```
WEBVTT

00:00:00.000 --> 00:00:08.000
$ npx vskill studio

00:00:08.000 --> 00:00:24.000
Pick a model. Type your skill in plain English. Studio drafts it.

...
```

Each scene → one cue block. `start = sum(prior.durationFrames - prior.transitionOverlap) / fps`. End = start + scene.durationFrames / fps. Cue text = `scene.caption ?? scene.voiceText.split('.')[0] + '.'` (truncated to ~80 chars per WCAG caption-line guidance).

### 5.3 Output: `public/video/skill-studio.vtt`

The page wires `<track src="/video/skill-studio.vtt">` (per §7 below) so the VTT lives in `public/video/` next to the mp4/webm. NOT `public/studio/` — `public/studio/` holds the voiceover source assets; the renderable sidecars (mp4/webm/vtt) live in `public/video/`.

### 5.4 npm script

```jsonc
"video:vtt:studio": "node scripts/generate-vtt.mjs studio"
```

## 6. Render plan — mp4 + webm + vtt together

### 6.1 npm scripts (already exist, verify they target the right composition)

`package.json` already has:

```jsonc
"video:render:studio": "npx remotion render src/remotion/index.ts SkillStudio --codec=h264 --crf=23 public/video/skill-studio.mp4",
"video:render:studio:webm": "npx remotion render src/remotion/index.ts SkillStudio --codec=vp8 --crf=30 public/video/skill-studio.webm"
```

Both target the `SkillStudio` composition id from `Root.tsx:33-39`. The composition `durationInFrames` MUST be updated to `STUDIO_EFFECTIVE_FRAMES` (current: 1005 — the new effective is ~4830 frames). This is a 1-line change in `Root.tsx`.

### 6.2 Add an "all" script to avoid drift

Current renders are 8 days drift apart (mp4 Mar 18, webm Mar 10) per the master plan. To prevent re-occurrence:

```jsonc
"video:render:studio:all": "npm run video:render:studio && npm run video:render:studio:webm && npm run video:vtt:studio"
```

This is the canonical entry point — running these in lockstep prevents future drift.

### 6.3 Wall-clock budget

`HackathonDemo` is 5535 frames and renders in ~60s on the dev machine (per the master plan note). Studio at 4830 frames is ~13% smaller → expect ~52s for mp4, ~75s for webm (vp8 is slower than h264 at same crf). Plus voiceover gen ~30s. Total wall-clock for one full render cycle: **~3 minutes**.

### 6.4 R2 upload — scope OUT

The `/studio/page.tsx:14` references `https://pub-…r2.dev/product-demo/skill-studio-overview.mp4` as the YouTube fallback mp4. Replacing the R2 asset is a manual `wrangler r2 object put` step. For INC-B we explicitly scope OUT the R2 upload — it's a follow-up after Anton verifies the local render. The local `public/video/skill-studio.mp4` is the source of truth for the page's `mp4=` prop in INC-B; the R2 URL stays pointing at the old upload until manually replaced. (The page's `ProductDemoCard` will need its `mp4=` prop pointed at the local `/video/skill-studio.mp4` — see §7.)

## 7. `studio/page.tsx` — chapters + video src

### 7.1 Current state: YouTube-first

`src/app/studio/page.tsx:10-31` defines `PRODUCT_DEMO_YOUTUBE_ID = "yEg46Ybh4Yk"` and `DEMO_CHAPTERS = [...]`. The chapters carry hardcoded MM:SS timestamps that map to the OLD hackathon-demo composition.

### 7.2 Decision: keep YouTube embed, regenerate chapters from script.ts

We keep the YouTube embed as primary (Anton's locked decision per memory `project_video_brand_decisions_2026_04.md` — "no YouTube embeds" referred to /watch entries; /studio's existing YouTube embed is the canonical SEO surface). However:

- Chapters MUST be regenerated from the new `STUDIO_SCRIPT` so `DEMO_CHAPTERS` and the SEO `hasPart` schema reflect the new beats.
- The `mp4=` prop on `ProductDemoCard` switches from the R2 fallback URL to `/video/skill-studio.mp4` (local). This makes the local render observable on `/studio` immediately, even before R2 re-upload.

### 7.3 Chapters auto-generation

We add a build helper at `src/app/studio/buildChapters.ts`:

```ts
import {
  STUDIO_SCRIPT,
  STUDIO_FPS,
  STUDIO_TRANSITION_FRAMES,
} from "@/remotion/scenes/studio/script";

export function buildStudioChapters(): { time: string; seconds: number; title: string }[] {
  let cumFrames = 0;
  return STUDIO_SCRIPT.map((scene, i) => {
    const seconds = Math.round(cumFrames / STUDIO_FPS);
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    const time = `${m}:${String(s).padStart(2, "0")}`;
    const isLast = i === STUDIO_SCRIPT.length - 1;
    const overlap = !isLast && scene.transitionType ? STUDIO_TRANSITION_FRAMES : 0;
    cumFrames += scene.durationFrames - overlap;
    return { time, seconds, title: scene.caption ?? scene.id };
  });
}
```

`page.tsx` consumes `DEMO_CHAPTERS = buildStudioChapters()` at module load. SEO `hasPart` clip array is generated from the same source.

### 7.4 Diff outline for `page.tsx`

```diff
- const DEMO_CHAPTERS = [
-   { time: "0:00", seconds: 0, title: "The pain — saving ≠ shipped" },
-   ... 9 more hardcoded ...
- ];
+ import { buildStudioChapters } from "./buildChapters";
+ import { STUDIO_DURATION_SECONDS } from "@/remotion/scenes/studio/script";
+ const DEMO_CHAPTERS = buildStudioChapters();

  ...
  <ProductDemoCard
    youtubeId={PRODUCT_DEMO_YOUTUBE_ID}
-   mp4={PRODUCT_DEMO_MP4}
+   mp4="/video/skill-studio.mp4"
+   captionsSrc="/video/skill-studio.vtt"
    title="Skill Studio in"
    titleAccent="3 minutes"
    ...
-   duration="3:04 · 1080p"
+   duration={`${formatDuration(STUDIO_DURATION_SECONDS)} · 1080p`}
    ...
    chapters={DEMO_CHAPTERS}
  />
```

(`STUDIO_DURATION_SECONDS` from `script.ts`. `formatDuration` is a 4-line helper — `M:SS`.)

The hardcoded `hasPart` array in `STRUCTURED_DATA` (`page.tsx:127-138`) gets the same chapter regeneration:

```diff
-     hasPart: [
-       { "@type": "Clip", name: "The pain — saving ≠ shipped", startOffset: 0, ... },
-       ... 9 more ...
-     ],
+     hasPart: DEMO_CHAPTERS.map(c => ({
+       "@type": "Clip",
+       name: c.title,
+       startOffset: c.seconds,
+       url: `${PRODUCT_DEMO_YOUTUBE_URL}&t=${c.seconds}s`,
+     })),
```

### 7.5 `STUDIO_DESCRIPTION` updated

The current description references "100% local · `npx vskill studio`" — keep. No change required.

## 8. `VideoPlayer` captions wiring

### 8.1 Current state

`src/app/components/shared/VideoPlayer.tsx:79`:

```tsx
<track kind="captions" label="English" default />
```

The `track` element exists but has NO `src=` — it's a no-op.

### 8.2 Fix

Add `srcLang` and an optional `captionsSrc` prop:

```tsx
interface VideoPlayerProps {
  mp4: string;
  webm?: string;
  ariaLabel: string;
  accentColor?: string;
  className?: string;
  eager?: boolean;
+ captionsSrc?: string;
}

...

- <track kind="captions" label="English" default />
+ {captionsSrc && (
+   <track kind="captions" srcLang="en" label="English" src={captionsSrc} default />
+ )}
```

We render the `<track>` ONLY when `captionsSrc` is provided — otherwise the empty track is invalid HTML and confuses Chrome. Existing callers (HomepageDemo on `/`) keep working without captions; the /studio caller passes `captionsSrc="/video/skill-studio.vtt"`.

### 8.3 But `/studio/page.tsx` uses `ProductDemoCard`, not `VideoPlayer`

`/studio` uses `ProductDemoCard` which embeds the YouTube iframe with R2/local mp4 as fallback. The YouTube iframe carries its own captions (uploaded to YouTube manually); the HTML5 fallback `<video>` inside `ProductDemoCard` is what we need to wire.

**T-01 (exploration task) reads `ProductDemoCard.tsx`** to understand the contract. If it uses `<VideoPlayer>` internally, the patch is pass-through. If it has its own inline `<video>`, we add `captionsSrc` to its prop surface and wire `<track>` there. Either way, the prop call-site at `studio/page.tsx:242-254` becomes:

```diff
  <ProductDemoCard
    ...
    mp4="/video/skill-studio.mp4"
+   captionsSrc="/video/skill-studio.vtt"
    ...
  />
```

`/docs/studio` (per §9 below) uses the bare `<VideoPlayer>` and benefits from the same `captionsSrc` prop.

## 9. `/docs/studio` page

### 9.1 Format: `.tsx`, not `.mdx`

Per `docs-nav.ts:13-16`, MDX pages auto-register via `scripts/generate-docs-nav.cjs`. Non-MDX (`.tsx`) pages need explicit nav entries. Looking at the surrounding pages — `getting-started`, `submitting`, `faq`, `plugins`, the docs index — they are all `.tsx` ("marketing-shaped" per the comment). `/docs/studio` is firmly marketing-shaped (top-of-page video embed + feature copy). So `.tsx` it is. No new MDX harvest pipeline change.

### 9.2 Path

`src/app/docs/studio/page.tsx`. Standard Next.js app-dir convention.

### 9.3 Content layout

```tsx
export default function StudioDocsPage() {
  return (
    <DocsLayout nav={DOCS_NAV} title="Studio">
      <h1>Skill Studio</h1>
      <p className="lead">
        Author, evaluate, publish, and update verified AI skills — locally,
        with any model, in your project folder.
      </p>

      {/* Top-of-page video — same source as /studio */}
      <VideoPlayer
        mp4="/video/skill-studio.mp4"
        webm="/video/skill-studio.webm"
        captionsSrc="/video/skill-studio.vtt"
        ariaLabel="Skill Studio product walkthrough"
        accentColor="#06b6d4"
      />

      <section id="evals">
        <h2>Plain-English Evals</h2>
        <p>Describe expected behavior in natural language. ...</p>
      </section>

      <section id="ab-compare">...</section>
      <section id="any-model">...</section>
      <section id="local-first">...</section>
      <section id="publish-to-github">...</section>
      <section id="install-scopes">...</section>
      <section id="updates">...</section>

      <section id="related">
        <h2>Related</h2>
        <ul>
          <li><Link href="/docs/security-guidelines">Security guidelines</Link></li>
          <li><Link href="/docs/plugins">Plugins</Link></li>
          <li><Link href="/docs/submitting">Submitting skills</Link></li>
        </ul>
      </section>
    </DocsLayout>
  );
}
```

The body sections mirror the 4 FEATURES on `/studio/page.tsx:143-168` (Plain-English Evals, A/B Compare, Any Model, 100% Local) plus 3 workflow sections (Publish to GitHub, Install Scopes, Updates) that map directly to the new Remotion scenes from §2.

### 9.4 The 7 body sections — 1-paragraph each

Each section has an `id` (so chapter anchor links work) and a 60–120 word paragraph. Cross-links cited above. PM owns the prose; architect owns only the structure.

## 10. `docs-nav.ts` insertion

### 10.1 Where in the array

Looking at `docs-nav.ts:29-84`, the section order is:

1. Overview
2. Quickstart
3. Core Concepts (Security Guidelines)
4. Skills (Submitting)
5. Workflows
6. Integrations (Plugins)
7. Reference (CLI Reference)
8. FAQ

`/docs/studio` is a **product surface page**. It belongs after "Quickstart" (so users can read the overview after they're started) and before "Core Concepts" (which is ecosystem-level, not product-level).

### 10.2 Exact diff

```diff
  export const DOCS_NAV: NavItem[] = [
    { label: "Overview", href: "/docs" },
    {
      label: "Quickstart",
      href: "/docs/getting-started",
      children: [
        { label: "Getting Started", href: "/docs/getting-started" },
      ],
    },
+   {
+     label: "Studio",
+     href: "/docs/studio",
+     children: [
+       { label: "Overview", href: "/docs/studio" },
+       { label: "Plain-English Evals", href: "/docs/studio#evals" },
+       { label: "A/B Compare", href: "/docs/studio#ab-compare" },
+       { label: "Any Model", href: "/docs/studio#any-model" },
+       { label: "Publish to GitHub", href: "/docs/studio#publish-to-github" },
+       { label: "Install Scopes", href: "/docs/studio#install-scopes" },
+       { label: "Updates", href: "/docs/studio#updates" },
+     ],
+   },
    {
      label: "Core Concepts",
      ...
```

### 10.3 The `docs-nav.test.ts` enforcer

ADR 0810-01 doesn't say so, but `docs-nav.test.ts` per the `docs-nav.ts:13-16` comment enforces the section hierarchy `Quickstart → Core Concepts → Skills → Workflows → Integrations → Reference → FAQ`. Adding "Studio" between Quickstart and Core Concepts may break the test. T-17 explicitly opens that test, expands the allow-list to include "Studio", and re-runs.

## 11. `sitemap.ts` addition

### 11.1 Exact entry

```diff
    { url: `${base}/docs`, changeFrequency: "weekly", priority: 0.7 },
    { url: `${base}/docs/plugins`, changeFrequency: "weekly", priority: 0.7 },
+   { url: `${base}/docs/studio`, changeFrequency: "weekly", priority: 0.7 },
```

Insert next to the existing `/docs/*` entries to keep them grouped. Priority 0.7 matches `/docs/plugins` — both are docs-level surfaces. (The team-lead's bootstrap message suggested 0.6, but `/docs/plugins` is precedent at 0.7 for a doc page that's NOT a top-level surface, so 0.7 is the right peer.)

## 12. Implementation order — 18 tasks

Strict dependency ordering. T-08 onward depends on T-01–T-07 being merged.

| T# | Task | Why it's here |
|----|------|---------------|
| **T-01** | Read `ProductDemoCard.tsx` + locate the `<video>` element to understand caption-wiring hook (no code change) | Discovery dep for T-15 |
| **T-02** | Create `src/remotion/scenes/studio/script.ts` (full 11-scene array, all `voiceText`/`caption`/`visualNotes`/`durationFrames`) | Source-of-truth — required by everything downstream |
| **T-03** | Refactor `src/remotion/SkillStudioDemo.tsx` to consume `STUDIO_SCRIPT` + scene-kit primitives (mirror `HackathonDemo.tsx:60-104` topology) | Core composition refactor |
| **T-04** | Update `src/remotion/Root.tsx`: `durationInFrames={STUDIO_EFFECTIVE_FRAMES}` | Required for new total runtime to render — without this, mp4 is truncated |
| **T-05** | Build `src/remotion/scenes/studio/TestsTabIntro.tsx` | New scene #1 |
| **T-06** | Build `src/remotion/scenes/studio/PublishToGitHub.tsx` | New scene #2 |
| **T-07** | Build `src/remotion/scenes/studio/InstallScopePicker.tsx` | New scene #3 |
| **T-08** | Build `src/remotion/scenes/studio/UpdateToast.tsx` | New scene #4 |
| **T-09** | Build `src/remotion/scenes/studio/CommandPalette.tsx` | New scene #5 |
| **T-10** | Add `video:voiceover:studio` + `video:render:studio:all` + `video:vtt:studio` to `package.json` | Enables T-11/12 |
| **T-11** | Run `npm run video:voiceover:studio` (pulls `ELEVENLABS_API_KEY` from `.env.local`); inspect `public/studio/voiceover-raw.mp3` (>50 KB, ffprobe duration ~155–170s) | Voiceover ready |
| **T-12** | Add `<Audio src={staticFile("studio/voiceover-raw.mp3")} volume={1.0}>` + BGM to `SkillStudioDemo.tsx` (mirror `HackathonDemo.tsx:64-69` cold-open offset) | Audio mixed into composition |
| **T-13** | Build `scripts/generate-vtt.mjs <video-name>` + unit test at `scripts/__tests__/generate-vtt.test.ts` (input fixture = a 3-scene mock script, asserts cue start/end times) | VTT generator + tests |
| **T-14** | Run `npm run video:render:studio:all`; verify `public/video/skill-studio.{mp4,webm,vtt}` (~30–40 MB mp4, ~12–18 MB webm, valid `.vtt`) | First full render |
| **T-15** | Update `VideoPlayer.tsx` to accept `captionsSrc` + render `<track>` only when present; add a Vitest unit test that verifies the conditional render | Caption wiring |
| **T-16** | Update `src/app/studio/buildChapters.ts` (NEW) + `src/app/studio/page.tsx` (auto-chapters, `mp4="/video/skill-studio.mp4"`, `captionsSrc="/video/skill-studio.vtt"`) | /studio page wired to local render |
| **T-17** | Create `src/app/docs/studio/page.tsx` (full content per §9.3) + update `src/app/docs/docs-nav.ts` per §10.2 + update `docs-nav.test.ts` allow-list + add `/docs/studio` to `sitemap.ts` per §11 | /docs/studio shipped |
| **T-18** | E2E smoke (Playwright) — `/studio` and `/docs/studio` load, video element is present and has a `<track src="/video/skill-studio.vtt">`, no console errors | Closure gate |

T-13 (VTT generator) is intentionally placed AFTER T-11 (voiceover) and BEFORE T-14 (render) so we can render mp4 + webm + vtt all in one `video:render:studio:all` invocation.

## 13. Risk matrix

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Voiceover render fails mid-pipeline** (ElevenLabs HTTP 429/500) | M | `generate-voiceover.mjs:252-258` already exits non-zero on HTTP error. Mitigation: T-11 is idempotent — re-run on failure. Output is `voiceover-raw.mp3`; the previous file is overwritten only on success (the generator writes via `createWriteStream` which truncates on open, but pipeline error throws before close — partial-write check at `:272` rejects <50 KB). **One scene** out of 11 will fail to read voice if API key is missing — caught by the script's pre-flight `process.env.ELEVENLABS_API_KEY` check. |
| **`generate-vtt.mjs` produces malformed cues** (negative end times, overlapping ranges) | M | Unit tests in T-13 with 3 fixture scenarios: scenes with all transitions, scenes with `transitionType: null`, scenes with empty `caption`. Validate every `end > start` and `start[i+1] >= end[i] - transitionFrames/fps`. |
| **New scenes have wrong dimensions / runtime errors at render time** | M | Each scene is a pure function-component with zero external state — runtime errors at render time propagate to the Chromium renderer and the render aborts cleanly. Mitigation: T-05 through T-09 each ship with a smoke test (`vitest run -t "scene-name renders"`) that mounts the component in jsdom and asserts no throw. Same pattern as `scene-kit/__tests__/`. |
| **Chapters array drifts from script.ts again** (the originating bug) | L | `buildChapters.ts` reads `STUDIO_SCRIPT` directly — drift is mechanically impossible. Snapshot test in T-16 asserts `DEMO_CHAPTERS.length === STUDIO_SCRIPT.length`. |
| **Existing 6 studio scenes break under new timing** (visual de-sync) | M | Each existing scene has internal animation timing tuned to the old `durationFrames`. Re-timing in §3.1 was conservative — the existing scenes' max-frame internal timings are bounded by their old durations (180/240/360 frames). New timings ≥ old timings, so existing animations finish before the scene boundary. **Justification**: looked at `StudioIntro.tsx:48-55` — the brand reveal completes at `frame=brandDelay+15+spring(60)` ≈ 75 frames; current scene is 90, new scene is 240 → safe. Architect confirms the same inspection pattern applies to scenes 2–6. |
| **R2 mp4 unchanged → /studio YouTube still serves old hackathon-demo if YouTube is broken** | L | R2 fallback is the second-tier fallback (after YouTube iframe). If YouTube embed loads, the R2 mp4 is dormant. The local `/video/skill-studio.mp4` becomes the primary fallback in INC-B by switching `mp4=` prop. R2 stays stale until a follow-up. **Acceptable** per scope. |
| **`docs-nav.test.ts` allow-list breaks** | L | Hierarchy enforcer test. T-17 includes "open the test, add 'Studio' to the allow-list array, re-run". 5-line change. |
| **Voiceover duration ≠ video duration** (over/under by >2s) | M | After T-11, ffprobe duration printed by `generate-voiceover.mjs:269`. Compare to `STUDIO_DURATION_SECONDS` from `script.ts`. If diff > 2s, adjust `durationFrames` per scene (most likely culprits: scenes with verbose `voiceText`). Iterate T-02 → T-11 → re-check until within 2s. **Budget: 1 retry maximum, then accept the cosmetic gap or trim the longest `voiceText` by 5 words.** |
| **Browser doesn't pick up new VTT** (cached old mp4) | L | `/studio` is statically generated — Next.js cache invalidates on rebuild. Local dev: hard-refresh. |

## 14. Out of scope (explicit)

- `/learn → /watch` rename (INC-C)
- Inline `<DocVideoEmbed>` on other `/docs/*` pages (INC-D)
- Deletion of `VideoHero.tsx` and orphan `public/video/{ship-while-you-sleep,specweave-promo}.{mp4,webm}` (INC-D)
- R2 upload of new `skill-studio.mp4` (manual follow-up — see §6.4)
- New YouTube upload (separate creator workflow — out of code-change scope)
- Voiceover mastering (loudness-normalize, compression) — Phase-2 if Anton hears clipping
- New BGM track selection — Skybound Circuits is universal per ADR 0810-01

## 15. Test plan (architect-level — TDD-strict per spec.md)

| Layer | What we test | Tool |
|-------|-------------|------|
| **Unit** | `script.ts` shape (every scene has all required keys, total frames math) | Vitest |
| **Unit** | `buildChapters.ts` — given a known `STUDIO_SCRIPT`, returns expected `DEMO_CHAPTERS` | Vitest |
| **Unit** | `generate-vtt.mjs` — given fixture script, emits valid `.vtt` (cue ordering, monotonic times) | Vitest |
| **Unit** | Each new scene component renders without throw in jsdom | Vitest + `@testing-library/react` |
| **Unit** | `VideoPlayer.tsx` — `<track>` only renders when `captionsSrc` provided | Vitest |
| **Integration** | Voiceover generator end-to-end with fake `fetch` (mocked ElevenLabs) | Vitest |
| **E2E** | `/studio` loads, `<video>` element present, `<track src=".vtt">` present, captions toggle works | Playwright |
| **E2E** | `/docs/studio` loads, `<video>` element present, nav highlights "Studio" | Playwright |
| **Snapshot** | `DEMO_CHAPTERS.length === STUDIO_SCRIPT.length` | Vitest |
| **Manual** | Anton plays the rendered video locally on `localhost:3000/studio` and verifies brand colors match `globals.css` | Manual (per closure gate) |

Coverage target: 90% (per spec.md frontmatter).

## 16. Files modified summary

**Modify:**
- `src/remotion/SkillStudioDemo.tsx` — script-as-data refactor
- `src/remotion/Root.tsx` — `durationInFrames` updated
- `src/app/studio/page.tsx` — chapters auto-gen, mp4 + captions src
- `src/app/components/shared/VideoPlayer.tsx` — `captionsSrc` prop
- `src/app/components/shared/ProductDemoCard.tsx` — `captionsSrc` pass-through (final shape determined by T-01)
- `src/app/docs/docs-nav.ts` — Studio section
- `src/app/sitemap.ts` — `/docs/studio` entry
- `package.json` — 3 new scripts
- `src/app/docs/__tests__/docs-nav.test.ts` (or equivalent — locate during T-17) — extend allow-list

**Create:**
- `src/remotion/scenes/studio/script.ts`
- `src/remotion/scenes/studio/TestsTabIntro.tsx`
- `src/remotion/scenes/studio/PublishToGitHub.tsx`
- `src/remotion/scenes/studio/InstallScopePicker.tsx`
- `src/remotion/scenes/studio/UpdateToast.tsx`
- `src/remotion/scenes/studio/CommandPalette.tsx`
- `src/app/studio/buildChapters.ts`
- `src/app/docs/studio/page.tsx`
- `scripts/generate-vtt.mjs`
- `scripts/__tests__/generate-vtt.test.ts`
- `public/studio/voiceover-raw.mp3` (artifact, not git-tracked per existing `.gitignore` for `public/<video>/voiceover*.mp3`)
- `public/video/skill-studio.mp4` (artifact — overwrites existing 2.6 MB Mar-18 file)
- `public/video/skill-studio.webm` (artifact — overwrites existing 1.0 MB Mar-10 file)
- `public/video/skill-studio.vtt` (NEW artifact)
- `.specweave/docs/internal/architecture/adr/0812-01-studio-video-refresh-and-docs.md`

**Delete:** none (INC-B does no cleanup; INC-D does).

## 17. ADR cross-refs

This plan implements the rules mandated by ADR 0810-01 §Consequences:

1. ✓ `script.ts` co-located at `src/remotion/scenes/studio/script.ts`
2. ✓ Composition registered in `Root.tsx` (already present, durationInFrames updated)
3. ✓ `video:render:studio` already in `package.json`; `video:render:studio:all` added per §6.2
4. ✓ Voiced via `node scripts/generate-voiceover.mjs studio` with Sarah default
5. ✓ No `BRAND_COLORS` or `globals.css` changes in INC-B (foundation locked in INC-A)

ADR 0812-01 records the four NEW decisions specific to /studio (chapters auto-gen from script.ts, .vtt strategy, /docs/studio placement, /studio page mp4 src switch).
