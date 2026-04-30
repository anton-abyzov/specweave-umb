---
increment: 0810-remotion-scene-kit-and-token-sync
title: "Remotion scene-kit foundation + globals.css token sync + Sarah voiceover pipeline"
tasks_version: 1
---

# Tasks — 0810-remotion-scene-kit-and-token-sync

Working tree: `repositories/anton-abyzov/vskill-platform/`

---

### T-001: Move uiTokens.ts + create scene-kit directory structure
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] completed

Move `src/remotion/scenes/hackathon/uiTokens.ts` to `src/remotion/scene-kit/uiTokens.ts` via `git mv`. Replace the original path with a one-line re-export shim (`export * from "../../scene-kit/uiTokens"`). Create directories: `src/remotion/scene-kit/primitives/`, `src/remotion/scene-kit/primitives/_internals/`, `src/remotion/scene-kit/__tests__/`. Run `npx tsc --noEmit` → must exit 0.

**Test Plan** (BDD):
- Given: `src/remotion/scenes/hackathon/uiTokens.ts` exists exporting `STUDIO_LIGHT`, `VERIFIED_DARK`, `TERMINAL_UI`, `HACKATHON_FONTS`
- When: file is moved via `git mv` to `src/remotion/scene-kit/uiTokens.ts` and a shim is written at the original path
- Then: `npx tsc --noEmit` exits 0; all hackathon scene files that `import { STUDIO_LIGHT } from "./uiTokens"` continue to resolve without modification; `STUDIO_LIGHT`, `VERIFIED_DARK`, `TERMINAL_UI`, `HACKATHON_FONTS` are importable from the original path via the shim.

---

### T-002: Move 5 existing primitives into scene-kit/primitives/ + patch import paths
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] completed

`git mv` five files from `src/remotion/components/` → `src/remotion/scene-kit/primitives/`:
`TerminalFrame.tsx`, `BigText.tsx`, `AgentIcon.tsx`, `TierBadgeVideo.tsx`, `TransitionWipe.tsx`.

Inside each moved file: patch `import { COLORS, FONTS } from "../constants"` → `"../../constants"` (5 one-line edits). Run `npx tsc --noEmit`.

**Test Plan** (BDD):
- Given: five primitives live at `src/remotion/components/` importing `../constants`
- When: files are moved to `src/remotion/scene-kit/primitives/` and each relative import is updated to `../../constants`
- Then: `npx tsc --noEmit` exits 0; importing any primitive from `scene-kit/primitives/<Name>` resolves correctly at the TypeScript level.

---

### T-003: Create backwards-compat re-export shims at old component paths + verify HackathonDemo render
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [x] completed

Create five 1-line re-export shim files at the OLD `src/remotion/components/` paths:
- `TerminalFrame.tsx` → `export { TerminalFrame } from "../scene-kit/primitives/TerminalFrame";`
- `BigText.tsx` → `export { BigText } from "../scene-kit/primitives/BigText";`
- `AgentIcon.tsx` → `export { AgentIcon } from "../scene-kit/primitives/AgentIcon";`
- `TierBadgeVideo.tsx` → `export { TierBadgeVideo } from "../scene-kit/primitives/TierBadgeVideo";`
- `TransitionWipe.tsx` → `export { TransitionWipe } from "../scene-kit/primitives/TransitionWipe";`

Run `npx tsc --noEmit` → 0 errors. Then `npx remotion render src/remotion/index.ts HackathonDemo --frames 0-30` → exits 0.

**Test Plan** (BDD):
- Given: five primitives are at `scene-kit/primitives/` (from T-002), old `src/remotion/components/` paths have no files
- When: five 1-line shim files are written at the old paths
- Then: `npx tsc --noEmit` exits 0; `SkillStudioDemo.tsx`, `PromoVideo`, `HomepageDemo`, hackathon scenes, `CLIShowcase.tsx`, learn scenes, and their `__tests__` all resolve primitive imports without any source modification (zero scene files changed); `npx remotion render … HackathonDemo --frames 0-30` exits 0.

---

