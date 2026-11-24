# Verify — 1304-force-update-setting-for-busy-machines-and-blockers-shown-only-on-the-machine-they-belong-to

PASS · 2026-11-12T09:12:38.048Z · commands from config testing.commands

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
Ran 13 tests in 8.779s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (1s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.399s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.091s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (560s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 81222418f5 against origin/main (merge base 81222418f5); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.Ns4RIh
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          4
typecheck                                    pass         36
fleet                                        pass        207
apps/chrome-extension                        pass          2
apps/desktop                                 pass         14
apps/marketing                               pass          1
apps/mobile                                  pass         15
apps/web                                     pass        201
infra/relay                                  pass         13
oxlint-plugin-studio                         pass          9
packages/client-runtime                      pass         13
packages/contracts                           pass          4
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          1
packages/shared                              pass         10
packages/ssh                                 pass          7
packages/tailscale                           pass          0
scripts                                      pass         18
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 560s
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (439s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.KVD3KTnVFy

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.KVD3KTnVFy
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       270.5    186    2439        0
2      0       396.3    201    2728        0
3      0       438.8    200    2569        0
4      0       421.8    201    2787        0
5      0       424.8    200    2643        0
6      0       383.9    201    2763        0
Server shards: passed in 438.8s
```

## Acceptance criteria

11/11 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A server setting `pauseWorkForUpdates` exists per machine and defaults to off, also on machines that update from an earlier release. It is never copied between machines. |
| AC-02 | x (tasks) | met | On a Mac with the setting off, an automatic service install never pauses running work. It waits until the machine is quiet, publishes no pause time, and its status line says the update installs once running work finishes. With the setting on it behaves as before this change: it waits "Pause running work after", pauses, installs, and the turns continue. When the service does not answer the agent's look, nothing is paused in that pass and a wait already running is kept. |
| AC-03 | x (tasks) | met | A forced fleet update request to a machine with the setting off is refused before anything is stopped. The refusal names the setting and says the machine is left for later by its owner's choice. The machine's fleet update status reports the setting. |
| AC-04 | x (tasks) | met | A Linux boot-service machine waits 30 minutes for quiet. With the setting off it then gives up as busy and names the setting. With it on it stops its work the way Update now does (turns interrupted for the update, open questions recorded), installs, and the turns continue. It pauses nothing when only another update's hold kept it waiting. A forced request, taken only with the setting on, still switches over when the drain fails. |
| AC-05 | x (tasks) | met | The rollout asks M4's service for the setting. Off: M4 is held only when idle and nothing is interrupted. On: drained as before. A service too old to report the setting is treated as before this change. A service that does not answer is held only when idle too, but is not left for later: if it never installs it fails as before. |
| AC-06 | x (tasks) | met | A host with the setting off that is still busy with running work after 30 minutes, with nothing held or started, ends `deferred` with the reason. A deferred worker does not fail the run, and its row carries a skipped desktop app step. Every host keeps its full deadline, and a host that fails for any other reason (its updater errored, it never offered the version) still ends `not-updated` and fails the run. The release script's verify step reports a machine left for later as pending, not failed. |
| AC-07 | x (tasks) | met | Update now, Restart now and a hand-run `specweave-studio update` work with the setting off exactly as before. |
| AC-08 | x (tasks) | met | With "Continue threads after restarts" off on a machine, no update pauses running work there, whatever the setting says, and the setting's row says why. |
| AC-09 | x (tasks) | met | The setting is a switch on this machine's update card in Settings > General and on every machine's card in Settings > Machines. A card's switch changes only that machine. "Pause running work after" is disabled while the switch is off. Strings exist in all eight catalogs. |
| AC-10 | x (tasks) | met | `docs/user/updating.md`, `docs/studio/releasing.md` and `CHANGELOG.md` describe the setting, its default and its bounds. |
| AC-11 | x (tasks) | met | Blocker placement follows D-10: the owner rule, the raise rule and every surface are written down in `reports/blocker-count-gate.md` and are acceptance criteria AC-11 to AC-16 of increment 1278, which owns the presence election they need. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/… |  |
| T-02 | done | claude@antons-macbook-m4max | cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/… |  |
| T-03 | done | claude@antons-macbook-m4max | cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/… |  |
| T-04 | done | claude@antons-macbook-m4max | cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/… |  |
| T-05 | done | claude@antons-macbook-m4max | cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/… |  |
| T-06 | done | claude@antons-macbook-m4max | grep -q "AC-16 (from 1304 D-10)" .specweave/increments/1278… |  |
| T-07 | done | claude@antons-macbook-m4max | test -s .specweave/increments/1304-force-update-setting-for… |  |
| T-08 | done | claude@antons-macbook-m4max | specweave verify 1304 on specwithcode-dev c776378216: all 5… |  |

8/8 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
