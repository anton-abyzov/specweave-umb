# Verify — 1092-refresh-and-revalidate-folder-copy-scans

PASS · 2026-11-25T00:22:12.934Z · commands from config testing.commands

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
Ran 13 tests in 10.099s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.352s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.095s

OK
recorded
```

- Working directory: . (explicit)
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
Ran 13 tests in 9.779s

OK
```

- Working directory: . (explicit)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.347s

OK
```

- Working directory: . (explicit)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.077s

OK
recorded
```

## Acceptance criteria

6/7 met · 1 skipped (accepted), not verified

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | Fresh scans count only existing registered external worktree folders; missing registrations are separately labelled and no registration is removed. |
| AC-02 | x (tasks) | met | Resumed scans expose their timestamp or unknown historical age. Refresh checks current source state without cancelling jobs, changing selections, approvals or secret exclusions. |
| AC-03 | x (tasks) | met | Copy approval validates the exact reviewed source artifact and destination preview before transfer. Legacy live-file jobs require fresh source inventory; durable captured-file jobs may copy reviewed bytes while newer source work continues. Missing or corrupt captured data never falls back to live files. Destination changes still require review. |
| AC-04 | x (tasks) | met | Removed and added worktrees, resume versus new scan, unchanged refresh and changed source/destination are covered by isolated tests. Current source, implementation and installed acceptance are reported separately. |
| AC-05 | x (tasks) | met | Copy comparison distinguishes planned counts from repository size and pending decisions, avoids asserting unproven destination repository identity, and offers compact group choices with explicit per-file review without applying a transfer. |
| AC-06 |   | skipped-accepted | The explicitly authorized M4 umbrella to Ministorm migration is completed through supported controls with prior destination outcomes reconciled, unique destination work preserved, secrets opt-in only, verified destination project/coordinator path and continuation, and real screenshots for every meaningful step. Source drafts, active workers and Stop holds survive. |
| AC-07 | x (tasks) | met | A durable immutable snapshot of selected non-secret files makes reviewed copies independent of later source churn, including existing destinations. Restart, corruption, disk failure, cancellation and cleanup preserve source files; live freshness and deferred move ownership checks remain honest and strict. |

### Accepted skips (not verified)

- AC-06 check `Ministorm migration through supported controls with screenshots` — Superseded: Ministorm has run the specweave project since the real M4 to ministorm move on released 1.0.110 (increment 1117, evidence ~/.specwithcode/m4/evidence/handoff-ux/real-move-1.0.110-run2), and 1390 Sync and Add replaced this copy flow. No migration performed, nothing discarded. Untested: the October 27 reconciliation, integrity and continuation screenshots for this flow were never captured. Basis: Anton's standing rule feedback_use_recommended_options (November 22, 2026), applied by the coordinator on November 24, 2026.. Accepted by Anton (standing rule) at 2026-11-24T15:30:49.719Z; authorization: "Do use all recommended. Where you wanted me to ask, just use recommended. That's my confirmed approach." (Anton, November 22, 2026, memory feedback_use_recommended_options); recommended option 'Skipped (accepted), superseded' applied by the coordinator, November 24, 2026 (recorded by claude@anton-m5max-proled at 2026-11-24T15:30:49.721Z)

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | 6607c9963a; 360 focused tests pass, 34 final service checks… |  |
| T-02 | done | codex@antons-macbook-m4max | 6607c9963a; 12 headless cases and 172 screenshots pass; unc… |  |
| T-03 | done | claude@anton-m5max-proled | Block cleared November 24, 2026: the October 27 no-live-cop… |  |
| T-04 | done | codex@antons-macbook-m4max | c06f65b344397036f01d398d9caaa8be1d77a14b; server package ty… |  |
| T-05 | done | codex@antons-macbook-m4max | acea943745713232e02837b899fcb9a568d04742; 76 tests/4files, … |  |
| T-06 | skipped | claude@anton-m5max-proled |  | Superseded: Ministorm has run the specweave project since t… |
| T-07 | done | codex@antons-macbook-m4max | e2f47939668a8092397e2070e9521af181795447; actual ready-reco… |  |
| T-08 | done | codex@antons-macbook-m4max | a6a4fb154a; PR #958; 123 focused tests, baseline disk regre… |  |
| T-09 | skipped | claude@anton-m5max-proled |  | Duplicate closing task of T-03; its migration gate is T-06,… |
| T-10 | done | copy-freshness-root | cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-… |  |
| T-11 | done | copy-freshness-root | cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-… |  |
| T-12 | done | claude@anton-m5max-proled | Owner copy-snapshot-fleet's lease expired October 29 with n… |  |

10/12 done · 2 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

### Skipped

- T-06 — Superseded: Ministorm has run the specweave project since the real M4 to ministorm move on released 1.0.110 (increment 1117, evidence ~/.specwithcode/m4/evidence/handoff-ux/real-move-1.0.110-run2), and 1390 Sync and Add replaced this copy flow. No migration performed, nothing discarded. Untested: the October 27 reconciliation, integrity and continuation screenshots for this flow were never captured. Basis: Anton's standing rule feedback_use_recommended_options (November 22, 2026), applied by the coordinator on November 24, 2026. (claude@anton-m5max-proled)
- T-09 — Duplicate closing task of T-03; its migration gate is T-06, skipped as superseded. Superseded: Ministorm has run the specweave project since the real M4 to ministorm move on released 1.0.110 (increment 1117, evidence ~/.specwithcode/m4/evidence/handoff-ux/real-move-1.0.110-run2), and 1390 Sync and Add replaced this copy flow. No migration performed, nothing discarded. Untested: the October 27 reconciliation, integrity and continuation screenshots for this flow were never captured. Basis: Anton's standing rule feedback_use_recommended_options (November 22, 2026), applied by the coordinator on November 24, 2026. (claude@anton-m5max-proled)
