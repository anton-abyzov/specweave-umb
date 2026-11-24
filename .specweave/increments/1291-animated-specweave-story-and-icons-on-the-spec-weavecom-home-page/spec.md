# Animated SpecWeave story and icons on the spec-weave.com home page

## Problem

The spec-weave.com home page explains SpecWeave with text, a pinned scroll diagram and static lists. It has no icons outside the hero, and its `#how` section hides three of its four beats until the visitor scrolls a pinned stage. The SpecWithCode page at `/code/` shows the opposite: provider logos, an icon card for the Chrome extension and a plan card that plays on its own. Anton compared the two on November 11, 2026 and called the home page boring: no icons, no animation that shows the plan, the ledger, the handoff, or verify and review.

## Scope

In: the home page at `docs-site/src/pages/index.tsx` and its components. Four self-running animated scenes in `#how` (plan, ledger, handoff, verify and review) in the visual language of the `/code/` hero stage; brand logos in the "Works with" row and in the scenes; a set of crafted icons generated with Kie.ai for the scenes and the section headings; translations of every new string in the 8 locales; updated e2e and unit checks.

Out: the hero, `/code/`, `/product` and other pages; the Weave tokens and `weave.css`; rendered video files; any change to CLI behaviour.

## Acceptance Criteria

- [x] AC-01: `#how` shows four scenes in order (The plan, The ledger in git, The handoff, Verify and review), each with a crafted icon, a short explanation and an animated stage that uses the formats specweave reads (`- [ ] AC-NN:` criteria, `### T-NN` tasks, one JSON object per ledger line, `specweave handoff`, `pickup`, `verify`, `review`, `complete`).
- [x] AC-02: Each stage plays only while it is on screen, loops, and rests on its complete final state in the server render, without JavaScript and under `prefers-reduced-motion: reduce`.
- [x] AC-03: The "Works with" row and the handoff scene show real brand logos for the agents that have one in `static/img/studio/providers/`; every titled content section on the home page carries an icon in its heading from one generated set, drawn the same size and shape.
- [x] AC-04: The page follows the Weave light and dark themes with no hard-coded colours in the story styles apart from the two logo plates `/code/` already uses, never scrolls sideways at 390 px, and keeps one `h1` and the existing section ids (`family`, `how`, `proof`, `app`, `tutorials`, `built-with`).
- [x] AC-05: Every new string has a message in `i18n/{de,es,fr,ja,ko,pt-BR,ru,zh-CN}/code.json`; the docs build (9 locales plus `verify-seo`) passes.
- [x] AC-06: The change is merged to `develop`, deployed, and `node docs-site/scripts/verify-live.mjs --browser` passes; headless screenshots exist for light and dark at desktop and mobile widths.

## Approach

1. Icons: generate one master icon with Kie `gpt-image-2-text-to-image`, then the rest with `gpt-image-2-image-to-image` using it as the style reference, as full-bleed square tiles so they need no transparency and read on both themes. Convert to 160 px WebP in `docs-site/static/img/home/icons/`. One `HomeIcon` component draws them with a fixed radius.
2. Scenes: `docs-site/src/components/home/story/`. A small step clock (`useSteps`) advances through a list of times while the stage is on screen; each scene renders from the step number, and CSS transitions do the motion. No animation library is added to the home bundle. Server render, no-JS and reduced motion get the last step.
3. `#how` keeps its heading and lead; the pinned `HomeHandoff` stage and its CSS are deleted. The `#proof` section keeps the folder listing; its three-command gate list moves into scene four, reusing the translated strings.
4. "Works with" becomes logo chips; section headings get icons.
5. Translations for new strings in 8 locales; update `e2e/hero.spec.ts`; add a unit test that checks scene data against the formats and that every new key exists in every locale.

Rejected: a rendered HyperFrames or Lottie video per scene (cannot follow the theme or the locale, heavy on phones); the `motion` library on the home page (CSS transitions are enough); transparent generated icons (edge matting on glossy shapes is unreliable).

Risk: generated icons may drift in style. Mitigation: one reference image for all, review each at 48 px in both themes, regenerate outliers.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Animations are live DOM and CSS, not video files → they follow theme and language (reversible).
- D-02 `#how` keeps its current heading "When Claude Code hits its limit, Codex picks up the same task" → the four scenes tell that one handoff (reversible).
- D-03 The receiving agent in the handoff scene is Codex, as in the real `specweave pickup` output on `/product`; other agents appear as a logo row (reversible).
- D-04 The closing call to action ("Bring every agent, keep your place") stays buttons only, without an icon → AC-03 covers the titled content sections (reversible).
### Open
- none

## Tasks

### T-01 Generate the icon set with Kie.ai
- AC: AC-03 | Files: docs-site/static/img/home/icons/, docs-site/src/components/home/HomeIcon.tsx | Test: ls repositories/anton-abyzov/specweave/docs-site/static/img/home/icons/*.webp

### T-02 Build the four animated scenes and replace the pinned stage
- AC: AC-01, AC-02 | Files: docs-site/src/components/home/story/, docs-site/src/pages/index.tsx, docs-site/src/components/landing/ | Test: cd repositories/anton-abyzov/specweave/docs-site && npx vitest run src/__tests__/home-story.test.ts

### T-03 Logos in "Works with" and icons on section headings
- AC: AC-03, AC-04 | Files: docs-site/src/pages/index.tsx, docs-site/src/components/landing/home.module.css, docs-site/src/components/home/ | Test: cd repositories/anton-abyzov/specweave/docs-site && npx vitest run src/__tests__/home-story.test.ts

### T-04 Translate new strings and update checks
- AC: AC-05 | Files: docs-site/i18n/*/code.json, docs-site/e2e/hero.spec.ts, docs-site/src/__tests__/home-story.test.ts | Test: cd repositories/anton-abyzov/specweave/docs-site && npx vitest run src/__tests__/home-story.test.ts src/__tests__/code-landing.test.ts

### T-05 Review, merge, deploy and verify live
- AC: AC-04, AC-06 | Files: docs-site/ | Test: node repositories/anton-abyzov/specweave/docs-site/scripts/verify-live.mjs --browser /
