# Verify — 1430-show-the-correct-connection-action-for-a-saved-connect-machine

PASS · 2026-11-20T05:53:41.464Z · commands from config testing.commands

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
Ran 13 tests in 11.143s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (1s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.449s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.107s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (822s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD e37236bbd9a against origin/main (merge base 8b381ad512c); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.G6k4wO
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          4
typecheck                                    pass         53
fleet                                        pass        247
apps/chrome-extension                        pass          2
apps/desktop                                 pass         19
apps/marketing                               pass          0
apps/mobile                                  pass         20
apps/web                                     pass        357
infra/relay                                  pass         19
oxlint-plugin-studio                         pass         12
packages/client-runtime                      pass         17
packages/contracts                           pass          5
packages/effect-acp                          pass          4
packages/effect-codex-app-server             pass          1
packages/shared                              pass         12
packages/ssh                                 pass          7
packages/tailscale                           pass          1
scripts                                      pass         40
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 822s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (1088s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.YwIoYug6Lb

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.YwIoYug6Lb
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       762.3    219    2944        0
2      0       771.8    233    3451        0
3      0         910    234    3052        0
4      0       762.5    234    2951        0
5      0      1088.1    235    3250        0
6      0       912.7    235    3229        0
Server shards: passed in 1088.1s
```

## Acceptance criteria

3/3 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A saved relay route for the same environment, preferred or alternate, matches that machine’s Connect address. The header and expanded details stop offering to pair it again, including while its existing session connects. |
| AC-02 | x (tasks) | met | A genuinely missing or changed direct address keeps its existing repair action. A relay route on a different environment and a rejected device cannot count as a successful saved connection. |
| AC-03 | x (tasks) | met | The view still uses its current connection state for Online, Connecting or an error. A work grant or saved route alone cannot mark a machine online or grant access. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | Application commit 9bc9b82ce on PR 778 recognizes preferred… |  |
| T-02 | done | codex@antons-macbook-m4max | App commit e37236bbd. Four assertions failed on 9bc9b82ce i… |  |

2/2 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
