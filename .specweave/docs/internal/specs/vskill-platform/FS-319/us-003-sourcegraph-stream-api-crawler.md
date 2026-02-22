---
id: US-003
feature: FS-319
title: Sourcegraph Stream API Crawler
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1267
    url: https://github.com/anton-abyzov/specweave/issues/1267
---
# US-003: Sourcegraph Stream API Crawler

**Feature**: [FS-319](./FEATURE.md)

platform operator
**I want** to discover skills via Sourcegraph's Stream API
**So that** I get the highest-yield single-query discovery (5k-50k repos, no auth)

---

## Acceptance Criteria

- [x] **AC-US3-01**: Crawl worker queries `sourcegraph.com/.api/search/stream?q=type:path file:SKILL.md count:all`
- [x] **AC-US3-02**: Also searches for `.cursorrules`, `mcp.json`, `.claude/commands/*.md`, `claude.config.json`
- [x] **AC-US3-03**: Parses SSE stream, extracts repo full names and file paths
- [x] **AC-US3-04**: Batch-submits results to platform via bulk endpoint
- [x] **AC-US3-05**: Handles streaming errors, timeouts, and partial results gracefully

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)

