---
id: US-006
feature: FS-319
title: GitHub Events API Monitor
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1270
    url: https://github.com/anton-abyzov/specweave/issues/1270
---
# US-006: GitHub Events API Monitor

**Feature**: [FS-319](./FEATURE.md)

platform operator
**I want** real-time monitoring of GitHub push events for new SKILL.md files
**So that** newly created skills are discovered within minutes, not hours

---

## Acceptance Criteria

- [x] **AC-US6-01**: Crawl worker polls `/events` endpoint continuously (respects `X-Poll-Interval` header)
- [x] **AC-US6-02**: Filters PushEvent payloads for commits adding SKILL.md, .cursorrules, mcp.json
- [x] **AC-US6-03**: Discovered repos are submitted to platform for scanning
- [x] **AC-US6-04**: Maintains last-seen event ID to avoid duplicates across poll cycles

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)

