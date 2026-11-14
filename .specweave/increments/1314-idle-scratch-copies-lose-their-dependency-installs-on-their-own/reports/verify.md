# Verify — 1314-idle-scratch-copies-lose-their-dependency-installs-on-their-own

PASS · 2026-11-14T02:41:40.312Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
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
Ran 13 tests in 9.453s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (1s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.406s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.121s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (586s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 6d9593696 against origin/main (merge base 6d9593696); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.euj6gC
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          4
typecheck                                    pass         31
fleet                                        pass        221
apps/chrome-extension                        pass          1
apps/desktop                                 pass         15
apps/marketing                               pass          0
apps/mobile                                  pass         16
apps/web                                     pass        215
infra/relay                                  pass         14
oxlint-plugin-studio                         pass          9
packages/client-runtime                      pass         14
packages/contracts                           pass          4
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          1
packages/shared                              pass         11
packages/ssh                                 pass          7
packages/tailscale                           pass          1
scripts                                      pass         17
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 586s
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (453s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.btNQzmf3Ix

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.btNQzmf3Ix
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       305.9    190    2725        0
2      0       423.2    205    2745        0
3      0       449.1    204    2333        0
4      0       366.7    205    2855        0
5      0       453.1    204    2754        0
6      0       429.7    206    2868        0
Server shards: passed in 453.1s
```

## Acceptance criteria

4/4 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | An idle source tree without `.git`, and a kept clone of a registered repository, lose their `node_modules` folders after a day unused, and every other file stays. |
| AC-02 | x (tasks) | met | The installs stay when a thread, agent session, terminal or process uses the copy, when anything outside the installs changed within the day, when the folder is not a package manager's install, and when any of that cannot be read. |
| AC-03 | x (tasks) | met | `specweave-studio clones sweep` lists the installs of each kept copy with the reason, and the released app on the M4 shows the same plan. |
| AC-04 | x (tasks) | met | Agents are told to remove their scratch copy, or its installs, when its pull request merges. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd ~/.specwithcode/m4/scratch/2026-11-12-scratch-deps-prune… |  |
| T-02 | done | claude@antons-macbook-m4max | grep -q "scratch copy" AGENTS.md && grep -q "Dependency ins… |  |
| T-03 | done | claude@antons-macbook-m4max | specweave-studio clones sweep --base-dir ~/.specwithcode/m4… |  |
| T-04 | done | claude@antons-macbook-m4max | specweave verify 2026-11-13 local: umbrella checks + verify… |  |

4/4 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
