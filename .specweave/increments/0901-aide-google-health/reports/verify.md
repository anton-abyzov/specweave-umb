# Verify — 0901-aide-google-health

PASS · 2026-10-13T13:16:33.335Z · commands from explicit

## Commands

### `python3 -B .specweave/increments/0901-aide-google-health/reports/verify-shipment-109.py` → exit 0 (1s)

```
{"checkedAt": "2026-10-13T13:16:33.251227+00:00", "version": "1.0.9", "sourceCommit": "51c49ab4603c17c87362e9700cd242b24ed83e2e", "result": "passed", "publicReceiptSha256": "01825a497f2701b36b3a0e47943bdd4394d1be3e59bda40728b7111cc739a773", "guardReceiptSha256": "796392c7d3ecfcab94479e34643358d71b84e43580bab722804e1b400eb92162", "nativeAboutReceiptSha256": "6450b3ce3ba14d47e85a25caf97e02fa8c7f9a149ade46c8c7b7d40c6ce59ef7", "runtimeArchiveSha256": "552c4c7101b5d71e62e43d9e6d59b8ed95e7edc803368dbe6dbf0a2e8c053a7f", "reviewedNavigationFilesMatched": 8, "chatTimelineLinkRetained": true, "installedManifestEntriesVerified": 7481, "runtimePid": 16665, "runtimeHTTP": 200, "webAssetHTTP": 200, "desktopPid": 49969, "desktopSignatureVerified": true, "nativeLoadedDesktopVersionVerified": true, "completeDatabaseContinuity": "verified", "rowPreservation": "verified-existing-browser-heartbeat", "protectedAuthIdentityAndOriginalServicesPreserved": true, "googleProof": "Separate real Aide proof on 1.0.8; no repeated Google calls"}
```

### `python3 -B .specweave/increments/0901-aide-google-health/reports/navigation/verify-receipts.py` → exit 0 (0s)

```
PASS: two saved headless receipts and retained artifact hashes; no live Google claim
```

### `python3 -B .specweave/increments/0901-aide-google-health/reports/verify-real-google.py .specweave/increments/0901-aide-google-health/reports/live-google-status-20261013T1214.json .specweave/increments/0901-aide-google-health/reports/live-google-native-20261013T1214.json --expected-version 1.0.8 --expected-source 291f919c24b600e400b8c64e9f3dd383795f33a6` → exit 0 (0s)

```
{"verifiedAt": "2026-10-13T13:16:33.329555+00:00", "version": "1.0.8", "sourceCommit": "291f919c24b600e400b8c64e9f3dd383795f33a6", "statusReceiptSha256": "61fb15934a114d2d651063586fc5a7717023b4ba3c07adbcfee7b7e08fc4e7bc", "nativeReceiptSha256": "306f6ed9dfffceb8ae1fee3c3bc0bfb9f3b9c86f3f93baa255acb9e992ea9514", "dispatchReceiptSha256": null, "proofPhase": "native", "nativeRunCompleted": true, "googleHealth": "all_three_apis_verified", "readCounts": {"studio_google_calendar_events": 1, "studio_google_gmail_search": 1, "studio_google_drive_search": 1}, "ownedTemporarySessionsRevoked": true, "existingSessionsPreserved": true}
```

## Acceptance criteria

9/9 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | Google status distinguishes missing sign-in, missing project authorization and failed API access without leaking ungranted account identity or personal data. |
| AC-02 | x (tasks) | Authorized health checks probe Gmail, Calendar and Drive with content-free field projections; revoked credentials and API/network failures remain explicit. |
| AC-03 | x (tasks) | Coordinators discover native Google tools and check readiness before delegating Google-only reads. |
| AC-04 | x (tasks) | Exhausted provider admission retains usage_limit and reset metadata so existing recovery can act, reusing completed 0899 work. |
| AC-05 | x (tasks) | Focused tests, builds and independent review pass; matching newer artifacts and update plans are published to both feeds and read back. |
| AC-06 | x (tasks) | The coordinated guarded updater installs 1.0.7 on M4 with preserved state, passing health, exact source/version readback, and matching desktop version. |
| AC-07 | x (tasks) | Aide completes real read-only Gmail, Calendar and Drive requests through its native Google tools after account consent and project authorization, with exact evidence and no fabricated success. |
| AC-08 | x (tasks) | Cancel, X, Escape and backdrop dismissal of Morning briefing return to its originating screen including settings scope and hash; direct links safely fall back to Scheduled tasks, successful saves remain there, and other Settings cancellation paths are audited and regression checked. |
| AC-09 | x (tasks) | The remaining chat-linked editor dismissal fixes are included in the coordinated follow-up release, with published and installed exact-source evidence; preserve the sole installer and the completed real Google proof. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-aide-google | cd /Users/antonabyzov/.codex/worktrees/aide-google-health/s… |  |
| T-02 | done | codex-aide-parent | cd repositories/anton-abyzov/specweave-studio && PWDEBUG=0 … |  |
| T-03 | done | codex-aide-parent | cd repositories/anton-abyzov/specweave-studio && PWDEBUG=0 … |  |
| T-04 | done | codex-aide-parent | python3 .specweave/increments/0901-aide-google-health/repor… |  |
| T-05 | done | codex-aide-parent | /usr/bin/python3 -B .specweave/increments/0901-aide-google-… |  |
| T-06 | done | codex@antons-macbook-m4max | python3 -B .specweave/increments/0901-aide-google-health/re… |  |
| T-07 | done | codex-aide-navigation | python3 -B .specweave/increments/0901-aide-google-health/re… |  |
| T-08 | done | codex@antons-macbook-m4max | python3 -B .specweave/increments/0901-aide-google-health/re… |  |

8/8 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
