# 1200 Preserve existing checkouts when linked repository cloning fails

## Problem

A failed linked-project clone can delete a checkout another request or person created at the same destination.

## Scope

Linked-project repository cloning and its failure cleanup.

## Acceptance Criteria

- [ ] AC-01 A failed clone cleans up its own partial files and preserves an independently populated destination.
- [ ] AC-02 Concurrent attempts for the same checkout cannot both clone.

## Approach

Reserve a destination before inspecting it. Clone into an owned staging directory on the same volume and publish only if the destination remains available. Remove only owned staging files.

## Tasks

### T-01 Stage and publish repository clones safely

- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectRepositoryPresence.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectRepositoryPresence.test.ts | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectRepositoryPresence.test.ts
