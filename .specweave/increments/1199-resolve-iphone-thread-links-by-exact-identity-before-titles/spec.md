# 1199 Resolve iPhone thread links by exact identity before titles

## Problem

Title fallback can open the wrong chat when the linked chat is archived or deleted on another paired machine.

## Scope

Resolve exact live and archived identities before a title fallback. Keep the existing behavior for links that name an unloaded machine.

## Acceptance Criteria

- [ ] AC-01 An exact remote tombstone wins over an unrelated title match.
- [ ] AC-02 An exact archived ID wins over a live chat whose title matches the link.

## Approach

Omit title candidates on the first live lookup. Preserve remote tombstones if no paired machine has a live exact match. Merge archived records before the title fallback.

## Tasks

### T-01 Fix native iPhone thread resolution

- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/ThreadLinkResolver.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/IncrementProgress.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCSyncTests/ThreadLinkResolverTests.swift | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit" && swift test --jobs 2 --filter ThreadLinkResolverTests