### T-004: Author tokens.ts + scene-kit barrel index.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03
**Status**: [x] completed

Create `src/remotion/scene-kit/tokens.ts`:
```ts
export const BRAND_COLORS = { green: "#22c55e", blue: "#3b82f6", purple: "#a855f7", cyan: "#06b6d4" } as const;
export type BrandColorKey = keyof typeof BRAND_COLORS;
export type AccentColor = (typeof BRAND_COLORS)[BrandColorKey];
export { STUDIO_LIGHT, VERIFIED_DARK, TERMINAL_UI, HACKATHON_FONTS } from "./uiTokens";
```

Create `src/remotion/scene-kit/index.ts` barrel re-exporting all 12 named component exports (5 lifted + 7 new) plus token/type re-exports per plan §1.2. Note: 7 new primitives don't exist until T-005–T-008; `tsc` over the barrel is run green after T-008 completes.

**Test Plan** (BDD):
- Given: `tokens.ts` is authored and `index.ts` barrel references all 12 components
- When: after T-008 all new primitives exist and `grep -c "^export" src/remotion/scene-kit/index.ts` is run
- Then: count equals 12 (component exports); `BRAND_COLORS.green === "#22c55e"`, `BRAND_COLORS.cyan === "#06b6d4"`, `BRAND_COLORS.purple === "#a855f7"`, `BRAND_COLORS.blue === "#3b82f6"`; `STUDIO_LIGHT`, `VERIFIED_DARK`, `TERMINAL_UI`, `HACKATHON_FONTS` importable from `scene-kit/tokens`.

---

### T-005: Extract BlinkingCursor + add TIER_CONFIG named export from TierBadgeVideo
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] completed

Extract blinking-cursor logic from `src/remotion/scene-kit/primitives/TerminalFrame.tsx` into a new `src/remotion/scene-kit/primitives/_internals/BlinkingCursor.tsx`. Update `TerminalFrame.tsx` to import from `./_internals/BlinkingCursor`.

Add a named `export const TIER_CONFIG` to `src/remotion/scene-kit/primitives/TierBadgeVideo.tsx` so `SkillCard` (T-008) can import without duplication.

Run `npx tsc --noEmit`.

**Test Plan** (BDD):
- Given: `TerminalFrame.tsx` contains inline blinking-cursor logic; `TierBadgeVideo.tsx` defines but does not export `TIER_CONFIG`
- When: `BlinkingCursor` is extracted to `_internals/` and `TierBadgeVideo.tsx` gains `export const TIER_CONFIG`
- Then: `npx tsc --noEmit` exits 0; `TerminalFrame` renders identically (verified by HackathonDemo smoke run in T-003); `SkillCard` in T-008 can `import { TIER_CONFIG } from "./TierBadgeVideo"` without duplication.

---

### T-006: Implement CaptionBar + PillTag primitives
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] completed

Create `src/remotion/scene-kit/primitives/CaptionBar.tsx`:
- Props: `text`, `accentColor?: AccentColor` (default `BRAND_COLORS.cyan`), `position?: "bottom"|"top"`, `fontSize?: number`, `delay?: number`
- Spring-in opacity + translateY (`damping: 200`); `rgba(0,0,0,0.78)` bg; `accentColor` drives 3px top border + text shadow

Create `src/remotion/scene-kit/primitives/PillTag.tsx`:
- Props: `label`, `accentColor: AccentColor` (required), `size?: "sm"|"md"|"lg"`, `delay?: number`
- 1px border + 6px circular swatch in `accentColor`; spring-in scale 0.9→1.0 + opacity over ~12 frames

**Test Plan** (BDD):
- Given: `CaptionBar` and `PillTag` are authored per plan §2.1 and §2.5
- When: `primitives-smoke.test.tsx` renders both inside a Remotion `<Composition>` mock at frame 15
- Then: no runtime error; `CaptionBar` with `accentColor="cyan"` renders a wrapper with `backgroundColor` matching `rgba(0,0,0,0.78)`; `PillTag` with `accentColor="green"` renders a swatch element with color `#22c55e`.

