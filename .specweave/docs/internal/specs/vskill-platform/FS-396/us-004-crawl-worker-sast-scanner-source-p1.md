---
id: US-004
feature: FS-396
title: "Crawl-Worker SAST Scanner Source (P1)"
status: completed
priority: P1
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-004: Crawl-Worker SAST Scanner Source (P1)

**Feature**: [FS-396](./FEATURE.md)

**As a** platform operator
**I want** a `sast-scanner` crawl-worker source that pulls pending SAST scans and dispatches them to the local scanner-worker
**So that** external SAST scans run reliably without depending on push dispatch from Cloudflare Workers

---

## Acceptance Criteria

- [x] **AC-US4-01**: New file `crawl-worker/sources/sast-scanner.js` exports a default `crawl(config)` function following the crawl-worker source contract
- [x] **AC-US4-02**: The source fetches pending scans via `GET /api/v1/internal/pending-sast-scans`, claims each via `POST /api/v1/internal/claim-sast-scan`, then dispatches to `http://localhost:9500/scan` with the existing scanner-worker payload format (`{ skillName, repoOwner, repoName, provider, callbackUrl }`)
- [x] **AC-US4-03**: The source uses `X-Worker-Signature` header with `WORKER_SECRET` env var for scanner-worker auth (same as current push dispatch)
- [x] **AC-US4-04**: Failed claims (already claimed by another VM) are skipped gracefully with a log line
- [x] **AC-US4-05**: The source processes one scan at a time (sequential claim-dispatch, no concurrency within a single cycle) for simplicity
- [x] **AC-US4-06**: The crawl function returns `{ checked, dispatched, skipped, errors }` summary matching the crawl-worker source return convention

---

## Implementation

**Increment**: [0396-pull-based-sast-scanner](../../../../../increments/0396-pull-based-sast-scanner/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
