# 1114 Original agent convergence ad

## Problem
Anton requested a polished original SpecWithCode ad informed by David Ondrej's October 28 Cloudroom post, produced and published to verified X and TikTok brand accounts with additional appropriate Postiz placement. The reference must inform pacing, not be copied or reused.

## Scope
In: deep reference analysis, accurate current product/source evidence, original physical-item/agent convergence concept, short rendered film and vertical adaptation, sound, factual and creative review, dedup and account identity checks, organic publication and public/provider verification. Premium Kie deliberate generation is authorized with cost receipts. Out: paid ads, fabricated UI/endorsements, unsupported remote/Connect claims, copying reference media, unrelated campaigns/posts, desktop restart/release, native foreground input, family YouTube.

## Acceptance Criteria
- [ ] AC-01: Source reference media is inspected and original storyboard/script identifies factual evidence and distinct creative choices.
- [ ] AC-02: Finished revised ad uses a simple hockey-goal metaphor with more current officially verified recognizable agent icons, minimal text and a punchier professionally generated instrumental; faithful product assets, readable mobile/landscape framing, inspected proof frames, full decode and source/cost provenance.
- [ ] AC-03: Current queues and account identities are checked, no duplicate creates occur, X and TikTok use Blotato, other selected placement uses Postiz, and receipts distinguish provider publication from public playback.
- [ ] AC-04: Final evidence and fresh review support scoped verification and completion without unresolved production or publication claims.

## Approach
Work only in /Users/antonabyzov/specwithcode-promo/agent-ad-20261028. Existing tutorial worker retains 1109 and product source. Read reference metadata and locally downloaded 12-second film; original narrative brings agents into one brief rather than copying the reference's trash-bin metaphor. Use official SVG marks and genuine app crop/demo with capture version disclosed. No narration required for a concise motion-led piece; if used, only verified Anton ElevenLabs voice. Inspect complete queues and rolling TikTok destination limits before creates. Preserve ambiguous pending receipts, never replay them. Review before render/publication. Existing user instruction explicitly authorizes producing and publishing this ad, so no redundant per-post permission gate.

## Decisions

User revision: more agent icons, one-by-one hockey shots into a SpecWithCode net. Replace separate interfaces in the metaphor, never imply replacement of the supported agents. Every mark requires current official provenance and visible theme contrast. No guarantee of virality. Hold further publication until revised media is inspected.
### Defaulted
- D-01: Brand @specwithcode on X and TikTok; one additional brand Postiz placement after queue check. Do not add YouTube.
- D-02: Original agent convergence with real app proof; no reference media in finished assets, no implication providers should be uninstalled.
- D-03: Short motion-led film, sound effects and rights-safe audio; narration only if useful and verified sole voice.
### Open
- None required before production.

## Tasks
### T-01 Analyze reference and verify creative claims
- AC: AC-01 | Files: /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/reference, /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/BRIEF.md, /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/STORYBOARD.md | Test: python3 -m json.tool /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/reference/post.json

### T-02 Produce and inspect original ad
- AC: AC-02 | Files: /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/creative | Test: ffmpeg -v error -i /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/creative/renders/video.mp4 -f null -
- **Dependencies**: T-01

### T-05 Apply shorter icon-motion and professional-music revision
- AC: AC-02 | Files: /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/creative | Test: ffmpeg -v error -i /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/creative/renders/video-portrait.mp4 -f null -
- **Dependencies**: T-02

### T-03 Verify destinations and publish once
- AC: AC-03 | Files: /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/publish | Test: python3 -m json.tool /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/publish/readback.json
- **Dependencies**: T-02, T-05

### T-06 Build verified-icon hockey revision with stronger professional music
- AC: AC-02 | Files: /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/creative | Test: ffmpeg -v error -i /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/creative/renders/video-portrait.mp4 -f null -

### T-07 Deliver corrected Meta posts and queued TikTok ad
- AC: AC-03 | Files: /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/publish | Test: python3 -m json.tool /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/publish/readback.json
- **Dependencies**: T-06

### T-04 Verify and close 1114
- AC: AC-01, AC-02, AC-03, AC-04 | Files: /Users/antonabyzov/specwithcode-promo/agent-ad-20261028/REPORT.md | Test: specweave verify 1114 with scoped artifact commands; fresh review; specweave complete 1114
- **Dependencies**: T-03
