---
status: completed
---
# 0378: External Intelligence for Security Reports

## Overview
Add an "External Intelligence" section to the skill security report that surfaces the skill's own npm package-level Socket.dev score and links to public Snyk and Socket.dev security reports.

## User Stories

### US-001: External Report Links
**As a** skill consumer reviewing security data,
**I want to** see links to Socket.dev and Snyk public reports for the skill's npm package,
**So that** I can access detailed third-party security analysis without leaving the platform.

**Acceptance Criteria:**
- [x] AC-US1-01: Security page shows Socket.dev report link for skills with npmPackage
- [x] AC-US1-02: Security page shows Snyk advisory link for skills with npmPackage
- [x] AC-US1-03: Skills without npmPackage show "Not on npm" message instead

### US-002: Socket.dev Package Score
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
