# Stop the iPhone signing itself out of Connect

## Problem

Anton's iPhone keeps dropping SpecWithCode Connect and makes him sign in again. On November 18, 2026 at 05:05:51Z he signed in on the Duo (iOS 0.1.8 build 48). Clerk recorded that session as `removed` 3.4 s later, which means the client signed itself out. The relay had no device-removal rows and accepted the phone's token at 05:05:55Z, so the relay refused nothing (`~/.specwithcode/m4/evidence/ios-disconnects/2026-11-18-signout-findings.md`).

The client signs itself out from `connectSessionRejected()` (`apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Connect.swift`), which calls Clerk `signOut()` on any inferred `.signedOut`. That signal comes from any machine's status (`LiveEngine.swift` `statusChanged`) or from `connectRefresh`, and it is inferred in two ways: from a nil Clerk session at that moment, or from two relay 401s in a row. A 401 also comes from a relay JWKS failure (`invalid_bearer`) or any DPoP problem (`invalid_dpop`). Nothing ties the signal to the session it was raised under, so a stale attempt kills a fresh sign-in.

## Scope

iOS app only (`apps/ios`). No relay or server change. The socket-drop half (backgrounding and the 3 s connecting grace) stays unproven without phone logs and is out of scope.

## Acceptance Criteria

- [x] AC-01: An inferred session rejection never ends the Clerk session by itself. The app asks Clerk again (`refreshClient`), and signs out and shows "Sign in" only when Clerk confirms the session is gone.
- [x] AC-02: When Clerk still holds the session, the phone stays signed in, clears its relay tokens and retries the affected computers at most once every 30 s, with no loop.
- [x] AC-03: A rejection raised before a newer sign-in finished is ignored. A sign-in generation is captured when the rejection starts and checked after every await.
- [x] AC-04: A relay 401 with reason `invalid_dpop` is treated as a token or proof problem, not as the account being signed out.
- [x] AC-05: `make test-core` passes, including new tests for AC-01 to AC-04.

## Approach

- `ConnectAccount.confirmSessionEnded()` (new, `SWCSync/Connect.swift`). `ClerkConnectAccount` refreshes the Clerk client and returns true only if no session remains. A refresh that fails returns false.
- `ConnectRuntime.signInGeneration` goes up on every successful sign-in. `connectSessionRejected()` captures it, awaits `confirmSessionEnded()`, and returns if the generation moved or Clerk kept the session. When Clerk kept it, the app resets the relay tokens and reconnects the machines that report `.connect(.signedOut)`, throttled to once per 30 s.
- `RelayClient.bearerRequest` and `dpopRequest` keep the second `invalid_dpop` 401 as the relay error and throw `.signedOut` only for other 401 reasons.

Auth change: needs Anton's yes before merge.

## Tasks

### T-01 Confirm with Clerk before signing out, and ignore stale rejections
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/Connect.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Connect.swift, repositories/anton-abyzov/specwithcode/apps/ios/App/ClerkConnectAccount.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/ConnectEngineTests.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/PhoneRemovalEngineTests.swift | Test: make -C repositories/anton-abyzov/specwithcode/apps/ios test-core

### T-02 Keep invalid_dpop refusals out of signed out
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCTransport/RelayClient.swift, repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCTransportTests/ConnectTests.swift | Test: make -C repositories/anton-abyzov/specwithcode/apps/ios test-core

### T-03 Verify and review
- AC: AC-05 | Files: .specweave/increments/1385-stop-the-iphone-signing-itself-out-of-connect/reports/ | Test: make -C repositories/anton-abyzov/specwithcode/apps/ios test-core
