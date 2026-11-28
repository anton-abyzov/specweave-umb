# Verify — 1498-mcp-servers-can-ask-you-to-open-a-link-in-claude-threads

PASS · 2026-11-28T12:35:01.146Z · commands from config testing.commands

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
Ran 13 tests in 10.080s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.310s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.088s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (704s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 45650362d07 against origin/main (merge base 8b381ad512c); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.ncdXnp
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          3
typecheck                                    pass         38
fleet                                        pass        226
apps/chrome-extension                        pass          2
apps/desktop                                 pass         18
apps/marketing                               pass          0
apps/mobile                                  pass         16
apps/web                                     pass        261
infra/relay                                  pass         16
oxlint-plugin-studio                         pass          9
packages/client-runtime                      pass         15
packages/contracts                           pass          4
packages/effect-acp                          pass          4
packages/effect-codex-app-server             pass          0
packages/shared                              pass         13
packages/ssh                                 pass          7
packages/tailscale                           pass          0
scripts                                      pass         69
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 703s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (811s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.2KKCEFWCA2

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.2KKCEFWCA2
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       669.5    241    3279        0
2      0       478.4    255    3488        0
3      0       761.5    257    3405        0
4      0       600.4    256    3354        0
5      0         659    257    3868        0
6      0       810.7    258    3620        0
Server shards: passed in 810.7s
```

## Acceptance criteria

7/7 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A URL request in a Claude thread shows a card with: |
| AC-02 | x (tasks) | met | The link opens in the system browser only when the person presses Open link. Nothing opens it automatically, not even when the card appears, or for an agent's answer, in Full access, or from an automatic responder. |
| AC-03 | x (tasks) | met | A URL whose host has Punycode (`xn--`), mixes scripts, or is not `https` (other than `http://localhost`) shows a warning on the card. A URL that is not `http` or `https`, or that has user info (`user@host`), is declined with a notice and gets no card. |
| AC-04 | x (tasks) | met |  |
| AC-05 | x (tasks) | met | A tool call that retries `-32042` up to 3 times shows one card. A retry after the person answered gets that answer and no new card. |
| AC-06 | x (tasks) | met | The URL path never reads, adds or sends a SpecWithCode sign-in, a Connect token or any credential. The open-link action passes only the server's URL to the system browser, unchanged. |
| AC-07 | x (tasks) | met | A headless screenshot of the URL card, including the lookalike warning, is saved in `reports/`. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-02 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-03 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-04 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-05 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-06 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-07 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-08 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-09 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |

9/9 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
