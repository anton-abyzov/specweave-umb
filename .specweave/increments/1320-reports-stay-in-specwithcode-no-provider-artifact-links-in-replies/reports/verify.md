# Verify — 1320-reports-stay-in-specwithcode-no-provider-artifact-links-in-replies

PASS · 2026-11-21T06:21:55.873Z · commands from config testing.commands

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
Ran 13 tests in 10.165s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.351s

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
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (670s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 4b8220a64 against origin/main (merge base 4b8220a64); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.dqESR3
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          3
typecheck                                    pass         39
fleet                                        pass        225
apps/chrome-extension                        pass          2
apps/desktop                                 pass         16
apps/marketing                               pass          0
apps/mobile                                  pass         17
apps/web                                     pass        269
infra/relay                                  pass         19
oxlint-plugin-studio                         pass         12
packages/client-runtime                      pass         16
packages/contracts                           pass          5
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          1
packages/shared                              pass         12
packages/ssh                                 pass          8
packages/tailscale                           pass          0
scripts                                      pass         23
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 670s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (759s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.KkK26mDk2B

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.KkK26mDk2B
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       438.2    221    2970        0
2      0       674.1    235    3317        0
3      0       715.7    236    3010        0
4      0       529.4    236    3362        0
5      0       758.3    237    3711        0
6      0       704.9    238    2858        0
Server shards: passed in 758.4s
```

## Acceptance criteria

5/5 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | Every provider's runtime instructions say that documents an agent makes or cites live in SpecWithCode: saved as reports (`studio_report_save`, or a Markdown file in the increment's `reports/`) and linked by local path, never published to or linked as a provider-hosted page; a document another tool made is imported first with its source recorded. The instructions stay within their length cap. |
| AC-02 | x (tasks) | met | A SpecWithCode Claude session has Claude Code's `Artifact` tool and the claude.ai Docs connector's write tools (`batch`, `update`, `create`, `delete`) in `disallowedTools`; its read tools are not disallowed, and a caller's own disallowed tools are kept. |
| AC-03 | x (tasks) | met | `studio_report_save` saves Markdown into the calling thread's project: the named increment's `reports/`, else the thread's increment, else `.specweave/reports/threads/`. The file has frontmatter `title`, `thread`, `increment`, `savedAt`, and for an import `source` and `original`. Saving the same text again returns the same file. It refuses an empty or over-512-KiB body, a non-https original, an unknown increment and a project without `.specweave`, and returns the absolute path and a ready Markdown link. |
| AC-04 | x (tasks) | met | In a reply, a link to a provider-hosted page (claude.ai artifacts, docs, chats and shares; ChatGPT and Codex shares, canvases and tasks; Gemini shares; Cursor agents; Devin sessions) renders as an outside-document chip: a document glyph, its label and a muted "outside · Claude" tag, never the provider favicon. Its tip says where it lives and who can open it; clicking offers "Save to this project" (drafts the import request into this thread's composer), "Open in Claude" and "Copy link". Every other link renders as before. Light and dark. |
| AC-05 | x (tasks) | met | "Before the move to the M5" is saved as a SpecWithCode report under `.specweave/reports/threads/` with its claude.ai origin in the frontmatter, opens in the app's document viewer, and the M5 thread has the local link. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specwithcode-dev/apps/server &… |  |
| T-02 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specwithcode-dev/apps/server &… |  |
| T-03 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specwithcode-dev/apps/server &… |  |
| T-04 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specwithcode-dev/apps/web && n… |  |
| T-05 | done | claude@antons-macbook-m4max | grep -l 'original: "https://claude.ai/artifact/KMQWxSYB5N7E… |  |
| T-06 | done | claude@antons-macbook-m4max | 8d8563c120 (PR 332 merged; CI green on bd93aa7b1a; two Sonn… |  |

6/6 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
