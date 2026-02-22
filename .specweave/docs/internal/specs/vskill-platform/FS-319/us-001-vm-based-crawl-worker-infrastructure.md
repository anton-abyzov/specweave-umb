---
id: US-001
feature: FS-319
title: VM-Based Crawl Worker Infrastructure
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1264
    url: https://github.com/anton-abyzov/specweave/issues/1264
---
# US-001: VM-Based Crawl Worker Infrastructure

**Feature**: [FS-319](./FEATURE.md)

platform operator
**I want** crawl workers running on Hetzner VMs alongside scanner workers
**So that** discovery can run for minutes/hours without Cloudflare Worker 30s timeouts

---

## Acceptance Criteria

- [x] **AC-US1-01**: Crawl worker HTTP server runs on port 9600 with `/health`, `/POST /crawl`, `/GET /status` endpoints
- [x] **AC-US1-02**: Auth via `X-Worker-Signature` header (same pattern as scanner-worker)
- [x] **AC-US1-03**: Docker Compose adds crawl-worker service alongside scanner-worker on same VMs
- [x] **AC-US1-04**: Deploy script SCPs crawl-worker files and health-checks port 9600
- [x] **AC-US1-05**: CF Worker dispatches crawl jobs to VMs via round-robin (like external-scan-dispatch.ts)

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)

