# Verify — 1199-resolve-iphone-thread-links-by-exact-identity-before-titles

PASS · 2026-11-03T23:57:39.604Z · commands from explicit

## Commands

### `cd "$HOME/.specwithcode/m4/worktrees/specwithcode-dev/recent-features-followup-20261103/apps/ios/SWCKit" && test "$(git rev-parse --short=10 HEAD)" = c70a90e702 && swift test --jobs 2 --filter ThreadLinkResolverTests` → exit 0 (37s)

```
[200/201] Linking SWCKitPackageTests
Build complete! (35.08s)
Test Suite 'Selected tests' started at 2026-11-03 18:57:39.535.
Test Suite 'SWCKitPackageTests.xctest' started at 2026-11-03 18:57:39.536.
Test Suite 'SWCKitPackageTests.xctest' passed at 2026-11-03 18:57:39.536.
	 Executed 0 tests, with 0 failures (0 unexpected) in 0.000 (0.000) seconds
Test Suite 'Selected tests' passed at 2026-11-03 18:57:39.536.
	 Executed 0 tests, with 0 failures (0 unexpected) in 0.000 (0.001) seconds
◇ Test run started.
↳ Testing Library Version: 1501
↳ Target Platform: arm64e-apple-macos14.0
◇ Suite ThreadLinkResolverTests started.
◇ Test firstLookupWaitsForAnArchiveWhenTheBareOriginIsUnloaded() started.
◇ Test aTitleWithASlashIsNotAMachine() started.
◇ Test archivedThreadsOpenAfterTheSecondRead() started.
◇ Test aLabelTitleIsTheLastResort() started.
◇ Test deletedAndUnpairedSaySo() started.
◇ Test aBareLinkWaitsForEveryMachine() started.
◇ Test theIdAsWrittenStillMatches() started.
◇ Test anArchivedExactIdOutranksALiveTitleInAppModel() started.
◇ Test bareLinkOpensAWorkerTheDrawerHides() started.
◇ Test anArchivedThreadOnAHealthyMachineOutranksAMachineStillLoading() started.
◇ Test namedMachineOpensThere() started.
◇ Test namedMachineIsNeverLeft() started.
◇ Test aUniqueTitleOpens() started.
◇ Test bareLinkFindsAWorkerOnAnotherMachine() started.
◇ Test aTitleTwoThreadsShareDoesNot() started.
◇ Test aMachineThatHasNotAnsweredOpensTheChatInstead() started.
◇ Test anExactRemoteTombstoneOutranksALocalTitle() started.
◇ Test aSlashTitleNeverFallsBackToItsLastSegment() started.
✔ Test aTitleTwoThreadsShareDoesNot() passed after 0.001 seconds.
✔ Test namedMachineIsNeverLeft() passed after 0.001 seconds.
✔ Test archivedThreadsOpenAfterTheSecondRead() passed after 0.001 seconds.
✔ Test aSlashTitleNeverFallsBackToItsLastSegment() passed after 0.001 seconds.
✔ Test bareLinkOpensAWorkerTheDrawerHides() passed after 0.001 seconds.
✔ Test bareLinkFindsAWorkerOnAnotherMachine() passed after 0.001 seconds.
✔ Test anArchivedThreadOnAHealthyMachineOutranksAMachineStillLoading() passed after 0.001 seconds.
✔ Test aMachineThatHasNotAnsweredOpensTheChatInstead() passed after 0.001 seconds.
✔ Test deletedAndUnpairedSaySo() passed after 0.001 seconds.
✔ Test aLabelTitleIsTheLastResort() passed after 0.001 seconds.
✔ Test firstLookupWaitsForAnArchiveWhenTheBareOriginIsUnloaded() passed after 0.001 seconds.
✔ Test aBareLinkWaitsForEveryMachine() passed after 0.001 seconds.
✔ Test theIdAsWrittenStillMatches() passed after 0.001 seconds.
✔ Test anExactRemoteTombstoneOutranksALocalTitle() passed after 0.001 seconds.
✔ Test aUniqueTitleOpens() passed after 0.001 seconds.
✔ Test aTitleWithASlashIsNotAMachine() passed after 0.001 seconds.
✔ Test namedMachineOpensThere() passed after 0.001 seconds.
✔ Test anArchivedExactIdOutranksALiveTitleInAppModel() passed after 0.018 seconds.
✔ Suite ThreadLinkResolverTests passed after 0.018 seconds.
✔ Test run with 18 tests in 1 suite passed after 0.018 seconds.
```

## Acceptance criteria

2/2 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | An exact remote tombstone wins over an unrelated title match. |
| AC-02 | x (tasks) | met | An exact archived ID wins over a live chat whose title matches the link. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-recent-features-review | cd "$HOME/.specwithcode/m4/worktrees/specwithcode-dev/recen… |  |

1/1 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
