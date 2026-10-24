# Brand search discovery and SEO audit

## Problem

The user sees generic Google results for "spec with code". Live October 22, 2026 reads find indexed SpecWithCode pages but no spaced brand phrase on the canonical product, home or download page. specwithcode.com returns NXDOMAIN. Search Console is connected through Supermetrics but account prioritization blocks analytics. Existing SEO work in completed 0938 must be preserved rather than duplicated.

## Scope

In: public domain and sitemap crawl, indexed result sampling, keyword intent, brand alias and entity relationships, product/download metadata, an educational comparison guide, generated-artifact verification and a comprehensive report. Out: domain purchase, account reprioritization, fabricated ranking/volume data, publishing social posts, production DNS changes. Target repository: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-seo-20261022, branch seo/brand-discovery-20261022.

## Acceptance Criteria

- [ ] AC-01: Saved live evidence identifies domain status, crawl/indexability signals, sitemap coverage, search observations, and the exact Search Console access limit without claiming zero indexing.
- [ ] AC-02: Generated product and download pages contain the visible spaced brand, unique metadata, product-specific social cards and a consistent SoftwareApplication alias; WebSite references resolve to the root site entity and the product page describes its relationship to that site.
- [ ] AC-03: An indexable comparison page explains spec as code, spec-driven development and intent-first development with a concrete example, accurate TechArticle markup, internal navigation and links to the existing product and comparison pages.
- [ ] AC-05: The generated site uses same-origin variable fonts with swap and no external Google Fonts stylesheet; published release metadata matches the verified GitHub asset.
- [ ] AC-04: Production build and SEO artifact checks pass; a fresh-context review is resolved; report states source/live boundaries and prioritized measurement and indexing actions.

## Approach

Keep https://spec-weave.com/code/ canonical. Add an explicit product alias, not a second competing product site. Keep SpecWeave's intent-first name, using spec-driven development in comparison content. Add entity IDs to existing site schema, link product WebPage to the existing WebSite and SoftwareApplication. Extend the generated artifact verifier to check observable HTML and schema relationships. Crawl the existing sitemap with bounded concurrency and inspect public primary-source Google guidance. Use the existing Docusaurus design. Finish with a reviewed PR; deployment and Google reindexing remain separate evidence gates.

## Decisions

### Asked
- None.

### Defaulted
- Preserve the current canonical host and SpecWeave name; no domain or subscription purchase.
- Use one spaced-name explanation and FAQ rather than repeating keywords across every heading.
- Keep existing FAQPage markup for semantic description without promising Google FAQ rich results.

### Open
- None for implementation. Exact Google ranking and submission status require authorized Search Console access beyond the Supermetrics plan gate.

## Tasks

### T-01 Audit public domains and search signals
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/seo-brand-20261022/ | Test: python3 /Users/antonabyzov/.specwithcode/m4/evidence/seo-brand-20261022/audit.py

### T-02 Repair brand and entity signals
- AC: AC-02 | Files: docs-site/src/pages/code.tsx, docs-site/src/pages/code/download.tsx, docs-site/src/pages/index.tsx, docs-site/docusaurus.config.ts, docs-site/static/llms.txt, docs-site/docs/overview/studio.mdx, docs-site/src/data/specwithcodeRelease.ts | Test: npm --prefix docs-site run build

### T-03 Add comparison content and artifact checks
- AC: AC-03 | Files: docs-site/docs/guides/spec-as-code.mdx, docs-site/docs/guides/spec-driven-tools-compared.md, docs-site/sidebars.ts, docs-site/src/pages/code.tsx, docs-site/scripts/verify-seo.mjs | Test: npm --prefix docs-site run build

### T-04 Verify, review and deliver the audit
- AC: AC-04 | Files: docs-site/marketing/seo-audit-20261022.md, /Users/antonabyzov/.specwithcode/m4/evidence/seo-brand-20261022/ | Test: npm --prefix docs-site run build

### T-05 Remove the measured font request bottleneck
- AC: AC-05 | Files: docs-site/docusaurus.config.ts, docs-site/src/css/custom.css, docs-site/src/css/fonts.css, docs-site/static/fonts/, docs-site/scripts/verify-seo.mjs, docs-site/src/data/specwithcodeRelease.ts | Test: npm --prefix docs-site run build
