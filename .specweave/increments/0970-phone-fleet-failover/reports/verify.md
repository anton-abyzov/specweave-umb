# Verify — 0970-phone-fleet-failover

PASS · 2026-11-24T21:00:39.220Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (11s)

```
test_absent_and_idempotent (__main__.SafetyTests.test_absent_and_idempotent) ... ok
test_dirty_and_untracked_preserved (__main__.SafetyTests.test_dirty_and_untracked_preserved) ... ok
test_existing_empty_and_atomic_race_preserved (__main__.SafetyTests.test_existing_empty_and_atomic_race_preserved) ... ok
test_final_readback_detects_descendant_and_staging (__main__.SafetyTests.test_final_readback_detects_descendant_and_staging) ... ok
test_incomplete_runtime_and_release_never_pass (__main__.SafetyTests.test_incomplete_runtime_and_release_never_pass) ... ok
test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts (__main__.SafetyTests.test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts) ... ok
test_missing_or_diverged_upstream_is_preserved (__main__.SafetyTests.test_missing_or_diverged_upstream_is_preserved) ... ok
test_new_and_legacy_clones_fetch_and_track_future_feature (__main__.SafetyTests.test_new_and_legacy_clones_fetch_and_track_future_feature) ... ok
test_offline_bundle_and_bad_digest (__main__.SafetyTests.test_offline_bundle_and_bad_digest) ... ok
test_remote_drift_preserves_old_checkout (__main__.SafetyTests.test_remote_drift_preserves_old_checkout) ... ok
test_scoped_transport_preserves_identity_and_rejects_redirects (__main__.SafetyTests.test_scoped_transport_preserves_identity_and_rejects_redirects) ... ok
test_unpushed_commit_preserved (__main__.SafetyTests.test_unpushed_commit_preserved) ... ok
test_unsafe_paths_urls_and_symlinks (__main__.SafetyTests.test_unsafe_paths_urls_and_symlinks) ... ok

----------------------------------------------------------------------
Ran 13 tests in 11.146s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.364s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.094s

OK
recorded
```

- Working directory: . (explicit)
### `test $(git -C /Users/antonabyzov/.specwithcode/m4/verify/specwithcode rev-parse HEAD) = 29d788d8cc51b30ec619acdb626ad31bebc10460` → exit 0 (0s)

```
(no output)
```

- Working directory: . (explicit)
### `swift test --no-parallel --package-path /Users/antonabyzov/.specwithcode/m4/verify/specwithcode/apps/ios/SWCKit --filter 'FleetEngineTests|FleetSummariesTests|FleetFixtureTests'` → exit 0 (2s)

