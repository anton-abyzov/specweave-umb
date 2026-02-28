---
id: US-001
feature: FS-378
title: "External Report Links"
status: completed
priority: P1
created: 2026-02-28
tldr: "**As a** skill consumer reviewing security data,
**I want to** see links to Socket."
---

# US-001: External Report Links

**Feature**: [FS-378](./FEATURE.md)

**As a** skill consumer reviewing security data,
**I want to** see links to Socket.dev and Snyk public reports for the skill's npm package,
**So that** I can access detailed third-party security analysis without leaving the platform.

**Acceptance Criteria:**
- [x] AC-US1-01: Security page shows Socket.dev report link for skills with npmPackage
- [x] AC-US1-02: Security page shows Snyk advisory link for skills with npmPackage
- [x] AC-US1-03: Skills without npmPackage show "Not on npm" message instead

---

## Acceptance Criteria

- [x] **AC-US1-01**: Security page shows Socket.dev report link for skills with npmPackage
- [x] **AC-US1-02**: Security page shows Snyk advisory link for skills with npmPackage
- [x] **AC-US1-03**: Skills without npmPackage show "Not on npm" message instead

---

## Implementation

**Increment**: [0378-snyk-scanner-external-report-links](../../../../../increments/0378-snyk-scanner-external-report-links/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add ExternalIntelligence type and fetcher to security-report.ts
- [x] **T-002**: Add tests for externalIntelligence
- [x] **T-003**: Render External Intelligence card on security page
- [x] **T-004**: Run tests and verify build
