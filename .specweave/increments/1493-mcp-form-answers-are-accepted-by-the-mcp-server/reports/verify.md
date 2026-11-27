# Verify — 1493-mcp-form-answers-are-accepted-by-the-mcp-server

PASS · 2026-11-27T03:22:04.827Z · commands from config testing.commands

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
Ran 13 tests in 9.117s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.241s

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
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (646s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD c8701bd9e6 against origin/main (merge base c66946d3c7); logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T//studio-pr-gate.UoByTf
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          4
typecheck                                    pass         40
fleet                                        pass        195
apps/chrome-extension                        pass          2
apps/desktop                                 pass         16
apps/marketing                               pass          0
apps/mobile                                  pass         17
apps/web                                     pass        287
infra/relay                                  pass         14
oxlint-plugin-studio                         pass          8
packages/client-runtime                      pass         14
packages/contracts                           pass          4
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          1
packages/shared                              pass         12
packages/ssh                                 pass          7
packages/tailscale                           pass          1
scripts                                      pass         20
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 645s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (716s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.uV8yWe0hzr

Running the server suite as 6 shards; logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.uV8yWe0hzr
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       443.5    239    3063        0
2      0       481.7    253    3497        0
3      0       716.3    255    3511        0
4      0         541    254    3306        0
5      0       623.4    255    3823        0
6      0       576.1    256    3609        0
Server shards: passed in 716.3s
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
Ran 13 tests in 9.165s

OK
```

- Working directory: . (explicit)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.255s

OK
```

- Working directory: . (explicit)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.082s

OK
recorded
```

## Acceptance criteria

14/14 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A `date-time` answer from the card reaches the server as RFC 3339 with seconds and the local offset, and the MCP SDK 1.32.2 validator accepts it. A value without seconds or a zone, an impossible date, or an out-of-range time is refused with "Enter a date and time." |
| AC-02 | x (tasks) | met | A date-time default with a zone shows in the card as the same instant in local time. A default the card can't show is not sent. |
| AC-03 | x (tasks) | met | A form with a number or integer field named as a secret (`pin`, `PINCode`, `otp`, `APIToken`, `cvv`) is declined, like a text field. Select and boolean fields, whose values the server lists itself, are not refused for their name. |
| AC-04 | x (tasks) | met | A string with a format is sent trimmed, and the SDK validator accepts it. |
| AC-05 | x (tasks) | met | An optional multi-select with `minItems` left empty is left out of the content, with no error. |
| AC-06 | x (tasks) | met | Once the adapter starts closing a card after Stop or the timer, an answer to it is refused with "This form was closed." and never recorded as resolved. An answer the app recorded first is passed on, as before. |
| AC-07 | x (tasks) | met | When the commit of an answer fails or is rejected, its answered mark and hand-off are dropped, so a later Stop or the timer closes the card instead of leaving it pending with no call behind it. A committed answer that never arrives keeps 1481 D-11: the record is not overwritten. |
| AC-08 | x (tasks) | met | A test fails if the committed `runtime-request.respond` effect carries raw answers. |
| AC-01 | x (tasks) | met | , AC-02:** new module `packages/shared/src/mcpElicitationDateTime.ts`: |
| AC-03 | x (tasks) | met | ** `findMcpElicitationSecretField` checks `text` and `number` fields, and `namesSecret` splits `([A-Z]+)([A-Z][a-z])` before the camelCase split. |
| AC-04 | x (tasks) | met | , AC-05:** `checkField` returns the trimmed string when a format applies and checks lengths on it. An optional multi-select with nothing chosen returns `{}` before the `minItems` check. |
| AC-06 | x (tasks) | met | , AC-07:** `ClaudeFormResponses.ts` gains a bounded `closing` set, plus `beginClosingClaudeForm(id)`. That function returns false when an answer was already recorded; otherwise it marks the form as closing. |
| AC-06 | x (tasks) | met | , AC-07 after review rounds 2 to 5:** a call whose answer never arrived waits for that answer's commit outcome before it ends, with an upper bound. |
| AC-08 | x (tasks) | met | ** `Orchestrator.claudeForms.test.ts` asserts that the committed effect's `answers` equals `{ confirm: "[redacted]" }`. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@anton-m5max-proled | grep -q 'Tests 66 passed (66)' .specweave/increments/1493-m… |  |
| T-02 | done | claude@anton-m5max-proled | grep -q 'refuses an answer once the adapter began closing t… |  |

2/2 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
