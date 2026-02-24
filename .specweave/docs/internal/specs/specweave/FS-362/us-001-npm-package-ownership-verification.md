---
id: US-001
feature: FS-362
title: npm Package Ownership Verification
status: completed
priority: P1
created: 2026-02-24
tldr: npm Package Ownership Verification
external:
  github:
    issue: 1311
    url: https://github.com/anton-abyzov/specweave/issues/1311
---

# US-001: npm Package Ownership Verification

**Feature**: [FS-362](./FEATURE.md)

---

## Acceptance Criteria

- [x] **AC-US1-01**: Prisma schema has `npmPackageVerified Boolean @default(false)` on Skill model
- [x] **AC-US1-02**: `normalizeNpmRepoUrl()` handles git+, git://, SSH, github: shorthand formats
- [x] **AC-US1-03**: Enrichment fetches npm registry metadata for unverified skills
- [x] **AC-US1-04**: When npm `repository.url` matches skill `repoUrl`, sets `npmPackageVerified = true`
- [x] **AC-US1-05**: When npm `repository.url` mismatches, clears `npmPackage = null` and `npmDownloads = 0`
- [x] **AC-US1-06**: When npm registry fetch fails, skips verification (no data loss)
- [x] **AC-US1-07**: Already-verified skills skip registry fetch on subsequent cycles
- [x] **AC-US1-08**: Stats queries filter by `npmPackageVerified = true` for npm counts/downloads
- [x] **AC-US1-09**: Admin bulk enrich endpoint also performs verification
- [x] **AC-US1-10**: All existing tests pass, new tests cover verification scenarios

---

## Implementation

**Increment**: [0362-validate-npm-package-ownership](../../../../../increments/0362-validate-npm-package-ownership/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
