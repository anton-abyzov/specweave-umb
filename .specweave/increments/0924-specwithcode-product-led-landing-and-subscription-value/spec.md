# SpecWithCode product-led landing and subscription value

## Problem
The landing hero uses oversized serif type and excessive space, hiding the product. Anton requested ScrollCraft, real screenshots, animated coordinator/thread communication, accurate subscription-value messaging, and restoration of /code.

## Scope
In: replace the product landing composition, use approved public footage as source, browser-native motion inspired by motion-graphics choreography, /code canonical with /studio redirect, promo copy from PR2053, review/build/browser evidence and deployment. Out: new paid provider runs, publishing social posts, spending, unsupported savings/adoption claims, changing runtime permissions.

## Acceptance Criteria
- [x] AC-01: /code leads with compact local-control copy and real product screenshot; cloud qualification is readable beside the CTA.
- [x] AC-02: ScrollCraft depth and a sticky coordinator-to-worker sequence explain assignment and returned evidence; reduced-motion and no-JS remain complete.
- [x] AC-03: Subscription-value section distinguishes eligible plan usage from API billing, preserves limits, and makes no unsupported 10x, customer or company-wide scale claims.
- [x] AC-04: /studio redirects to /code, nav and SEO canonicals use /code; existing docs remain reachable.
- [x] AC-05: Production build, SEO, focused browser checks, 8 scroll stops at 1440/375, light/dark, reduced-motion/no-JS and fresh review pass; merged source is verified live.

## Approach
Own branch codex/subscription-value-copy and PR2053 at /Users/antonabyzov/.codex/worktrees/local-control-copy/specweave. Prior review task has no active file claims. Use existing sanitized public recordings, not private desktop screenshots. ScrollCraft is already installed; apply composition rules and motion-graphics motion principles to the interactive webpage (no separate rendered-film deliverable). Palette: porcelain #f5f7fb, ink #152542, cobalt #315ce8, teal #087c85, slate #52627c. Use existing IBM Plex Sans for display and body, tighter measure and paired screenshot. No giant serif display. 3 planes: background field, product capture, foreground flow. Native sticky and CSS view timelines avoid extra animation dependencies. Preserve exact PR2052 deployed source separately. New admin bypass is not implied by its consumed one-time authorization.

## Tasks
### T-01 Build landing and route
- AC: AC-01, AC-02, AC-03, AC-04 | Files: docs-site/src/pages/code.tsx, docs-site/src/pages/studio.tsx, docs-site/src/pages/code.module.css, docs-site/src/components/ecosystem/CoordinatorFlow.tsx, docs-site/src/components/ecosystem/CoordinatorFlow.module.css, docs-site/static/img/studio/coordinator-capture.webp, docs-site/static/img/studio/coordinator-capture-source.md, docs-site/docusaurus.config.ts, docs-site/scripts/verify-seo.mjs, docs-site/src/pages/index.tsx, docs-site/src/pages/product.tsx, docs-site/src/pages/pricing.tsx, docs-site/src/components/ecosystem/Architecture.tsx, docs-site/src/components/sections/SkillStudioSection.tsx, docs-site/src/__tests__/sidebars.test.ts, docs-site/src/data/tutorials.json, docs-site/docs, README.md, docs-site/marketing/specwithcode-local-control.md | Test: npm --prefix /Users/antonabyzov/.codex/worktrees/local-control-copy/specweave/docs-site run build
### T-02 Review and release
- AC: AC-05 | Files: reports under /Users/antonabyzov/Projects/research/0924-landing-redesign | Test: headless browser verification and GitHub Pages deployment readback

## Progress (2026-10-14, Claude Code taking over the stalled Codex thread)
- T-01 done: commit 56338d0eb on codex/subscription-value-copy (PR #2053). Local build plus verify-seo green; code-landing guard test passes; 10 legacy vitest failures match origin/develop.
- T-02: headless QA saved under ~/Projects/github/.cw-runs/l2/shots-final (8 stops at 1440 and 375, light and dark, reduced motion, no-JS). Merge is blocked by develop's required approving review (1). Waiting on Anton: approve the PR or allow a one-time admin merge. After that, push to develop deploys through deploy-docs.yml and the live check follows.
- 2026-10-15: PR #2053 merged (8d5194715) and deployed by deploy-docs (run 38659889293). Live headless readback of https://spec-weave.com/code/ passes at 1440 and 375 in light and dark, with 8 scroll stops, reduced motion and no-JS. /studio/ lands on /code/. Both fresh-review findings are resolved live. Evidence: reports/live-verification.md and reports/live/.
