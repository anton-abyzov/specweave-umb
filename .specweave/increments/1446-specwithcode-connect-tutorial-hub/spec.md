# SpecWithCode Connect tutorial hub

## Problem

On `https://spec-weave.com/tutorials/`, the only device/machine connection tutorials (`add-a-machine` and `join-a-mac`) were recorded on SpecWithCode 1.0.47 (October 18, 2026) and still teach the retired join-line (`swc-machine-...`), pasting main machine environment IDs, and Tailscale-first setup. There is no current SpecWithCode Connect device-pairing tutorial leading the hub, nor companion tutorials covering iPhone/other-device Connect pairing, the two named permission lines in Settings > Machines (`Agents on {here} can start work on {there}` / `Agents on {there} can start work on {here}` and `Who can run work here`), and troubleshooting (offline machines, dismissed join codes, and Connect vs MCP vs Tailscale fallback).

## Scope

In:
- Three new 1920x1080 captioned tutorial videos (Remotion, zero new paid API spend) hosted on Cloudflare R2 (`media.spec-weave.com/video/tutorials/`), with `.jpg` posters and `.en.vtt` WebVTT caption tracks:
  1. `connect-devices`: Connect your devices with SpecWithCode Connect (leads the hub)
  2. `machine-permissions`: Set machine permissions and worker access
  3. `connect-troubleshooting`: Fix offline machines, codes and Connect routes
- New **Connect your devices** learning path placed first on `https://spec-weave.com/tutorials/` (`#path-connect-devices`) and the new Connect tutorials placed first in `tutorials.json` so `connect-devices` leads both the hero stack and All guides.
- Updated `docs/studio/connect.md` and `docs/studio/add-a-machine.md` embedding `<TutorialEmbed slug="connect-devices" />` and reflecting current shipped Connect, device approval code, and permission flows while keeping legacy tutorial URLs working with updated cross-links.
- R2 upload (`npm run videos:publish`), full catalogue/build validation (`verify-tutorials.mjs --built`), PR to `anton-abyzov/specweave` (`develop`), merge when green, docs deployment, and live desktop + mobile headless Playwright verification.

Out:
- Paid voiceover or external media generation (no new spend).
- Public social media posting or YouTube uploads.
- Changes to SpecWithCode desktop/server runtime code or live owner threads.

## Acceptance Criteria

- [ ] AC-01: `connect-devices`, `machine-permissions`, and `connect-troubleshooting` render cleanly at 1920x1080 30fps MP4 (`yuv420p`, `+faststart`) with matching `.jpg` posters and `.en.vtt` WebVTT captions, zero black frames, zero private secrets/real codes, and accurate shipped SpecWithCode 1.0.407 Connect UI copy.
- [ ] AC-02: `docs-site/src/data/tutorials.json`, `tutorial-extras.json`, `docs/studio/connect.md`, and `docs/studio/add-a-machine.md` expose **Connect your devices** as the first learning path and `connect-devices` as the first guide on `/tutorials/`, pass `node scripts/verify-tutorials.mjs --built` and `npm run build` with zero errors.
- [ ] AC-03: All 3 MP4s are published to Cloudflare R2 (`https://media.spec-weave.com/video/tutorials/<slug>.mp4`), PR is merged to `anton-abyzov/specweave` (`develop`), `deploy-docs.yml` completes green, and live headless Playwright verification on both desktop (1280x800) and mobile (390x844) confirms navbar discovery, clickable `/tutorials/` and `/tutorials/connect-devices/` pages, real `<video>` playback (`readyState >= 3`, advancing `currentTime`, `videoWidth === 1920`), and loaded captions.

## Approach

