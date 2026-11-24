# SpecWithCode tutorials and website design system

## Problem

Anton asked (2026-10-11) for concise, professional tutorials, mostly about the SpecWithCode app (formerly SpecWeave Studio) with some terminal, one per agent (Claude Code, Codex, OpenCode, Antigravity, Grok, maybe more), published on the website with improved UI/UX and one design system. Today: spec-weave.com has no Tutorials section (/tutorials and /docs/tutorials return 404); videos are raw `<video>` tags in four near-identical wrappers, two hosted off-site on postiz.easychamp.com; the site carries three conflicting visual layers (legacy indigo `tokens.css`, the paper/ink/orange `brand-tokens.css`, an olive Infima override), the marketing pages have no dark mode (navbar turns dark, body stays paper), and the navbar logo is the old purple weave. The app's own palette (terracotta shell) matches none of them. Research: session scratchpad `understand.json` (7 readers + critic, 2026-10-11).

## Scope

In: one design system on spec-weave.com built on `brand-tokens.css` (accent #bd481f) with dark mode; a /tutorials gallery with a shared accessible video component (poster, captions, chapters); SpecWithCode copy on /studio and /docs/studio pages (URLs unchanged); six tutorial scripts and storyboards; terminal segments from real command output; app footage once the renamed build ships; narration, render and publish.
Out: renaming the app itself (the naming thread owns it), the `specweave` CLI name, a new domain, Copilot tutorial (unless Anton picks it), the app's in-product theme.

## Acceptance Criteria

- [ ] AC-01: spec-weave.com uses one token source: brand colors, type and radius come from `brand-tokens.css`; no page renders the legacy indigo primary or the olive Infima primary; every marketing page has working light and dark modes (headless check of /, /studio, /tutorials in both schemes).
- [ ] AC-02: /tutorials lists every tutorial with poster, title, duration and agent, and each tutorial plays from first-party hosting with captions (VTT) and chapter markers; the navbar and footer link to it; `npm run build` passes with `onBrokenLinks: 'throw'`.
- [ ] AC-03: /studio and the docs/studio pages call the app SpecWithCode, keep the CLI name `specweave`, keep every existing URL, and never say bare "Studio" where Skill Studio could be meant.
- [ ] AC-04: Six scripts (Claude Code, Codex, OpenCode, Antigravity, Grok, Cursor), each 60-120 s of narration in plain language, showing setup, one real task through the app, and the result, with every command and UI label checked against the running build.
- [ ] AC-05: Terminal segments are typeset from real stdout captured from real runs; no invented output.
- [ ] AC-06: Each tutorial renders at 1920x1080 with burned captions plus a VTT, loudness -16 LUFS, no HyperFrames lint errors, and is published on /tutorials.

## Approach

Website work lands in `repositories/anton-abyzov/specweave/docs-site` (worktree `0895-site`, branch from `develop`, PR to `develop`; deploys to GitHub Pages). Tutorials are HyperFrames projects under `repositories/anton-abyzov/specweave/video/tutorials/<agent>/`, reusing the Oct 8 launch package's brand frame. Narration via ElevenLabs over curl, key loaded from the vault per session, never printed. App footage via headless Playwright `recordVideo` against a disposable `--base-dir` home with seeded demo projects (no real names, no pairing tokens on screen). Defaults until Anton answers: public install path not yet available (scripts say how to get access), orange palette, Anton's voice, six agents.

Rejected: recording against v0.2.4 now (every app shot would be re-shot after the rename); ffmpeg caption burn-in (this ffmpeg has no libass/drawtext).

## Open questions

- none. Anton approved the recommended defaults on 2026-10-11: pilot-access wording until a public install path exists, orange palette, Anton's cloned voice, six agents (Claude Code, Codex, OpenCode, Antigravity, Grok, Cursor).
- Later on 2026-10-11 Anton confirmed: SpecWithCode is free in early access (no "pilot" wording in copy or videos), and the Cursor episode stays "coming soon" on /tutorials until a Cursor Pro account exists (the free plan is refused; see video/tutorials/PIPELINE.md). AC-06 is met by the five episodes that can be recorded; the Cursor script and terminal captures stay in the repo for that later render.

## Tasks

### T-01 Unify the site on brand tokens with dark mode
- AC: AC-01 | Files: repositories/anton-abyzov/specweave/docs-site/src/css/custom.css, repositories/anton-abyzov/specweave/docs-site/src/css/tokens.css, repositories/anton-abyzov/specweave/src/styles/brand-tokens.css | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0895-site/docs-site && npm run build

### T-02 Tutorials gallery and shared video component
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/docs-site/src/pages/tutorials.tsx, repositories/anton-abyzov/specweave/docs-site/src/components/TutorialVideo, repositories/anton-abyzov/specweave/docs-site/docusaurus.config.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0895-site/docs-site && npm run build

### T-03 SpecWithCode copy on the studio pages
- AC: AC-03 | Files: repositories/anton-abyzov/specweave/docs-site/src/pages/studio.tsx, repositories/anton-abyzov/specweave/docs-site/docs/overview/studio.mdx, repositories/anton-abyzov/specweave/docs-site/docs/studio | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0895-site/docs-site && npm run build && ! grep -rn "SpecWeave Studio" src/pages docs/overview/studio.mdx docs/studio

### T-04 Six tutorial scripts and storyboards
- AC: AC-04 | Files: repositories/anton-abyzov/specweave/video/tutorials | Test: test $(ls /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0895-site/video/tutorials/*/SCRIPT.md | wc -l) -ge 6

### T-05 Terminal segments from real runs
- AC: AC-05 | Files: repositories/anton-abyzov/specweave/video/tutorials | Test: ls /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0895-site/video/tutorials/*/captures/*.json

### T-06 Record app footage, narrate, render and publish
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/video/tutorials, repositories/anton-abyzov/specweave/docs-site/static/video/tutorials | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0895-site/docs-site && npm run build
