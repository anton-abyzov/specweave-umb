# Verify — 1351-reviewer-order-family-rule

FAIL · 2026-11-15T04:16:10.179Z · commands from config testing.commands

## Commands

- FAIL: No testing.ownerCommands configured for repositories/anton-abyzov/specwithcode
- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (2s)

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
Ran 13 tests in 1.961s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.167s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.036s

OK
recorded
```

## Acceptance criteria

5/5 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | Each Review row names its model family; a row whose family wrote the work here (the Daily and Hard models) carries "Skipped for <Family> work". |
| AC-02 | x (tasks) | met | Under the Review list, one line per author family in Daily and Hard says which model reviews that work now ("Work by Opus 5.5 or Fable 5.2 → muse-wonder-full-1.0 reviews"), computed by `resolveReviewer`, or says no reviewer can run and why. |
| AC-03 | x (tasks) | met | Project settings > Adversarial review shows the same Review card as the Models page (project-scoped), with no stacked-icon chip anywhere; other sources of a model read as text. |
| AC-04 | x (tasks) | met | A Review source whose usage is unknown shows "Usage unknown" with the reason (no recent reading, last check failed, sign-in cannot report usage, refused turn, reset passed) and a Check now action that re-reads providers. |
| AC-05 | x (tasks) | met | `resolveReviewer` keeps skipping same-family entries when the author is Fable 5.2 and Claude Opus 5.5 is #1 (test), and the settings links ("fallback order", "app-wide reviewer order") land on existing targets. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@minisforum | cd /srv/specwithcode/ministorm/worktrees/reviewer-order-fam… |  |
| T-02 | done | claude@minisforum | cd /srv/specwithcode/ministorm/worktrees/reviewer-order-fam… |  |
| T-03 | done | claude@minisforum | cd /srv/specwithcode/ministorm/worktrees/reviewer-order-fam… |  |

3/3 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
