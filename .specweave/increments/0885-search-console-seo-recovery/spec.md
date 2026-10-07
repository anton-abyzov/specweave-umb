# 0885 Search Console SEO recovery across public sites

## Problem
Admin mailbox Search Console alerts identify indexing failures on verified-skill.com and spec-weave.com, and Event/Video schema failures on easychamp.com. Live audits confirm sitemap/robots disagreement, missing canonical metadata, unavailable social assets, and indexable unfinished video pages. Historical notices and intentional exclusions must be distinguished from current defects.

## Scope
In: read every Search Console email in admin@easychamp.com; reconcile current source, deployed content, and owners; correct supported public-site indexing, canonical/sitemap/schema/media metadata and internal navigation consistency; update stale public version information; push reviewed changes, deploy, and verify public responses and headless rendering.
Out: modifying deprecated EasyChamp repositories; unrelated major dependency upgrades; private production records; paid campaigns or outreach; promising Google's recrawl/indexing outcome.

## Acceptance Criteria
- [ ] AC-01: All 88 matching Search Console emails are read and summarized without secrets or tracking URLs; current and historical findings have dispositions.
- [ ] AC-02: spec-weave.com sitemap excludes robots-blocked utility URLs and matches public canonical URLs; affected static site build and regression checks pass.
- [ ] AC-03: verified-skill.com public routes have consistent canonical/social metadata, available social images, published video schema and thumbnails; unfinished/operational routes are excluded; sitemap contains only eligible URLs.
- [ ] AC-04: EasyChamp's supported source and live pages are checked against Event image/location and Video date/thumbnail notices; remaining verified source defects are corrected and tested, with current owners preserved.
- [ ] AC-05: Independent review resolves critical/high findings; each changed repo is pushed and deployment identity plus public/headless evidence proves the released behavior; remaining Google validation limitations are recorded.

## Approach
Use current stable SpecWeave 3.0.3 (registry verified 2026-10-07). Keep dirty primary checkouts untouched. Coordinator uses isolated umbrella worktree from remote main af15f099. Each implementation lane uses its own isolated checkout from latest remote default/develop and reviews relevant ADRs and owner claims before writes. Use one coherent SEO recovery increment across these sites, with one implementation branch per nested repo. Preserve existing public design components while consolidating route identity and crawl eligibility. Never manufacture Event data or dates to satisfy schema. Treat correct alternate canonicals, authentication exclusions and removed-page 404 responses as expected. Verify source tests/builds and public deployment separately. All browser automation explicitly headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never, HTML reporters open:'never'.

## Tasks

### T-01 Mailbox inventory and current SEO evidence
- AC: AC-01 | Files: .specweave/increments/0885-search-console-seo-recovery/reports, .specweave/increments/0885-search-console-seo-recovery/scripts | Test: python3 .specweave/increments/0885-search-console-seo-recovery/scripts/verify-mail-inventory.py

### T-02 SpecWeave public-site indexing correction
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/docs-site | Test: npm --prefix <isolated-specweave-checkout>/docs-site run build

### T-03 Verified Skills canonical, sitemap and video correction
- AC: AC-03 | Files: repositories/anton-abyzov/vskill-platform/src, repositories/anton-abyzov/vskill-platform/public, repositories/anton-abyzov/vskill-platform/tests | Test: npm --prefix <isolated-vskill-checkout> test -- --run

### T-04 EasyChamp structured-data and public SEO correction
- AC: AC-04 | Files: EasyChamp/ec-landing, EasyChamp/ec-arena-ui, EasyChamp/ec-uikit | Test: <affected-EasyChamp-checkout regression tests and build>

### T-05 Independent review, release and public verification
- AC: AC-05 | Files: .specweave/increments/0885-search-console-seo-recovery/reports | Test: <public SEO verification against released sites>
