# 1015 Prepare Mac and mobile release

## Problem
Anton requested the latest verified SpecWithCode mobile and macOS work released roughly five hours after October 23, 2026 at 1:26 AM EDT. Independent dispatchers and pending iOS review can produce competing releases or omit completed work.

## Scope
In: reconcile release owners/runs/schedules; prepare a source-bound candidate manifest; release macOS and submit the latest verified iOS build at the sole coordinator trigger; verify published artifacts and report installed/public boundaries. Out: early publication, forced service restart, physical phone testing without named authorization, unverified redesigns and showcase claims.

## Acceptance Criteria
- [ ] AC-01: Current owners, release runs and sole trigger are recorded; no duplicate dispatch or schedule is created.
- [ ] AC-02: Candidate manifest records source SHAs, review/test evidence and explicit inclusion or exclusion for completed work through the cutoff.
- [ ] AC-03: App Store state, latest iOS source/build and readiness gates are checked before an authorized submission at or after the trigger.
- [ ] AC-04: macOS publication at or after the trigger has exact SHA/run/artifact digests, Developer ID NMCB2JZ7QG and notarization proof; updater/service acceptance is reported separately.
- [ ] AC-05: Durable trigger handoff identifies gates, commands, owners and evidence; release verification and fresh review precede increment completion.

## Approach
Write preparation receipts and a trigger handoff here. Inspect remote release/PR/run state and supported ASC APIs. Coordinate current owners before reserving dispatch. At the trigger re-read all state, freeze exact main SHA and choose the next unclaimed version. Use the approved application checkout and official signed release pipeline; no shared-checkout branch switching or stash. Follow ASC dry-run/validate/confirm gates, preserving an active submission until replacement is necessary and authorized. Browser automation is headless:true with PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never and report open:never. Never directly access userdata/statev2.sqlite files. Do not restart the running service or force a drain without existing authorization.

## Decisions
### Asked
- D-01: User authorized release/submission, not before the coordinator trigger October 23, 2026 at 6:26 AM EDT.
### Defaulted
- D-02: Merge cutoff 6:00 AM EDT, accepted by coordinator; reconcile completed verified items again by release time.
- D-03: Version/build numbers remain unreserved until current dispatchers and App Store state are reconciled.
- D-04: Showcase1008 material is review input only; diagnostics and open installed acceptance remain excluded from release claims.
### Open
- none

## Tasks

### T-01 Reconcile owners, schedules and current releases
- AC: AC-01 | Files: release-readiness.md | Test: gh run list -R anton-abyzov/specwithcode-dev --limit 10

### T-02 Prepare candidate evidence and cutoff handoff
- AC: AC-02, AC-05 | Files: release-readiness.md, handoff.md | Test: test -s .specweave/increments/1015-prepare-mac-and-mobile-release/handoff.md

### T-03 Validate mobile source/build and submit at trigger
- AC: AC-03 | Files: mobile-receipt.md | Test: asc status --app 6824245458 --include builds,appstore,submission,review --output json

### T-04 Publish and verify signed macOS candidate at trigger
- AC: AC-04 | Files: macos-receipt.md | Test: gh release view -R anton-abyzov/specwithcode-dev

### T-05 Verify and close 1015
- AC: AC-05 | Files: review.md | Test: specweave verify 1015
