# Final fresh-context review: 1015

Verdict: PASS for the release and submission evidence. No critical or high findings. CLI verification must finish green before completion; this review does not claim its outcome.

Reviewer context: independent fresh subagent on October 23, 2026. Read-only review of receipts and source-bound release records. No browser actions, provider calls, product changes, tests, installations, restarts, drain operations, live database access or release dispatch performed.

## Conclusions

The retained Apple submission response binds app `6824245458`, version `0.1.0`, version ID `08b06b7f-6e58-4982-8cbd-65681a10740b`, and exact build ID `0b60cfe0-71eb-40da-b44f-140e5c9c8a53` to new submission `3cf1d21d-dc72-418d-a88e-f8ec77586a4f`. The subsequent status receipt identifies build 8 as VALID and the same submission as WAITING_FOR_REVIEW, with no blocking issues. The earlier build 4 submission cancellation and build 8 attachment have explicit success receipts. This supports submitted, not approved or publicly available.

The Chrome extension snapshot is for the intended app ID and displays “Published 5 days ago by Anton Abyzov”, “Data Not Collected” and “Data is not collected from this app.” This resolves the prior privacy publication uncertainty; the public API advisory alone was not treated as proof. Validation has zero blocking errors, with the empty initial-version whatsNew warning reported rather than hidden.

The iOS source/tree and retained signature evidence remain bound to build 8. The existing physical receipt records development archive build 8 launch and an independently matched running executable/PID. This is archive development launch evidence, not a TestFlight launch or complete native feature acceptance. The release receipt preserves that distinction and does not claim a new phone action.

The retained Mac terminal run is successful at frozen source `ddeaee06b130f8c582e6d4801d636fd66c6936e4`. Manifest records twelve included merge ancestors and explicit exclusions; digest receipt binds published source `c52ee223ae58bf79e6aa313089f81aaf56286e9c`, shared feed digest equality and downloaded artifact hashes. The earlier independent review records recomputation of downloaded sums and ancestry. Signature/notarization statements apply to the application inside DMG/ZIP; the unsigned DMG container and local mount refusal remain explicit.

Mac publication and installed acceptance remain separate. Current receipt reports service 1.0.75 verified while desktop app was last reported 1.0.74. No installed UI or all-features acceptance follows from this release. PR #633 remains excluded from 1.0.75 despite its later merge for a future candidate.

Incident accounting explicitly identifies seven measurement-job restarts, six stop-work windows and 118 affected runs across 24 threads. It corrects stopped 9 to the last prepare result, distinguishes two substantive interrupted work threads from nine lost 1011 result relays, and routes recovery to original owners. Job/hold absence and user-Stop classification are attributed to the owner's evidence. Recovery is not claimed completed. Peak disk and next-upgrade held-snapshot behavior remain unproven.

## Evidence reviewed

- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/spec.md`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/macos-receipt.md`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/mobile-receipt.md`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/review.md`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-submit-build8.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-status-build8-submitted.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-cancel-build4.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-attach-build8.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ios-validate-build8.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/app-privacy-browser.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/app-privacy-published.png` (existence and nonempty file checked; image not independently visually inspected)
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/trigger-manifest.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/macos-digest-verification.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/macos-run-terminal.json`
- `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/ipa-verification.json`
- `/Users/antonabyzov/.specwithcode/m4/evidence/iphone-latest-afdafde6c-b8/receipt.json`
- `/Users/antonabyzov/.specwithcode/m4/evidence/update-measure-1075/recovery/receipt.md`

Current receipt headers and chronological supersession were re-read after parent corrected stale status wording. No remaining review finding blocks the release evidence close. App Review outcome, desktop installation, individual feature runtime acceptance and incident work recovery remain separate owner follow-ups.
