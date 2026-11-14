# Verify — 1321-composer-foot-shows-the-model-and-machine-first-no-runs-on-wording-voice-skills-and-run-state-as-icons

PASS · 2026-11-14T02:05:09.122Z · commands from config testing.commands

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
Ran 13 tests in 8.694s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.315s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.085s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (579s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 6d9593696 against origin/main (merge base 6d9593696); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.DippgM
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          4
typecheck                                    pass         31
fleet                                        pass        221
apps/chrome-extension                        pass          1
apps/desktop                                 pass         15
apps/marketing                               pass          0
apps/mobile                                  pass         15
apps/web                                     pass        212
infra/relay                                  pass         13
oxlint-plugin-studio                         pass          9
packages/client-runtime                      pass         13
packages/contracts                           pass          4
packages/effect-acp                          pass          4
packages/effect-codex-app-server             pass          1
packages/shared                              pass          9
packages/ssh                                 pass          8
packages/tailscale                           pass          0
scripts                                      pass         18
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 579s
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (431s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.jIGuw8mpZ4

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.jIGuw8mpZ4
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       288.8    190    2725        0
2      0       397.7    205    2745        0
3      0       426.5    204    2333        0
4      0         364    205    2855        0
5      0       430.8    204    2754        0
6      0       403.9    206    2868        0
Server shards: passed in 430.8s
```

## Acceptance criteria

8/8 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | Two or three designs are mocked up at desktop, half and phone width, one is picked with the reason, and the mockup page is saved in this increment's reports. |
| AC-02 | x (tasks) | met | The machine chip keeps "Runs on <machine>" and sits first, with the model right beside it on the same row: the thread chip and the coordinator chip read in full (not cut, not shortened) at 1100, 600 and 390 px. |
| AC-03 | x (tasks) | met | In the thread composer the model's name stays readable at 390 px and up: below 560 px the foot wraps, machine and model on the first row and voice, attach, skills and Send on the second; Send shows the machine's short label instead of "Send to <machine>" below 720 px. The machine chip counts at its full width in the fit, so other controls fold before its name is cut; only when even that does not fit does it shrink to its short label, never hiding the machine and model. |
| AC-04 | x (tasks) | met | Voice and Skills are icon buttons at every width (no "Voice" or "Skills 50" words); their tooltip and accessible name keep the full wording and count, and their menus work as before. |
| AC-05 | x (tasks) | met | The coordinator foot shows the machine and the model together on its first row when they fit; its run state is a dot with a tooltip, and it shows words only when it needs the person ("Needs you", "Run failed"). |
| AC-06 | x (tasks) | met | No window-wide machine bar. Each pane says which machine runs it by its own colored leading edge: the coordinator pane in its machine's color, the thread pane in its thread's machine color. |
| AC-07 | x (tasks) | met | A thread composer keeps its machine-colored border while a banner (resume, subagents) sits above it, as the coordinator composer does. |
| AC-08 | x (tasks) | met | A headless browser check renders the real composer controls at 1100, 600 and 390 px in light and dark, asserts the above, and saves before and after screenshots. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | test -s .specweave/increments/1321-composer-foot-shows-the-… |  |
| T-02 | done | claude@antons-macbook-m4max | specweave-studio checks run --label 1321 -- bash -c 'cd ~/.… |  |
| T-03 | done | claude@antons-macbook-m4max | specweave-studio checks run --label 1321 -- bash -c 'cd ~/.… |  |
| T-04 | done | claude@antons-macbook-m4max | specweave-studio checks run --label 1321 -- bash -c 'cd ~/.… |  |
| T-05 | done | claude@antons-macbook-m4max | specweave-studio checks run --label 1321 -- bash -c 'cd ~/.… |  |
| T-06 | done | claude@antons-macbook-m4max | specweave-studio checks run --label 1321 -- bash -c 'cd ~/.… |  |
| T-07 | done | claude@antons-macbook-m4max | specweave verify 1321 on specwithcode-dev ead36eac1+ (v1.0.… |  |

7/7 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
