---
id: US-001
feature: FS-420
title: "Vendor skills bypass discovery dedup (P0)"
status: completed
priority: P1
created: 2026-03-03T00:00:00.000Z
tldr: "**As a** vskill user searching for official skills."
project: vskill-platform
external:
  github:
    issue: 2
    url: https://github.com/anton-abyzov/vskill-platform/issues/2
---

# US-001: Vendor skills bypass discovery dedup (P0)

**Feature**: [FS-420](./FEATURE.md)

**As a** vskill user searching for official skills
**I want** vendor org skills to always be re-submitted during discovery
**So that** new skills from Anthropic, OpenAI, and other vendors appear in search automatically

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a candidate from `vendor-orgs` source where `hasBeenDiscovered` returns true, when `processRepo` processes it, then the candidate is NOT skipped and is submitted for processing
- [x] **AC-US1-02**: Given a candidate from `github-code` source where `hasBeenDiscovered` returns true, when `processRepo` processes it, then the candidate IS skipped (existing dedup behavior preserved)

---

## Implementation

**Increment**: [0420-vendor-skill-freshness](../../../../../increments/0420-vendor-skill-freshness/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Write failing tests for vendor dedup bypass (TDD RED)
- [x] **T-002**: Implement vendor dedup bypass in processRepo (TDD GREEN)
