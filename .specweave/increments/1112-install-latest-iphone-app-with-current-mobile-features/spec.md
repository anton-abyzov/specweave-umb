# Install latest iPhone app with current mobile features

## Problem

Anton requests the latest SpecWithCode iPhone app, including the latest merged mobile features. iPhoneA currently has 0.1.0 (10), with Connect build configuration empty.

## Scope

Build exact merged main in isolated evidence source, test simulator first, then install in place on authorized iPhoneA. Preserve app data, drafts, pairing and other runs. No store publication, project identity mutation or service restart.

## Acceptance Criteria

- [ ] AC-01: Exact source, latest merged iOS feature inventory, device identity and prior installed build are recorded.
- [ ] AC-02: Core Swift tests and simulator build/checks pass for the candidate with Connect public build configuration.
- [ ] AC-03: A signed Release candidate is installed in place on iPhoneA and independent version/build readback and launch outcome are recorded.
- [ ] AC-04: Included features and remaining server/account/native proof limits are recorded with screenshots where supported.

## Approach

Use existing Apple team NMCB2JZ7QG and store bundle id com.specwithcode.ios. Build 11 from exact main 2233025d4fe526ffb756c8addb9225b0067729e1. Public Connect settings come from current GitHub repository variables. Use current project generators and Xcode tools, stripping injected GIT_CONFIG variables. No credential reads or account changes. Simulator work stays headless and file-backed.

## Tasks

### T-01 Reconcile ownership and candidate provenance
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/iphone-latest-20261028/receipt.md | Test: source and device readback

### T-02 Test candidate on simulator
- AC: AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/iphone-latest-20261028/ | Test: Swift core tests, simulator build and focused UI checks

### T-03 Install and verify physical candidate
- AC: AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/iphone-latest-20261028/ | Test: signing, install, independent readback and launch/screenshots

### T-04 Verify and close 1112
- AC: AC-01, AC-02, AC-03, AC-04 | Files: reports/ | Test: specweave verify and fresh-context review
