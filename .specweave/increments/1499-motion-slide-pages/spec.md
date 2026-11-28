# Motion slide pages: WebGL scenes, music, slide navigation and a loading bar run in SpecWithCode pages, installed apps and standalone downloads

## Problem

On November 26, 2026 the owner shared a Claude artifact, "The Last Boring Slide": a 13-scene WebGL presentation with photoreal procedural scenes, generated music, slide navigation, a loading bar and Install as app. The owner wants SpecWithCode pages to support this kind of motion presentation, and wants to know how it is built.

Research (report `reports/research-claude-motion-slides.md`) found two things:

- **The deck is one self-contained 5.1 MB HTML file.** It inlines three.js, its own deck engine, synthesized audio and base64 fonts and images. It uses no host APIs. Its beauty comes from authoring technique, not from the host.
- **Our host blocks or degrades such a page in six places.** A harness ran the captured deck and a probe page under origin/main's exact embed conditions (bootstrap, CSP sandbox header, opaque-origin frame, theme fragment) in headless Chrome:
  1. **Size.** `html_render` takes the page only as a 512,000-character tool argument, so a 5 MB page cannot be published (`apps/server/src/mcp/toolkits/html/tools.ts:21`).
  2. **Deep links.** The bootstrap removes the whole URL fragment after reading the theme, so `#scene-2` never reaches the page. Measured: `hashAtBoot ""`.
  3. **Fullscreen.** The frame has no `allow` attribute, so `requestFullscreen()` fails with "Disallowed by permissions policy" even after a click.
  4. **Keyboard.** Keys reach the page only after something focuses the frame. Nothing does today.
  5. **Sizing.** A presentation needs a fixed stage. Reports size to their content, the inline preview runs the page live (GPU and audio in the thread), and installed windows scroll.
  6. **Libraries.** No three.js or deck runtime is available offline. A CDN copy breaks installed apps offline and standalone downloads.

Working today: WebGL2 with float render targets on the GPU, and SwiftShader in the preview browser. `history.replaceState` and `hashchange` work on the opaque origin. An `AudioContext` resumes after a click inside the frame without `allow="autoplay"`.

## Scope

In:

- **Stage pages.** A page declares it is a presentation. The thread shows a card that runs nothing. The reader and installed windows give it a fixed, focused, fullscreen-capable stage that receives deep links.
- **Large pages.** `html_render` accepts a file path.
- **Bundled libraries**, inlined at publish so pages run offline:
  - `specwithcode:three` (three.js r180, already a dependency).
  - `specwithcode:motion-deck`, our own deck runtime: beats, hash routing, keys and touch, a loading bar with real progress, a post-processing pass, a DOM text layer for kinetic type, and synthesized Web Audio music and sound effects.
- **`html_preview` waits** for a stage page to say it is ready.
- **An original demo deck** in the repository, and the agent guide in the tool description.

Out:

- **Claude-desktop extras:** frameless or transparent windows, `downloads.save` exports, host text-to-speech, and full computer access (held for the owner per `decision_installed_page_apps`).
- **New packaging.** Install as app stays the 1475/1485 launcher with per-version powers; this increment only makes stage pages fill the window.
- **Copying the reference.** No Anthropic code, assets, scenes, copy or tuning constants. The spec describes techniques only.
- **Audio files.** Music is synthesized in the page.

## Acceptance Criteria

- [ ] AC-01: **Stage flag at publish.** A page whose head has `<meta name="specwithcode-page" content="stage">` is published with `stage: true` on its html_render reference, and publishing skips the 9-width height measurement for it. A page without the tag publishes exactly as before.
- [ ] AC-02: **Thread card.** A stage page shows a presentation card that mounts no frame, so it runs no WebGL or audio. The card has the title and a Play button. Play shows the page in the reader at the full size of the viewer area. The frame is focused when the reader opens, so arrow keys work without a click.
- [ ] AC-03: **Stage frame permissions.** A stage page's frame, in the reader and in an installed window, has `allow="autoplay; fullscreen"`. Report frames keep no `allow` attribute.
  - Harness: after one click inside a stage frame, `requestFullscreen()` succeeds and the page's `AudioContext` is `running`.
- [ ] AC-04: **Deep links.** The page bootstrap removes only its own fragment keys (`studio-theme`, `studio-contain-scroll`). The page's own fragment is kept: a frame loaded with `#deck-2` sees `location.hash === "#deck-2"` at boot. A report with no fragment of its own still ends with an empty hash.
- [ ] AC-05: **Installed window.** An installed stage page fills its window exactly (no window scroll) and its frame takes focus when mounted. Report pages in installed windows are unchanged, and 1475/1485 launchers and powers work as before.
- [ ] AC-06: **File-path input.** `html_render` accepts `path`, an absolute path to an existing `.html` or `.htm` file, instead of `html`.
  - Exactly one of the two is required.
  - The file passes the agent path guard and is at most 25 MiB.
  - Local images and libraries inline as for `html`.
  - `html_preview` accepts `path` the same way.