```
◇ Test removingAMachineDismissesIt() started.
✔ Test removingAMachineDismissesIt() passed after 0.016 seconds.
✔ Suite FleetEngineTests passed after 0.273 seconds.
◇ Suite FleetSummariesTests started.
◇ Test rowShowsWhereTheThreadLivesAndRuns() started.
✔ Test rowShowsWhereTheThreadLivesAndRuns() passed after 0.001 seconds.
◇ Test nicknamesNameEveryMachineIncludingRosterOnlyOnes() started.
✔ Test nicknamesNameEveryMachineIncludingRosterOnlyOnes() passed after 0.001 seconds.
◇ Test executionMachineNameComesFromTheRosterOrTheServer() started.
✔ Test executionMachineNameComesFromTheRosterOrTheServer() passed after 0.001 seconds.
◇ Test unreachableMachineThreadsStayListedAsUnknown() started.
✔ Test unreachableMachineThreadsStayListedAsUnknown() passed after 0.001 seconds.
◇ Test threadIsUnknownWhenTheMachineRunningItIsUnreachable() started.
✔ Test threadIsUnknownWhenTheMachineRunningItIsUnreachable() passed after 0.001 seconds.
◇ Test handedOffCopyIsHiddenOnlyWhileItsContinuationIsListed() started.
✔ Test handedOffCopyIsHiddenOnlyWhileItsContinuationIsListed() passed after 0.001 seconds.
◇ Test linkedProjectIsOneRowWithEveryMachinesThreads() started.
✔ Test linkedProjectIsOneRowWithEveryMachinesThreads() passed after 0.001 seconds.
◇ Test offlineCoordinatorStaysTheRowsMachine() started.
✔ Test offlineCoordinatorStaysTheRowsMachine() passed after 0.001 seconds.
◇ Test rowOpensTheNewestActiveCoordinatorNotTheFirstListedCopy() started.
✔ Test rowOpensTheNewestActiveCoordinatorNotTheFirstListedCopy() passed after 0.001 seconds.
◇ Test rowCarriesTheLinkedProjectsOtherMachinesWithOneMachinePaired() started.
✔ Test rowCarriesTheLinkedProjectsOtherMachinesWithOneMachinePaired() passed after 0.001 seconds.
◇ Test workersOnlyCopyFollowsItsCoordinatorAlongLaterMoves() started.
✔ Test workersOnlyCopyFollowsItsCoordinatorAlongLaterMoves() passed after 0.001 seconds.
◇ Test withoutAnActiveCoordinatorTheRowOpensAReachableMachine() started.
✔ Test withoutAnActiveCoordinatorTheRowOpensAReachableMachine() passed after 0.001 seconds.
✔ Suite FleetSummariesTests passed after 0.006 seconds.
◇ Suite MachineNicknameTests started.
◇ Test nicknameWinsThenShortName() started.
✔ Test nicknameWinsThenShortName() passed after 0.001 seconds.
◇ Test nicknamesFollowTheWebRules() started.
✔ Test nicknamesFollowTheWebRules() passed after 0.001 seconds.
◇ Test configStreamCarriesSettingsUpdates() started.
✔ Test configStreamCarriesSettingsUpdates() passed after 0.001 seconds.
◇ Test mergeKeepsTheNewestRenameAndBreaksTiesByName() started.
✔ Test mergeKeepsTheNewestRenameAndBreaksTiesByName() passed after 0.001 seconds.
◇ Test settingsCarryNicknamesAndSkipBadEntries() started.
✔ Test settingsCarryNicknamesAndSkipBadEntries() passed after 0.001 seconds.
◇ Test unknownLabelNamesTheMissingMachineOnlyWhenNeeded() started.
✔ Test unknownLabelNamesTheMissingMachineOnlyWhenNeeded() passed after 0.001 seconds.
✔ Suite MachineNicknameTests passed after 0.001 seconds.
◇ Suite ThreadExecutionWireTests started.
◇ Test decodesWhereAThreadRuns() started.
✔ Test decodesWhereAThreadRuns() passed after 0.001 seconds.
◇ Test olderOrNewerValuesDoNotBreakTheThread() started.
✔ Test olderOrNewerValuesDoNotBreakTheThread() passed after 0.001 seconds.
✔ Suite ThreadExecutionWireTests passed after 0.001 seconds.
✔ Test run with 40 tests in 5 suites passed after 0.643 seconds.
```

- Working directory: . (explicit)
### `cd /Users/antonabyzov/.specwithcode/m4/verify/specwithcode/apps/server && /Users/antonabyzov/.specwithcode/m4/verify/specwithcode/node_modules/.bin/vp test run src/fleet/phoneLinks.test.ts` → exit 0 (1s)

```
note: You are running `vp test` as a Vite+ built-in command. If you meant to run the test npm script, use `vpr test` instead.

[1m[30m[46m RUN [49m[39m[22m [36mv5.1.0 [39m[90m/Users/antonabyzov/.specwithcode/m4/verify/specwithcode/apps/server[39m

(node:17993) ExperimentalWarning: SQLite is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 [32m✓[39m src/fleet/phoneLinks.test.ts [2m([22m[2m23 tests[22m[2m)[22m[32m 138[2mms[22m[39m

[2m Test Files [22m [1m[32m1 passed[39m[22m[90m (1)[39m
[2m      Tests [22m [1m[32m23 passed[39m[22m[90m (23)[39m
[2m   Start at [22m 16:00:38
[2m   Duration [22m 976ms[2m (import 47%, transform 37%, tests 15%, setup 1%)[22m
```

## Acceptance criteria

