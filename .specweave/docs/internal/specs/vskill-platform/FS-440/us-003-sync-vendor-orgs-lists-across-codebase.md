---
id: US-003
feature: FS-440
title: "Sync VENDOR_ORGS Lists Across Codebase"
status: not_started
priority: P0
created: 2026-03-06
tldr: "**As a** platform maintainer."
project: vskill-platform
external:
  github:
    issue: 21
    url: https://github.com/anton-abyzov/vskill-platform/issues/21
---

# US-003: Sync VENDOR_ORGS Lists Across Codebase

**Feature**: [FS-440](./FEATURE.md)

**As a** platform maintainer
**I want** all VENDOR_ORGS hardcoded lists to match the authoritative `trusted-orgs.ts`
**So that** vendor detection is consistent across crawler and platform

---

## Acceptance Criteria

- [ ] **AC-US3-01**: `crawl-worker/sources/vendor-org-discovery.js` VENDOR_ORGS list contains all 7 orgs: anthropics, openai, google-gemini, google, microsoft, vercel, cloudflare
- [ ] **AC-US3-02**: `crawl-worker/lib/vendor-detect.js` TRUSTED_ORGS list contains all 7 orgs matching `trusted-orgs.ts`
- [ ] **AC-US3-03**: A code comment in each JS file references `src/lib/trust/trusted-orgs.ts` as the source of truth
- [ ] **AC-US3-04**: Post-deploy: manual re-crawl of vendor orgs is triggered to pick up previously filtered repos

---

## Implementation

**Increment**: [0440-fix-anthropic-skills-search](../../../../../increments/0440-fix-anthropic-skills-search/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Sync VENDOR_ORGS in crawl-worker/sources/vendor-org-discovery.js and crawl-worker/lib/vendor-detect.js
- [x] **T-002**: Document post-deploy re-crawl step for AC-US3-04
