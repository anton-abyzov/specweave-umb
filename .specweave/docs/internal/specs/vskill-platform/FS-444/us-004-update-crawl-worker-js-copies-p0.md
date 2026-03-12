---
id: US-004
feature: FS-444
title: "Update Crawl-Worker JS Copies (P0)"
status: completed
priority: P0
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** platform developer."
project: vskill-platform
external:
  github:
    issue: 34
    url: "https://github.com/anton-abyzov/vskill-platform/issues/34"
---

# US-004: Update Crawl-Worker JS Copies (P0)

**Feature**: [FS-444](./FEATURE.md)

**As a** platform developer
**I want** all 4 crawl-worker JavaScript files to include framework plugin filtering
**So that** the crawl workers (running on Hetzner VMs) also reject framework plugin paths

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given `crawl-worker/lib/repo-files.js`, when updated, then it exports `isFrameworkPluginPath()` and `shouldRejectSkillPath()` alongside existing exports
- [x] **AC-US4-02**: Given `crawl-worker/lib/skill-discovery.js`, when updated, then it imports and uses `shouldRejectSkillPath` from `repo-files.js`
- [x] **AC-US4-03**: Given `crawl-worker/sources/queue-processor.js`, when updated, then it has an inline `isFrameworkPluginPath()` and combined check (does not import from repo-files)
- [x] **AC-US4-04**: Given `crawl-worker/sources/vendor-org-discovery.js`, when updated, then it has an inline framework plugin regex and combined check (does not import from repo-files)

---

## Implementation

**Increment**: [0444-filter-framework-plugin-skills](../../../../../increments/0444-filter-framework-plugin-skills/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: Update crawl-worker/lib/repo-files.js and skill-discovery.js
- [x] **T-011**: Update crawl-worker/sources/queue-processor.js (inline copy)
- [x] **T-012**: Update crawl-worker/sources/vendor-org-discovery.js (inline copy)
