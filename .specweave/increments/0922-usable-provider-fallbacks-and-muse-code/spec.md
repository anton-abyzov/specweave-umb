# 0922 Usable provider fallbacks and Muse Code

## Problem
Fallback suggestions accept unknown quota and can suggest an unusable Grok account. Muse Code and its subscription-only Wonder Full model are missing.

## Scope
Conservative fallback eligibility, Muse native protocol driver, authenticated model discovery, setup guidance and focused verification. No account purchases or changes to other owners' checkouts.

## Acceptance Criteria
- [ ] AC-01: Suggested fallbacks require authenticated, fresh positive usage evidence and a listed model; unknown, denied, stale and exhausted accounts are excluded.
- [ ] AC-02: Muse Code is a configurable provider using the official session protocol, with streaming turns, cancellation and approval handling.
- [ ] AC-03: Wonder Full appears only when the native account exposes it; API-key access does not imply Full entitlement. Missing CLI/auth have actionable setup guidance.
- [ ] AC-04: Focused tests and relevant builds pass; headless UI evidence is saved and credit-recovery integration is reconciled without overwriting its work.

## Approach
Own checkout /Users/antonabyzov/Projects/github/studio-muse-fallback, branch codex/muse-fallback from origin/main 4d6e30488. Coordinate with chat 01a13a74-d940-7f02-91db-0af2ed1bf663 (0918); avoid its credit controls, banner, timeline and ChatView edits. Use native Muse MSP documentation and SDK schema, never infer entitlement from install/login alone. Optional provider disabled by default. Sparse checkout excludes large mobile binaries. All browser automation headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never.

## Tasks
### T-01 Require usable fallback evidence
- AC: AC-01 | Files: /Users/antonabyzov/Projects/github/studio-muse-fallback/packages/shared/src/providerFallback.ts, /Users/antonabyzov/Projects/github/studio-muse-fallback/packages/shared/src/providerFallback.test.ts, /Users/antonabyzov/Projects/github/studio-muse-fallback/packages/shared/src/providerFallbackEligibility.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/providerFallback.test.ts packages/shared/src/providerFallbackEligibility.test.ts
### T-02 Integrate Muse Code
- AC: AC-02, AC-03, AC-04 | Files: /Users/antonabyzov/Projects/github/studio-muse-fallback/apps/server/, /Users/antonabyzov/Projects/github/studio-muse-fallback/packages/contracts/, /Users/antonabyzov/Projects/github/studio-muse-fallback/packages/shared/, /Users/antonabyzov/Projects/github/studio-muse-fallback/apps/web/src/components/settings/providerDriverMeta.ts, /Users/antonabyzov/Projects/github/studio-muse-fallback/apps/web/src/components/settings/ProviderSettingsForm.test.ts, /Users/antonabyzov/Projects/github/studio-muse-fallback/apps/web/tests/provider-usability/, /Users/antonabyzov/Projects/github/studio-muse-fallback/scripts/studio-verify/muse-picker.mjs, /Users/antonabyzov/Projects/github/studio-muse-fallback/docs/studio/muse-code.md, /Users/antonabyzov/Projects/github/studio-muse-fallback/pnpm-lock.yaml | Test: focused Muse provider, adapter and contract tests plus web/server production builds and headless fixture

## Implementation receipt — 2026-10-14

Owned product checkout: `/Users/antonabyzov/Projects/github/studio-muse-fallback`, branch `codex/muse-fallback`.
Commits: `d09180375` initial usable fallback gate; `62fe1c185` expired exhausted-window and custom model follow-ups; `263448ff8` Muse native preview.

Credit-recovery chat `01a13a74-d940-7f02-91db-0af2ed1bf663` received exact commit boundaries and evidence. Its ChatView/banner files were not edited. No remote push, release, account purchase, authentication or paid model call was performed here.

Fresh-context sw-review found and verified fixes for expired exhausted-window eligibility, restored approvals, live unsupported questions, unbounded control requests and approval-stage acknowledgement races. Final re-review reports no remaining high findings; 82 focused tests pass. Native question dialogs and background title/commit/PR generation are explicitly unsupported in this preview.

### Manual acceptance gate

