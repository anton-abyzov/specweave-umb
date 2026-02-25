---
increment: 0277-multi-package-manager-docs
title: "Multi-Package-Manager Documentation Update"
status: planned
---

# Plan: Multi-Package-Manager Documentation Update

## Overview

Replace all npm-only install/run snippets in user-facing pages across three repos (vskill-platform, specweave docs-site, vskill CLI) with multi-runner examples showing npx, bunx, pnpx, and yarn dlx. Purely content/UI changes -- no CLI logic changes.

## Architecture Decisions

### AD-001: Consistent Snippet Format
Use comment-annotated code blocks (`# npm` / `# bun` / `# pnpm` / `# yarn`) as the universal format across all repos. This works in Markdown, Docusaurus MDX, and JSX.

### AD-002: vskill-platform Install Snippet
Replace the single-line `$ npm install -g vskill` code element in the homepage hero with a multi-line code block showing all four runners. Keep it compact -- the hero area is tight.

### AD-003: AnimatedTerminal Variation
Distribute package runners across the three existing scenarios:
- Scenario "init": keep `npx vskill init` (most familiar)
- Scenario "add": change to `bunx vskill install ...` (showcase bun)
- Scenario "scan": change to `pnpx vskill scan ...` (showcase pnpm)

This demonstrates variety without adding new scenarios or complicating the animation logic.

### AD-004: Skill Detail Page
Replace the single `installCmd` string with a multi-line code block showing all four runners. Use the existing `TerminalBlock` component for consistent styling.

### AD-005: Docusaurus Docs (spec-weave.com)
Use standard fenced code blocks with comment annotations. Simple annotated code blocks are clearer and more portable than Docusaurus `<Tabs>`.

## Repos and Files to Change

### vskill-platform (repositories/anton-abyzov/vskill-platform/)
1. `src/app/page.tsx` -- Hero install snippet (line ~164-170)
2. `src/app/components/AnimatedTerminal.tsx` -- Vary runners in scenarios
3. `src/app/skills/[name]/page.tsx` -- Install section multi-runner

### specweave docs-site (repositories/anton-abyzov/specweave/)
4. `docs-site/src/pages/index.tsx` -- CTA section install snippet (line ~517)
5. `docs-site/docs/quick-start.md` -- Installation section
6. `docs-site/docs/guides/getting-started/installation.md` -- Methods 1 & 2
7. `docs-site/docs/skills/verified/verified-skills.md` -- npx vskill CLI section
8. `docs-site/docs/skills/index.md` -- npx vskill reference

### vskill CLI (repositories/anton-abyzov/vskill/)
9. `README.md` -- Top code block and Commands section

## Risk Assessment

- **Low risk**: All changes are content/UI only. No logic changes.
- **No breaking changes**: Existing npm commands still work; we are adding alternatives.
- **Testing**: Visual verification only -- no unit tests needed for docs content changes.
