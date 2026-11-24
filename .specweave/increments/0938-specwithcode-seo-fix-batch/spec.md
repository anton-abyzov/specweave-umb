# SpecWithCode SEO fix batch

## Problem

spec-weave.com/code, the SpecWithCode download page, names neither Claude Code nor Codex in its title or H1, has no SpecWithCode structured data (only the CLI's SoftwareApplication), shares the CLI's og-weave.jpg card, and shows version 1.0.44 while 1.0.50 is the latest release. The six highest-intent guides (usage limit, switching, Claude Code vs Codex, three compare pages) have no in-body link to /code. The homepage description is 281 characters, llms.txt still calls SpecWithCode "early access", the sitemap has no lastmod and lists thin tag and archive pages, Spec Kit lives outside /docs/compare/, and 11 tutorial descriptions run 186 to 682 characters. Evidence: promo/seo-audit.md (2026-10-18 crawl of 142 pages) and promo/plan.md section 3.

## Scope

In: docs-site changes for blocks A (/code landing), B (release data), C (share image), D (internal links), F (site meta and config) of plan.md section 3. Out: block E (PostHog analytics), block G (Cloudflare redirect, GitHub repo metadata, specwithcode README), the "Built on T3 Code" line and the T3 Code relationship row (wait for Anton's decision), new comparison pages, noindex swizzles for tag pages.

## Acceptance Criteria

- [ ] AC-01: /code renders the title "SpecWithCode: run Claude Code and Codex agents on your Mac" with no suffix, a description of at most 160 characters, an H1 that names SpecWithCode, Claude Code and Codex, og:image and twitter:image pointing at /img/studio/og-specwithcode.jpg (1200x630), a JSON-LD @graph with a SpecWithCode SoftwareApplication (version, downloadUrl, MIT license, price 0, isAccessibleForFree), a VideoObject and a FAQPage, data-track="download_click" on both download links, and body links to the usage-limit guide, the provider-runs-out tutorial and the BridgeMind compare page.
- [ ] AC-02: The release constant shows the latest SpecWithCode release (1.0.50) with its exact DMG size, and the opt-in release-link test passes against GitHub.
- [ ] AC-03: static/img/studio/og-specwithcode.jpg exists, 1200x630, under 200 KB, with the real SpecWithCode mark and readable headline and footer.
- [ ] AC-04: The usage-limit, switching and Claude Code vs Codex guides carry the "Prefer a desktop app?" tip before Common questions, all six guides list SpecWithCode under See also, and the switching guide opens with a short answer and has the title "How to continue a Claude Code task in Codex when you hit the limit".
- [ ] AC-05: The homepage title and 150-character description are replaced; llms.txt describes SpecWithCode as MIT with the /code download and has a SpecWithCode section; blogDescription is rewritten; the sitemap has lastmod and excludes tag, archive and author pages; the Spec Kit page lives at /docs/compare/specweave-vs-github-spec-kit/ with a redirect from the old URL; the Organization has an @id and the four new sameAs links; the T3 Code compare page has its new title; tutorial pages use seoDescription (at most 155 characters) and seoTitle (at most 60).

## Approach

Worktree `wt-seo-swc` on branch `seo/specwithcode-fix-batch` from `origin/develop`. /code builds its JSON-LD from SPECWITHCODE_RELEASE and reuses buildVideoObject for the embedded tour video; the FAQ gets a plain-text copy for FAQPage. The share card is an HTML page (docs-site/marketing/og-specwithcode.html) rendered by headless Playwright, chosen over AI art for crisp text. The default limit rule quoted in the tip is "Switch automatically" (docs/overview/studio.mdx). verify-tutorials.mjs now enforces the seoTitle and seoDescription limits. The changelog gets a 1.0.45 to 1.0.50 entry so "What is new in 1.0.50" lands on matching notes.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Fork disclosure ("Built on T3 Code") → left out until Anton decides
- D-02 Share image → HTML card rendered headless, not GPT Image options
### Open
- D-03 Fork wording on /code and the T3 Code compare page (Anton)

## Tasks

### T-01 /code title, H1, share tags, JSON-LD, tracking attributes and links
- AC: AC-01 | Files: docs-site/src/pages/code.tsx, docs-site/src/components/ecosystem/WhySpecWithCode.tsx | Test: npm --prefix docs-site run build

### T-02 Release 1.0.50 and its DMG size
- AC: AC-02 | Files: docs-site/src/data/specwithcodeRelease.ts, docs-site/docs/reference/changelog.md | Test: npm --prefix docs-site run build

### T-03 SpecWithCode share image
- AC: AC-03 | Files: docs-site/static/img/studio/og-specwithcode.jpg, docs-site/marketing/og-specwithcode.html | Test: npm --prefix docs-site run build

### T-04 Internal links into /code
- AC: AC-04 | Files: docs-site/docs/guides/claude-code-usage-limit.md, switch-claude-code-to-codex.md, claude-code-vs-codex.md, spec-driven-tools-compared.md, specweave-vs-openspec.md, specweave-vs-bmad.md | Test: npm --prefix docs-site run build

### T-05 Site meta, llms.txt, sitemap, Spec Kit slug, Organization, tutorials
- AC: AC-05 | Files: docs-site/src/pages/index.tsx, docs-site/static/llms.txt, docs-site/docusaurus.config.ts, docs-site/docs/guides/specweave-vs-speckit.md, docs-site/docs/guides/specwithcode-vs-opencode-t3-code.md, docs-site/src/data/tutorials.json, docs-site/src/data/tutorials.ts, docs-site/src/components/TutorialVideo/TutorialGuide.tsx, docs-site/scripts/verify-tutorials.mjs | Test: npm --prefix docs-site run build
