# Cinematic motion deck: shader transitions, filmic post and a rebuilt demo

## Problem

On November 28, 2026 the owner watched the demo deck "Work that keeps going" (`examples/motion-deck/demo.html`) as an installed app on 1.0.454 and asked for "richer animations and motions, design, graphics, 3D ... like in Claude Code design and in the examples that I've shown you, with the really rich, beautiful styles, graphics, transitions, fonts, colors".

Their screenshot of scene 03 shows the gap: a flat black background, a sparse node graph across the top half, an empty middle and a system-font headline.

The reference, Claude's "The Last Boring Slide" (anatomy in `1499-motion-slide-pages/reports/research-claude-motion-slides.md`), gets its look from authoring technique that our runtime (1499) does not offer:

- full-frame lit worlds: skies, terrain, fields of thousands of instanced tiles;
- a filmic post pass with AgX, halation and chromatic aberration;
- ten distinct shader transitions with scored sound cues;
- a wide display face and per-glyph kinetic type;
- rolling odometer numbers.

Our runtime has three blend transitions (fade, iris, wipe), ACES only, no reusable world helpers and no bundled font, so every author starts from a dark void.

## Scope

In:

- Runtime: a transition registry with at least four new shader transitions and a sound cue each; AgX tone mapping, halation, stronger chromatic aberration and a split-tone grade in the post pass; reusable world helpers (sky, terrain, instanced tile field, light arcs, motes); per-glyph kinetic type presets; a bundled OFL display face.
- An original five-scene demo deck about SpecWithCode: plan, agents in parallel, hand off across machines, review, ship.
- The agent guide (tool descriptions and `docs/studio/motion-pages.md`).
- Tests and headless evidence beside the reference frames.

Out:

- A WebGL text layer, PADsynth audio, shadow maps, SSAO and depth of field. These are follow-ups.
- Copying anything from the reference: no Anthropic code, shaders, fonts, images or text. Technique and behaviour only.

## Acceptance Criteria

- [ ] AC-01: **Transitions.** A scene's `transition` accepts `fade`, `iris`, `wipe` and at least four new shader transitions (`portal`, `flaps`, `curl`, `wash`, `slam`, `tear`, `zoom`). Each new one has its own duration and a synthesized sound cue. An unknown name falls back to `fade`. `SpecWithCodeDeck.transitions` lists them, and authors can register their own GLSL transition.
- [ ] AC-02: **Filmic post.** `post` accepts `tone` (`aces` default, `agx`, `none`), `halation`, `ca`, `shadows` and `highlights` (split-tone colours) on top of the 1499 options. Existing options keep their meaning and defaults, so 1499 decks render as before.
- [ ] AC-03: **World helpers.** `ctx.world` offers `sky`, `terrain`, `field` (instanced glowing tiles on the terrain, at least 20,000), `arcs` and `motes`, built on custom GLSL with sun, sky ambient and fog. Each returns a three.js object with a `set(options)` method for animation.
- [ ] AC-04: **Kinetic type.** `ctx.type(element, p, {style})` animates per glyph with `rise`, `blur`, `track`, `scatter`, `drop` and `type`. `rise`, `words` and `odometer` keep their 1499 behaviour.
- [ ] AC-05: **Display face.** The runtime registers Archivo (SIL OFL 1.1) as `SpecWithCode Display` from an inlined data URI, before the first frame, with its width axis, so `font-stretch: 125%` gives the wide cut. The licence ships beside the font in the source tree and is named in `THIRD_PARTY_NOTICES.md` and the generated Settings notices; `node scripts/studio-brand-audit.mjs` passes.
- [ ] AC-06: **One tag, offline.** `<script src="specwithcode:motion-deck">` still inlines everything (core, transitions, worlds, font) in one script, in development and from the CLI build, and the 1499 tests still pass. The runtime source files each stay under 1,500 lines.
- [ ] AC-07: **Demo deck.** `examples/motion-deck/demo.html` is rebuilt as an original five-scene story: plan, agents working in parallel, hand off across machines, review, ship. Every scene is a lit, full-frame world with its own palette and a distinct transition into it. No scene has a dark void or an empty middle. It runs offline, publishes under the 25 MiB path cap and holds 60 fps at 1080p on an M-series Mac.
- [ ] AC-08: **Agent guide.** The html_render and html_preview tool descriptions name the transitions, the post options and `ctx.world`, keeping the stage guide under 2,400 characters (1499 AC-12 allowed 1,800 added characters; this raises it by 600). `docs/studio/motion-pages.md` documents the full API with a worked scene.
- [ ] AC-09: **Tests.** `motionDeck.browser.test.ts` covers every transition compiling and rendering mid-way without errors, AgX and halation, each world helper, kinetic presets and the font. `localArtifactLibs.test.ts` covers the joined library and its notice.
- [ ] AC-10: **Evidence.** Headless screenshots of every scene and of mid-transition frames are in `reports/`, on a side-by-side page with the reference frames and the old deck, published with html_render.

