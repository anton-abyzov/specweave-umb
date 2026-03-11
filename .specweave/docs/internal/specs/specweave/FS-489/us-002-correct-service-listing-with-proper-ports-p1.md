---
id: US-002
feature: FS-489
title: "Correct service listing with proper ports (P1)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** developer viewing the Services page."
project: specweave
external:
  github:
    issue: 1535
    url: https://github.com/anton-abyzov/specweave/issues/1535
---

# US-002: Correct service listing with proper ports (P1)

**Feature**: [FS-489](./FEATURE.md)

**As a** developer viewing the Services page
**I want** to see "Internal Docs" and "Public Docs" as separate services with correct port status
**So that** I know which documentation server is running and on which port

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the `/api/services` endpoint, when called, then it returns two docs services: "Internal Docs" (checking port 3015) and "Public Docs" (checking port 3016)
- [x] **AC-US2-02**: Given a docs service entry, when the port is reachable, then the service status is "running"; otherwise "stopped"
- [x] **AC-US2-03**: Given the old "Docs Preview" service, when the code is updated, then it no longer appears in the service list
- [x] **AC-US2-04**: Given SCOPE_PORTS from `docs-preview/types.ts`, when ports are resolved, then the server uses these constants (not hardcoded 3000 or config fallback)

---

## Implementation

**Increment**: [0489-dashboard-docs-services](../../../../../increments/0489-dashboard-docs-services/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-002**: Update /api/services in dashboard-server.ts
- [x] **T-005**: Build and manual smoke test
