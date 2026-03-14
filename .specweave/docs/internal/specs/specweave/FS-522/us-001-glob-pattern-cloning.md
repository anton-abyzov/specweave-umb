---
id: US-001
feature: FS-522
title: "Glob pattern cloning"
status: completed
priority: P1
created: 2026-03-14
tldr: "**As a** developer onboarding a new team workspace,."
project: specweave
---

# US-001: Glob pattern cloning

**Feature**: [FS-522](./FEATURE.md)

**As a** developer onboarding a new team workspace,
**I want to** run `specweave get "acme-corp/service-*"` to clone all repos matching a glob,
**So that** I don't need to run 30 individual `specweave get` commands.

**Acceptance Criteria:**
- [x] AC-US1-01: `specweave get "org/prefix-*"` detects glob pattern and enters bulk mode
- [x] AC-US1-02: GitHub org repos are fetched (up to 1000, paginated) and filtered by glob
- [x] AC-US1-03: Matching repos are queued in a background clone job via `launchCloneJob()`
- [x] AC-US1-04: User sees "Found N repos matching pattern-*. Launching background clone job..."
- [x] AC-US1-05: `specweave get "org/*"` clones all repos in org (null pattern = no filter)

---

## Acceptance Criteria

- [x] **AC-US1-01**: `specweave get "org/prefix-*"` detects glob pattern and enters bulk mode
- [x] **AC-US1-02**: GitHub org repos are fetched (up to 1000, paginated) and filtered by glob
- [x] **AC-US1-03**: Matching repos are queued in a background clone job via `launchCloneJob()`
- [x] **AC-US1-04**: User sees "Found N repos matching pattern-*. Launching background clone job..."
- [x] **AC-US1-05**: `specweave get "org/*"` clones all repos in org (null pattern = no filter)

---

## Implementation

**Increment**: [0522-specweave-get-bulk](../../../../../increments/0522-specweave-get-bulk/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: get command bulk path — unit tests (RED)
- [x] **T-005**: get.ts — implement bulk path (GREEN)