## Decisions

- D-01: The runtime stays one library name. Its source splits into parts that the inliner joins, so files stay under 1,500 lines and pages keep one tag.
- D-02: The display face is Archivo (OFL 1.1, wdth 62 to 125, wght 100 to 900), vendored as one Latin woff2 with its licence. It is not the reference's face, and its width axis gives both a wide display cut and a body cut from one file.
- D-03: Transitions blend the two post-processed frames, so they work for every scene without scene cooperation. Scene-linked portals (the reference's homography into a surface of the next scene) are a follow-up.

## Approach

1. Split `motion-deck.js` into `motion-deck.js` (core), `motion-deck-fx.js` (transitions and cues) and `motion-deck-world.js` (world helpers and kinetic type). Add the font as `fonts/archivo-latin-wdth.woff2` plus `fonts/OFL.txt`; the loader wraps it into a `FontFace` part. `loadSpecWithCodeLibrary("motion-deck")` joins the parts; the CLI build writes the joined file.
2. Core: transition registry and per-transition materials compiled at warm-up; AgX, halation, split tone in the composite; a deterministic `transitionFrame` test hook; await the font before warm-up.
3. Worlds: shared GLSL for terrain height so the field sits on the terrain; one lighting model (sun, hemispheric ambient, fog toward the sky colour with sun scatter).
4. Demo: five scenes on the helpers, each with one hero element, a palette and a transition.
5. Evidence harness in scratch: headless Chrome on Metal, `seek` and `transitionFrame` stills.

## Tasks

### T-01 Runtime split, transitions, filmic post, font and world helpers
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/artifact-libs/motion-deck.js, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/artifact-libs/motion-deck-fx.js, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/artifact-libs/motion-deck-world.js, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/artifact-libs/fonts/, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/localArtifactLibs.ts, repositories/anton-abyzov/specwithcode/apps/server/scripts/cli.ts, repositories/anton-abyzov/specwithcode/THIRD_PARTY_NOTICES.md, repositories/anton-abyzov/specwithcode/third-party-licenses.config.json] | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/htmlRender/localArtifactLibs.test.ts apps/server/src/htmlRender/motionDeck.browser.test.ts

### T-02 Tests for transitions, post, worlds, type, font and the joined library
- AC: AC-09 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/motionDeck.browser.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/localArtifactLibs.test.ts] | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/htmlRender/localArtifactLibs.test.ts apps/server/src/htmlRender/motionDeck.browser.test.ts

### T-03 Rebuilt demo deck
- AC: AC-07 | Files: [repositories/anton-abyzov/specwithcode/examples/motion-deck/demo.html] | Test: scratch harness renders every scene and transition headless with no console errors and measures frame time

### T-04 Agent guide
- AC: AC-08 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/html/tools.ts, repositories/anton-abyzov/specwithcode/docs/studio/motion-pages.md] | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/html

### T-05 Evidence page, review, merge and release
- AC: AC-10 | Files: [.specweave/increments/1516-cinematic-motion-deck-shader-transitions-filmic-post-and-a-rebuilt-demo/reports/] | Test: side-by-side page published with html_render; cross-family review; CI green; request-release.sh
