---
id: US-004
feature: FS-499
title: "Sync Gap Detection CLI (P1)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** SpecWeave user."
project: specweave
---

# US-004: Sync Gap Detection CLI (P1)

**Feature**: [FS-499](./FEATURE.md)

**As a** SpecWeave user
**I want** CLI commands to detect and remediate sync gaps
**So that** I can verify all increments are properly synced to configured providers and fix any that are not

---

## Acceptance Criteria

- [ ] **AC-US4-01**: Given the user runs `specweave sync-gaps`, when increments have metadata with partial provider coverage (e.g., synced to GitHub but not JIRA), then each gap is listed with increment ID, synced providers, and missing providers
- [ ] **AC-US4-02**: Given the user runs `specweave sync-gaps --fix`, when gaps are detected, then the command attempts the missing provider syncs for each listed increment
- [ ] **AC-US4-03**: Given the user runs `specweave sync-gaps --json`, when gaps exist, then the output is a valid JSON array with objects containing incrementId, syncedProviders, missingProviders, and lastSyncTimestamp
- [ ] **AC-US4-04**: Given the user runs `specweave sync-status`, when the sync infrastructure is active, then the output shows retry queue depth, per-provider circuit breaker state, and rate limit remaining counts
- [ ] **AC-US4-05**: Given the user runs `specweave sync-gaps` or `specweave sync-status`, when issues are found, then the command exits with a non-zero exit code

---

## Implementation

**Increment**: [0499-external-sync-resilience](../../../../../increments/0499-external-sync-resilience/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-011**: Implement sync-gaps CLI command
- [ ] **T-012**: Implement sync-status CLI command
- [ ] **T-013**: Register all CLI commands and add graceful missing-file guards
