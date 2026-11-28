# Verify — 1495-mcp-form-cards-follow-the-servers-real-deadlines

PASS · 2026-11-28T10:18:54.410Z · commands from config testing.commands

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
Ran 13 tests in 10.409s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.299s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.094s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (772s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 03cdc099cef against origin/main (merge base 8b381ad512c); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.CHDhzd
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          2
typecheck                                    pass         41
fleet                                        pass        229
apps/chrome-extension                        pass          2
apps/desktop                                 pass         18
apps/marketing                               pass          1
apps/mobile                                  pass         18
apps/web                                     pass        299
infra/relay                                  pass         20
oxlint-plugin-studio                         pass         10
packages/client-runtime                      pass         17
packages/contracts                           pass          6
packages/effect-acp                          pass          4
packages/effect-codex-app-server             pass          1
packages/shared                              pass         19
packages/ssh                                 pass          7
packages/tailscale                           pass          1
scripts                                      pass         75
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 771s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (850s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.XvbO2HYPjB

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.XvbO2HYPjB
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       596.3    241    3159        0
2      0       619.7    255    3881        0
3      0       850.2    256    3283        0
4      0       608.3    256    3470        0
5      0       715.5    257    3738        0
6      0       793.4    257    3438        0
Server shards: passed in 850.2s
```

## Acceptance criteria

8/8 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A probe report records what reaches a Claude thread's card from a server on the current MCP SDK: an `input_required` form, a task's `tasks/update` question, and a `-32042` URL request. It states whether Tasks are on for the Agent SDK entrypoint the app ships. |
| AC-02 | x (tasks) | met | When the SDK stops waiting for a form (its abort signal fires) and no answer is recorded, the card closes and the thread shows "`<server>` stopped waiting for an answer." A recorded answer keeps 1481 D-11. |
| AC-03 | x (tasks) | met | The probe report records whether answering a form over HTTP works at 6 and at 11 minutes. The unattended timeout is no longer than the shortest real deadline that nothing signals (a signalled one closes the card through the SDK's abort, AC-02), and the spec says which deadline set it. On that timeout the server gets `cancel`. |
| AC-04 | x (tasks) | met | One tool call that retries a URL request shows one URL-decline notice, not one per retry. |
| AC-01 | x (tasks) | met | , AC-03 probe:** use a scratch folder at `/Users/anton/.specwithcode/m4/scratch/2026-11-27-1495/probe/`, holding the current `@modelcontextprotocol/sdk` server with stdio and Streamable HTTP transports. It has three tools: |
| AC-02 | x (tasks) | met | ** in `ClaudeMcpElicitation.ts`, when the call ends with `by: "stop"` and the turn is not stopping, the adapter shows a new `stoppedWaitingNotice`. Telling an SDK abort apart from the person's Stop comes from the turn's own state. |
| AC-03 | x (tasks) | met | ** set `UNATTENDED_MCP_ELICITATION_TIMEOUT_MS` to the shortest deadline the probe measures (expected 5 minutes, from the HTTP idle timeout), and update `unattendedTimeoutNotice` to match. Measured (D-03): 5 minutes, set by Claude Code's HTTP stream drop after about 356 s without keepalives. |
| AC-04 | x (tasks) | met | ** key the URL-decline notice by the tool call (the SDK's tool use id if the elicitation carries it, otherwise the single running `mcp__<server>__*` call), so retries replace one notice. Measured (D-05): with no single such call, the request keys itself. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antonm5axproled | grep -q "Tasks on the SDK entrypoint" .specweave/increments… |  |
| T-02 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |
| T-03 | done | claude@antonm5axproled | cd repositories/anton-abyzov/specwithcode && node node_modu… |  |

3/3 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
