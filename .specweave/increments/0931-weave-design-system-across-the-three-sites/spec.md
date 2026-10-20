# Weave design system across the three sites

## Problem

verified-skill.com, spec-weave.com and spec-weave.com/code look like three unrelated, generated sites (owner, 2026-10-18: "completely an AI sloppy design"). The audit found four palettes (forest green paper, GitHub white plus teal and orange, warm paper plus burnt orange, a separate blue palette on /code), five font families, monospace used for labels and navigation, uppercase eyebrows over every heading, radii from 3px to 14px with no rule, and AI-generated hero images (magnifier still life, glowing fibre networks, a silhouette at three blank monitors) where real product screens exist.

## Scope

In: one shared design system (Weave: tokens, type, components, imagery rules), applied to verified-skill.com (home, skills list, skill detail, studio, header, footer, global tokens) and spec-weave.com (home, /code, /product, docs chrome, header, footer, global tokens); AI images on those pages replaced with real captures or token-built diagrams; one scroll-driven layered sequence per site. Out: the SpecWithCode marketing Astro app (no live domain), the SpecWithCode desktop app UI, admin pages, the specweave dashboard (src/styles/brand-tokens.css stays as is).

## Acceptance Criteria

- [ ] AC-01: The Weave system is published (tokens, README, 8 components) and its canonical files live in specweave design/weave/.
- [ ] AC-02: verified-skill.com uses only Weave tokens and fonts on home, skills, skill detail and studio; no AI-generated image remains on those pages; light, dark and phone widths render without overflow.
- [ ] AC-03: spec-weave.com home, /code and /product use only Weave tokens and fonts (the /code blue palette is gone); no AI-generated image remains on those pages; docs chrome follows the system.
- [ ] AC-04: Each site has at most one scroll-driven sequence, complete at rest with reduced motion and without JavaScript.
- [ ] AC-05: Both sites build and their existing unit tests pass; before/after screenshots are shown to the owner before merge.

## Approach

Tokens come from the SpecWithCode Iris theme (packages/shared/src/themePalettes.ts), tuned for long pages; type is Schibsted Grotesk plus JetBrains Mono for real code only. weave.css is generated from design/weave/tokens.json and copied into each site, then each site's legacy variables are remapped onto Weave tokens so untouched pages shift too. docs-site loads weave.css after brand-tokens.css and overrides the brand variables inside the site only, so the dashboard is unaffected. Rejected: editing brand-tokens.css (it also styles the local dashboard). One PR per repo; merge needs the owner's word in the project thread.

## Open questions

- none

## Tasks

### T-01 Publish the Weave design system
- AC: AC-01 | Files: design/weave/tokens.json, design/weave/weave.css, design/weave/README.md | Test: test -s repositories/anton-abyzov/specweave/design/weave/weave.css

### T-02 Apply Weave to verified-skill.com
- AC: AC-02, AC-04 | Files: repositories/anton-abyzov/vskill-platform/src/app/** | Test: npm --prefix repositories/anton-abyzov/vskill-platform run build

### T-03 Apply Weave to spec-weave.com and /code
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specweave/docs-site/** | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build

### T-04 Before/after review
- AC: AC-05 | Files: none | Test: owner approval in the project thread