---

### T-007: Implement CommandTypewriter + TUIFrame primitives
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] completed

Create `src/remotion/scene-kit/primitives/CommandTypewriter.tsx`:
- Props: `command`, `charSpeed?` (default 2), `prefix?` (default `"$ "`), `delay?`, `onCompleteFrame?`, `fontSize?`, `accentColor?` (default `BRAND_COLORS.green`)
- Reuses `_internals/BlinkingCursor` (T-005); `accentColor` colors the prefix; typed text uses `TERMINAL_UI.text`

Create `src/remotion/scene-kit/primitives/TUIFrame.tsx`:
- Props: `bannerTitle?` (default `"Claude Code"`), `bannerSubtitle?`, `children`, `width?`
- Composes `<TerminalFrame>` with a terra-cotta banner row above using `TERMINAL_UI` tokens; no `accentColor` prop

**Test Plan** (BDD):
- Given: `CommandTypewriter` and `TUIFrame` are authored per plan §2.4 and §2.3
- When: smoke test renders `<CommandTypewriter command="vskill install" charSpeed={2} />` at frame 20
- Then: no runtime error; rendered text includes a substring of `"vskill install"` of length `Math.floor(20 / 2) = 10`; `TUIFrame` wraps `TerminalFrame` and renders a banner element containing the `bannerTitle` text.

---

### T-008: Implement BrowserChrome + MetricBar + SkillCard primitives; run tsc gate
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

Create `src/remotion/scene-kit/primitives/BrowserChrome.tsx`:
- Props: `url`, `width?`, `height?`, `children`, `accentColor?`
- Traffic lights from `TERMINAL_UI.dotRed/dotYellow/dotGreen`; frame border `#262626`, address-bar bg `#1a1a1a`; no CSS dependency

Create `src/remotion/scene-kit/primitives/MetricBar.tsx`:
- Props: `label`, `value` (0–100), `accentColor?` (default `green`), `width?`, `height?`, `delay?`, `durationFrames?` (default 30)
- `interpolate(frame, [delay, delay+durationFrames], [0, value], { easing: Easing.out(Easing.cubic) })`

Create `src/remotion/scene-kit/primitives/SkillCard.tsx`:
- Props: `name`, `publisher`, `tier`, `description?`, `width?`, `delay?`, `accentColor?`
- Imports `TIER_CONFIG` from `./TierBadgeVideo` (T-005); uses `STUDIO_LIGHT` tokens

After all 7 new primitives exist: run `npx tsc --noEmit` (barrel from T-004 now fully resolves). Confirm `grep -c "^export" src/remotion/scene-kit/index.ts` → 12.

**Test Plan** (BDD):
- Given: all 7 new primitives are authored; `index.ts` barrel references all 12 components
- When: `grep -c "^export" src/remotion/scene-kit/index.ts` and `npx tsc --noEmit` run
- Then: grep == 12; `tsc` exits 0; smoke test renders each of the 3 new primitives without error; `SkillCard` with `tier="verified"` renders a badge element with color from `TIER_CONFIG["verified"].color` (no value duplication from `TierBadgeVideo`).

---

### T-009: Update src/app/globals.css — 4 token value swaps + 4 new accent-purple tokens
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

Apply in-place edits per plan §4.1 and §4.2.

`:root` block:
- `--bg-code: #111111` → `#1a1a1a`
- `--code-green: #4ADE80` → `#22c55e`
- `--accent-cyan: #0891B2` → `#06b6d4`
- Add after `--accent-cyan-on: #FFFFFF`: `--accent-purple: #a855f7`, `--accent-purple-bg: #F5F0FE`, `--accent-purple-border: #DDD0FA`, `--accent-purple-on: #FFFFFF`

`[data-theme="dark"]` block:
- `--bg-code: #161B22` → `#1a1a1a`
- `--code-green: #3FB950` → `#22c55e`
- `--accent-cyan: #22D3EE` → `#06b6d4`
- Add after `--accent-cyan-on: #0D1117`: `--accent-purple: #a855f7`, `--accent-purple-bg: rgba(168, 85, 247, 0.10)`, `--accent-purple-border: rgba(168, 85, 247, 0.32)`, `--accent-purple-on: #0D1117`

