# 0885 Search Console SEO recovery across public sites

## Problem
Admin mailbox Search Console alerts identify indexing failures on verified-skill.com and spec-weave.com, and Event/Video schema failures on easychamp.com. Live audits confirm sitemap/robots disagreement, missing canonical metadata, unavailable social assets, and indexable unfinished video pages. Historical notices and intentional exclusions must be distinguished from current defects.

## Scope
In: read every Search Console email in admin@easychamp.com; reconcile current source, deployed content, and owners; correct supported public-site indexing, canonical/sitemap/schema/media metadata and internal navigation consistency; update stale public version information; push reviewed changes, deploy, and verify public responses and headless rendering.
Out: modifying deprecated EasyChamp repositories; unrelated major dependency upgrades; private production records; paid campaigns or outreach; promising Google's recrawl/indexing outcome.

## Acceptance Criteria
- [ ] AC-01: All 88 matching Search Console emails are read and summarized without secrets or tracking URLs; current and historical findings have dispositions.
- [ ] AC-02: spec-weave.com sitemap excludes robots-blocked utility URLs and matches public canonical URLs; affected static site build and regression checks pass.
- [ ] AC-03: verified-skill.com public routes have consistent canonical/social metadata, available social images, published video schema and thumbnails; unfinished/operational routes are excluded; sitemap contains only eligible URLs. Public publisher listings and search return correct records/totals on uncached requests within the existing database timeout.
- [ ] AC-04: EasyChamp's supported source and live pages are checked against Event image/location and Video date/thumbnail notices; remaining verified source defects are corrected and tested, with current owners preserved.
- [ ] AC-05: Independent review resolves critical/high findings; each changed repo is pushed and deployment identity plus public/headless evidence proves the released behavior; remaining Google validation limitations are recorded.
- [ ] AC-06: Documentation links retain the shared olive identity and readable contrast in both themes; deployed headless checks prove at least 4.5:1 for normal text and 3:1 for large text.

- [ ] AC-07: Every Help tutorial video has an accessible, visible player in initial HTML without a user click; player URLs agree with structured data, remain responsive and do not autoplay.

## Approach
Use current stable SpecWeave 3.0.3 (registry verified 2026-10-07). Keep dirty primary checkouts untouched. Coordinator uses isolated umbrella worktree from remote main af15f099. Each implementation lane uses its own isolated checkout from latest remote default/develop and reviews relevant ADRs and owner claims before writes. Use one coherent SEO recovery increment across these sites, with one implementation branch per nested repo. Preserve existing public design components while consolidating route identity and crawl eligibility. Never manufacture Event data or dates to satisfy schema. Treat correct alternate canonicals, authentication exclusions and removed-page 404 responses as expected. Verify source tests/builds and public deployment separately. All browser automation explicitly headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never, HTML reporters open:'never'.

Production publisher follow-up: retained cold HTTP500s trace to a missing covering index for `LOWER(author)` over a 2.09 GiB heap. Prefer one reviewed nonunique partial covering index over an unshipped query rewrite. Build `Skill_public_author_metrics_idx` concurrently on `LOWER(author), normalizedRepoUrl`, including `author, githubStars, trustScore, isTainted`, for public nondeprecated rows. The independent reviewer requires raw author in INCLUDE for expression-index index-only planning ([PostgreSQL documentation](https://www.postgresql.org/docs/17/indexes-index-only-scans.html)). Apply only this exact DDL after name/definition, existing-build, width and operational prestate checks; preserve database timeout, cache bounds, data, policies and existing application SQL. Read back valid/ready/live definition and actual query plans/timing. Stop on unexpected identity or another active index build. Never automatically remove an index after a failed CREATE: another actor may have registered the same name. Retain failure/readback and require proven ownership plus separately reviewed exact OID/definition for concurrent rollback. Forward the verified direct connection explicitly to the one-migration ledger recorder; never run unrelated pending migrations. Record migration provenance and rollback separately from application deployment.

## Tasks

### T-01 Mailbox inventory and current SEO evidence
- AC: AC-01 | Files: .specweave/increments/0885-search-console-seo-recovery/reports, .specweave/increments/0885-search-console-seo-recovery/scripts | Test: python3 .specweave/increments/0885-search-console-seo-recovery/scripts/verify-mail-inventory.py

### T-02 SpecWeave public-site indexing correction
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/docs-site | Test: PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm --prefix /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0885-seo/docs-site run build

### T-03 Verified Skills canonical, sitemap and video correction
- AC: AC-03 | Files: repositories/anton-abyzov/vskill-platform/src, repositories/anton-abyzov/vskill-platform/public, repositories/anton-abyzov/vskill-platform/tests, repositories/anton-abyzov/vskill-platform/scripts, repositories/anton-abyzov/vskill-platform/prisma/migrations | Test: PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm --prefix /Users/antonabyzov/.codex/worktrees/search-console-seo/vskill-platform test -- --run

### T-04 EasyChamp structured-data and public SEO correction
- AC: AC-04 | Files: EasyChamp/ec-landing, EasyChamp/ec-arena-ui, EasyChamp/ec-uikit | Test: PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm --prefix /tmp/easychamp-seo-inventory-landing-20261007 test -- --run && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm --prefix /tmp/easychamp-seo-inventory-arena-20261007 test -- --run && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm --prefix /tmp/easychamp-seo-inventory-uikit-20261007 run build

### T-05 Independent review, release and public verification
- AC: AC-05 | Files: .specweave/increments/0885-search-console-seo-recovery/reports, .specweave/increments/0885-search-console-seo-recovery/scripts | Test: python3 .specweave/increments/0885-search-console-seo-recovery/scripts/verify-live-seo.py

### T-06 Documentation dark-theme link readability
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/docs-site/src/css/custom.css, .specweave/increments/0885-search-console-seo-recovery/scripts/verify-specweave-design.mjs | Test: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never PLAYWRIGHT_MODULE=/Users/antonabyzov/.codex/worktrees/search-console-seo/vskill-platform/node_modules/playwright PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node .specweave/increments/0885-search-console-seo-recovery/scripts/verify-specweave-design.mjs

### T-07 Help video player discoverability
- AC: AC-07 | Files: EasyChamp/ec-landing/src/components/help, EasyChamp/ec-landing/src/app/help | Test: PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm --prefix /tmp/easychamp-seo-inventory-landing-20261007 test -- --run
