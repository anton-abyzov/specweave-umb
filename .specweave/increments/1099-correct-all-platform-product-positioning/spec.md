# 1099 Correct all-platform product positioning

## Problem
Generic SpecWithCode marketing still says Mac-only despite published Windows and Linux installers. Social previews repeat this limitation.

## Scope
Correct current website/docs/metadata/OG and editable promotional source wording; audit app docs with their owner. Preserve platform-specific native limitations and install details. No desktop release, restart, new publishing or historical social edits.

## Acceptance Criteria
- [ ] AC-01: Product landing/download metadata, generic copy and share graphic say computers and list macOS, Windows and Linux; platform limits remain truthful.
- [ ] AC-02: Current docs and editable promotional sources contain no unsupported generic Mac-only positioning; release/install evidence and exclusions are recorded.
- [ ] AC-03: Reviewed site changes reach develop and public pages/OG image bytes are verified headless; external preview cache limits are reported.

## Approach
Inspect claims/worktrees/PRs and coordinate release/1008/Windows-Linux owners. Use installed OS receipts rather than infer native capability parity. Revise scoped docs sources, regenerate share JPG, cache-bust its URL, build and verify SEO. Audit editable campaign sources and DRAFT posts while preserving QUEUE/PUBLISHED records. Fresh review before merge; observe normal docs deployment.

## Decisions
### Asked
- User: generic phrase on your own computers; name macOS, Windows and Linux where useful.
### Defaulted
- Keep historical videos/tutorial captures labeled for their actual Mac recording; retain macOS-only computer use and voice caveats.
- Do not mutate scheduled or published posts; record stale queued copy for channel approval.
### Open
- none

## Tasks
### T-01 Correct website, metadata and social graphic
- AC: AC-01 | Files: docs-site/src/pages/code.tsx, docs-site/src/pages/code/download.tsx, docs-site/src/components/ecosystem/StudioSections.tsx, docs-site/src/components/ecosystem/WhySpecWithCode.tsx, docs-site/marketing/og-specwithcode.html, docs-site/static/img/studio/og-specwithcode.jpg, docs-site/scripts/verify-seo.mjs | Test: npm --prefix docs-site run build

### T-02 Audit and correct current docs and editable promotion sources
- AC: AC-02 | Files: docs-site/docs/overview, docs-site/docs/studio, docs-site/docs/guides, /Users/antonabyzov/specwithcode-promo/launch-2026-10-20, /Users/antonabyzov/specwithcode-promo/platform-positioning-20261027 | Test: Review scoped wording diff and retained platform/install receipts; build included in T-01.

### T-03 Deliver public site and verify
- AC: AC-03 | Files: /Users/antonabyzov/specwithcode-promo/platform-positioning-20261027 | Test: Headless public page metadata, OS download URLs and OG image-byte readback.

### T-04 Verify and close 1099
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1099-correct-all-platform-product-positioning/reports | Test: specweave verify 1099; fresh-context review; specweave complete 1099