Pre-edit: run `grep -rn '0891B2\|4ADE80\|22D3EE\|3FB950' src/app/` — document any hardcoded literal usages (do NOT change them in this increment; file a follow-up if found).

**Test Plan** (BDD):
- Given: `src/app/globals.css` contains old token values in both `:root` and `[data-theme="dark"]`
- When: the 4 value swaps and 4 new `--accent-purple-*` lines are applied in-place
- Then: `grep -c "accent-cyan: #06b6d4" src/app/globals.css` == 2; `grep -c "code-green: #22c55e" src/app/globals.css` == 2; `grep -c "bg-code: #1a1a1a" src/app/globals.css` == 2; `grep -c "accent-purple: #a855f7" src/app/globals.css` == 2; existing `color-mix()` rules at ~lines 849, 851, 964, 1066, 1083 compile without CSS errors (confirmed in T-015 visual smoke).

---

### T-010: Write globals-token-sync.test.ts — CSS ↔ canonical hexes bidirectional
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05
**Status**: [x] completed

Create `src/app/__tests__/globals-token-sync.test.ts` per plan §4.4. The test reads `src/app/globals.css` via `readFileSync`, parses `:root` and `[data-theme="dark"]` blocks, and asserts all four canonical values (`--accent-cyan: #06b6d4`, `--code-green: #22c55e`, `--bg-code: #1a1a1a`, `--accent-purple: #a855f7`) are present in BOTH blocks. Build fails if either block drifts.

If `vitest.config.ts` `include` array does not cover `src/app/**/__tests__/**`, add one line to extend it.

**Test Plan** (BDD):
- Given: `globals.css` has been updated in T-009 with canonical values; test file is authored
- When: `npx vitest run src/app/__tests__/globals-token-sync.test.ts` executes
- Then: all 8 assertions pass (4 tokens × 2 blocks); running the same test against the unedited CSS (old values) fails with a descriptive message naming the token and selector.

---

### T-011: Write tokens.test.ts — BRAND_COLORS ↔ Studio FEATURES parity
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06
**Status**: [x] completed

Create `src/remotion/scene-kit/__tests__/tokens.test.ts`. The test:
- Imports `BRAND_COLORS` from `../tokens`
- Reads `src/app/studio/page.tsx` as text; extracts `FEATURES` array color values via regex
- Asserts `BRAND_COLORS.cyan` matches `FEATURES[3].color` (the "100% Local" / cyan entry)
- Asserts `Object.values(BRAND_COLORS)` exactly matches the set of 4 FEATURES colors (order-independent set equality)

**Test Plan** (BDD):
- Given: `tokens.ts` exports `BRAND_COLORS`; `src/app/studio/page.tsx` defines a `FEATURES` array with 4 color values
- When: `npx vitest run src/remotion/scene-kit/__tests__/tokens.test.ts` executes
- Then: all assertions pass; setting `BRAND_COLORS.cyan` to a wrong value causes the test to fail with a message showing expected vs actual hex.

---

### T-012: Generalize scripts/generate-voiceover.mjs (rename + parameterize + error handling)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [ ] pending

Rename `scripts/generate-hackathon-voiceover.mjs` → `scripts/generate-voiceover.mjs` via `git mv`. Delete the old file after rename. Apply parameterization per plan §5:

1. Positional `<video-name>` arg required; exit 1 with usage if missing
2. Optional `--voice <sarah|rachel|anton>` flag; default `sarah` (voice ID `EXAVITQu4vr4xnSDxMaL`, model `eleven_v3`); exit 1 for unknown values
3. `VIDEO_SOURCES` map: `{ "hackathon-demo": "src/remotion/scenes/hackathon/script.ts" }`; fallback `src/remotion/scenes/<video-name>/script.ts`
4. Output: `public/<video-name>/voiceover-raw.mp3`; `mkdirSync({ recursive: true })` for missing dirs
5. Error table (exit codes): missing arg → 1; unknown voice → 1; missing script.ts → 1 with path; missing `ELEVENLABS_API_KEY` → 1 legacy message; empty voiceText → 1; HTTP non-2xx → 2; output <50KB → 3 warning

