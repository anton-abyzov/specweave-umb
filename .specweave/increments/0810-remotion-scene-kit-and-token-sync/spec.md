---
increment: 0810-remotion-scene-kit-and-token-sync
title: >-
  Remotion scene-kit foundation + globals.css token sync + Sarah voiceover
  pipeline
type: feature
priority: P1
status: completed
created: 2026-04-30T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Remotion scene-kit foundation + globals.css token sync + Sarah voiceover pipeline

## Overview

Foundation increment (INC-A of 4) for the verified-skill.com video + docs IA restructure approved in `~/.claude/plans/curried-beaming-summit.md`. This increment delivers the **plumbing only** — no IA changes, no new routes, no user-facing surface changes. Subsequent INC-B (Studio re-render), INC-C (/watch library), and INC-D (docs embeds + cleanup) all consume what this lands.

Three coordinated changes inside `repositories/anton-abyzov/vskill-platform/`:

1. **Extract `src/remotion/scene-kit/`** — lift 5 existing primitives (`TerminalFrame`, `BigText`, `AgentIcon`, `TierBadgeVideo`, `TransitionWipe`) out of `src/remotion/components/` and add 7 new primitives (`CaptionBar`, `BrowserChrome`, `TUIFrame`, `CommandTypewriter`, `PillTag`, `MetricBar`, `SkillCard`). A single `tokens.ts` mirrors `globals.css` brand colors and lifts `STUDIO_LIGHT` / `VERIFIED_DARK` / `TERMINAL_UI` from `src/remotion/scenes/hackathon/uiTokens.ts`. Re-export shims at the old `src/remotion/components/*` paths preserve compat for the existing `SkillStudioDemo`, `PromoVideo`, `HomepageDemo`, and `HackathonDemo` compositions.

