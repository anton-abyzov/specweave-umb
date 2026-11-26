# Verify — 1492-update-consent-helper-reads-the-grant-on-apple-sqlite-3540

PASS · 2026-11-26T20:54:58.323Z · commands from config testing.commands

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
Ran 13 tests in 8.684s

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
Ran 17 tests in 0.071s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (644s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 5ddc104e8b against origin/main (merge base c66946d3c7); logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T//studio-pr-gate.CVVJc1
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          3
typecheck                                    pass         33
fleet                                        pass        196
apps/chrome-extension                        pass          1
apps/desktop                                 pass         16
apps/marketing                               pass          0
apps/mobile                                  pass         16
apps/web                                     pass        293
infra/relay                                  pass         14
oxlint-plugin-studio                         pass          8
packages/client-runtime                      pass         13
packages/contracts                           pass          4
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          0
packages/shared                              pass         13
packages/ssh                                 pass          7
packages/tailscale                           pass          1
scripts                                      pass         22
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 643s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (734s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.UOjuirVg4C

Running the server suite as 6 shards; logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.UOjuirVg4C
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0         465    239    2950        0
2      0       529.3    253    3639        0
3      0         734    254    3302        0
4      0         596    254    3328        0
5      0       688.4    255    3912        0
6      0       701.7    256    3663        0
Server shards: passed in 734s
```

- Working directory: . (explicit)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (10s)

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
Ran 13 tests in 9.699s

OK
```

- Working directory: . (explicit)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.259s

OK
```

- Working directory: . (explicit)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.088s

OK
recorded
```

## Acceptance criteria

3/3 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | On `/usr/bin/python3` (SQLite 3.54.0), the consent helper reads the grant of a stopped service's WAL database (only the main file on disk): status reports `not-enrolled`, enrolment succeeds, and a revoked grant is still refused as `unauthorized`. |
| AC-02 | x (tasks) | met | On the same build, `rehearse_update.protected` reads a clone of a stopped source that has only its main file. |
| AC-03 | x (tasks) | met | The fleet suite passes on `/usr/bin/python3` (3.54.0) and on uv Python 3.12 (3.53.1) in the gated checks copy with the server built. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@anton-m5max-proled | cd repositories/anton-abyzov/specwithcode/scripts/studio-fl… |  |
| T-02 | done | claude@anton-m5max-proled | grep -q 'both builds pass' .specweave/increments/1492-updat… |  |

2/2 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
