# Download page animated how-it-works explainer

## Problem

The spec-weave.com/code/download/ hero shows `code-hero-worker-20261015.webp`, a 920x1130 crop of a 15 October 2026 capture, scaled up inside a "Worker thread · Codex, GPT-6.1-Sol" card. Anton (November 8, 2026): it looks blurry and does not explain what happens. The same static card sits on /product (`flow-worker-claude-20261015.webp`).

## Scope

In: a new animated explainer component (`docs-site/src/components/code/HowItWorks.tsx` + CSS module) replacing the static worker card on `/code/download` and `/product`; fresh native-resolution captures of the current released SpecWithCode UI used inside it; capture provenance note. Out: the `/code` FlowStage hero, BuiltWithItself, OG images, app code.

## Acceptance Criteria

- [ ] AC-01: The download hero plays a looping explainer with five beats: request reaches the coordinator; it splits into workers that each own their files; workers run in parallel on named models and machines; results return with evidence; it ships (PR merged).
- [ ] AC-02: The animation is HTML/CSS/SVG, deterministic and seek-safe (CSS animation with a single timeline variable or negative delays), adds under 2 MB to the page, and under `prefers-reduced-motion: reduce` shows a static, complete final frame with no motion.
- [ ] AC-03: Product UI shown inside it comes from headless captures of the current released SpecWithCode at 2x device scale, displayed at or below native pixel size (never upscaled), sharp in light and dark color schemes; no plain black backgrounds; the product is written "SpecWithCode".
- [ ] AC-04: Headless screenshots at 1440px and 390px widths, light and dark, show the explainer rendered with no overflow; `npm run build` in docs-site passes.
- [ ] AC-05: PR merged to develop and the live https://spec-weave.com/code/download/ serves the explainer.

## Approach

Recapture the released server UI headlessly (recipe in `docs-site/static/img/studio/coordinator-capture-source.md`), crop small UI pieces at native 2x pixels (composer, coordinator plan, worker rows, evidence report, PR state), and compose them in an HTML/CSS stage with SVG connectors. Rejected: video (weight, not seek-safe, blurry when scaled); HyperFrames render (MP4 weight, no dark variant).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Replace the /product worker card too (same component family, same blur) → yes
### Open
- none

## Tasks

### T-01 Capture current UI headlessly at native resolution
- AC: AC-03 | Files: docs-site/static/img/studio/howitworks-*, docs-site/static/img/studio/coordinator-capture-source.md | Test: file docs-site/static/img/studio/howitworks-*

### T-02 Build HowItWorks animated explainer and wire it in
- AC: AC-01, AC-02, AC-03 | Files: docs-site/src/components/code/HowItWorks.tsx, docs-site/src/components/code/HowItWorks.module.css, docs-site/src/pages/code/download.tsx, docs-site/src/pages/product.tsx | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build

### T-03 Headless verification at desktop and mobile, light and dark
- AC: AC-04 | Files: docs-site/scripts/ | Test: ls /tmp/howitworks-shots/*.png

### T-04 Ship and verify live
- AC: AC-05 | Files: none | Test: curl -s https://spec-weave.com/code/download/ | grep -c howItWorks
