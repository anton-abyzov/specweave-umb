# iPhone always offers sign-in; phones show their exact model

## Problem

The owner's iPhone Duo showed "Pair a machine" with no way to sign in. A device test on November 2, 2026 installed `SpecWithCode Dev` 0.1.1 (12) with no Connect settings, and the app hides sign-in when a build has none. Clerk also refuses the dev bundle's callback, so settings alone would not fix it.

Settings > Connections shows two rows reading "iPhone · iPhone": the model table stops at iPhone 17 Pro, so a Duo reports "iPhone".

## Scope

In: sign-in on every build type, the model table, phone rows on desktop and phone, the merged "Your phones" section, a build on the Duo.

Out: Machines page (1177), Android model names, entitlement for the system device name.

## Acceptance Criteria

- [x] AC-01: A build with no Connect settings opens with sign-in and reaches Google's page.
- [x] AC-02: A build without the Apple entitlement hides Sign in with Apple. A store build still offers it first.
- [x] AC-03: Signed out, expired or removed sessions return to a screen that offers sign-in.
- [x] AC-04: The phone reports its marketing model (iPhone Duo, 18 Pro and older), and an unknown phone sends its identifier.
- [x] AC-05: A phone row shows the chosen name or model, iOS, app version, dev build, last seen, "This phone" and Remove. An old entry says the model shows after the app updates.
- [x] AC-06: Status and phone rows sit in one "Your phones" section.

## Approach

`ConnectConfig.main` falls back to the public hosted settings. Clerk uses the store app's callback on every build: the system returns it to the build that started the session, so production Clerk needs no change. `-SWCDirectOnly` keeps tests against disposable servers on direct pairing. The relay returns `iosMajorVersion` and `bundleId`, both optional in the contract.

## Verification

Merged as `1fafa161fc` (PR 1222). `ConnectSignInUITests` reached `accounts.google.com` on a build with no settings in the simulator. `swift test`: 532 passed. Evidence is in `reports/`. Finishing a sign-in needs the owner's account, so AC-01 is proven up to Google's page; the Duo check was asked of the owner. AC-03 rests on existing engine tests and code review.

## Tasks

### T-01 Sign-in on every build
- AC: AC-01, AC-02, AC-03 | Files: apps/ios/SWCKit/Sources/SWCTransport/ConnectConfig.swift, apps/ios/SWCKit/Sources/SWCSync/Connect.swift, apps/ios/App/ClerkConnectAccount.swift, apps/ios/App/SpecWithCodeApp.swift, apps/ios/UITests/ConnectSignInUITests.swift | Test: cd apps/ios/SWCKit && swift test --filter Connect

### T-02 Exact model and phone rows
- AC: AC-04, AC-05, AC-06 | Files: apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Push.swift, apps/ios/SWCKit/Sources/SWCFeatures/Settings/ConnectPhonesCard.swift, apps/web/src/components/settings/PhoneDevices.logic.ts, apps/web/src/components/settings/PhoneDevicesSettings.tsx, apps/web/src/components/settings/PhoneConnectSettings.tsx, packages/contracts/src/relay.ts, infra/relay/src/agentActivity/PhoneRemovals.ts | Test: cd apps/web && pnpm exec vp test run src/components/settings/PhoneDevices.logic.test.ts

### T-03 Put the build on the Duo
- AC: AC-01 | Files: none | Test: devicectl lists the installed version

### T-04 Verify and close 1180
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1180
