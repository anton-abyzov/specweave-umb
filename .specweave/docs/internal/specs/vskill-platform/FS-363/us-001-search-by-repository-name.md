---
id: US-001
feature: FS-363
title: Search by repository name
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
external:
  github:
    issue: 1325
    url: https://github.com/anton-abyzov/specweave/issues/1325
---
# US-001: Search by repository name

**Feature**: [FS-363](./FEATURE.md)

**As a** user searching for skills from a specific repository,
**I want** the search to match against the repository name,
**So that** I can find all skills from a given repository.

---

## Acceptance Criteria

- [x] **AC-US1-01**: Searching "spec" returns skills from the specweave repository regardless of skill name
- [x] **AC-US1-02**: `repoUrl` is included in the Postgres search vector (weight D)
- [x] **AC-US1-03**: URL is tokenized properly (non-alphanumeric chars → spaces) before indexing

---

## Implementation

**Increment**: [0363-search-repo-name-matching](../../../../../increments/0363-search-repo-name-matching/spec.md)

**Tasks**: See increment tasks.md for implementation details.

## Tasks

_Completed_
