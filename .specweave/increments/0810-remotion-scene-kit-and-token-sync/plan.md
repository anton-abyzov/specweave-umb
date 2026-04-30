# Plan — Remotion scene-kit + globals.css token sync + Sarah voiceover pipeline

**Increment**: `0810-remotion-scene-kit-and-token-sync`
**Working tree**: `repositories/anton-abyzov/vskill-platform/`
**Architect agent**: this plan
**Companion**: `spec.md` (US-001 … US-004), `tasks.md` (planner agent), ADR `0810-01-video-pipeline-and-token-sync.md`

---

## 1. System architecture

### 1.1 Module boundary — `src/remotion/scene-kit/`

Single new directory inside the existing Remotion tree. **Justified** at `src/remotion/scene-kit/` (NOT a separate workspace package like `packages/remotion-kit/`) because:

- vskill-platform is a single Next.js app — no `pnpm-workspace.yaml`, npm workspaces, or Turborepo config exists. Introducing one for a 12-export module would add a build-system bombshell to a foundation increment.
- Remotion's `Root.tsx` already imports relatively from `./components/...` and `./scenes/...`. A sibling `./scene-kit/` matches that convention.
- The scene-kit ships only with the Remotion bundle (`@remotion/cli` builds compositions for offline render). It is NOT imported by `next.config.ts` or any route, so it never reaches the browser bundle. Co-location under `src/remotion/` makes that boundary self-evident.

### 1.2 Public API surface (12 component exports + tokens)

```
src/remotion/scene-kit/
├── index.ts                       # barrel — re-exports everything
├── tokens.ts                      # BRAND_COLORS, STUDIO_LIGHT, VERIFIED_DARK, TERMINAL_UI, HACKATHON_FONTS
├── uiTokens.ts                    # PHYSICALLY MOVED from scenes/hackathon/uiTokens.ts
├── primitives/
│   ├── _internals/
│   │   └── BlinkingCursor.tsx     # extracted from TerminalFrame; reused by CommandTypewriter
│   ├── TerminalFrame.tsx          # LIFTED from src/remotion/components/TerminalFrame.tsx
│   ├── BigText.tsx                # LIFTED
│   ├── AgentIcon.tsx              # LIFTED
│   ├── TierBadgeVideo.tsx         # LIFTED (also exports TIER_CONFIG for SkillCard reuse)
│   ├── TransitionWipe.tsx         # LIFTED
│   ├── CaptionBar.tsx             # NEW — lower-third caption per HackathonScene.caption
│   ├── BrowserChrome.tsx          # NEW — Chrome address-bar frame (used by ConsumeBrowserExcellent)
│   ├── TUIFrame.tsx               # NEW — Claude Code TUI mock (terminal + terra-cotta banner)
│   ├── CommandTypewriter.tsx      # NEW — extracted typing logic, no terminal chrome
│   ├── PillTag.tsx                # NEW — matches Studio FEATURES pill (label + accentColor swatch)
│   ├── MetricBar.tsx              # NEW — animated horizontal % bar (eval scores)
│   └── SkillCard.tsx              # NEW — Remotion port of website SkillCard (registry grid)
└── __tests__/
    ├── tokens.test.ts             # AC-US1-06 — BRAND_COLORS vs Studio FEATURES alignment
    └── primitives-smoke.test.tsx  # AC-US1-02 — each new primitive renders inside <Composition>
```

`index.ts` exact shape:

```ts
// scene-kit/index.ts
export { TerminalFrame } from "./primitives/TerminalFrame";
export { BigText } from "./primitives/BigText";
export { AgentIcon } from "./primitives/AgentIcon";
export { TierBadgeVideo } from "./primitives/TierBadgeVideo";
export { TransitionWipe } from "./primitives/TransitionWipe";
export { CaptionBar } from "./primitives/CaptionBar";
export { BrowserChrome } from "./primitives/BrowserChrome";
export { TUIFrame } from "./primitives/TUIFrame";
export { CommandTypewriter } from "./primitives/CommandTypewriter";
export { PillTag } from "./primitives/PillTag";
export { MetricBar } from "./primitives/MetricBar";
export { SkillCard } from "./primitives/SkillCard";
export {
  BRAND_COLORS,
  STUDIO_LIGHT,
  VERIFIED_DARK,
  TERMINAL_UI,
  HACKATHON_FONTS,
  type BrandColorKey,
  type AccentColor,
} from "./tokens";
```

