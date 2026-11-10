# One design system and shared shell for SpecWeave, SpecWithCode and Verified Skill

## Problem

Anton, November 10, 2026: "Why is the look and feel of this not consolidated? Rethink and review the whole design. Include the motion graphics effects... It must be all consolidated. Rethink the whole landing page for all products we have on SpecWeave. Focus on SpecWithCode and vskill, and all the skills management."

spec-weave.com (Docusaurus, `docs-site/`) and verified-skill.com (Next.js, `vskill-platform`) look like two companies. Only the thin product bar is shared.

Audit, headless Chromium, November 10, 2026, 8 pages, light and dark, 1440px and 390px. Evidence: `~/.specwithcode/m4/scratch/2026-11-10-design-consolidation/audit.json` and `~/.specwithcode/m4/scratch/2026-11-10-design-consolidation/shots/` (48 screenshots).

| Area | spec-weave.com | verified-skill.com | Verdict |
|---|---|---|---|
| Typefaces | Schibsted Grotesk, JetBrains Mono | same | Same |
| Palette | paper `#F8F7F9`, ink `#241523`, violet `#6D4FB5`; dark `#16131D`, `#A88CF6` | identical | Same |
| Light or dark | stored per domain (Docusaurus `theme` key) | stored per domain (`localStorage.theme`) | One can be dark while the other is light |
| Navbar | full width, 24px gutter, links left, search field, language menu | 1136px column, links right, shortcut chip, Login | Differs |
| Brand slot | "SpecWeave" even on `/code/` | "Verified Skill" | Differs |
| h1 | 64 to 72px, weights 700 and 750 | 72px home, 48px Skill Studio, 32px Claude Code skills | Differs |
| h2 weight | 600, 650, 800 | 600, 700 | Differs |
| Main button height | 48px, 60px | 40px | Differs |
| Hero background | lavender wash on `/code/` only | flat | Differs |
| Footer | 33 links, 600px | 21 links, 415px, other columns | Differs |
| Motion | 29 to 61 running animations per page, no shared pattern | 12 on home, 0 elsewhere | Differs |

## Scope

In: one token set and type scale, one shared shell (product bar, navbar, footer, theme behaviour) on both domains, one motion rule set, rethought landing pages for spec-weave.com, SpecWithCode (`/code/`) and verified-skill.com with a skills-management chapter, shipped as one PR per repository and checked live.

Out: the per-product navbar GitHub link (owned by another thread), docs content, the SpecWithCode app UI, Skill Studio's own UI, registry data pages beyond their page header, new copy claims (license and provider rules in project memory "Marketing and brand rules" apply unchanged).

## Acceptance Criteria

- [ ] AC-01: Anton has picked one of the three directions on the decision page, and the pick is recorded under Decisions.
- [ ] AC-02: At 1440px and 390px, in light and dark, the product bar and navbar on spec-weave.com/code/ and verified-skill.com have the same height, column width, gutter, brand-slot position, link position and right-hand cluster; measured in headless Chromium, differences are 0px.
- [ ] AC-03: The brand slot shows the current product's name: SpecWeave on `/`, SpecWithCode on `/code/...`, Verified Skill on verified-skill.com.
- [ ] AC-04: With no stored choice both domains follow `prefers-color-scheme`; a manual choice made on one domain is applied on the other after following a product bar link.
- [ ] AC-05: Both footers render the same four-column structure; only the "This product" column differs.
- [ ] AC-06: Page titles use exactly three sizes (landing, page, doc) and one weight, section headings one weight, main buttons one height, on every audited page of both domains.
- [ ] AC-07: Each landing (spec-weave.com, `/code/`, verified-skill.com) has one orchestrated hero motion; the thread draws the family bar underline and the hero stage outline once; idle decorative loops and per-section fade-ups are gone. Scroll-linked motion that shows structure may stay.
- [ ] AC-08: With `prefers-reduced-motion: reduce`, the thread and every decorative animation are off and the final state shows; only the SpecWithCode hero demo keeps its slower explanatory variant (D-07).
- [ ] AC-09: The SpecWithCode landing has a skills chapter (browse, install, test, update) linking to Verified Skill, and the Verified Skill landing covers find, check, install and manage in Skill Studio.
- [ ] AC-10: No em dashes in new copy, every named provider shows its official logo, the product is never called "Studio", and no AI attribution appears in commits or PRs.
- [ ] AC-11: Both PRs are merged and the live sites pass the AC-02 to AC-08 checks in headless Chromium, with before and after screenshots saved.

## Approach

Decision page first (three directions, live mockups, motion export), build only after the pick.

Shared shell without a shared package: the two sites are different frameworks in different repositories, so the shell is one small CSS file (`shell.css`: tokens, product bar, navbar, footer, type scale, motion tokens) kept byte-identical in both repositories, with a unit test in each that fails when its checksum differs from the recorded one. Markup is implemented per framework against the same class names. Rejected: an npm package (a release step for a few hundred lines of CSS) and iframes or remote includes (network dependency in the shell).

Theme across domains: product bar links to the other domain carry `?theme=light|dark` only when the visitor chose one manually; the receiving site stores it and strips the parameter. Rejected: a shared cookie (different registrable domains).

Motion: CSS for the shell (thread underline), GSAP for the one hero sequence per landing, loaded only on landings and gated on `prefers-reduced-motion`. Film assets, where a direction needs them, are rendered with HyperFrames to MP4 and WebM with a poster.

