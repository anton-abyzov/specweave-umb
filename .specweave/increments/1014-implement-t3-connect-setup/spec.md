# Implement T3 Connect setup

## Problem

Phone pairing currently mints a five-minute code before explaining the network setup. A Tailscale address alone does not mean the phone can reach it. Hosted Connect and private Tailscale pairing have different prerequisites, and the hosted relay is not deployed.

## Scope

In: inspect the shipped T3 Code release with REA; document clean-room behavior and actual setup; guide SpecWithCode phone onboarding through route preparation, phone prerequisites, and fresh expiring pairing codes; verify isolated UI and relevant tests.

Original October 23 exclusions retained historically. October 28 authorized scope now includes deployment and safe installation on M4/M1/M3/Ministorm, Connect primary with Tailscale fallback, and a durable unlimited entitlement for Anton's verified account. No new remote grants, credential copying, paid dummy tunnels, unrelated account changes or Anna changes. Publication remains with established release owners; transfer/update admission gates remain mandatory.

## Acceptance Criteria

- [ ] AC-01: Findings identify the shipped artifact and REA Evidence IDs, distinguish observed/inferred/unknown behavior, explain hosted versus Tailscale setup, and define independent implementation behavior before code changes.
- [ ] AC-02: Phone setup explains the selected route and prerequisites before generating credentials, guides missing-route users to existing access controls, and preserves permission limits and credential-free diagnostics.
- [ ] AC-03: QR credentials stay bound to the address they were created for, expired codes are not presented as usable, and users can generate a fresh code without leaving setup.
- [ ] AC-05: Mobile evaluation compares the supplied T3 screenshot and verified release source with our native app, identifies useful approaches, and states runtime limits without editing iOS.
- [ ] AC-04: Focused behavior tests, production web build, headless setup-flow captures, and fresh-context review validate the implementation. Installed phone/network acceptance is reported separately.

- [ ] AC-06: The verified account has an explicit durable unlimited managed-tunnel entitlement; normal accounts retain three; provisioning and authenticated API represent unlimited without numeric sentinels.
- [ ] AC-07: Configured Connect routes are selected before Tailscale, identity/DPoP checks are retained, and route diagnostics distinguish unregistered from unavailable endpoints.
- [ ] AC-08: Existing authorized M4/M1/M3/Ministorm installations and authenticated routes are reconciled without Tailscale, preserving transfer/session/Stop gates and Anna state; unresolved user-only gates are exact.

## Approach

Use an isolated worktree at `/Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014` on `feat/t3-connect-onboarding`. Reuse existing Tailscale HTTPS and pairing APIs. Keep all mutations user initiated; never claim phone reachability from host-only discovery. Implement from the findings' behavior specification without copying competitor code or assets.

## Decisions

### Asked
- D-01: User explicitly assigned replacement implementation ownership; previous worker made no edits or claims.
### Defaulted
- D-02: Retain existing direct private pairing and hosted deployment gates. Improve the available onboarding without deploying infrastructure or introducing LAN proxies.
- D-03: Manual phone/network verification remains a release acceptance boundary, not a synthetic fixture claim.
### Open
- none

## Tasks

### T-01 Inspect shipped Connect and write the clean-room specification
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014/docs/research/t3-connect-1014.md | Test: inspect exported REA evidence and artifact identity

### T-02 Implement route preparation and safe expiring phone pairing
- AC: AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014/apps/web/src/components/settings/PairPhoneSettings.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014/apps/web/src/components/settings/PairPhone.logic.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014/apps/web/src/components/settings/PairPhone.logic.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014/apps/web/src/components/settings/PhoneSetupDialog.tsx | Test: focused phone pairing tests and production web build

### T-03 Verify and close 1014
- AC: AC-04, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014/apps/web/tests/phone-setup/, /Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014/docs/research/t3-connect-1014.md | Test: headless setup flow, fresh-context review, specweave verify and complete

## October 28 continuation decisions

