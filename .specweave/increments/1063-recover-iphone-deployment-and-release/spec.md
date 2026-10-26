# Recover iPhone deployment and release

## Problem

On October 24, 2026 at 7:22 PM EDT the iPhone deployment worker (Codex, GPT-6.1-Sol) failed in 2 seconds with the provider error "Your access token could not be refreshed because you have since logged out or signed in to another account. Please sign in again." The user had just re-logged the coordinator's Codex subscription. The user still sees duplicated EasyChamp rows in Projects on the iPhone, and wants the latest Mac release cut and the latest iOS source on the phone.

## Scope

In: root cause of the refresh failure (Codex home/profile isolation and refresh behavior, without reading credential contents or changing accounts); findings for the all-thread recovery owner; routing the release authorization to the existing release owner; a development-signed install of current iOS source on iPhoneA with app data and pairing preserved; an on-device check of EasyChamp rows in Projects. Out: App Store/TestFlight upload or submission (release owner), deleting, archiving or merging projects, account login/logout, resuming other threads (completion-sweep owner).

## Acceptance Criteria

- [x] AC-01: A root-cause note names which Codex home each affected thread used, whether the coordinator's relogin shares that home, and how Codex refresh fails after a relogin, separating evidence from inference.
- [x] AC-02: The completion-sweep owner receives the list of threads affected by the failure and the safe resume condition.
- [x] AC-03: The release owner has the user's release authorization, and the report names the released version or the gate that stops it.
- [x] AC-04: iPhoneA runs a build of current iOS source: installed CFBundleVersion, source SHA and a launched process are read back from the device, and the app data container is unchanged.
- [x] AC-05: The EasyChamp entries in Projects on the updated phone are checked and the outcome (fixed, or still duplicated with the cause) is recorded with evidence.

## Approach

Read provider config and service code for Codex instance homes (`CODEX_HOME`), compare file metadata (not contents) of auth files per home, and read the failed thread's run. Build with the existing workflow from the earlier worker: xcodegen, `asc xcode archive` with team NMCB2JZ7QG, `devicectl device install app` on E7C41CC8-90F0-551A-BBAD-31DCF8201E9F, which upgrades in place and keeps the container.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Release is cut by the existing release owner thread, not this worker → avoids a duplicate release lane.
- D-02: Install a development-signed build directly to the phone; no upload.
### Open
- none

## Tasks

### T-01 Root-cause the Codex refresh failure
- AC: AC-01 | Files: .specweave/increments/1063-recover-iphone-deployment-and-release/reports/codex-auth-root-cause.md | Test: test -s .specweave/increments/1063-recover-iphone-deployment-and-release/reports/codex-auth-root-cause.md

### T-02 Send recovery findings to the completion-sweep owner
- AC: AC-02 | Files: none | Test: thread send receipt in the report

### T-03 Route release authorization and read back the release
- AC: AC-03 | Files: none | Test: gh release view on the new tag

### T-04 Install current iOS source on iPhoneA
- AC: AC-04 | Files: ~/.specwithcode/m4/evidence/iphone-latest-20261024/receipt.json | Test: ideviceinstaller list readback of CFBundleVersion and container

### T-05 Check EasyChamp rows in Projects on the phone
- AC: AC-05 | Files: ~/.specwithcode/m4/evidence/iphone-latest-20261024/ | Test: on-device screenshot or source trace in the report

### T-06 Verify and close 1063
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1063-recover-iphone-deployment-and-release
