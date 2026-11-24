# Ship Chrome no-window recovery

## Problem

chrome_open fails with No current window when the paired profile has no window.

## Scope

Recover the existing tab-create command in the extension, test it, merge and release extension and app through one dispatcher. Do not drive Chrome or run DCFC.

## Acceptance Criteria

- [ ] AC-01: Missing current window creates a normal window and returns its tab; unrelated errors remain errors.
- [ ] AC-02: Required CI and exact-head review pass before merge.
- [ ] AC-03: Extension and app releases are verified and installed status is reported accurately.

## Approach

Catch only the exact Chrome missing-window error for implicit-window tab creation. Keep the existing server claim, attach and navigation contract.

## Tasks

### T-01: Implement and test recovery
- AC: AC-01 | Files: apps/chrome-extension/src/relayConnection.js, apps/chrome-extension/test/extension.test.js | Test: extension unit suite

### T-02: Review, merge and release
- AC: AC-02, AC-03 | Files: release metadata | Test: CI and publication receipts

### T-03: Verify and close 1241
- AC: AC-01, AC-02, AC-03 | Files: spec.md | Test: specweave verify