- D-04: User authorizes full Connect deployment/install on existing granted machines and account-specific unlimited entitlement. Existing source work remains intact.
- D-05: Stable Clerk user verified server-to-server plus matching relay links; entitlement is keyed by user id, not email or client setting.
- D-06: Keep existing per-user override table, add explicit unlimited flag, and expose discriminated account policy. Existing finite rows keep their meaning.

### T-04 Implement explicit account-scoped unlimited managed tunnels
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/infra/relay/src/environments/ManagedTunnelLimits.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/infra/relay/src/environments/ManagedTunnelLimits.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/infra/relay/src/persistence/schema.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/infra/relay/migrations/d1/, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/contracts/src/relay.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/infra/relay/src/http/Api.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/infra/relay/src/http/Api.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/client-runtime/src/relay/managedRelay.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/web/src/cloud/managedAuth.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/web/src/cloud/managedTunnelPolicy.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/web/src/components/cloud/CloudEnvironmentConnectList.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/infra/relay/src/environments/ManagedEndpointProvider.test.ts , /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/infra/relay/src/account/AccountDeletion.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/client-runtime/src/relay/managedRelay.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/web/src/cloud/managedTunnelPolicy.test.tsx | Test: relay limit/API focused tests and contract tests

### T-05 Prefer Connect while preserving route security
- AC: AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/fleet/fleetTransport.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/fleet/fleetTransport.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/studioFleetJoin.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/studioFleetJoin.test.ts | Test: fleet transport focused tests

### T-06 Deploy and register verified account and routes
- AC: AC-06, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/docs/operations/connect-fleet-repair.md | Test: stable account/D1 policy readback and authenticated pinned fleet identity probes

### T-07 Reconcile safe installed fleet acceptance
- AC: AC-08 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/docs/operations/connect-fleet-repair.md | Test: per-machine service source/version/route/session/transfer/update-admission receipts with no Tailscale

### T-09 Preserve existing worker consent while binding legacy grants
- AC: AC-07, AC-08 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/fleet/FleetWorkerGrants.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/fleet/workerGrantMint.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/auth/SessionStore.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/auth/http.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/contracts/src/auth.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/contracts/src/environmentHttp.ts | Test: authenticated binding lifecycle preserves session identity, expiry, access and existing consent; no unbound credential crosses Connect

October 28 runtime finding: management invitation renewal alone restores management routes, but existing bearer-only worker grants remain nonrenewable and fail through Connect. Never fix this by sending bearer credentials through the relay, extending the grant, enabling ongoing consent or changing the Settings permission. A supported binding transition must preserve the existing grant's identity and expiration and reject a mismatched coordinator/key. Deployment requires destination admission under T-07.

### T-10 Repair full client-runtime typecheck coverage
- AC: AC-06, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/client-runtime/src/authorization/layer.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/client-runtime/src/connection/supervisor.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/client-runtime/src/relay/discovery.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/packages/client-runtime/src/relay/managedRelayState.test.ts | Test: full touched-package repository typecheck gate with no baseline changes or new waivers, raw client-runtime zero diagnostics, affected runtime tests, fresh exact-head review

T-10 validation clarification: an additional empty-baseline experiment is retained as failed for 79 existing server diagnostics. The saved original CI server log and repaired-head server log have identical file/code/count diagnostics. The committed repository gate is the release criterion; its baseline is unchanged, and the client-runtime repair passes raw without baseline coverage.

### T-11 Reconcile discovery expectations with Connect-first routing
- AC: AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/apps/server/src/studioFleet.test.ts | Test: reproduce stale discovery transport expectation, verify credential-free Connect primary and Tailscale fallback, full related fleet discovery/transport/authorization tests, fresh exact-head review

### T-12 Diagnose the Windows terminal timeout
- AC: AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/connect-fleet-repair-20261028/windows-timeout-report.md | Test: exact-head job/artifact/source readback, completed-file and timing analysis, existing sharding-owner reconciliation and bounded guarded integration recommendation; no rerun or gate waiver

### T-08 Verify and close 1014
- AC: AC-06, AC-07, AC-08 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/connect-fleet-repair/docs/operations/connect-fleet-repair.md | Test: focused tests, build, fresh exact-head review, CI and installed identity-bound operations
