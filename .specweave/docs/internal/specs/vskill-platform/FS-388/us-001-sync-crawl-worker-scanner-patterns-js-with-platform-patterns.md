---
id: US-001
feature: FS-388
title: Sync crawl-worker scanner-patterns.js with platform patterns.ts
status: complete
priority: P2
created: 2026-02-27
project: vskill-platform
external:
  github:
    issue: 1422
    url: https://github.com/anton-abyzov/specweave/issues/1422
---
# US-001: Sync crawl-worker scanner-patterns.js with platform patterns.ts

**Feature**: [FS-388](./FEATURE.md)

platform operator
**I want** the crawl-worker scanner patterns to have the same context-aware severity downgrades as the platform-side patterns
**So that** scans on Hetzner VMs produce the same false-positive-reduced results as the platform's local scanner

---

## Acceptance Criteria

- [x] **AC-US1-01**: `scanner-patterns.js` includes `isInsideInlineCode()` function matching `patterns.ts` logic
- [x] **AC-US1-02**: `scanner-patterns.js` includes `isMarkdownProseLine()` function and `MARKDOWN_PROSE_RE`
- [x] **AC-US1-03**: `scanner-patterns.js` includes spawn context detection (`isSpawnWithSafeTarget`, `isSpawnWithDangerousPattern`, `SAFE_SPAWN_TARGETS`)
- [x] **AC-US1-04**: `scanner-patterns.js` includes CI-005 context detection (`isCi005Import`, `isExecLikeWithSafeTarget`, `isExecLikeWithDangerousPattern`)
- [x] **AC-US1-05**: `scanner-patterns.js` includes CT-003 safe reference detection (`isCt003SafeReference`)
- [x] **AC-US1-06**: `scanContent()` in `scanner-patterns.js` applies all context-aware downgrades (inline code, markdown prose, CI-002, CI-005, CT-003) matching `patterns.ts`
- [x] **AC-US1-07**: `DOCUMENTATION_SAFE_PATTERNS` set in `scanner-patterns.js` matches the platform version (includes CI-002, CI-004, CI-005, DE-005, NA-003)
- [x] **AC-US1-08**: CI-002 severity in `scanner-patterns.js` pattern definition changes from "medium" to "low" (matches platform)
- [x] **AC-US1-09**: DE-005 severity changes from "medium" to "low" (matches platform)
- [x] **AC-US1-10**: NA-003 severity changes from "medium" to "low" (matches platform)

---

## Implementation

**Increment**: [0388-pattern-guided-llm-verdict](../../../../../increments/0388-pattern-guided-llm-verdict/spec.md)