- [ ] AC-07: **Bundled libraries.** At publish and preview, `<script src="specwithcode:three"></script>` is replaced by an inline classic script that defines `window.THREE` (three.js r180, MIT notice kept), and `<script src="specwithcode:motion-deck"></script>` by the deck runtime.
  - The stored page makes no network request when it runs (harness with non-local requests blocked).
  - The stored file opened directly from disk runs, which is the standalone download.
  - An unknown `specwithcode:` library fails the publish with an error naming it.
- [ ] AC-08: **Deck runtime: navigation.** `SpecWithCodeDeck.start({scenes})` runs scenes made of beats.
  - The URL hash is `#<scene>-<beat>`, written with `replaceState`. A `hashchange` jumps.
  - Next: Right, Down, Space, PageDown, Enter, click, left swipe. Back: Left, Up, PageUp, Backspace, right swipe. Home and End jump to the first and last scene.
  - F toggles fullscreen, M mutes, N shows speaker notes, A auto-plays.
  - Escape is consumed only when it closed something.
  - The loading overlay shows a determinate bar driven by scene initialisation and shader warm-up, then sets `window.specwithcodeReady = true`.
  - Under reduced motion, transitions are cut. The loop pauses while the page is hidden.
- [ ] AC-09: **Deck runtime: look and sound.**
  - Scenes render into an HDR target. A shared post pass applies bloom, ACES tone mapping, a vignette and film grain, set per scene.
  - Text is a DOM layer with kinetic-type helpers (word rise, an odometer counter).
  - Music and sound effects are synthesized with Web Audio: detuned pads through filters and a generated-impulse reverb, plus noise and tone hits, on a compressor-limited master. Audio starts on the first gesture in the page, and per-scene beds cross-fade on scene change.
  - Beat-local animation windows (`s.win(beat, t0, t1, ease)`) give deterministic seeking and rewinding.
- [ ] AC-10: **Preview waits.** `html_preview` of a stage page waits up to 90 s for `window.specwithcodeReady` before it screenshots. It reports a console warning when the page never became ready.
- [ ] AC-11: **Demo deck.** `examples/motion-deck/demo.html` is an original 3-scene deck that uses only the bundled libraries:
  - a constellation of thousands of instanced lights;
  - a task grid lighting up with an odometer;
  - linked nodes with travelling pulses.

  It runs in the harness under the stage frame with GPU. A screenshot of each scene and a short recording are saved to this increment's `reports/`.
- [ ] AC-12: **Agent guide.** The html_render and html_preview tool descriptions explain stage pages, `path`, the two libraries and the deck API, in under 1,800 added characters. `docs/studio/motion-pages.md` holds the full guide.
- [ ] AC-13: **One card per report title.** When a thread holds several report pages with the same title (ignoring case and surrounding spaces), only the newest shows as a full card. Each earlier one shows its header with "Earlier version. The newest is further down." and Open report: no preview, no Install as app, and its page loads only when opened. Diagrams (`kind: "visual"`) are never grouped. The html_render description tells agents to revise by republishing under the same title.
- [ ] AC-14: **Honest report label.** The report card says "Report", and its footer says the thread shows a preview and the opened report has the links, tabs and evidence files. The phrase is translated in every catalog, and "Interactive report" no longer appears.
- [ ] AC-15: **Quit closes only an installed page.** In an installed page window, Command-Q on macOS (Control-Q on Windows and Linux, with no other modifier) closes that window and never reaches the menu's Quit. Quit from the menu bar still quits SpecWithCode.

## Approach

- **Shared, `packages/shared/src/htmlRender.ts`:**
  - `HtmlRenderReference.stage?: true`, read by `readHtmlRenderReference`.
  - `isHtmlRenderStagePage(html)` detects the meta tag in the head.
  - The bootstrap strips only its own fragment keys.
  - `HTML_RENDER_STAGE_ALLOW = "autoplay; fullscreen"`.
- **Server, `apps/server/src/htmlRender/`:**
  - `HtmlRender.publish` sets `stage` and skips `measure` for stage pages. `preview` waits for ready on stage pages through `headlessChrome.ts`.
  - `localArtifactLibs.ts` gains a `specwithcode:` scheme resolver, kept beside the mermaid rewrite.
  - `artifact-libs/motion-deck.js` is our runtime, a plain ES2020 IIFE. three.js comes from `three/build/three.cjs`, wrapped in a classic IIFE. The CLI build minifies it with esbuild into `dist/client/artifact-libs/three.js` and copies `motion-deck.js`. Dev runs fall back to `node_modules`.
  - `mcp/toolkits/html/tools.ts` adds `path` (read through the agent path guard) and the guide.
