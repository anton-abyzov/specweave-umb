# Verify — 1491-fleet-update-scripts-read-the-database-on-apple-sqlite-3540

PASS · 2026-11-26T17:05:53.741Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (9s)

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
Ran 13 tests in 8.553s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.238s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.074s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (639s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD ff75993a52 against origin/main (merge base c66946d3c7); logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T//studio-pr-gate.frqtIT
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          4
typecheck                                    pass         43
fleet                                        pass        194
apps/chrome-extension                        pass          2
apps/desktop                                 pass         16
apps/marketing                               pass          0
apps/mobile                                  pass         16
apps/web                                     pass        283
infra/relay                                  pass         13
oxlint-plugin-studio                         pass          8
packages/client-runtime                      pass         13
packages/contracts                           pass          3
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          1
packages/shared                              pass         11
packages/ssh                                 pass          7
packages/tailscale                           pass          0
scripts                                      pass         21
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 638s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (656s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.V2dZQWjTqC

Running the server suite as 6 shards; logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.V2dZQWjTqC
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       387.5    239    2950        0
2      0       448.5    253    3639        0
3      0       655.7    254    3302        0
4      0       518.2    254    3328        0
5      0       606.7    255    3912        0
6      0       625.3    256    3663        0
Server shards: passed in 655.7s
```

- Working directory: . (explicit)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (9s)

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
Ran 13 tests in 8.831s

OK
```

- Working directory: . (explicit)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.236s

OK
```

- Working directory: . (explicit)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.081s

OK
recorded
```

## Acceptance criteria

2/2 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | On `/usr/bin/python3` with Apple's SQLite 3.54.0, `live_database.connect` reads a WAL database whose service has closed it (only the main file on disk), and the connection refuses writes. The reader holds SQLite's WAL read locks, so a service that starts during the read cannot checkpoint over the pages it uses. A database with `-shm` on disk never takes that fallback, and one that a process holds without its `-wal` and `-shm` is refused. |
| AC-02 | x (tasks) | met | The fleet suite (`scripts/studio-fleet/run-tests.sh`) passes on `/usr/bin/python3` (SQLite 3.54.0) and on a stock-SQLite Python 3.12 (3.53.1), including the six files above, in the gated checks copy with the server built. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@anton-m5max-proled | cd repositories/anton-abyzov/specwithcode/scripts/studio-fl… |  |
| T-02 | done | claude@anton-m5max-proled | grep -q 'both builds pass' .specweave/increments/1491-fleet… |  |

2/2 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
