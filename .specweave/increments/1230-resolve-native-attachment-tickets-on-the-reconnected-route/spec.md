# Resolve native attachment tickets on the reconnected route

## Problem

A retry can mint an attachment URL using a new connection, while the caller retains the old base.

## Scope

Resolve native attachment tickets on the reconnected route and targeted regression verification.

## Acceptance Criteria
- [ ] AC-01: The returned ticket uses the route selected by the successful retry.

## Tasks
### T-01 Resolve native attachment tickets on the reconnected route
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCSyncTests/PhotoAttachmentTests.swift | Test: swift test --package-path apps/ios/SWCKit --filter PhotoAttachmentTests
