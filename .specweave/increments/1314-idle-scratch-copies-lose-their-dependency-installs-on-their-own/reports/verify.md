# Verify — 1314-idle-scratch-copies-lose-their-dependency-installs-on-their-own

FAIL · 2026-11-13T07:50:16.618Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (42s)

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
Ran 13 tests in 42.164s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (1s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.714s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.243s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 143 (1201s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 773829328c against origin/main (merge base 773829328c); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.gKJmNh
Stage 1: 18 jobs, 1 at a time

[timeout after 20 min]
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 143 (1201s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.lTWlvlBqgJ

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.lTWlvlBqgJ

[timeout after 20 min]
```

## Acceptance criteria

3/4 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 |   | open | An idle source tree without `.git`, and a kept clone of a registered repository, lose their `node_modules` folders after a day unused, and every other file stays. |
| AC-02 | x (tasks) | met | The installs stay when a thread, agent session, terminal or process uses the copy, when anything outside the installs changed within the day, when the folder is not a package manager's install, and when any of that cannot be read. |
| AC-03 | x (tasks) | met | `specweave-studio clones sweep` lists the installs of each kept copy with the reason, and the released app on the M4 shows the same plan. |
| AC-04 | x (tasks) | met | Agents are told to remove their scratch copy, or its installs, when its pull request merges. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd ~/.specwithcode/m4/scratch/2026-11-12-scratch-deps-prune… |  |
| T-02 | done | claude@antons-macbook-m4max | grep -q "scratch copy" AGENTS.md && grep -q "Dependency ins… |  |
| T-03 | done | claude@antons-macbook-m4max | specweave-studio clones sweep --base-dir ~/.specwithcode/m4… |  |
| T-04 | open |  |  |  |

3/4 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 1 open
