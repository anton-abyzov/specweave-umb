# Verify — 1315-aide-is-its-own-space-out-of-project-lists-one-entry-point-topics-wording-google-settings-grouped-by-aide-and-projects

FAIL · 2026-11-13T06:45:03.248Z · commands from config testing.commands

## Commands

- FAIL: No testing.ownerCommands configured for repositories/anton-abyzov/specwithcode
- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (30s)

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
Ran 13 tests in 30.169s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (4s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 3.599s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.284s

OK
recorded
```

## Acceptance criteria

5/5 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | With Aide on, Aide is not a card in the Overview Projects panel and is not counted in "in N projects"; it has its own entry above Projects that opens it. |
| AC-02 | x (tasks) | met | Ordinary project pickers (Overview new chat, command palette go-to and new-thread lists, Move thread, default new chat, provider settings, sidebar scope, Automated and Archived sidebar lists) do not offer Aide; Routines, Messaging and design pickers still do, named as Aide without a "(personal)" suffix. |
| AC-03 | x (tasks) | met | Inside Aide every label in the list pane and the open-topic header says topic, never thread; a code project still says thread. |
| AC-04 | x (tasks) | met | Settings > Google account shows Aide in its own group above "Projects that may read it"; project counts and "Enable for all" cover projects only; the copy says Aide, not "Personal project"; existing grants are unchanged. |
| AC-05 | x (tasks) | met | Server text an agent or person reads names the page "Settings > Google account" consistently and Aide's prompt keeps saying topic. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | gh pr view 298 -R anton-abyzov/specwithcode --json state -q… |  |
| T-02 | done | claude@antons-macbook-m4max | gh pr view 298 -R anton-abyzov/specwithcode --json state -q… |  |
| T-03 | done | claude@antons-macbook-m4max | gh pr view 298 -R anton-abyzov/specwithcode --json state -q… |  |
| T-04 | done | claude@antons-macbook-m4max | gh pr view 298 -R anton-abyzov/specwithcode --json state -q… |  |
| T-05 | done | claude@antons-macbook-m4max | bash /private/tmp/claude-501/-Users-antonabyzov-Projects-gi… |  |

5/5 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
