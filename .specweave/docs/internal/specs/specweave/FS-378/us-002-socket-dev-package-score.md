---
id: US-002
feature: FS-378
title: "Socket.dev Package Score"
status: completed
priority: P1
created: 2026-02-28
tldr: "**As a** skill consumer,
**I want to** see the Socket."
---

# US-002: Socket.dev Package Score

**Feature**: [FS-378](./FEATURE.md)

**As a** skill consumer,
**I want to** see the Socket.dev supply chain score for the skill's own npm package,
**So that** I can assess the package-level risk alongside dependency-level scores.

**Acceptance Criteria:**
- [x] AC-US2-01: UnifiedSecurityReport includes externalIntelligence field with Socket.dev score
- [x] AC-US2-02: Socket.dev score fetched via existing fetchSocketScores client with KV caching (24h TTL)
- [x] AC-US2-03: Score breakdown shows supplyChain, vulnerability, quality, maintenance, license percentages
- [x] AC-US2-04: Graceful degradation when Socket.dev API is unavailable (shows "unavailable", links still present)

## Technical Decisions
- Snyk: Link only, no API fetching (deferred)
- Socket.dev: Reuse existing socket-client.ts (no new code)
- Caching: Existing fetchSocketScores KV cache (socket:npm:{name}, 24h TTL)
- Storage: New field on UnifiedSecurityReport (not in external-scan-store)
- Trust score: Not modified (data surfacing only, score integration deferred)

---

## Acceptance Criteria

- [x] **AC-US2-01**: UnifiedSecurityReport includes externalIntelligence field with Socket.dev score
- [x] **AC-US2-02**: Socket.dev score fetched via existing fetchSocketScores client with KV caching (24h TTL)
- [x] **AC-US2-03**: Score breakdown shows supplyChain, vulnerability, quality, maintenance, license percentages
- [x] **AC-US2-04**: Graceful degradation when Socket.dev API is unavailable (shows "unavailable", links still present)

---

## Implementation

**Increment**: [0378-snyk-scanner-external-report-links](../../../../../increments/0378-snyk-scanner-external-report-links/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