12 component exports satisfies AC-US1-01 — `grep -E "^export \{ [A-Z][A-Za-z]+ \} from" src/remotion/scene-kit/index.ts | wc -l` → 12.

### 1.3 Token model (`tokens.ts`)

```ts
// scene-kit/tokens.ts
export const BRAND_COLORS = {
  green:  "#22c55e",   // Plain-English Evals
  blue:   "#3b82f6",   // A/B Compare
  purple: "#a855f7",   // Any Model
  cyan:   "#06b6d4",   // 100% Local
} as const;

export type BrandColorKey = keyof typeof BRAND_COLORS;
export type AccentColor = (typeof BRAND_COLORS)[BrandColorKey];

// Re-exported from the moved hackathon uiTokens (now sibling at scene-kit/uiTokens.ts)
export { STUDIO_LIGHT, VERIFIED_DARK, TERMINAL_UI, HACKATHON_FONTS } from "./uiTokens";
```

**Physical move of `uiTokens.ts`**: `src/remotion/scenes/hackathon/uiTokens.ts` → `src/remotion/scene-kit/uiTokens.ts` (file body unchanged). Replace the original with a one-line re-export shim:

```ts
// src/remotion/scenes/hackathon/uiTokens.ts (shim)
export * from "../../scene-kit/uiTokens";
```

Rationale: every hackathon scene file imports from `./uiTokens` or `../uiTokens`. Modifying ~12 scene files is out of scope for a foundation increment. Shim keeps blast radius zero.

### 1.4 Backwards-compat re-export shims (FR-001, AC-US1-04)

Five 1-line shims at the OLD primitive paths:

```ts
// src/remotion/components/TerminalFrame.tsx
export { TerminalFrame } from "../scene-kit/primitives/TerminalFrame";
```
```ts
// src/remotion/components/BigText.tsx
export { BigText } from "../scene-kit/primitives/BigText";
```
```ts
// src/remotion/components/AgentIcon.tsx
export { AgentIcon } from "../scene-kit/primitives/AgentIcon";
```
```ts
// src/remotion/components/TierBadgeVideo.tsx
export { TierBadgeVideo } from "../scene-kit/primitives/TierBadgeVideo";
```
```ts
// src/remotion/components/TransitionWipe.tsx
export { TransitionWipe } from "../scene-kit/primitives/TransitionWipe";
```

This preserves every existing import in `CLIShowcase.tsx`, scene files under `scenes/studio/`, `scenes/learn/`, `scenes/hackathon/`, plus their `__tests__/`.

**Inside the lifted primitive files**: each currently does `import { COLORS, FONTS } from "../constants"`. After the move it becomes `"../../constants"` (one extra `../` — they moved one level deeper). 5-file × 1-line patch applied at move-time. `COLORS`/`FONTS` themselves stay in `src/remotion/constants.ts` — those describe the dark-Geist promo aesthetic specific to PromoVideo/HomepageDemo and are NOT brand tokens. The new `BRAND_COLORS` is the canonical brand layer; it does NOT replace `COLORS`.

---

## 2. New primitive component design

Each block: props contract → theming hook → render-time concerns.

### 2.1 `<CaptionBar>`

Lower-third pull-quote bar. Renders the `caption` field from any `script.ts` scene.

```ts
type CaptionBarProps = {
  text: string;
  accentColor?: AccentColor;       // default BRAND_COLORS.cyan
  position?: "bottom" | "top";     // default "bottom"
  fontSize?: number;               // default 36
  delay?: number;                  // frames; default 0
};
```

Theming: `accentColor` drives a 3 px top border + the text shadow. Body bg is always `rgba(0,0,0,0.78)` — caption must read on any underlying scene.