Do not close this increment or claim live Muse acceptance yet. Per AGENTS.md, new UI/auth needs Anton's acceptance. On an eligible native account, accept installation/sign-in, Wonder Full discovery, an authorized turn, approval, cancellation and reconnect. Local MSP fixtures and headless model-picker evidence do not establish account entitlement or release deployment.

## Release validation receipt — 2026-10-14

User explicitly requested deployment/release and approved: "Ship Muse preview; validate my account later". Account acceptance remains deferred; preview release is authorized. Release owner chat `01a133f7-afb4-7771-8e87-55cfabfd6858` reserved these changes for 1.0.19 and retains sole build/publication/install ownership. Credit-recovery chat was notified; explicit paid-credit gates remain unchanged.

PR: https://github.com/anton-abyzov/specweave-studio/pull/183 . Head `6f441d50628cc249aafc996fe4c8ebd7322d2c25`, rebased onto main `ce42cb039`; commits `8d0259874`, `596e46a9a`, `3328c7c1d`, `6f441d506`. Barrel conflict preserved logicalProject, managedUpdates and Muse exports.

Official Muse installer was inspected and installed only into ignored `.artifacts/muse-native/bin`, without PATH/profile changes or authentication. CLI 1.4.8-R6256.1 exposed a protocol fingerprint mismatch with SDK 1.4.7; upgraded exact SDK pin to 1.4.8. Real native offline echo streaming and durable reconnect pass in isolated XDG state. No paid inference or account entitlement claim. 83 focused tests pass; four headless picker checks pass; production server/bundled web build passes. Independent fresh review passed 16 tests and found no blocking findings. Native opt-in test cleans its owned temporary directory.

Full patched typechecks remain red: dependency install activated the repository's effect-tsgo prepare hook; 807 server and 10 web Effect-policy errors, zero standard TypeScript errors. Native adapter Node/timer/Date policy diagnostics are included, not hidden. PR and release owner explicitly informed. Evidence: owned checkout `.artifacts/muse-native/{final-tests.log,native-final.log,production-build.log,server-types.log,web-types.log,browser-check.log}` and `.artifacts/muse-picker/evidence/`.

Deployment is not yet evidenced by this receipt; await release owner's merge/publication/install readback. Do not claim increment closed or native account acceptance complete.

PR183 merged to main as `dc0116de724e0a15bea727076ba0a44112ae8473`. Sole release owner received exact merge SHA and all validation limits for 1.0.19 publication/deployment. Merge is not installation proof.

Release owner acknowledged merged183 in 1.0.19 with credit recovery, settings181 and permissions182, and owns continuation through publication/install on all three machines. Remaining gates: 1.0.18 remote quiet-period/postcapture, approved management enrollment, final1.0.19 CTA/updater UI integration/review/build. No reliable ETA; no further user response needed. Exact merged tree passes 83 Muse/fallback tests plus 18 ACP permission tests and a fresh production server/bundled-web build. Account validation remains explicitly deferred.

### T-03 Repair release typechecks and verify installed rollout
- AC: AC-04 | Files: /Users/antonabyzov/Projects/github/studio-muse-fallback/apps/desktop/, /Users/antonabyzov/Projects/github/studio-muse-fallback/apps/server/, /Users/antonabyzov/Projects/github/studio-muse-fallback/apps/web/, /Users/antonabyzov/Projects/github/studio-muse-fallback/packages/, /Users/antonabyzov/Projects/github/studio-muse-fallback/scripts/ | Test: supported server and web typechecks, focused changed behavior tests, production build; release owner installed receipts for all three machines

Typecheck continuation is owned in existing isolated checkout on new branch codex/typecheck-release119. Preserve all configured diagnostic severities. Root cause: repository prepare patches the TypeScript binary with Effect diagnostics, exposing accumulated policy violations. Coordinate file overlap before edits with active CTA/release owners. No competing publication or live sessions.

### T-04 Anton validates Muse on an eligible native account
- AC: AC-02, AC-03 | Files: .specweave/increments/0922-usable-provider-fallbacks-and-muse-code/reports/ | Test: Anton accepts installation/sign-in, Wonder Full discovery, an authorized turn, approval, cancellation and reconnect on an eligible native Muse account

Added 2026-10-15 at close-out. Anton deferred this ("validate my account later"). 1.0.19 rollout is verified on all three machines. Server typecheck on F is still red on Effect-policy diagnostics (see reports/release-readback.md), so T-03 stays open.
