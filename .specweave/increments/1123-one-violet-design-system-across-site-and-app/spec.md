# One violet design system across site and app

## Problem

spec-weave.com mixes three accents. /pricing and the rest of the site use Weave iris violet, but /code and /code/download override it to terracotta (code.module.css), the YouTube embed uses its own amber/navy palette, and badges, callouts and the web manifest use Tailwind blue. The desktop app's default theme shows terracotta (shell.css) over a blue base (index.css). The owner says violet is the brand colour. The /code hero is a 1520x360 screenshot of a 1.0.76 delegation that is unreadable at page size and does not show what happens.

## Scope

In: Weave iris as the only brand accent on every site page, docs and the desktop app's default theme; a new /code hero that shows goal, coordinator split, parallel agents and review. Out: logo/wordmark tile colour and app icons (brand-asset decision), named user-selectable app themes, provider logos, unlinked legacy static pages and orphan SVGs, re-recorded tutorial videos (separate thread).

## Acceptance Criteria

- [ ] AC-01: On /, /code, /code/download, /pricing, /product and docs, in light and dark, --wv-iris resolves to #6d4fb5 / #a88cf6 and the /code primary button is iris.
- [ ] AC-02: The /code hero shows four labelled steps (goal, coordinator splits, agents work, review) with a link to the real run, readable at 375px with no sideways scroll, finished state without motion.
- [ ] AC-03: Site components (YouTube embed, badges, callouts, steps, accent tokens, manifest, docs diagrams) use Weave tokens, not private palettes.
- [ ] AC-04: The desktop app default theme uses iris as primary in light and dark, with AA contrast, and its tests pass.

## Approach

Weave (docs-site/src/css/weave.css) already defines the system; the fix is removing overrides and private palettes. /code: delete the terracotta .page override, replace the screenshot figure with HeroFlow (CSS-only 12s replay; resting state is the finished run). Studio: point shell.css and index.css default --primary at iris, retune default stage art from the existing iris theme block, swap blue fallbacks. Risk: another thread edits provider logos on the same page; it owns providers/*.svg.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Logo tile stays #5B6CFF; recolouring brand marks and app icons is a separate decision.
- D-02 Hero is an illustration labelled as such; the real recorded run stays further down the page.
### Open
- none

## Tasks

### T-01 /code on Weave iris with a clear hero
- AC: AC-01, AC-02 | Files: docs-site/src/pages/code.tsx, docs-site/src/pages/code.module.css, docs-site/src/components/ecosystem/HeroFlow.tsx, docs-site/src/components/ecosystem/HeroFlow.module.css, docs-site/e2e/design-system.spec.ts | Test: cd repositories/anton-abyzov/specweave/docs-site && npx playwright test e2e/design-system.spec.ts

### T-02 Site components onto Weave tokens
- AC: AC-03 | Files: docs-site/src/components/**, docs-site/src/css/tokens.css, docs-site/static/site.webmanifest, docs-site/docs/** | Test: cd repositories/anton-abyzov/specweave/docs-site && npx playwright test e2e/design-system.spec.ts

### T-03 Desktop app default theme to iris
- AC: AC-04 | Files: specweave-studio apps/web/src/index.css, apps/web/src/components/studio/shell/shell.css, apps/web/src/styles/base.css, apps/web/index.html | Test: cd repositories/anton-abyzov/specweave-studio/apps/web && npx vitest run src/components/studio/shell

### T-04 Verify and close 1123
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specweave verify 1123