Render-time: spring-in opacity + translateY (mirror `BigText`'s spring config: `damping: 200`). Premount-safe (uses `useCurrentFrame()` only).

### 2.2 `<BrowserChrome>`

Mac Chrome frame for "viewport" scenes (used by `ConsumeBrowserExcellent`). Three traffic lights, address-bar pill, child viewport area.

```ts
type BrowserChromeProps = {
  url: string;                      // e.g. "localhost:3000/hero"
  width?: number;                   // default 1560 (matches TerminalFrame width)
  height?: number;                  // default 880 — fits inside 1080p comp with margin
  children: React.ReactNode;        // viewport content
  accentColor?: AccentColor;        // address-bar focus ring (default cyan)
};
```

Theming: traffic-light colors come from `TERMINAL_UI.dotRed/dotYellow/dotGreen` (already audited in `uiTokens.ts:75-78`). Frame border `#262626`, address-bar bg `#1a1a1a`. NO dependency on globals.css — Remotion compositions are bundled separately and never load CSS.

Render-time: pure layout, no animation hooks. Drop into any scene.

### 2.3 `<TUIFrame>`

Wrapper around `<TerminalFrame>` that adds the Claude Code terra-cotta banner header (mirrors `TERMINAL_UI.bannerBorder/bannerTitle` at `uiTokens.ts:84-87`). Used for any scene mocking the Claude Code REPL.

```ts
type TUIFrameProps = {
  bannerTitle?: string;             // default "Claude Code"
  bannerSubtitle?: string;
  children: React.ReactNode;        // typically <CommandTypewriter> content
  width?: number;                   // default 1560
};
```

Theming: locked to `TERMINAL_UI` tokens (NO `accentColor` prop — Claude branding is fixed). Banner is a flex row above the inner terminal area.

Render-time: composes `<TerminalFrame>` inside; banner is a bare div, no animation.

### 2.4 `<CommandTypewriter>`

Extracted typing logic from `TerminalFrame.tsx`. Useful when a scene needs the typing effect WITHOUT the full terminal chrome (e.g. inline command demos in `AuthorEditAndPublish`).

```ts
type CommandTypewriterProps = {
  command: string;                  // text to type
  charSpeed?: number;               // frames per char, default 2
  prefix?: string;                  // default "$ "
  delay?: number;                   // start delay
  onCompleteFrame?: number;         // frame at which the cursor stops blinking
  fontSize?: number;                // default 32
  accentColor?: AccentColor;        // colors the prefix; default BRAND_COLORS.green
};
```

Theming: `accentColor` for the prefix only; typed text is always `TERMINAL_UI.text` (`#e5e5e5`).

Render-time: same `useCurrentFrame()` + `interpolate` pattern from `TerminalFrame.tsx:95-115`. **Reuses** `<BlinkingCursor>` extracted from `TerminalFrame.tsx` into `_internals/BlinkingCursor.tsx` so it is NOT duplicated.

### 2.5 `<PillTag>`

Matches the Studio FEATURES pills exactly (`src/app/studio/page.tsx:25-50`). Used for tag rows, feature lists, scene callouts.

```ts
type PillTagProps = {
  label: string;
  accentColor: AccentColor;         // REQUIRED — drives swatch + border
  size?: "sm" | "md" | "lg";        // default "md"
  delay?: number;
};
```

Theming: 1 px border using `accentColor`, 6 px circular swatch on the left also `accentColor`, label text `STUDIO_LIGHT.text`. Background `STUDIO_LIGHT.surface` — lives on the light Studio aesthetic.

Render-time: spring-in scale 0.9 → 1.0 + opacity 0 → 1 over ~12 frames.

### 2.6 `<MetricBar>`

Animated horizontal bar — used for eval pass percentages, tier scores, benchmark results.

```ts
type MetricBarProps = {
  label: string;
  value: number;                    // 0–100 target percentage
  accentColor?: AccentColor;        // default green
  width?: number;                   // default 600
  height?: number;                  // default 32
  delay?: number;
  durationFrames?: number;          // animation duration; default 30
};
```

Theming: track `rgba(255,255,255,0.08)`; fill `accentColor`. Label text `currentColor` so the parent scene controls foreground.

Render-time: `interpolate(frame, [delay, delay + durationFrames], [0, value], { easing: Easing.out(Easing.cubic) })`.

### 2.7 `<SkillCard>`

Remotion port of the website's SkillCard — used for registry-grid scenes (e.g. the upcoming `skills-manager-overview` video).

```ts
type SkillCardProps = {
  name: string;                      // e.g. "frontend-design"
  publisher: string;                 // e.g. "anton-abyzov"
  tier: "basic" | "verified" | "certified";
  description?: string;
  width?: number;                    // default 360
  delay?: number;
  accentColor?: AccentColor;         // accent border (default cyan)
};
```

Theming: card surface `STUDIO_LIGHT.surface`, border `STUDIO_LIGHT.border`, tier badge color from `TIER_CONFIG[tier].color` lifted from `TierBadgeVideo.tsx:13-35`. **Reuse** `TIER_CONFIG` — DO NOT duplicate. `TierBadgeVideo` exports it (named export) so `SkillCard` can import.

Render-time: scale-in spring + tiny stagger when used in a grid (handled by parent via `delay` prop).

---

## 3. Migration plan for existing primitives

### 3.1 Physical move

```bash
# Inside repositories/anton-abyzov/vskill-platform/
mkdir -p src/remotion/scene-kit/primitives/_internals \
         src/remotion/scene-kit/__tests__

git mv src/remotion/components/TerminalFrame.tsx     src/remotion/scene-kit/primitives/TerminalFrame.tsx
git mv src/remotion/components/BigText.tsx           src/remotion/scene-kit/primitives/BigText.tsx
git mv src/remotion/components/AgentIcon.tsx         src/remotion/scene-kit/primitives/AgentIcon.tsx
git mv src/remotion/components/TierBadgeVideo.tsx    src/remotion/scene-kit/primitives/TierBadgeVideo.tsx
git mv src/remotion/components/TransitionWipe.tsx    src/remotion/scene-kit/primitives/TransitionWipe.tsx
git mv src/remotion/scenes/hackathon/uiTokens.ts     src/remotion/scene-kit/uiTokens.ts
```

`git mv` preserves rename detection so reviewers see clean renames + small shim insertions, NOT 5 deletions + 5 additions.

### 3.2 Import-path patch inside each lifted file

Each lifted primitive currently does `import { COLORS, FONTS } from "../constants"`. After the move it becomes `import { COLORS, FONTS } from "../../constants"`. 5-file × 1-line edit, applied as part of the move task.

### 3.3 Re-export shims at old paths

Five 1-line shims at `src/remotion/components/` (see §1.4). Plus the `uiTokens.ts` shim at the old hackathon path (see §1.3). Importers continue to resolve unchanged in:

- `src/remotion/scenes/studio/Studio*.tsx` — many import `TerminalFrame`, `BigText` from `../../components/...`.
- `src/remotion/scenes/learn/*.tsx` — import `TitleCard` etc. (these stay in `scenes/learn/` — not lifted; they are scenes, not primitives).
- `src/remotion/scenes/hackathon/*.tsx` — import `TerminalFrame` from `../../components/TerminalFrame` and `uiTokens` from `./uiTokens`.
- `src/remotion/scenes/CLIShowcase.tsx:10-12` — imports `TerminalFrame`, `AgentIcon`, `BigText` from `../components/...`.
- `src/remotion/scenes/learn/__tests__/*.test.tsx` — likely import primitives.

**Zero scene file is modified in this increment.**

### 3.4 Verification gate

Run `npx tsc --noEmit` after the moves + shims. Must produce 0 errors. Then `npx remotion render src/remotion/index.ts HackathonDemo --frames 0-30 ...` succeeds — proves the gold-standard composition compiles and renders against the post-extraction tree (AC-US1-05).

---

## 4. `globals.css` token-sync diff

Exact before/after for every modified line in `src/app/globals.css`.

### 4.1 `:root` block

```diff
   --bg: #FFFFFF;
-  --bg-code: #111111;
+  --bg-code: #1a1a1a;
   /* `--bg-shiki` is ... */
```

```diff
-  --code-green: #4ADE80;
+  --code-green: #22c55e;
   --code-red: #F87171;
```

```diff
-  --accent-cyan: #0891B2;
+  --accent-cyan: #06b6d4;
   --accent-cyan-bg: #ECFEFF;
   --accent-cyan-border: #A5F3FC;
   --accent-cyan-on: #FFFFFF;
+  --accent-purple: #a855f7;
+  --accent-purple-bg: #F5F0FE;
+  --accent-purple-border: #DDD0FA;
+  --accent-purple-on: #FFFFFF;
```

### 4.2 `[data-theme="dark"]` block

```diff
-  --bg-code: #161B22;
+  --bg-code: #1a1a1a;
   --bg-shiki: #161B22;
```

```diff
-  --code-green: #3FB950;
+  --code-green: #22c55e;
   --code-red: #F85149;
```

```diff
-  --accent-cyan: #22D3EE;
+  --accent-cyan: #06b6d4;
   --accent-cyan-bg: rgba(34, 211, 238, 0.10);
   --accent-cyan-border: rgba(34, 211, 238, 0.32);
   --accent-cyan-on: #0D1117;
+  --accent-purple: #a855f7;
+  --accent-purple-bg: rgba(168, 85, 247, 0.10);
+  --accent-purple-border: rgba(168, 85, 247, 0.32);
+  --accent-purple-on: #0D1117;
```

**Why also keep the cyan `-bg`/`-border`/`-on` siblings unchanged?** Intentional. The `-bg`/`-border` tints were tuned for the prior cyan and provide background washes still visually correct for buttons/chips. Touching them risks contrast-token regressions in surfaces like `.tier-card` (globals.css ~line 849). Spec AC-US2-07 explicitly requires the existing `color-mix` rules to re-validate; leaving the tint tokens unchanged minimizes blast radius. INC-B/C/D can revisit per-component if needed.

**Why the 4 new `--accent-purple-*` tokens?** Symmetry — every other accent (cyan, red, amber, teal) ships as a 4-token group. Purple at parity prevents future "accent-purple-bg doesn't exist" wrongness when consumers reach for it.

### 4.3 Net byte change

`+8 lines × ~30 bytes = ~240 bytes` for the new purple group.
`±0 lines net` from the cyan/green/bg-code value swaps (in-place edits).
**Net diff: ~+240 bytes.** Brotli-compressed: ~+80 bytes. Negligible.

### 4.4 Snapshot test (AC-US2-05)

New file `src/app/__tests__/globals-token-sync.test.ts`:

```ts
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const CSS = readFileSync("src/app/globals.css", "utf8");

const CANONICAL = {
  "--accent-cyan":   "#06b6d4",
  "--code-green":    "#22c55e",
  "--bg-code":       "#1a1a1a",
  "--accent-purple": "#a855f7",
};

function rule(selector: string): string {
  // crude — capture from `<selector> {` until first `}`
  const re = new RegExp(`${selector.replace(/[.[\]"\\]/g, "\\$&")}\\s*\\{([^}]+)\\}`);
  const m = CSS.match(re);
  if (!m) throw new Error(`no rule for ${selector}`);
  return m[1];
}

describe("globals.css canonical brand tokens (AC-US2-01..04)", () => {
  for (const [token, hex] of Object.entries(CANONICAL)) {
    it(`:root has ${token}: ${hex}`, () => {
      expect(rule(":root")).toMatch(new RegExp(`${token}\\s*:\\s*${hex}\\b`, "i"));
    });
    it(`[data-theme="dark"] has ${token}: ${hex}`, () => {
      expect(rule(`\\[data-theme="dark"\\]`)).toMatch(
        new RegExp(`${token}\\s*:\\s*${hex}\\b`, "i"),
      );
    });
  }
});
```

If `vitest.config.ts` does not currently include `src/app/**/__tests__/**`, add it (one-line edit). The repo already collects `src/lib/learn/__tests__/` so the convention exists.

---

## 5. `scripts/generate-voiceover.mjs` — design

### 5.1 Source-of-truth choice (script.ts location)

**Decision**: read from `src/remotion/scenes/<video-name>/script.ts`, NOT `scripts/<video-name>/script.ts`.

**Justification**:
1. The hackathon precedent already lives at `src/remotion/scenes/hackathon/script.ts` — the script is consumed by both the voiceover generator AND the composition (`HackathonDemo.tsx:9-13` imports from there). Splitting them creates a two-source-of-truth problem.
2. `script.ts` exports a typed `<NAME>_SCRIPT` array consumed at composition build time. Moving it to `scripts/` would force a tsx transpile step from inside `src/`.
3. The voiceover script regex-parses the file as text — it does not care about tsconfig paths. Source location is operationally irrelevant; the only constraint is "PM/Architect/Planner agents always know where to put it." Co-located with the composition is the obvious answer.

Hackathon-specific edge: `src/remotion/scenes/hackathon/script.ts` lives at `<scene-dir> = "hackathon"` but the video output directory is `public/hackathon-demo/`. To preserve the existing path, `<video-name>` parameter accepts the OUTPUT slug (e.g. `hackathon-demo`), and the script resolves source via a small map:

```js
const VIDEO_SOURCES = {
  "hackathon-demo": "src/remotion/scenes/hackathon/script.ts",
  // Default convention for new videos:
  //   "<slug>" → "src/remotion/scenes/<slug>/script.ts"
};

function resolveScriptPath(videoName) {
  if (VIDEO_SOURCES[videoName]) {
    return resolve(PROJECT_ROOT, VIDEO_SOURCES[videoName]);
  }
  return resolve(PROJECT_ROOT, `src/remotion/scenes/${videoName}/script.ts`);
}
```

Output always at `public/<video-name>/voiceover-raw.mp3` (no map needed).

### 5.2 CLI surface

```
node scripts/generate-voiceover.mjs <video-name> [--voice <sarah|rachel|anton>]

Examples:
  node scripts/generate-voiceover.mjs hackathon-demo               # Sarah default
  node scripts/generate-voiceover.mjs hackathon-demo --voice anton
  node scripts/generate-voiceover.mjs studio-tour                  # NEW video
```

`<video-name>` is positional and **required**. If omitted, exit code 1 with usage:

```
Usage: node scripts/generate-voiceover.mjs <video-name> [--voice <sarah|rachel|anton>]
       Default voice: sarah (EXAVITQu4vr4xnSDxMaL)
```

### 5.3 Error handling (AC-US3-04)

| Failure mode                          | Exit code | Message |
|---------------------------------------|-----------|---------|
| Missing `<video-name>` arg            | 1         | `Usage: ...` to stderr |
| Unknown `--voice` value               | 1         | `Unknown voice "..."  Use one of: sarah, rachel, anton` |
| Resolved `script.ts` does not exist   | 1         | `ERROR: script not found at <abs path>. Create it following the script-as-data pattern (see ADR 0810-01).` |
| `ELEVENLABS_API_KEY` env var missing  | 1         | `ERROR: ELEVENLABS_API_KEY env var is required.` (legacy message preserved) |
| `extractVoiceText()` returns `[]`     | 1         | `ERROR: Could not extract any voiceText from <abs path>.` (legacy preserved) |
| ElevenLabs HTTP non-2xx               | 2         | `[elevenlabs] HTTP <status>: <body[:500]>` |
| Output MP3 < 50 KB                    | 3         | `[done] WARN: file size <50KB — likely silent/corrupt` (legacy gate preserved) |
| Uncaught error                        | 99        | `err.stack` |

Identical exit codes to the legacy script except for the two new "missing video-name" / "missing script.ts" cases. AC-US3-04 satisfied.

### 5.4 Backwards-compat (AC-US3-05)

**Choice**: delete `scripts/generate-hackathon-voiceover.mjs`, add a `package.json` alias.

```json
"scripts": {
  ...
  "video:voiceover":           "node scripts/generate-voiceover.mjs",
  "video:voiceover:hackathon": "node scripts/generate-voiceover.mjs hackathon-demo"
}
```

Rejected alternative: leave the old filename as a 3-line shim. Reason: file proliferation. The npm-scripts indirection IS the canonical "stable interface" — anyone calling `npm run video:voiceover:hackathon` keeps working; anyone calling the old `.mjs` path directly was internal and is updated in the same PR. Documented in the ADR.

### 5.5 Voice-ID provenance

`EXAVITQu4vr4xnSDxMaL` (Sarah) is **already** in `scripts/generate-hackathon-voiceover.mjs:33` and `src/remotion/scenes/hackathon/script.ts:217` (`HACKATHON_VOICE.primary`). No new lookup needed; no runtime API call to ElevenLabs to fetch voice metadata. **Risk**: ElevenLabs could deprecate Sarah's voice ID server-side (rare; voice IDs are persistent per their API contract). Mitigation: if a future render returns 404, the existing exit-code-2 handler logs the body — easily diagnosable.

---

## 6. `package.json` render-script additions

Add to the `scripts` block (additive — no removals):

```json
"video:voiceover":              "node scripts/generate-voiceover.mjs",
"video:voiceover:hackathon":    "node scripts/generate-voiceover.mjs hackathon-demo",

"video:render:hackathon":       "npx remotion render src/remotion/index.ts HackathonDemo --codec=h264 --crf=23 public/video/hackathon-demo.mp4",
"video:render:hackathon:webm":  "npx remotion render src/remotion/index.ts HackathonDemo --codec=vp8 --crf=30 public/video/hackathon-demo.webm",

"video:render:learn:getting-started":     "npx remotion render src/remotion/index.ts Learn101TitleCard --codec=h264 --crf=23 public/video/learn/getting-started-101.mp4",
"video:render:learn:cli-commands":        "npx remotion render src/remotion/index.ts Learn101SpecWeave --codec=h264 --crf=23 public/video/learn/cli-commands-101.mp4",
"video:render:learn:security-scan":       "npx remotion render src/remotion/index.ts Learn101Security --codec=h264 --crf=23 public/video/learn/security-scan-101.mp4",
"video:render:learn:plugin-marketplace":  "npx remotion render src/remotion/index.ts Learn101Plugins --codec=h264 --crf=23 public/video/learn/plugin-marketplace-101.mp4"
```

The 4 Learn101 entries map to the 4 currently-published-but-broken /learn videos identified in the master plan. They ship in INC-A as **scripts only** (capability) — actual rendering happens in INC-C. AC-US3-06 satisfied.

The composition IDs (`Learn101TitleCard`, `Learn101Plugins`, `Learn101SpecWeave`, `Learn101Security`) are reused from `Root.tsx:50-81` — no new compositions registered in this increment. INC-C will register fully-named per-video compositions and update the script paths.

---

## 7. ADR — `0810-01-video-pipeline-and-token-sync.md`

Path: `.specweave/docs/internal/architecture/adr/0810-01-video-pipeline-and-token-sync.md` (umbrella, NOT child repo). Status `Accepted`, dated `2026-04-30`. The architect agent writes this file alongside plan.md.

Summary of decisions captured (see ADR for full text):
1. **Module boundary** — `src/remotion/scene-kit/` with 12-export contract.
2. **Canonical-color rule** — `BRAND_COLORS` in `tokens.ts` is source-of-truth; `globals.css` mirrors. Four mappings: `--accent-cyan: #06b6d4`, `--code-green: #22c55e`, `--bg-code: #1a1a1a`, `--accent-purple: #a855f7`.
3. **Script-as-data pattern** — every video has `src/remotion/scenes/<slug>/script.ts` exporting a typed scene array.
4. **Sarah-default voiceover** — `EXAVITQu4vr4xnSDxMaL`, model `eleven_v3`, `voice_settings { stability: 0.5, similarity_boost: 0.75, style: 0.3, use_speaker_boost: true }`.

---

## 8. Risk matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `globals.css` cyan/green change cascades to hardcoded `#0891B2`/`#4ADE80`/`#22D3EE`/`#3FB950` literals across the website | Medium | Visual drift on small components | Pre-edit grep: `grep -rn '0891B2\|4ADE80\|22D3EE\|3FB950' src/app/`. Any usages found → file an INC-A follow-up task to convert to `var(--accent-cyan)`/`var(--code-green)`. Document the grep result in plan execution log. |
| Re-export shim is forgotten on a primitive → existing scene file fails to compile | Low | Build break | `npx tsc --noEmit` gate in CI catches it. Task plan mandates "create 5 shim files BEFORE the move task is marked complete." |
| Sarah voice ID changes server-side → 404 from ElevenLabs | Very low | Voiceover render fails | Existing exit-code-2 handler logs the body. Trivial to diagnose; voice IDs are persistent per ElevenLabs contract. |
| `BRAND_COLORS.cyan` import in scene-kit drifts from globals.css `--accent-cyan` over time (someone updates one but not both) | Medium (long-term) | Brand drift returns | Token-sync snapshot test (§4.4) AND `tokens.test.ts` (AC-US1-06) catch the two directions. ADR Consequences section codifies the rule: any PR changing one MUST change both — enforced via PR-review checklist. |
| `uiTokens.ts` shim at old hackathon path is forgotten → 12 hackathon scene files break | Low | Build break | Task couples the move with the shim creation; tsc gate catches anyway. |
| `npm run video:voiceover:hackathon` produces a different MP3 byte-for-byte than the legacy script (regression) | Low | Re-rendering cost | AC-US3-02 explicitly requires byte-equivalence. The unit test stubs `fetch` and validates the request body matches the legacy `voice_settings`. Manual A/B render in a side branch acts as belt-and-braces. |
| `package.json` Learn101 render scripts target compositions that produce visually-stale output (predates updates) | High (intentional) | Confusing for INC-C | Documented as intentional in §6 above and in the ADR. INC-C will register fresh compositions per video and update the script paths. INC-A only proves render-pipeline plumbing. |
| Test file `src/app/__tests__/globals-token-sync.test.ts` lives outside the existing test-collection pattern | Low | Lint warning / not collected | `vitest.config.ts` may need its `include` array extended (one-line edit). The repo already collects `src/lib/learn/__tests__/` so the convention exists. |
| `BlinkingCursor` extraction from `TerminalFrame.tsx` introduces a regression in scenes using the old terminal | Low | Visual glitch | Smoke-render `HackathonDemo --frames 0-30` covers a TerminalFrame instance. Plus `vitest run` exercises any unit tests already covering TerminalFrame. |

---

## 9. Performance considerations

- **Scene-kit module is build-time only.** Remotion compositions are bundled by `@remotion/cli` for offline render; they are NOT imported by `next.config.ts` or any route. Net browser-bytes shipped to a verified-skill.com visitor: **0**.
- **`globals.css` net change**: ~+240 bytes (uncompressed), ~+80 bytes Brotli. No measurable LCP/FCP impact.
- **`tokens.ts` cold-import cost** in Remotion's bundler: <1 ms. The file exports plain object literals; no IIFE side effects.
- **Re-export shims** (5 components × ~50 bytes + 1 uiTokens shim) are inlined by Remotion's esbuild; no runtime indirection at compose-time.
- **Voiceover script** runs offline as a Node CLI. NOT on the request path — performance is "fast enough" if it returns within 60 s. The existing hackathon script takes ~22 s for the 219-word script; the new generic script has identical wire time.

---

## 10. Implementation order (consumed by Planner / `/sw:do`)

The tasks.md authored by the planner should sequence:

1. **Move `uiTokens.ts`** (`git mv`) + write the shim at the old path. Run `tsc --noEmit`.
2. **Create `src/remotion/scene-kit/{primitives,primitives/_internals,__tests__}/` directories.**
3. **`git mv` the 5 existing primitives** into `scene-kit/primitives/`. Patch their `import { COLORS, FONTS } from "../constants"` → `"../../constants"`. Run `tsc --noEmit`.
4. **Create the 5 backwards-compat shims** at `src/remotion/components/*.tsx`. Run `tsc --noEmit`. Run `npx remotion render … HackathonDemo --frames 0-30`.
5. **Author `tokens.ts`** with `BRAND_COLORS` + re-exports of `STUDIO_LIGHT/VERIFIED_DARK/TERMINAL_UI/HACKATHON_FONTS` from the moved `uiTokens.ts`.
6. **Author `index.ts`** barrel.
7. **Extract `BlinkingCursor`** from `TerminalFrame.tsx` into `_internals/BlinkingCursor.tsx`. Update `TerminalFrame` import.
8. **Author the 7 new primitive files** per §2 specs (CaptionBar, BrowserChrome, TUIFrame, CommandTypewriter using `BlinkingCursor`, PillTag, MetricBar, SkillCard).
9. **Patch `TierBadgeVideo.tsx`** to add a named export for `TIER_CONFIG` (so `SkillCard` can reuse).
10. **Patch `globals.css`** per §4 diffs.
11. **Author `src/app/__tests__/globals-token-sync.test.ts`** per §4.4. Add to `vitest.config.ts` `include` if needed.
12. **Author `tokens.test.ts`** under `scene-kit/__tests__/` per AC-US1-06.
13. **Author `primitives-smoke.test.tsx`** per AC-US1-02.
14. **Rename `scripts/generate-hackathon-voiceover.mjs` → `scripts/generate-voiceover.mjs`** and apply the parameterization per §5.
15. **Author the unit test** stubbing `fetch` per AC-US3-07. New file `scripts/__tests__/generate-voiceover.test.mjs` (or `.test.ts` if scripts/ tests are not currently collected — extend `vitest.config.ts` if needed).
16. **Patch `package.json`** with the 8 new entries per §6.
17. **Update ADR README index** (if `.specweave/docs/internal/architecture/adr/README.md` exists) with a one-line link. ADR file itself is authored by the architect agent in this session — no T-task required.
18. **Verification gates**: `npx tsc --noEmit`, `npx vitest run`, `npx remotion render … HackathonDemo --frames 0-30`, `node scripts/generate-voiceover.mjs hackathon-demo` (requires `ELEVENLABS_API_KEY` — gate skipped with WARN if not set, NOT a build break).

The planner's tasks.md may collapse adjacent tasks (e.g. steps 1–4 into a single "extract primitives" task) per its own task-cap rules, but the dependency order above MUST be preserved.

---

## 11. Open questions deferred to implementation

None. Spec is fully decided; brand colors, voice ID, module boundary, and shim policy are all locked. The implementer can code from this plan without re-reading the master plan.