- **Web:**
  - `components/files/BrowserDocumentFrame.tsx` `HtmlRenderDocument` gets `stage`, `hash` and `autoFocus` props.
  - `components/chat/HtmlRenderFrame.tsx` shows the card and the full-size reader for stage pages.
  - `components/artifactApps/ArtifactAppView.tsx` sizes the installed window to the stage.
- **Demo and evidence:** `examples/motion-deck/demo.html`. The harness lives outside the repository (scratch) and its output goes to `reports/`.
- **Rejected:**
  - Running the page `same-origin` like Claude's per-artifact origin: our frame must stay opaque (app session).
  - A CDN three.js: it breaks offline installs and downloads, and needs CORS for modules.
  - Generated audio files: inline synthesis keeps pages small and licence-free.
  - A canvas glyph-atlas text engine like the reference's: DOM text is accessible and much smaller. A WebGL text layer can follow.
  - Pinning a single fixed 16:9: the stage fills the viewer, and the deck letterboxes itself.
- **Risks:**
  - Shader warm-up on weak GPUs is slow; the loading bar shows progress.
  - Electron's autoplay default is not proven headless (proof limit).
  - A 2 MB three.js per page counts toward the 25 MiB cap.

## Decisions

### Asked
- none (the coordinator's brief set research-first, clean room, review, merge and release)
### Defaulted (change any before sw-do)
- D-01: A page opts in with a meta tag, not a tool flag. The flag travels with the file into installed windows and downloads.
- D-02: In the thread a stage page is a static card, never a live frame, so a thread with several decks costs no GPU or audio until one is opened.
- D-03: `allow="autoplay; fullscreen"` only for stage pages; reports keep today's frame.
- D-04: Libraries are inlined at publish and never served by URL, so every copy is self-contained.
- D-05: The demo deck's visual polish is marked for a Fable 5.2 pass after November 28, 2026 (weekly limit).
### Open
- D-06 (owner): Move macOS installs to Electron's app-shim, as Claude desktop does, for a Dock icon, menu bar and Command-Q of their own. This needs ad-hoc signing and hash checks, which reverses part of `decision_installed_page_apps`. It is a follow-up increment, not 1499. Recommended: yes.

## Tasks

### T-01 Research report and compatibility harness evidence
- AC: AC-03, AC-04 | Files: [.specweave/increments/1499-motion-slide-pages/reports/research-claude-motion-slides.md] | Test: report lists the harness results for main and for the stage frame

### T-02 Shared stage flag, bootstrap fragment keeping, allow constant
- AC: AC-01, AC-04 | Files: [repositories/anton-abyzov/specwithcode/packages/shared/src/htmlRender.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/htmlRender.test.ts] | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/htmlRender.test.ts

### T-03 Server: path input, stage publish without measuring, specwithcode libraries, preview ready wait
- AC: AC-01, AC-06, AC-07, AC-10 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/HtmlRender.ts, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/localArtifactLibs.ts, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/headlessChrome.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/html/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/scripts/cli.ts] | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/htmlRender

### T-04 Web: stage card, full-size focused reader, allow attribute, installed window stage
- AC: AC-02, AC-03, AC-05 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/files/BrowserDocumentFrame.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/HtmlRenderFrame.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/artifactApps/ArtifactAppView.tsx] | Test: cd apps/web && vp test run on the touched component tests

### T-05 Motion deck runtime
- AC: AC-08, AC-09 | Files: [repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/artifact-libs/motion-deck.js, repositories/anton-abyzov/specwithcode/apps/server/src/htmlRender/motionDeck.test.ts] | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/htmlRender/motionDeck.test.ts

### T-06 Original demo deck, guide and harness run under the stage frame
- AC: AC-07, AC-11, AC-12 | Files: [repositories/anton-abyzov/specwithcode/examples/motion-deck/demo.html, repositories/anton-abyzov/specwithcode/docs/studio/motion-pages.md, .specweave/increments/1499-motion-slide-pages/reports/] | Test: harness.mjs stage run with the published demo; screenshots and recording in reports/

### T-08 Owner follow-ups: duplicate report cards, report label, installed-page quit, Claude app comparison
- AC: AC-13, AC-14, AC-15 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.replacedReports.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/HtmlRenderFrame.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/HtmlRenderFrame.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppWindows.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/artifactApps/ArtifactAppWindows.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/html/tools.ts, .specweave/increments/1499-motion-slide-pages/reports/owner-questions-reports-and-installed-apps.md] | Test: cd apps/web && vp test run src/components/chat/HtmlRenderFrame.test.tsx src/components/chat/MessagesTimeline.replacedReports.test.ts src/i18n; vp test run apps/desktop/src/artifactApps/ArtifactAppWindows.test.ts

### T-07 Review, merge and release
- AC: AC-01..AC-15 | Files: [] | Test: Gemini 4 Neon then GPT-6.2 Sol review recorded; CI green; request-release.sh
