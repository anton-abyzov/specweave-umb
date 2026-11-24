# Keep selected photos attached when sending native chat

## Problem

The composer can send text while a selected photo is still loading.

## Scope

Keep selected photos attached when sending native chat and targeted regression verification.

## Acceptance Criteria
- [ ] AC-01: Pending photo loads and encoding block send until all batches settle.

## Tasks
### T-01 Keep selected photos attached when sending native chat
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatAttachments.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCFeaturesTests/NavigationTests.swift | Test: swift test --package-path apps/ios/SWCKit
