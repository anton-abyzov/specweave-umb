# 1000 iOS thread list desktop parity

## Problem
The iPhone drawer has a flat eight-chat list and project threads lack recognizable provider/model identity. Desktop and iOS use different grouping labels and attention rules.

## Scope
In: iOS recent date groups, project state groups, provider/model identity on thread rows, deterministic simulator fixtures and screenshots, PR and CI verification.
Out: physical iPhone installs, releases, provider routing or server mutations.

## Acceptance Criteria
- [ ] AC-01: Recent chats use Today, Yesterday, Previous 7 days, Previous 30 days and Older in local calendar order; project threads use Waiting on you, Working, Idle and Resolved with offline state explicit on rows.
- [ ] AC-02: Recent, project and search thread rows show recognizable provider/model marks and readable names, preserving unknown/custom identities and accessible labels.
- [ ] AC-03: Swift tests and simulator UI checks pass with retained light/dark screenshots; a PR is opened and CI passes.

## Approach
Port the desktop calendar and state precedence into pure iOS presentation logic. Carry provider catalog labels and stable activity timestamps through shell summaries. Bundle the existing desktop provider marks for offline native rendering. Keep coordinator selection and explicit Threads navigation. Run simulator checks in the owned worktree and retain evidence.

## Decisions
### Asked
- None. Scope is explicit.
### Defaulted
- Keep project selection opening the coordinator; grouped threads remain available via the existing Threads control.
- Show offline threads under Idle, retaining their Unknown/offline row labels, matching desktop.
- Date groups cover the existing thirty-chat model limit with an explicit Show more control.
### Open
- None.

## Tasks
### T-01 Match lists and identity
- AC: AC-01, AC-02 | Files: apps/ios/SWCKit/Sources, apps/ios/SWCKit/Tests, apps/ios/UITests | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/ios-thread-grouping/apps/ios/SWCKit && swift test --no-parallel

### T-02 Simulator proof, PR and CI. Verify and close 1000
- AC: AC-03 | Files: apps/ios/UITests, apps/ios/docs | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/ios-thread-grouping/apps/ios && SIM_NAME=SWC-Thread-Lists make sim-test ONLY=SpecWithCodeUITests/ThreadListParityUITests
