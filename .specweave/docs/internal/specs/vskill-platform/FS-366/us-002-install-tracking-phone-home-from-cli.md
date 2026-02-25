---
id: US-002
feature: FS-366
title: Install Tracking Phone-Home from CLI
status: not_started
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1331
    url: https://github.com/anton-abyzov/specweave/issues/1331
---
# US-002: Install Tracking Phone-Home from CLI

**Feature**: [FS-366](./FEATURE.md)

**As a** platform operator,
**I want** the vskill CLI to report successful installs to the platform
**So that** `vskillInstalls` reflects real usage and feeds into trending scores.

---

## Acceptance Criteria

- [ ] **AC-US2-01**: After a successful `vskill install <skill>`, the CLI sends `POST /api/v1/skills/:name/installs` to the platform
- [ ] **AC-US2-02**: The phone-home uses the same `BASE_URL` ("https://verified-skill.com") as existing API calls
- [ ] **AC-US2-03**: The phone-home has a 2-second timeout and silently swallows ALL errors (network, HTTP, parse)
- [ ] **AC-US2-04**: The phone-home never blocks or delays the CLI command -- it runs as fire-and-forget
- [ ] **AC-US2-05**: Setting `VSKILL_NO_TELEMETRY=1` disables the phone-home entirely
- [ ] **AC-US2-06**: The platform endpoint increments `Skill.vskillInstalls` by 1 for the named skill
- [ ] **AC-US2-07**: The platform endpoint is rate-limited at 60 requests/hour per IP using existing `checkRateLimit()` from `src/lib/rate-limit.ts` with `RATE_LIMIT_KV`
- [ ] **AC-US2-08**: The platform endpoint returns 404 if the skill does not exist
- [ ] **AC-US2-09**: No deduplication of installs -- simple counter increment

---

## Implementation

**Increment**: [0366-orphan-cleanup-install-tracking](../../../../../increments/0366-orphan-cleanup-install-tracking/spec.md)

## Tasks

_Not started_
