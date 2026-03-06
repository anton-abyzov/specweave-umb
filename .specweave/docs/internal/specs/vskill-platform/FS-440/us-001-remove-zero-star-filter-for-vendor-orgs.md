---
id: US-001
feature: FS-440
title: "Remove Zero-Star Filter for Vendor Orgs"
status: not_started
priority: P0
created: 2026-03-06
tldr: "**As a** user searching for official vendor skills."
project: vskill-platform
external:
  github:
    issue: 17
    url: https://github.com/anton-abyzov/vskill-platform/issues/17
---

# US-001: Remove Zero-Star Filter for Vendor Orgs

**Feature**: [FS-440](./FEATURE.md)

**As a** user searching for official vendor skills
**I want** vendor repos with zero GitHub stars to be discoverable
**So that** all vendor-published skills appear in search results regardless of star count

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a vendor org repo with 0 GitHub stars and a valid SKILL.md, when vendor-org-discovery runs, then the repo is included in discovery results (not filtered out)
- [ ] **AC-US1-02**: Given a non-vendor org repo with 0 GitHub stars, when any discovery source runs, then existing zero-star filtering behavior is unchanged
- [ ] **AC-US1-03**: Both `crawl-worker/sources/vendor-org-discovery.js` and `src/lib/crawler/vendor-org-discovery.ts` skip the zero-star filter for vendor org repos
- [ ] **AC-US1-04**: Fork repos are still filtered out regardless of vendor status

---

## Implementation

**Increment**: [0440-fix-anthropic-skills-search](../../../../../increments/0440-fix-anthropic-skills-search/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Remove zero-star filter from crawl-worker/sources/vendor-org-discovery.js
- [x] **T-004**: Remove zero-star filter from src/lib/crawler/vendor-org-discovery.ts
