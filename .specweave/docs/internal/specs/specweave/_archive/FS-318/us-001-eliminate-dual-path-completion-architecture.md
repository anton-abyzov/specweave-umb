---
id: US-001
feature: FS-318
title: Eliminate dual-path completion architecture
status: complete
priority: P1
created: 2026-02-22
project: specweave
external:
  github:
    issue: 1254
    url: https://github.com/anton-abyzov/specweave/issues/1254
---
# US-001: Eliminate dual-path completion architecture

**Feature**: [FS-318](./FEATURE.md)

SpecWeave framework maintainer
**I want** the `/sw:done` skill to use the CLI `completeIncrement()` function as its single completion path
**So that** post-closure hooks (living docs sync, GitHub issue closure, external sync) fire reliably regardless of how an increment is closed

---

## Acceptance Criteria

- [x] **AC-US1-01**: The done skill's Step 8 instructs the LLM to call `specweave complete <id>` CLI command instead of directly editing metadata.json
- [x] **AC-US1-02**: `completeIncrement()` in `status-commands.ts` awaits `LifecycleHookDispatcher.onIncrementDone()` instead of fire-and-forget (void async IIFE)
- [x] **AC-US1-03**: The fire-and-forget pattern is replaced with a logged-but-non-blocking await pattern that reports hook results to the user
- [x] **AC-US1-04**: Existing unit tests for `completeIncrement()` continue to pass

---

## Implementation

**Increment**: [0318-post-closure-sync-pipeline](../../../../../increments/0318-post-closure-sync-pipeline/spec.md)

