---
id: US-003
feature: FS-393
title: "Multi-Token GitHub Support in CF Worker (P1)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-003: Multi-Token GitHub Support in CF Worker (P1)

**Feature**: [FS-393](./FEATURE.md)

**As a** platform operator
**I want** the CF Worker consumer to support multiple GitHub PATs via comma-separated `GITHUB_TOKENS` env var
**So that** rate limits are distributed across 3-5 tokens, increasing effective throughput from 5000 to 15000-25000 req/hr

---

## Acceptance Criteria

- [x] **AC-US3-01**: `consumer.ts` reads `GITHUB_TOKENS` (comma-separated) from env, falling back to `GITHUB_TOKEN` (single) for backward compatibility
- [x] **AC-US3-02**: A `TokenRotator` utility is created in `src/lib/token-rotator.ts` that round-robin rotates through available tokens
- [x] **AC-US3-03**: The rotator is passed to `processSubmission` via the `githubToken` option, providing a fresh token per submission
- [x] **AC-US3-04**: `env.d.ts` is updated to declare the `GITHUB_TOKENS` binding
- [x] **AC-US3-05**: `.env.example` in `crawl-worker/` documents the `GITHUB_TOKENS` format (already present, verify accuracy)

---

## Implementation

**Increment**: [0393-crawl-pipeline-throughput](../../../../../increments/0393-crawl-pipeline-throughput/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