9/10 met · 1 skipped (accepted), not verified

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | Pairing the phone with M4 also gives it the endpoints of every machine paired with M4, and each of those machines mints a phone token scoped to the phone, on M4's request, without the user pairing again. |
| AC-02 | x (tasks) | met | The home screen merges a logical project across machines into one row, showing which machine owns each thread. |
| AC-03 | x (tasks) | met | When a machine is unreachable, its threads show an offline badge and the project offers "Continue on <machine>" for any reachable member. |
| AC-04 | x (tasks) | met | Revoking the phone on any machine revokes it on all of them. |
| AC-05 | x (tasks) | met | After 0967 merges: "Handoff ready" badges and "Continue here on <machine>" appear on the phone. |
| AC-06 |   | skipped-accepted | Tested on the simulator and on LAN with two Macs (M4 off, Minis on); the network gap is reported. |
| AC-07 | x (tasks) | met | Each thread row on the phone shows its machine by nickname: "M4" when it lives and runs on one machine, "M4 → Minis" when it lives on M4 and runs on Minis. The names come from 0967's ownerMachineId, executionMachineId and executionState through 0966's machineNickname helper. |
| AC-08 | x (tasks) | met | The threads of an unreachable machine stay listed with "Unknown · last seen <time>"; they are never hidden and the list never goes empty because one machine is out. |
| AC-09 | x (tasks) | met | The phone can view each machine's orchestrator separately, and a message sent from that view goes only to that machine's coordinator. "Continue on <machine>" runs 0967's handoff with its per-thread preflight result and never runs from switching the view. |
| AC-10 | x (tasks) | met | Fault tests with simulator screenshots: M4 goes off mid-session and comes back (the phone reconnects with no duplicate rows), and Minis goes off while its orchestrator is being viewed. |

### Accepted skips (not verified)

- AC-06 check `two physical Macs on LAN with M4 off` — Cannot be run as written: fleet addresses must be HTTPS tailnet or Connect (fleetOrigin.ts:40-68), the owner decided on October 20, 2026 not to build a LAN mode, Connect replaced the hub as the phone route (1139), and a hub-off run would need live Tailscale Serve or Connect changes. Simulator and live two-server runs passed October 20; physical hub-off stays untested.. Accepted by Anton Abyzov at 2026-11-24T00:00:00Z; authorization: Anton Abyzov, November 24, 2026, M5 thread 0970: "If it's superseded, record it as skipped with the evidence, the way the closure rules allow." and "once T-05's check passes, or is recorded as superseded with evidence, unblock T-10 and close 0970." (recorded by claude@antons-macbook-m4max at 2026-11-24T15:34:23.269Z)

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | cli@antons-macbook-m4max | anton-abyzov/specwithcode-dev#493 merged as 118849515e HEAD… |  |
| T-02 | done | cli@antons-macbook-m4max | anton-abyzov/specwithcode-dev#500 merged as ba13ae6465; swi… |  |
| T-03 | done | cli@antons-macbook-m4max | anton-abyzov/specwithcode-dev#500 merged as ba13ae6465; swi… |  |
| T-04 | done | codex@antons-macbook-m4max | e2fbbdef113abba950200fdc630e590df0cf03a1; 349 Swift tests p… |  |
| T-05 | skipped | claude@antons-macbook-m4max |  | Two-Mac LAN M4-off run superseded: fleet links refuse LAN, … |
| T-06 | done | cli@antons-macbook-m4max | anton-abyzov/specwithcode-dev#500 merged as ba13ae6465; swi… |  |
| T-07 | done | cli@antons-macbook-m4max | anton-abyzov/specwithcode-dev#500 merged as ba13ae6465; swi… |  |
| T-08 | done | cli@antons-macbook-m4max | anton-abyzov/specwithcode-dev#500 merged as ba13ae6465; swi… |  |
| T-09 | done | cli@antons-macbook-m4max | anton-abyzov/specwithcode-dev#500 merged as ba13ae6465; swi… |  |
| T-10 | blocked | codex@antons-macbook-m4max |  | Merged #547 and #552; 351 Swift tests pass on 006ed1a08ba4c… |

8/10 done · 1 skipped · 0 claimed · 1 blocked · 0 stale · 0 open

### Skipped

- T-05 — Two-Mac LAN M4-off run superseded: fleet links refuse LAN, Connect is the phone route; see report (claude@antons-macbook-m4max)