Backwards-compat handled by `package.json` alias in T-013 (not a shim file). Document in a comment near the top of the script.

**Test Plan** (BDD):
- Given: `generate-hackathon-voiceover.mjs` is renamed and parameterized
- When: `node scripts/generate-voiceover.mjs hackathon-demo` is invoked with `ELEVENLABS_API_KEY` set
- Then: reads `src/remotion/scenes/hackathon/script.ts`, POSTs to ElevenLabs with `EXAVITQu4vr4xnSDxMaL` and `eleven_v3`, writes `public/hackathon-demo/voiceover-raw.mp3`; `node scripts/generate-voiceover.mjs unknown-video` exits 1 naming the resolved path; `node scripts/generate-voiceover.mjs` (no args) exits 1 with usage; `node scripts/generate-voiceover.mjs hackathon-demo --voice bad` exits 1.

---

### T-013: Update package.json — add 8 video scripts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06
**Status**: [ ] pending

Add 8 new entries to `package.json` `scripts` block per plan §6:
- `"video:voiceover"`: `"node scripts/generate-voiceover.mjs"`
- `"video:voiceover:hackathon"`: `"node scripts/generate-voiceover.mjs hackathon-demo"`
- `"video:render:hackathon"`: h264 render for HackathonDemo → `public/video/hackathon-demo.mp4`
- `"video:render:hackathon:webm"`: vp8 render → `.webm`
- `"video:render:learn:getting-started"`: Learn101TitleCard → `public/video/learn/getting-started-101.mp4`
- `"video:render:learn:cli-commands"`: Learn101SpecWeave → `public/video/learn/cli-commands-101.mp4`
- `"video:render:learn:security-scan"`: Learn101Security → `public/video/learn/security-scan-101.mp4`
- `"video:render:learn:plugin-marketplace"`: Learn101Plugins → `public/video/learn/plugin-marketplace-101.mp4`

**Test Plan** (BDD):
- Given: `package.json` has existing render scripts for Promo, HomepageDemo, SkillStudio
- When: 8 new entries are added
- Then: `Object.keys(require('./package.json').scripts).filter(k=>k.startsWith('video:')).length` >= 10; `video:voiceover:hackathon` resolves to the new script invocation; all 4 Learn101 composition IDs (`Learn101TitleCard`, `Learn101SpecWeave`, `Learn101Security`, `Learn101Plugins`) exist in `Root.tsx`.

---

### T-014: Write voiceover unit test — fetch stub validates voice_settings shape
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07
**Status**: [ ] pending

Create `scripts/__tests__/generate-voiceover.test.mjs` (or `.test.ts`). The test:
- Stubs global `fetch`
- Calls the script's request-building logic for `video-name = "hackathon-demo"`
- Asserts the POST URL contains `EXAVITQu4vr4xnSDxMaL`
- Asserts request body `model_id === "eleven_v3"`
- Asserts `voice_settings` deeply equals `{ stability: 0.5, similarity_boost: 0.75, style: 0.3, use_speaker_boost: true }`

If `vitest.config.ts` `include` doesn't cover `scripts/**/__tests__/**`, add a one-line extension.

**Test Plan** (BDD):
- Given: `generate-voiceover.mjs` exposes a testable request-building function or the request body can be captured via stubbed `fetch`
- When: `npx vitest run scripts/__tests__/generate-voiceover.test.mjs` executes
- Then: all 3 assertions pass with no real HTTP call to ElevenLabs; changing `voice_settings.stability` to `0.9` causes the test to fail immediately with a diff.

---

### T-015: ADR index update + run all verification gates
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-05, AC-US2-06, AC-US2-07, AC-US4-01, AC-US4-06
**Status**: [ ] pending

Verification-only task — no new source files authored.

