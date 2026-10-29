# 1109 Refresh landing visuals and replace agent tutorials

## Problem

The product landing page relies on long copy and small old screenshots. Anton requested a cleaner visual hierarchy, official provider icons, larger faithful product imagery, meaningful diagrams and scroll motion. Five first-task tutorials use outdated interface footage and audio the user rejects. Their existing voice configuration alone does not prove the provenance of cached audio.

## Scope

In: reviewable visual direction before major page implementation, current genuine UI evidence, shorter landing copy, official logos, responsive and reduced-motion behavior; source and cache voice audit; rebuild the Claude Code, Codex, OpenCode, Grok and Antigravity/Gemini tutorials with verified Anton narration; safe retirement of their wrong-voice active outputs; first-party site delivery and public media checks. Research short names/domains as proposals.

Out: domain purchases, DNS changes, global renaming, social publication or queue edits, desktop app release/restart, unrelated voice assets or original recordings, new model-provider spend. Existing all-platform wording and product/legal notices remain.

## Acceptance Criteria

- [ ] AC-01: A visual preview shows a larger faithful product image, official provider icons, a concise product story and at least one explanatory diagram before major page edits; naming/domain choices remain proposals.
- [ ] AC-02: Delivered landing page works at 1440 and 375 CSS pixels without overflow; reduced motion and no-JavaScript preserve readable content; metadata, downloads and legal/platform caveats remain correct.
- [ ] AC-03: Canonical voice identity is established from actual catalog/assets, the old audio reuse path is audited, and generation rejects unsupported voice/cache provenance instead of silently reusing audio.
- [ ] AC-04: All five first-task tutorials have reviewed current-flow scripts, faithful source footage, verified sole-voice request receipts and inspected/listened final media with captions. Rejected outputs are absent from active playback paths; original recordings and unrelated media remain intact.
- [ ] AC-05: Reviewed PR is merged and site deploy succeeds; public page and exact media bytes/links match delivered artifacts. Task evidence, scoped verify and fresh closure review support completion.

## Approach

Use the existing clean managed worktree at /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/fix-all-platform-positioning on feat/landing-tutorial-refresh, based on origin/develop. Separate landing and tutorial Files to preserve ownership. Official SVGs and actual app capture stay faithful; premium generated material is limited to editorial art with receipts. All browser automation is headless. No active native input without a current exclusive grant. Run current stable SpecWeave 3.1.15 session-locally. Existing 1099 remains completed and is not reopened.

## Decisions

### Defaulted

- D-01: Keep SpecWithCode, spec-weave.com/code and the existing terracotta/ink brand until Anton chooses a name/domain proposal.
- D-02: Prefer a focused authentic app preview and outcome-led flow over decorative effects. Motion progressively enhances readable resting states.
- D-03: Never synthesize or delete audio before verifying canonical identity and exact target inventory. No substitute voice. Natural voice timing determines visuals.

### Open

- Product/domain rename remains a proposal only and does not block improvements under the existing name.

## Tasks

### T-01 Produce visual direction and naming research
- AC: AC-01 | Files: docs-site/marketing/landing-refresh-1109, /Users/antonabyzov/specwithcode-promo/landing-refresh-20261027 | Test: node /Users/antonabyzov/specwithcode-promo/landing-refresh-20261027/verify-direction.mjs

### T-02 Implement landing visuals and responsive motion
- AC: AC-02 | Files: docs-site/src/pages/code.tsx, docs-site/src/pages/code.module.css, docs-site/src/components/ecosystem, docs-site/static/img/studio, docs-site/scripts/verify-seo.mjs | Test: npm --prefix docs-site run build; npx tsc --noEmit -p .; headless desktop/mobile/reduced-motion/no-JavaScript checks
- **Dependencies**: T-01

### T-03 Establish voice provenance and guarded generation
- AC: AC-03 | Files: video/tutorials, /Users/antonabyzov/specwithcode-promo/tutorial-refresh-20261027 | Test: generation preflight rejects wrong voice and stale cache without making a billed call; save catalog and cache audit evidence

### T-04 Recreate five tutorials and update playback metadata
- AC: AC-04 | Files: video/tutorials, docs-site/src/data/tutorials.json, docs-site/static/video/tutorials, /Users/antonabyzov/specwithcode-promo/tutorial-refresh-20261027 | Test: full media decode, voice receipts, captions/timing and human-readable current-flow evidence; npm --prefix docs-site run build
- **Dependencies**: T-03

### T-05 Deliver reviewed page and tutorial assets
- AC: AC-05 | Files: docs-site/marketing/landing-refresh-1109, /Users/antonabyzov/specwithcode-promo/landing-refresh-20261027 | Test: exact-head fresh review; green PR checks; merged deployment; public headless and exact-byte media verification
- **Dependencies**: T-02, T-04

### T-06 Verify and close 1109
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1109-refresh-landing-visuals-and-replace-agent-tutorials/reports | Test: specweave verify 1109 with scoped absolute-worktree commands; fresh-context review; specweave complete 1109
- **Dependencies**: T-05
