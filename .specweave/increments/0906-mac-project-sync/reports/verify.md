# Verify — 0906-mac-project-sync

PASS · 2026-10-13T13:59:39.963Z · commands from explicit

## Commands

### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (6s)

```
test_absent_and_idempotent (__main__.SafetyTests.test_absent_and_idempotent) ... ok
test_dirty_and_untracked_preserved (__main__.SafetyTests.test_dirty_and_untracked_preserved) ... ok
test_existing_empty_and_atomic_race_preserved (__main__.SafetyTests.test_existing_empty_and_atomic_race_preserved) ... ok
test_final_readback_detects_descendant_and_staging (__main__.SafetyTests.test_final_readback_detects_descendant_and_staging) ... ok
test_incomplete_runtime_and_release_never_pass (__main__.SafetyTests.test_incomplete_runtime_and_release_never_pass) ... ok
test_missing_or_diverged_upstream_is_preserved (__main__.SafetyTests.test_missing_or_diverged_upstream_is_preserved) ... ok
test_offline_bundle_and_bad_digest (__main__.SafetyTests.test_offline_bundle_and_bad_digest) ... ok
test_remote_drift_preserves_old_checkout (__main__.SafetyTests.test_remote_drift_preserves_old_checkout) ... ok
test_scoped_transport_preserves_identity_and_rejects_redirects (__main__.SafetyTests.test_scoped_transport_preserves_identity_and_rejects_redirects) ... ok
test_unpushed_commit_preserved (__main__.SafetyTests.test_unpushed_commit_preserved) ... ok
test_unsafe_paths_urls_and_symlinks (__main__.SafetyTests.test_unsafe_paths_urls_and_symlinks) ... ok

----------------------------------------------------------------------
Ran 11 tests in 6.161s

OK
```

### `python3 scripts/fleet-project-sync.py --verify-receipt /Users/antonabyzov/.local/share/specweave/fleet/project-sync-20261013/receipt.json` → exit 0 (0s)

```
Recorded evidence verified; this is not a fresh live probe.
```

### `python3 scripts/fleet-project-sync.py --verify-release /Users/antonabyzov/.local/share/specweave/fleet/project-sync-20261013/release.json` → exit 0 (0s)

```
Recorded evidence verified; this is not a fresh live probe.
```

## Acceptance criteria

4/4 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | A manifest identifies the published branch and exact commit for each umbrella and canonical nested repository, plus source and ownership blockers. |
| AC-02 | x (tasks) | M1 and M3 have independent clean copies matching the manifest; existing dirty or diverged destinations are preserved and reported. |
| AC-03 | x (tasks) | Destination project folders are registered or discoverable, and bounded coordinator and worker execution is verified on each Mac with exact source/version receipts. |
| AC-04 | x (tasks) | One coordinated SpecWithCode Mac release is published and installed where safe, with version/source readback and outstanding gates explicit. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-mac-project-sync | python3 scripts/fleet-project-sync.py --self-test → exit 0 … |  |
| T-02 | done | codex@antons-macbook-m4max | python3 scripts/fleet-project-sync.py --verify-receipt /Use… |  |
| T-03 | done | codex@antons-macbook-m4max | python3 scripts/fleet-project-sync.py --verify-release /Use… |  |

3/3 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
