---
id: US-002
feature: FS-522
title: "--all flag cloning"
status: completed
priority: P1
created: 2026-03-14
tldr: "**As a** developer,."
project: specweave
---

# US-002: --all flag cloning

**Feature**: [FS-522](./FEATURE.md)

**As a** developer,
**I want to** run `specweave get --all acme-corp` to clone every repo in an org,
**So that** I can clone an entire organization without a wildcard expression.

**Acceptance Criteria:**
- [x] AC-US2-01: `specweave get --all acme-corp` treats source as org name and enters bulk mode
- [x] AC-US2-02: Combined with `--pattern "service-*"` acts as glob filter on the org

---

## Acceptance Criteria

- [x] **AC-US2-01**: `specweave get --all acme-corp` treats source as org name and enters bulk mode
- [x] **AC-US2-02**: Combined with `--pattern "service-*"` acts as glob filter on the org

---

## Implementation

**Increment**: [0522-specweave-get-bulk](../../../../../increments/0522-specweave-get-bulk/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: bin/specweave.js — add bulk CLI options
