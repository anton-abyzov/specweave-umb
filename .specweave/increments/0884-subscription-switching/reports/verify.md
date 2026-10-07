# Verify — 0884-subscription-switching

PASS · 2026-10-07T08:13:29.910Z · commands from explicit

## Commands

### `/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node --test /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0884-switch/contrib/subscription-switch/test/*.test.mjs` → exit 0 (7s)

```
ok 24 - quota failover occurs only after exit; retains failed attempt, checkpoints dirty tracked files
  ---
  duration_ms: 834.812458
  type: 'test'
  ...
# Subtest: dirty workspace without allowlist stops failover and timeout cannot become success
ok 25 - dirty workspace without allowlist stops failover and timeout cannot become success
  ---
  duration_ms: 1616.681791
  type: 'test'
  ...
# Subtest: explicit Claude file-write run uses ordinary permissions and passes mandatory headless rules
ok 26 - explicit Claude file-write run uses ordinary permissions and passes mandatory headless rules
  ---
  duration_ms: 576.818125
  type: 'test'
  ...
# Subtest: authoritative quota failure excludes profile across groups until newer valid observation
ok 27 - authoritative quota failure excludes profile across groups until newer valid observation
  ---
  duration_ms: 785.589042
  type: 'test'
  ...
# Subtest: real-shaped Codex NDJSON nested strings and secret fields are redacted in receipts
ok 28 - real-shaped Codex NDJSON nested strings and secret fields are redacted in receipts
  ---
  duration_ms: 576.620333
  type: 'test'
  ...
# Subtest: loopback API rejects cross-origin/Host/schema/oversize and never exposes an exec route
ok 29 - loopback API rejects cross-origin/Host/schema/oversize and never exposes an exec route
  ---
  duration_ms: 570.688334
  type: 'test'
  ...
# Subtest: dedicated SSH dashboard aliases require exact same-origin JSON and exclude other hosts/ports
ok 30 - dedicated SSH dashboard aliases require exact same-origin JSON and exclude other hosts/ports
  ---
  duration_ms: 490.080708
  type: 'test'
  ...
1..30
# tests 30
# suites 0
# pass 30
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 6950.654125
```

### `/usr/bin/python3 /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0884-switch/contrib/subscription-switch/scripts/installer-check.py` → exit 0 (5s)

```
test_duplicate_members_rejected (__main__.ArchiveTests) ... ok
test_regular_archive_and_executable_mode (__main__.ArchiveTests) ... ok
test_unsafe_archive_rejected_before_any_file_created (__main__.ArchiveTests) ... ok
test_asynchronous_teardown_waits_before_replacement (__main__.InstallerTests) ... ok
test_bootstrap_failure_rolls_back_exact_service (__main__.InstallerTests) ... ok
test_changed_old_bundle_preserved (__main__.InstallerTests) ... ok
test_existing_install_lock_preserved (__main__.InstallerTests) ... ok
test_failed_bootout_keeps_loaded_prior_service (__main__.InstallerTests) ... ok
test_init_failure_and_missing_domain_do_not_stop_service (__main__.InstallerTests) ... ok
test_modified_service_and_loaded_foreign_identity_preserved (__main__.InstallerTests) ... ok
test_receipt_failure_after_bootstrap_rolls_back (__main__.InstallerTests) ... ok
test_unknown_launcher_preserved_even_optimized (__main__.InstallerTests) ... ok
test_update_success_preserves_profiles_and_previous_bundle (__main__.InstallerTests) ... ok
test_wait_is_bounded_and_rejects_unknown_errors (__main__.InstallerTests) ... ok

----------------------------------------------------------------------
Ran 14 tests in 4.564s

OK
```

### `PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never SWITCH_EVIDENCE_DIR=/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification /opt/anaconda3/envs/ml_env39/bin/python /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0884-switch/contrib/subscription-switch/scripts/ui-check.py` → exit 0 (6s)