Files, in order. specweave `docs-site/`: `src/css/tokens.css`, `src/css/weave.css`, `src/css/custom.css`, `src/theme/Navbar/index.tsx`, `src/theme/Navbar/FamilyBar.tsx`, `src/theme/Footer/index.tsx`, `src/pages/index.tsx`, `src/pages/code.tsx`, `src/pages/code/download.tsx`, `docusaurus.config.ts`. vskill-platform: `src/app/globals.css`, `src/app/weave.css`, `src/app/layout.tsx`, `src/app/components/LayoutShell.tsx`, `src/app/components/ThemeToggle.tsx`, `src/app/components/MobileNav.tsx`, `src/app/page.tsx`, `src/app/claude-code-skills/`, `src/app/skill-studio/`.

Risks: Docusaurus swizzled Navbar drift on upgrade; the navbar GitHub link is being changed by another thread, so rebase on it and leave that item's href alone; visual regressions on docs pages from the type scale change.

## Decisions

### Asked
- D-01 Which direction: A "One thread", B "Three inks" or C "Night shift"? → A. One thread (Anton, November 10, 2026). Decision page: `~/.specwithcode/m4/scratch/2026-11-10-design-consolidation/decision.html`.
### Defaulted (change any before sw-do)
- D-02 After Effects is unavailable → motion is GSAP and CSS on the sites, HyperFrames for rendered exports.
- D-03 Shell shared as a checksum-locked CSS file in both repositories, not a package.
- D-04 Theme default follows the system on both domains.
- D-05 spec-weave.com `/` becomes the family front door with SpecWithCode leading.
- D-06 The shell lives in the existing Weave system: `design/weave/weave.css` and `design/weave/weave-shell.js`, with `design/weave/checksums.json`, instead of a new `shell.css`.
- D-07 The SpecWithCode hero demo (FlowStage) stays the page's one self-playing sequence and keeps its documented slower variant under reduced motion; idle float, breathe and glow loops and section fade-ups are removed.
- D-08 Footer on spec-weave.com is trimmed from 33 to about 30 links in four columns; 7 guide links leave the footer and stay reachable from docs.
### Open
- none

## Tasks

### T-01 Audit both sites and publish the decision page
- AC: AC-01 | Files: [~/.specwithcode/m4/scratch/2026-11-10-design-consolidation/decision.html] | Test: `test -s ~/.specwithcode/m4/scratch/2026-11-10-design-consolidation/audit.json`

### T-02 Record the picked direction and revise T-03 onward for it
- AC: AC-01 | Files: [.specweave/increments/1271-one-design-system-and-shared-shell-for-specweave-specwithcode-and-verified-skill/spec.md] | Test: `grep -q "D-01.*→ [ABC]" spec.md`

### T-03 shell.css: tokens, type scale, button, motion tokens, product bar, navbar, footer
- AC: AC-06 | Files: [docs-site/src/css/shell.css, docs-site/src/css/tokens.css, docs-site/src/css/weave.css, tests/unit/docs-site/shell-checksum.test.ts] | Test: `npx vitest run tests/unit/docs-site/shell-checksum.test.ts`

### T-04 Docusaurus shell: navbar with per-product brand slot, product bar thread, footer
- AC: AC-02, AC-03, AC-05 | Files: [docs-site/src/theme/Navbar/index.tsx, docs-site/src/theme/Navbar/FamilyBar.tsx, docs-site/src/theme/Footer/index.tsx, docs-site/docusaurus.config.ts, docs-site/src/css/custom.css] | Test: `cd docs-site && npx playwright test e2e/shell.spec.ts`

### T-05 Theme: system default and cross-domain carry on spec-weave.com
- AC: AC-04 | Files: [docs-site/src/theme/Navbar/FamilyBar.tsx, docs-site/src/theme/Layout/index.tsx] | Test: `cd docs-site && npx playwright test e2e/theme-carry.spec.ts`

### T-06 Landings on spec-weave.com: family front door and SpecWithCode with the skills chapter
- AC: AC-07, AC-08, AC-09, AC-10 | Files: [docs-site/src/pages/index.tsx, docs-site/src/pages/code.tsx, docs-site/src/pages/code.module.css, docs-site/src/components/home/, docs-site/src/css/animations.css] | Test: `cd docs-site && npx playwright test e2e/landing-motion.spec.ts`

### T-07 vskill-platform shell: same shell.css, navbar, footer, theme carry
- AC: AC-02, AC-03, AC-04, AC-05, AC-06 | Files: [vskill-platform/src/app/shell.css, vskill-platform/src/app/globals.css, vskill-platform/src/app/layout.tsx, vskill-platform/src/app/components/LayoutShell.tsx, vskill-platform/src/app/components/ThemeToggle.tsx, vskill-platform/src/app/components/MobileNav.tsx] | Test: `cd vskill-platform && npx vitest run src/app/__tests__/shell-checksum.test.ts && npx playwright test e2e/shell.spec.ts`

### T-08 Verified Skill landing and inner page headers
- AC: AC-06, AC-07, AC-08, AC-09, AC-10 | Files: [vskill-platform/src/app/page.tsx, vskill-platform/src/app/home.module.css, vskill-platform/src/app/components/home/, vskill-platform/src/app/claude-code-skills/, vskill-platform/src/app/skill-studio/] | Test: `cd vskill-platform && npx playwright test e2e/landing-motion.spec.ts`

### T-09 Ship both PRs and verify live
- AC: AC-11 | Files: [docs-site/scripts/verify-live.mjs, vskill-platform/e2e/shell.spec.ts] | Test: `node docs-site/scripts/verify-live.mjs --browser` plus the cross-site shell measurement script, screenshots saved
