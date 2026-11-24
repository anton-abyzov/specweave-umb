Current closure review: see `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/fresh-review-final.md`. Earlier HOLD findings below are historical; App Privacy and build 8 submission have since been resolved.

# Fresh-context release review

Verdict: PASS for macOS 1.0.75 publication. HOLD increment completion. Mobile App Review replacement and App Privacy confirmation remain pending; installed updater and feature acceptance remain separate.

Scope: Read-only review of retained release evidence on October 23, 2026. No product changes, provider calls, account changes, installation, restart, browser automation or live database access.

## Verification

- Workflow `39939287862` concluded `success` on frozen source `ddeaee06b130f8c582e6d4801d636fd66c6936e4`. Release job and all executed steps succeeded. Evidence: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/macos-run-terminal.json`.
- Independently checked Git ancestry against published private source `c52ee223ae58bf79e6aa313089f81aaf56286e9c`: frozen source and all 12 intended merges are ancestors. Frozen-to-published diff contains only four package version changes. Reviewed source manifest: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/trigger-manifest.json`.
- Independently recomputed SHA-256 for all eight locally downloaded assets covered by `/Volumes/Work/specwithcode-release-1075-verify/public/SHA256SUMS`. Both DMG names, ZIP, updater metadata, helper manifest, runtime archive, helper archive and latest-mac metadata match. Retained public/private release digests also match. Evidence: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/macos-digest-verification.json` and `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/macos-plan-and-sums.json`.
- Public and private releases are published, not drafts. The workflow checks the exact DMG/ZIP inner apps for Developer ID `NMCB2JZ7QG` and notarization before publication. Local downloaded ZIP check independently passes. Evidence: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/macos-run-complete.log` and `/Volumes/Work/specwithcode-release-1075-verify/signature-zip.json`.
- Local DMG mount denial does not invalidate matching exact-artifact CI proof. It does limit local verification. The container itself must not be described as signed/stapled; Developer ID/notarization claims apply to the inner application.
- Independently recomputed retained IPA SHA-256 as `cef31915b41b3268207e4efe276cf9da71fb5291c97a35414b0644758e4757ac`, matching the export receipt. Apple build `0b60cfe0-71eb-40da-b44f-140e5c9c8a53` is build 8, version 0.1.0, `VALID`, linked to the existing Internal group and `IN_BETA_TESTING`. Evidence: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ipa-verification.json`, `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-build8-info.json`, `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-build8-groups-readback.json` and `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-build8-beta-detail.json`.

## Remaining gates and reporting limits

No blocking defect found in Mac publication evidence. Do not close 1015 or claim build 8 App Store submission/public availability. Existing build 4 review remains preserved; pending published App Privacy confirmation is unresolved. Source privacy configuration and cached Apple authentication state do not prove publication either way. Retained Apple status: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-status-after-upload.json`.

Installed app/service remain reported as 1.0.74. No receipt supports installed 1.0.75, new updater agent activation, held/disconnected timing, filesystem peak delta, feature UI/manual acceptance or physical TestFlight launch. Original owners must receive actual identity and their requested evidence following an authorized installation.

Minor wording correction: Apple beta detail has `autoNotifyEnabled: true`. The receipt can say no explicit tester-notification command was issued; it cannot prove no automatic notification occurred. The older `uploaded: false` in the pre-upload IPA verification is a historical export-time field, superseded by the Apple build readback, not a current upload failure.

Receipt status headers were stale at initial inspection; parent is updating those concurrently. No completion gate was waived by this review.