```
      "viewport": "desktop-dark",
      "overflow": false,
      "policy_refresh_selection": "passed",
      "automatic_selection": "passed",
      "unknown_exhausted": "passed",
      "invalid_measurements": "passed",
      "xss_long_rtl": "passed",
      "failed_run": "passed",
      "newest_receipts_first": "passed",
      "api_error": "passed",
      "legacy_auth_gates": "passed"
    },
    {
      "viewport": "phone-light",
      "overflow": false,
      "policy_refresh_selection": "passed",
      "automatic_selection": "passed",
      "unknown_exhausted": "passed",
      "invalid_measurements": "passed",
      "xss_long_rtl": "passed",
      "failed_run": "passed",
      "newest_receipts_first": "passed",
      "api_error": "passed",
      "legacy_auth_gates": "passed"
    },
    {
      "viewport": "phone-dark",
      "overflow": false,
      "policy_refresh_selection": "passed",
      "automatic_selection": "passed",
      "unknown_exhausted": "passed",
      "invalid_measurements": "passed",
      "xss_long_rtl": "passed",
      "failed_run": "passed",
      "newest_receipts_first": "passed",
      "api_error": "passed",
      "legacy_auth_gates": "passed"
    }
  ],
  "screenshots": [
    "/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification/desktop-light.png",
    "/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification/desktop-light-auth-gates.png",
    "/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification/desktop-dark.png",
    "/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification/desktop-dark-auth-gates.png",
    "/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification/phone-light.png",
    "/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification/phone-light-auth-gates.png",
    "/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification/phone-dark.png",
    "/Users/antonabyzov/Projects/research/subscription-switching-2026-10-07/ui-increment-verification/phone-dark-auth-gates.png"
  ]
}
```

### `bash -n /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0884-switch/contrib/subscription-switch/scripts/worker-bootstrap.sh` → exit 0 (0s)

```
(no output)
```

## Acceptance criteria

8/8 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | Research maps transcript claims to current primary sources, names exact products/forks, resolves Obsidian contradictions, and evaluates SpecWeave naming. |
| AC-02 | x (tasks) | CLIProxyAPI and VibeProxy install with verified digests; proxy binds loopback, authenticates clients, keeps management local, enables session affinity and bounded retry, and exposes no credentials in receipts. |
| AC-03 | x (tasks) | Seven native profile slots preserve existing authentication; refreshed quota observations separate window/weekly limits, remain unknown when unavailable, and eligible selection supports reset-first/spend-first while avoiding exhausted profiles. |
| AC-04 | x (tasks) | Native runs hold an exclusive workspace lease, record actual outcomes, can fail over only after the prior run ends with a quota error, and never turn a failed run into success. |
| AC-05 | x (tasks) | A dirty tracked workspace can checkpoint and restore into a fresh isolated worktree with hashes/base verification; unsafe paths, symlinks, secrets and arbitrary untracked files are rejected. |
| AC-06 | x (tasks) | Loopback dashboard displays account/host/service state, refresh and policy controls with same-origin guarded mutations; desktop/phone/light/dark checks run explicitly headless. |
| AC-07 | x (tasks) | T3 nightly installs separately from stable and passes version/startup/headless state capture; selected native Codex completes a real read-only run through the companion. |
| AC-08 | x (tasks) | Authenticated installation and readback on M1/M3 complete, or exact missing external authorization/access is documented with a reproducible bootstrap; no unreachable worker is represented as installed. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | test -s .specweave/increments/0884-subscription-switching/r… |  |
| T-02 | done | codex@antons-macbook-m4max | /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node --t… |  |
| T-03 | done | codex@antons-macbook-m4max | PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never SWITCH_EVIDENCE_DIR=/U… |  |
| T-04 | done | codex@antons-macbook-m4max | /Users/antonabyzov/.local/bin/specweave-switch doctor → exi… |  |
| T-05 | done | codex@antons-macbook-m4max | bash -n /Users/antonabyzov/Projects/github/specweave-umb/re… |  |

5/5 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
