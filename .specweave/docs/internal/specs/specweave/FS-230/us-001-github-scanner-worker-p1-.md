---
id: US-001
feature: FS-230
title: "GitHub Scanner Worker (P1)"
status: completed
priority: P1
created: 2026-02-16T00:00:00.000Z
tldr: "**As a** marketplace operator
**I want** a background worker that scans GitHub for community Claude Code skills
**So that** the marketplace automatically discovers new skills without manual effort."
project: specweave
---

# US-001: GitHub Scanner Worker (P1)

**Feature**: [FS-230](./FEATURE.md)

**As a** marketplace operator
**I want** a background worker that scans GitHub for community Claude Code skills
**So that** the marketplace automatically discovers new skills without manual effort

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given configured search topics, when scanner runs, then it queries GitHub Search API for repos matching topics/filenames
- [x] **AC-US1-02**: Given GitHub rate limits, when limit is approached, then scanner applies exponential backoff
- [x] **AC-US1-03**: Given a scanner crash, when restarted, then it resumes from last checkpoint cursor
- [x] **AC-US1-04**: Given a previously discovered repo, when seen again, then it is skipped (dedup by full_name)
- [x] **AC-US1-05**: Given config with intervalMinutes=30, when scanner runs, then it sleeps 30 min between scans

---

## Implementation

**Increment**: [0230-marketplace-scanner-dashboard](../../../../../increments/0230-marketplace-scanner-dashboard/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