2. **Align `src/app/globals.css` to Remotion canonical colors** — `--accent-cyan` flips from `#0891B2` (light) / `#22D3EE` (dark) to a unified `#06b6d4`; `--code-green` flips from `#4ADE80` (light) / `#3FB950` (dark) to `#22c55e`; `--bg-code` flips from `#111111` / `#161B22` to `#1a1a1a`; new `--accent-purple: #a855f7` is added (used by Studio's "Any Model" feature card and matches Remotion `STUDIO_LIGHT.accentPurple`). The four canonical colors then exactly match the Studio page `FEATURES` swatches at `src/app/studio/page.tsx:25-50`.

3. **Generalize the voiceover pipeline** — rename `scripts/generate-hackathon-voiceover.mjs` to `scripts/generate-voiceover.mjs` and parameterize on `<video-name>` so any composition with a sibling `script.ts` (the script-as-data pattern from `src/remotion/scenes/hackathon/script.ts`) can produce its voiceover via one command. Default voice is ElevenLabs **Sarah** (`EXAVITQu4vr4xnSDxMaL`, already in the script's `VOICES` map). Output path becomes `public/<video-name>/voiceover-raw.mp3`. The existing hackathon flow is preserved as a no-arg compatibility path. Add render scripts to `package.json` for `HackathonDemo` and the `Learn101*` compositions (currently only `Promo`, `HomepageDemo`, `SkillStudio` have render scripts).

A new ADR `0810-01-video-pipeline-and-token-sync.md` documents the scene-kit module boundary, the canonical-color rule (Remotion is source-of-truth, CSS mirrors it), the script-as-data pattern, and the Sarah-VO pipeline so future contributors don't drift.

The interview state at `.specweave/state/interview-0810-remotion-scene-kit-and-token-sync.json` covers all six categories (architecture, integrations, ui-ux, performance, security, edge-cases) — deep-interview is bypassed.

## User Stories

### US-001: Scene-kit primitives module (P1)
**Project**: vskill-platform

**As a** Remotion scene developer
**I want** a single `src/remotion/scene-kit/` module that exports every reusable primitive plus shared color tokens
**So that** every new video composes from the same primitives without copy-pasting components or hand-mixing color hex codes scene-by-scene

**Acceptance Criteria**:
- [x] **AC-US1-01**: `src/remotion/scene-kit/index.ts` exists and re-exports the 5 lifted primitives (`TerminalFrame`, `BigText`, `AgentIcon`, `TierBadgeVideo`, `TransitionWipe`) plus the 7 new primitives (`CaptionBar`, `BrowserChrome`, `TUIFrame`, `CommandTypewriter`, `PillTag`, `MetricBar`, `SkillCard`) — exactly 12 named exports, verifiable by `grep -c "^export" src/remotion/scene-kit/index.ts`.
- [x] **AC-US1-02**: Each of the 7 new primitives renders without runtime error inside a Remotion `<Composition>` smoke test and accepts an `accentColor` prop typed from the canonical brand 4-color taxonomy (`green | blue | purple | cyan`).
- [x] **AC-US1-03**: `src/remotion/scene-kit/tokens.ts` exports `BRAND_COLORS` containing exactly `{ green: "#22c55e", blue: "#3b82f6", purple: "#a855f7", cyan: "#06b6d4" }`, plus `STUDIO_LIGHT`, `VERIFIED_DARK`, and `TERMINAL_UI` re-exported from the lifted hackathon `uiTokens.ts`.
- [x] **AC-US1-04**: Backwards-compat re-export shims at `src/remotion/components/{TerminalFrame,BigText,AgentIcon,TierBadgeVideo,TransitionWipe}.tsx` re-export from `scene-kit/` so all existing imports across `SkillStudioDemo.tsx`, `PromoVideo`, `HomepageDemo`, the `Learn101*` scenes, and the `hackathon/` scenes continue to resolve without source changes.
- [x] **AC-US1-05**: `npx remotion render src/remotion/index.ts HackathonDemo --frames 0-30 …` (or the equivalent first-frame snapshot) succeeds against the post-extraction tree, proving no regression in the gold-standard composition.
- [x] **AC-US1-06**: A unit test under `src/remotion/scene-kit/__tests__/` asserts that `tokens.ts` `BRAND_COLORS.cyan` matches the `--accent-cyan` value in `src/app/studio/page.tsx` `FEATURES[3].color` and that the four FEATURES colors exactly equal `Object.values(BRAND_COLORS)`.

---

### US-002: globals.css token sync to Remotion canonical (P1)
**Project**: vskill-platform

**As a** brand owner
**I want** the page CSS color tokens (`--accent-cyan`, `--code-green`, `--bg-code`, plus a new `--accent-purple`) to match the canonical Remotion video colors
**So that** videos visually bleed into the page chrome instead of clashing — no more cyan drift between the inline `<video>` and the surrounding container

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/app/globals.css` `:root` block has `--accent-cyan: #06b6d4` (was `#0891B2`); the `[data-theme="dark"]` block has `--accent-cyan: #06b6d4` (was `#22D3EE`) — both themes resolve to the same canonical cyan.
- [x] **AC-US2-02**: `:root` `--code-green: #22c55e` (was `#4ADE80`); `[data-theme="dark"]` `--code-green: #22c55e` (was `#3FB950`).
- [x] **AC-US2-03**: `:root` `--bg-code: #1a1a1a` (was `#111111`); `[data-theme="dark"]` `--bg-code: #1a1a1a` (was `#161B22`).
- [x] **AC-US2-04**: A new token `--accent-purple: #a855f7` is added to both `:root` and `[data-theme="dark"]` blocks, matching `STUDIO_LIGHT.accentPurple` semantics in Remotion (used for AI-Assisted / Generate / Any-Model surfaces).
- [x] **AC-US2-05**: A Vitest snapshot test parses `globals.css` and asserts the four canonical values above are present in BOTH `:root` and `[data-theme="dark"]` blocks; the test fails the build if either block drifts.
- [x] **AC-US2-06**: Visual smoke check via `npm run dev` + Claude Preview MCP: the `/studio` page's four `FEATURES` swatches (`#22c55e`, `#3b82f6`, `#a855f7`, `#06b6d4`) and the four CSS tokens render as the same colors when sampled in DevTools — no perceptible drift.
- [x] **AC-US2-07**: All downstream tier-card / status-token rules that currently `color-mix()` against `--code-green` or `--accent-cyan` (lines 849, 851, 964, 1066, 1083, 1066-1068 in globals.css) continue to render without contrast regressions — verified by re-running the existing Track E tier-card visual snapshot tests.

---

### US-003: Generic Sarah-voice voiceover pipeline (P1)
**Project**: vskill-platform

**As a** video producer
**I want** a single command `node scripts/generate-voiceover.mjs <video-name>` (with ElevenLabs Sarah as the default voice) that reads `src/remotion/scenes/<video-name>/script.ts` and writes `public/<video-name>/voiceover-raw.mp3`
**So that** any new video composition can produce its voiceover with one command — no hardcoded paths, no per-video scripts to maintain

**Acceptance Criteria**:
- [x] **AC-US3-01**: `scripts/generate-voiceover.mjs` exists (renamed from `generate-hackathon-voiceover.mjs`) and accepts a positional `<video-name>` argument plus an optional `--voice <sarah|rachel|anton>` flag, defaulting to `sarah` (voice ID `EXAVITQu4vr4xnSDxMaL`, model `eleven_v3`).
- [x] **AC-US3-02**: `node scripts/generate-voiceover.mjs hackathon-demo` reads `src/remotion/scenes/hackathon/script.ts`, extracts every `voiceText` field via the existing parser, joins with `\n\n`, POSTs to ElevenLabs, and writes `public/hackathon-demo/voiceover-raw.mp3` — byte-for-byte equivalent to the legacy `generate-hackathon-voiceover.mjs` output (same voice, same model, same `voice_settings`).
- [x] **AC-US3-03**: For an arbitrary `<video-name>`, the script resolves the source at `src/remotion/scenes/<video-name>/script.ts` and writes to `public/<video-name>/voiceover-raw.mp3`; the output directory is created with `mkdirSync({ recursive: true })` if missing.
- [x] **AC-US3-04**: If `src/remotion/scenes/<video-name>/script.ts` does not exist, the script exits with code 1 and a human-readable error naming the resolved path; if `ELEVENLABS_API_KEY` is missing, exit code 1 with the same legacy "ELEVENLABS_API_KEY env var is required" message.
- [x] **AC-US3-05**: A backwards-compat shim `scripts/generate-hackathon-voiceover.mjs` is left in place that simply `import`s and runs the new script with `hackathon-demo` hardcoded (so any external doc or CI step referencing the old path keeps working); OR the old filename is deleted and the shim is replaced by an entry in `package.json` `scripts` aliased to the new command — pick one and document in the ADR.
- [x] **AC-US3-06**: `package.json` `scripts` block adds `video:voiceover` (calls the new script with positional arg from npm `--`) and adds render entries for the existing `HackathonDemo` composition (`video:render:hackathon` mp4 + webm) and the four `Learn101*` compositions referenced in the master plan (`getting-started-101`, `cli-commands-101`, `security-scan-101`, `plugin-marketplace-101`); each render targets `public/video/learn/<slug>.mp4` and `.webm` so INC-C can wire them straight into the catalog.
- [x] **AC-US3-07**: A unit test stubs `fetch` and asserts that for `<video-name> = "hackathon-demo"` the POST URL contains `EXAVITQu4vr4xnSDxMaL`, the request body's `model_id` is `eleven_v3`, and `voice_settings` matches the legacy `{ stability: 0.5, similarity_boost: 0.75, style: 0.3, use_speaker_boost: true }`.

---

### US-004: Architecture Decision Record for the video pipeline + token sync (P2)
**Project**: vskill-platform

**As a** future contributor
**I want** an ADR explaining the scene-kit module boundary, the canonical-color rule (Remotion is source-of-truth, CSS mirrors it), the script-as-data pattern, and the Sarah-voiceover pipeline
**So that** the architectural intent isn't lost when the hackathon-demo context fades and someone is tempted to re-introduce per-scene hex codes or per-video VO scripts

**Acceptance Criteria**:
- [x] **AC-US4-01**: A new ADR file exists at `.specweave/docs/internal/architecture/adr/0810-01-video-pipeline-and-token-sync.md` (umbrella `.specweave/`, NOT inside the `vskill-platform/` child repo, per umbrella-mode rules).
- [x] **AC-US4-02**: The ADR uses the standard SpecWeave ADR format with sections: `# Status`, `# Context`, `# Decision`, `# Consequences`, `# Alternatives Considered`. Status is `Accepted` and dated `2026-04-30`.
- [x] **AC-US4-03**: The Decision section explicitly documents (a) the `src/remotion/scene-kit/` module boundary and the 12-export contract, (b) the rule that Remotion `BRAND_COLORS` is canonical and `globals.css` mirrors it (with the four token mappings spelled out: `--accent-cyan #06b6d4`, `--code-green #22c55e`, `--bg-code #1a1a1a`, `--accent-purple #a855f7`), (c) the script-as-data pattern (every `src/remotion/scenes/<video-name>/script.ts` exports a `<NAME>_SCRIPT` array of `{ id, durationFrames, transitionType, voiceText, caption?, visualNotes }`), and (d) the Sarah-voiceover default with the ElevenLabs voice ID `EXAVITQu4vr4xnSDxMaL` and model `eleven_v3`.
- [x] **AC-US4-04**: The Consequences section names INC-B / INC-C / INC-D as the immediate consumers and notes that any future video added MUST land its script.ts + render-script entry + Sarah-voiceover invocation, not bespoke alternatives.
- [x] **AC-US4-05**: The Alternatives Considered section briefly addresses (and rejects with a one-line reason): keeping per-scene `COLORS` constants, forking `generate-hackathon-voiceover.mjs` per video, and inlining text-to-speech inside Remotion compositions.
- [x] **AC-US4-06**: The ADR is linked from a one-line addition to the closest existing index (`.specweave/docs/internal/architecture/adr/README.md` if present, otherwise the new ADR's existence is recorded in the increment's plan.md by the architect).

## Functional Requirements

### FR-001: Backwards-compatible re-export shims
The 5 lifted primitives MUST remain importable from their old `src/remotion/components/<Name>.tsx` paths via thin re-export files. Existing compositions and tests are NOT modified in this increment.

### FR-002: Single source of truth for brand colors
After this increment, the four brand hex codes (`#22c55e`, `#3b82f6`, `#a855f7`, `#06b6d4`) appear in exactly two places: `src/remotion/scene-kit/tokens.ts` (canonical) and `src/app/globals.css` (mirror). All other usages (Studio FEATURES array, scene component props) reference one of those two via import or `var(--…)`.

### FR-003: Script-as-data contract
Every new video lives under `src/remotion/scenes/<video-name>/` with a sibling `script.ts` that exports a typed array following the shape established in `src/remotion/scenes/hackathon/script.ts` (`{ id, durationFrames, transitionType, voiceText, caption?, visualNotes }`). The voiceover script consumes this contract.

### FR-004: Sarah is the default voice
ElevenLabs Sarah (`EXAVITQu4vr4xnSDxMaL`, `eleven_v3`) is the default for every `generate-voiceover.mjs` invocation. Other voices remain selectable via `--voice` for A/B but are never the default.

## Success Criteria

- All 12 scene-kit exports importable; 0 broken imports in the existing compositions tree (verified by `tsc --noEmit`).
- `globals.css` post-edit produces zero diff in any existing visual snapshot test that does NOT depend on the four changed token values; the four intentional drifts are documented in the snapshot updates.
- `node scripts/generate-voiceover.mjs hackathon-demo` produces a Sarah-voiced MP3 ≥50KB with non-zero ffprobe duration — same gate as the legacy script's `<50KB → exit 3` warning.
- Vitest unit suite passes; existing Playwright E2E suite passes (no UI changes shipped, so no E2E additions required in this increment).
- ADR file lints clean against the SpecWeave ADR validator.

## Out of Scope

This increment is **foundation only**. Explicitly NOT in scope:

- **No video re-rendering** — INC-B re-renders `/studio`; INC-C renders the `/watch` library MP4s. This increment only creates the *capability* to render via the new render scripts, it does not run them.
- **No /watch IA changes** — the rename of `src/app/learn/` to `src/app/watch/`, the `next.config.ts` 301 redirects, the global nav addition, and the sitemap edit are all INC-C.
- **No inline `/docs` video embeds** — the `<DocVideoEmbed>` server component and the per-page video embeds are INC-D.
- **No deletion of dead code** — `VideoHero.tsx`, the orphan `ship-while-you-sleep.mp4`, and the `specweave-promo.{mp4,webm}` files are INC-D's responsibility.
- **No `/docs/studio` section creation** — that's INC-B (paired with the Studio re-render).
- **No public-facing UI surface change** — by design, no user visiting verified-skill.com sees anything different after this increment ships. The only observable diffs are in `globals.css` token values (which downstream components inherit but the visible output is sub-perceptual until INC-B/C/D consume it) and in build-time tooling (`scripts/`, `package.json`).
- **No changes to `src/remotion/SkillStudioDemo.tsx`, `Root.tsx`, or any composition source file** — only the import paths change *implicitly* via the re-export shims, source files are untouched.
- **No `<DocVideoEmbed>` component, no `WatchVideoPlayer`, no `VideoPlayer.tsx` changes** — INC-B/C/D each touch one of these.

## Dependencies

- **Blocks**: INC-B (`/studio` re-render + `/docs/studio` section), INC-C (`/watch` library), INC-D (`/docs` embeds + cleanup). All three depend on the scene-kit module, the canonical token sync, and the generic voiceover script landing here first.
- **Approved master plan**: `~/.claude/plans/curried-beaming-summit.md` (read by the PM/Architect/Planner agents before they write spec/plan/tasks).
- **Locked brand decisions**: user memory `project_video_brand_decisions_2026_04.md` (Sarah VO universal, Studio Remotion colors are source-of-truth).
- **Reusable assets** (not modified in this increment, just relied on): `public/hackathon-demo/bgm.mp3` (Skybound BGM bed for future videos), `src/remotion/scenes/hackathon/script.ts` (script-as-data template), `src/remotion/scenes/hackathon/uiTokens.ts` (lifted into scene-kit).
- **External**: ElevenLabs API (key in `.env` as `ELEVENLABS_API_KEY`, already wired for the legacy hackathon script).
