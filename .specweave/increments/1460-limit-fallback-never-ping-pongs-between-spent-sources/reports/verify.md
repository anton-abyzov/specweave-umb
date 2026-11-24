# Verify — 1460-limit-fallback-never-ping-pongs-between-spent-sources

PASS · 2026-11-24T18:29:52.713Z · commands from config testing.commands

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
Ran 13 tests in 8.845s

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
Ran 17 tests in 0.073s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (603s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD dad226959 against origin/main (merge base dad226959); logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T//studio-pr-gate.kC0Me3
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          3
typecheck                                    pass         33
fleet                                        pass        195
apps/chrome-extension                        pass          2
apps/desktop                                 pass         14
apps/marketing                               pass          1
apps/mobile                                  pass         16
apps/web                                     pass        254
infra/relay                                  pass         13
oxlint-plugin-studio                         pass          8
packages/client-runtime                      pass         14
packages/contracts                           pass          4
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          1
packages/shared                              pass         12
packages/ssh                                 pass          7
packages/tailscale                           pass          0
scripts                                      pass         21
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 603s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (689s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.U8O1J3qPNC

Running the server suite as 6 shards; logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.U8O1J3qPNC
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       526.7    226    3296        0
2      0       617.8    239    3471        0
3      0       689.4    241    2982        0
4      0       506.3    241    3311        0
5      0       645.8    241    3703        0
6      0         662    242    3030        0
Server shards: passed in 689.4s
```

## Acceptance criteria

6/6 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A thread stopped on a usage limit holds its source (instance and model) until the reset the stop names, or for 60 minutes when it names none. The hold applies whether or not the provider reports usage, and other models on the same instance stay usable. |
| AC-02 | x (tasks) | met | No automatic limit fallback, for any thread on the machine, moves onto a held source. With two spent sources of one model on a Tracks project, the second stop moves the thread to the track's next model with room (reproduction: Copilot → Cursor → Claude Opus 5.5, never back to Copilot). |
| AC-03 | x (tasks) | met | A hold ends early only when a run on that same source starts after the stop and completes, or, for a maker's own harness whose read covers each model (Claude, Codex), when a usage read taken after the stop shows room for that model. |
| AC-04 | x (tasks) | met | Automatic limit fallback makes at most 4 hops in one chain (each stop on a run the sweep's own continuation of the previous stop started). After the cap the thread parks: no further automatic switch, and the existing limit card stays the one place to act. |
| AC-05 | x (tasks) | met | A usage-limit row reads "resolved" only when a later run completed or did tool work; a later run that itself failed (its text is the provider's refusal) does not resolve it. |
| AC-06 | x (tasks) | met | Consecutive limit hops in the timeline show as one collapsed line naming the hop count and the sources tried, expandable to the individual rows. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@anton-m5max-proled | PR #875 merged as 525b3b2c0 (head dad226959). CI green, 27 … |  |
| T-02 | done | claude@anton-m5max-proled | PR #875 merged as 525b3b2c0 (head dad226959). CI green, 27 … |  |
| T-03 | done | claude@anton-m5max-proled | PR #875 merged as 525b3b2c0 (head dad226959). CI green, 27 … |  |

3/3 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
