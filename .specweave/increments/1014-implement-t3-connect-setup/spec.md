# Implement T3 Connect setup

## Problem

Phone pairing currently mints a five-minute code before explaining the network setup. A Tailscale address alone does not mean the phone can reach it. Hosted Connect and private Tailscale pairing have different prerequisites, and the hosted relay is not deployed.

## Scope

In: inspect the shipped T3 Code release with REA; document clean-room behavior and actual setup; guide SpecWithCode phone onboarding through route preparation, phone prerequisites, and fresh expiring pairing codes; verify isolated UI and relevant tests.

Out: deploying hosted services, changing accounts or network settings, installing VPNs, paid spend, releasing the desktop or iOS app, changing existing relay owners' branches.

## Acceptance Criteria

- [ ] AC-01: Findings identify the shipped artifact and REA Evidence IDs, distinguish observed/inferred/unknown behavior, explain hosted versus Tailscale setup, and define independent implementation behavior before code changes.
- [ ] AC-02: Phone setup explains the selected route and prerequisites before generating credentials, guides missing-route users to existing access controls, and preserves permission limits and credential-free diagnostics.
- [ ] AC-03: QR credentials stay bound to the address they were created for, expired codes are not presented as usable, and users can generate a fresh code without leaving setup.
- [ ] AC-05: Mobile evaluation compares the supplied T3 screenshot and verified release source with our native app, identifies useful approaches, and states runtime limits without editing iOS.
- [ ] AC-04: Focused behavior tests, production web build, headless setup-flow captures, and fresh-context review validate the implementation. Installed phone/network acceptance is reported separately.

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
