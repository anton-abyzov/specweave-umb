# Verify — 1309-brand-audit-passes-on-specwithcode-main

PASS · 2026-11-24T18:54:43.647Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (12s)

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
Ran 13 tests in 12.180s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.381s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.099s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (869s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD bf2021f9e97 against origin/main (merge base 8b381ad512c); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.XewXH6
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          4
typecheck                                    pass         52
fleet                                        pass        266
apps/chrome-extension                        pass          2
apps/desktop                                 pass         22
apps/marketing                               pass          1
apps/mobile                                  pass         23
apps/web                                     pass        358
infra/relay                                  pass         19
oxlint-plugin-studio                         pass         11
packages/client-runtime                      pass         19
packages/contracts                           pass          6
packages/effect-acp                          pass          4
packages/effect-codex-app-server             pass          1
packages/shared                              pass         16
packages/ssh                                 pass          7
packages/tailscale                           pass          0
scripts                                      pass         58
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 869s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (970s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.kYOmxkNAnB

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.kYOmxkNAnB
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       566.1    225    2773        0
2      0       821.9    239    3436        0
3      0       949.8    240    3086        0
4      0       730.1    240    3307        0
5      0       925.5    241    3646        0
6      0         970    242    3523        0
Server shards: passed in 970s
```

## Acceptance criteria

6/6 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x | met | `node scripts/studio-brand-audit.mjs` exits 0 with no failed check in the shared checkout at the PR head, and again at `origin/main` after the merge. |
| AC-02 | x | met | The audit still fails, proven by unit tests, when: the inherited license text in `THIRD_PARTY_NOTICES.md` is altered, missing or duplicated; `LICENSE` is missing, is not the MIT text or carries the inherited copyright; an inherited fixture changes without a pinned reviewed hash; an inherited patch changes or disappears without a reviewed lock change; a publishable key outside a test is not for an owned host, or any key is for an upstream host. |
| AC-03 | x | met | Studio-owned fixture files are scanned for upstream names like any other owned file. |
| AC-04 | x | met | The PR changes no byte of `LICENSE`, `THIRD_PARTY_NOTICES.md` or `UPSTREAM.md`, and its description says for each of the seven checks whether the check or the code was stale. |
| AC-05 | x | met | The shared checkout is back on detached `origin/main` with a clean status, and the "Onboarding and new-project-from-folder UX" thread is told main passes. |
| AC-06 | x | met | Generated manifests state the license Anton chose, or stay untouched if he says so. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | cli@antons-macbook-m4max | cd repositories/anton-abyzov/specwithcode-dev && node --tes… |  |
| T-02 | done | cli@antons-macbook-m4max | cd repositories/anton-abyzov/specwithcode-dev && node --tes… |  |
| T-03 | done | cli@antons-macbook-m4max | cd repositories/anton-abyzov/specwithcode-dev && node --tes… |  |
| T-04 | done | cli@antons-macbook-m4max | cd repositories/anton-abyzov/specwithcode-dev && git fetch … |  |
| T-05 | done | claude@antons-macbook-m4max | bash .specweave/increments/1309-brand-audit-passes-on-specw… |  |
| T-06 | open |  |  |  |

5/6 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 1 open