1. Confirm ADR exists at `.specweave/docs/internal/architecture/adr/0810-01-video-pipeline-and-token-sync.md`. If `.specweave/docs/internal/architecture/adr/README.md` exists, add a one-line link entry for the ADR.

2. Run in order:
   - `npx tsc --noEmit` → exit 0
   - `npx vitest run` → exit 0; all new tests pass (globals-token-sync, tokens parity, voiceover fetch-stub)
   - `grep -rn '0891B2\|4ADE80\|22D3EE\|3FB950' repositories/anton-abyzov/vskill-platform/src/app/` → document any remaining literals (informational; not a blocker)
   - `npx remotion render src/remotion/index.ts HackathonDemo --frames 0-30` → exits 0
   - `npm run dev` → start dev server; use Claude Preview MCP to load `/studio` page and confirm four FEATURES swatches match DevTools-sampled CSS token values (AC-US2-06)
   - Confirm existing Track E tier-card visual snapshot tests pass with no contrast regressions after `globals.css` edits (AC-US2-07)

**Test Plan** (BDD):
- Given: all T-001 through T-014 tasks are complete
- When: the full verification sequence runs end-to-end
- Then: `tsc` exits 0; `vitest run` exits 0 with all tests passing; HackathonDemo renders frames 0-30 without error; `/studio` page color swatches match canonical hex values; existing tier-card snapshot tests pass unchanged.

---

## Bidirectional AC Coverage

Every AC from spec.md is mapped to at least one task.

| AC | Satisfied by |
|----|--------------|
| AC-US1-01 | T-004 (barrel created), T-008 (12-export count confirmed) |
| AC-US1-02 | T-006 (CaptionBar, PillTag), T-007 (CommandTypewriter, TUIFrame), T-008 (BrowserChrome, MetricBar, SkillCard) |
| AC-US1-03 | T-001 (uiTokens moved), T-004 (tokens.ts with BRAND_COLORS + re-exports) |
| AC-US1-04 | T-002 (move + import patch), T-003 (5 shim files at old component paths) |
| AC-US1-05 | T-003 (first HackathonDemo smoke after shims), T-015 (final verification gate) |
| AC-US1-06 | T-011 (tokens.test.ts — BRAND_COLORS vs FEATURES parity) |
| AC-US2-01 | T-009 (`--accent-cyan: #06b6d4` in both blocks) |
| AC-US2-02 | T-009 (`--code-green: #22c55e` in both blocks) |
| AC-US2-03 | T-009 (`--bg-code: #1a1a1a` in both blocks) |
| AC-US2-04 | T-009 (new `--accent-purple-*` tokens in both blocks) |
| AC-US2-05 | T-010 (globals-token-sync.test.ts) |
| AC-US2-06 | T-015 (dev-server visual smoke via Claude Preview MCP) |
| AC-US2-07 | T-015 (existing tier-card snapshot tests re-run after edits) |
| AC-US3-01 | T-012 (`<video-name>` positional arg + `--voice` flag, default sarah) |
| AC-US3-02 | T-012 (hackathon-demo path preserved, byte-equivalent request body) |
| AC-US3-03 | T-012 (arbitrary video-name fallback path + `mkdirSync`) |
| AC-US3-04 | T-012 (exit codes for missing script.ts and missing API key) |
| AC-US3-05 | T-013 (`video:voiceover:hackathon` npm alias replaces deleted old file) |
| AC-US3-06 | T-013 (8 new `package.json` script entries) |
| AC-US3-07 | T-014 (fetch-stub unit test for voice_settings shape) |
| AC-US4-01 | T-015 (ADR file existence confirmed at umbrella path) |
| AC-US4-02 | Architect (ADR format: Status Accepted, dated 2026-04-30) |
| AC-US4-03 | Architect (Decision section covers all 4 decisions) |
| AC-US4-04 | Architect (Consequences section names INC-B/C/D) |
| AC-US4-05 | Architect (Alternatives Considered section) |
| AC-US4-06 | T-015 (ADR README.md index link if file exists) |
