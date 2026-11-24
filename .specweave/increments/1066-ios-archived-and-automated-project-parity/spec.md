# 1066 iOS Archived and Automated project parity

## Problem
SpecWithCode iOS has no Archived drawer section and merged project archive state inherits its primary member. The reported Automated 5 versus desktop 1 needs a matched host/account/logical-project/member snapshot before a cause or corrected total can be claimed. Totals count project groups, not threads or requests.

## Scope
In: apps/ios project grouping, partition presentation, Swift tests and isolated simulator proof; read-only desktop comparison. Preserve explicit logical identity or same environment plus normalized folder grouping. Out: server/shared edits, project mutation, physical phone use, deployment, restart, release and merge. Preserve /Users/antonabyzov/.specwithcode/m4/worktrees/ios-thread-grouping read-only.

## Acceptance Criteria
- [ ] AC-01: Record exact source, host/account scope, logical IDs, member identities, archive/origin flags and freshness for the compared snapshot; unknown historical facts remain explicit.
- [ ] AC-02: A group is archived only when all real members are archived; primary choice and offline cached members do not change this rule.
- [ ] AC-03: The drawer exposes a folded Archived section with separate project-group totals; archived automated groups appear only there. Automated counts match desktop for the same snapshot and scope, without deleting or reclassifying records.
- [ ] AC-04: Identity regressions preserve distinct same-title/same-remote projects. The 1040 attention/working contract is preserved; partial/offline evidence is not presented as zero or Idle.
- [ ] AC-05: Swift tests and simulator UI checks pass with saved screenshots; a fresh native review has no unresolved findings; the PR exact head passes CI and remains unmerged.

## Approach
Inspect current ShellSummaries, AppModel and DrawerView and desktop grouping read-only. Capture the available matched snapshot before attributing the reported difference. Aggregate archive flags across real copies; partition groups after merging; expose Archived in the drawer. Extend focused Swift coverage and a deterministic simulator fixture. Coordinate any server/shared dependency with its existing owner. Save evidence under /Users/antonabyzov/.specwithcode/m4/evidence/1066-ios-project-parity.

## Decisions
### Asked
- The user owns merge and physical phone/release authorization.
### Defaulted
- Keep cached members visible and retain explicit freshness uncertainty.
- No title or remote based deduplication and no project writes to equalize totals.
### Open
- none

## Tasks

### T-01 Inspect matched scope and implement iOS partition parity
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift, apps/ios/SWCKit/Sources/SWCSync/AppModel.swift, apps/ios/SWCKit/Sources/SWCFeatures/Drawer/DrawerView.swift, apps/ios/SWCKit/Sources/SWCSync/FixtureDuplicates.swift, apps/ios/SWCKit/Tests/SWCSyncTests/ShellSummariesTests.swift, apps/ios/UITests/DrawerUITests.swift | Test: cd apps/ios/SWCKit && swift test

### T-02 Verify simulator, fresh review and exact-head PR CI
- AC: AC-05 | Files: apps/ios/UITests/DrawerUITests.swift | Test: cd apps/ios && make sim-test ONLY=SpecWithCodeUITests/DrawerUITests

### T-03 Verify and close 1066
- AC: AC-05 | Files: none | Test: specweave verify 1066