1. Add a clean Remotion tutorial module under `repositories/anton-abyzov/specweave/docs-site/remotion/connect-tutorials/` reusing the existing `studio-tutorial/theme.ts` and `studio-tutorial/primitives.tsx` visual system (warm `#f6f4ee` paper backdrop, Newsreader + IBM Plex Sans + IBM Plex Mono, crisp macOS/iPhone SpecWithCode UI frames, animated callouts, and redacted placeholder codes like `K7M-4QP`). Register compositions in `remotion/Root.tsx`.
2. Render the 3 MP4s + posters to `docs-site/static/video/tutorials/`, author matching WebVTT `.en.vtt` captions, inspect contact sheets via `ffmpeg` to verify zero visual glitches, and publish MP4s to R2 with `npm --prefix docs-site run videos:publish`.
3. Update `docs-site/src/data/tutorials.json`, `tutorial-extras.json`, `docs-site/docs/studio/connect.md`, `docs-site/docs/studio/add-a-machine.md`, and `docs-site/scripts/verify-tutorials.mjs` (`STUDIO_DOCS` mapping) so `connect-devices` leads `/tutorials/` and studio docs embed it cleanly.
4. Run `verify-tutorials.mjs --built`, `npm run typecheck`, `npm test`, and `npm run build` (using `specweave-studio checks` for heavy suites), commit on a branch in `repositories/anton-abyzov/specweave`, open PR to `develop`, merge when CI is green, wait for `deploy-docs.yml`, and verify live desktop + mobile playback in headless Playwright with saved screenshot evidence.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Hosting target -> Reuse canonical `https://spec-weave.com/tutorials/` and Cloudflare R2 (`media.spec-weave.com/video/tutorials/`) via `videos:publish` instead of a new YouTube upload (zero spend, immediate website playback, reversible).
- D-02 Audio track -> Silent captioned 1920x1080 tutorials (`audio: "silent"`, `captionsOn: true`, WebVTT + open transcript) to honor the zero-spend rule and never substitute another voice for Anton's ElevenLabs voice (reversible).
- D-03 Legacy tutorials -> Keep `add-a-machine` and `join-a-mac` published so existing links never 404, while placing the new `connect-devices` learning path and tutorials first and linking older entries to `connect-devices` (reversible).

### Open
- none

## Tasks

### T-01 Build and render the three SpecWithCode Connect tutorial videos, posters, and captions
- AC: AC-01 | Files: [repositories/anton-abyzov/specweave/docs-site/remotion/Root.tsx, repositories/anton-abyzov/specweave/docs-site/remotion/connect-tutorials/ConnectTutorials.tsx, repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/connect-devices.jpg, repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/connect-devices.en.vtt, repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/machine-permissions.jpg, repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/machine-permissions.en.vtt, repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/connect-troubleshooting.jpg, repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/connect-troubleshooting.en.vtt] | Test: ffprobe -v error -select_streams v:0 -show_entries stream=width,height,codec_name -show_entries format=duration -of compact repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/connect-devices.mp4 repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/machine-permissions.mp4 repositories/anton-abyzov/specweave/docs-site/static/video/tutorials/connect-troubleshooting.mp4

### T-02 Update tutorials catalogue, hub ordering, and Studio Connect docs
- AC: AC-02 | Files: [repositories/anton-abyzov/specweave/docs-site/src/data/tutorials.json, repositories/anton-abyzov/specweave/docs-site/src/data/tutorial-extras.json, repositories/anton-abyzov/specweave/docs-site/docs/studio/connect.md, repositories/anton-abyzov/specweave/docs-site/docs/studio/add-a-machine.md, repositories/anton-abyzov/specweave/docs-site/scripts/verify-tutorials.mjs] | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build && node repositories/anton-abyzov/specweave/docs-site/scripts/verify-tutorials.mjs --built

### T-03 Publish videos to R2, ship PR to develop, deploy docs, and verify live desktop and mobile playback
- AC: AC-03 | Files: [repositories/anton-abyzov/specweave/docs-site/src/data/tutorials.json] | Test: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node .specweave/increments/1446-specwithcode-connect-tutorial-hub/reports/verify-live.mjs
