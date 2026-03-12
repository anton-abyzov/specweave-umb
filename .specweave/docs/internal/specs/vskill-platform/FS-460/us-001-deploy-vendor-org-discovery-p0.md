---
id: US-001
feature: FS-460
title: "Deploy vendor-org-discovery (P0)"
status: completed
priority: P0
created: "2026-03-09T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
related_projects: [vskill]
external:
  github:
    issue: 46
    url: "https://github.com/anton-abyzov/vskill-platform/issues/46"
---

# US-001: Deploy vendor-org-discovery (P0)

**Feature**: [FS-460](./FEATURE.md)

**As a** platform operator
**I want** vendor-org-discovery deployed to VM-2
**So that** vendor skills from Anthropic, OpenAI, and other trusted orgs are discovered and indexed in the registry

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given VM-2 env file at `crawl-worker/.env.vm2`, when deployment runs via `deploy.sh`, then `vendor-org-discovery` is present in `ASSIGNED_SOURCES` and the crawl-worker starts without errors
- [x] **AC-US1-02**: Given the crawl-worker is running on VM-2, when the health endpoint is queried, then the response includes `vendor-org-discovery` as an active source
- [x] **AC-US1-03**: Given vendor-org-discovery has run at least once, when a user searches `vskill find frontend-design`, then Anthropic skills appear in results with `certTier: CERTIFIED` and `trustTier: T4`
- [x] **AC-US1-04**: Given the admin vendor-orgs endpoint exists, when an on-demand discovery is triggered via `POST /api/v1/admin/discovery/vendor-orgs`, then the response includes `orgBreakdown` with skill counts per vendor org

---

## Implementation

**Increment**: [0460-vendor-provider-discovery](../../../../../increments/0460-vendor-provider-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Verify .env.vm2 includes vendor-org-discovery and run deploy.sh
- [x] **T-005**: Trigger on-demand discovery and verify vendor skills are indexed
