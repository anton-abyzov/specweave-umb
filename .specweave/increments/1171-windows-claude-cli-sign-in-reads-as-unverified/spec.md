# Windows Claude CLI sign-in reads as unverified

## Problem

On a from-scratch Windows install (machine `PRCTY-AABYZOV`, photo `IMG_9381.DNG`, no version visible) every chat fails with "Native subscription authorization is unverified. Sign in with the official native CLI on this machine and refresh provider status." under a banner "Claude provider has limited availability.", although the user is signed in within a terminal.

A clean `windows-latest` probe (runs 41464910942 and 41465251932) shows the real CLI reads credentials from `%USERPROFILE%\.claude` correctly, so plan names and CLI lookup are not at fault. That banner and denial come from one state: the CLI the app runs answers `tokenSource: "none"`, meaning it is signed out from its own point of view. Two defects make that state hard to leave and impossible to understand:

1. The signed-out read is labelled `subscription-auth-unverified` with no message, so the app never says which CLI and folder it checked. A login inside WSL, under another user or in another `CLAUDE_CONFIG_DIR` looks identical to a working one.
2. The signed-out init result stays in the capabilities cache for 5 minutes, and the start gate's refresh does not invalidate it. Unless the login watcher fires, signing in during that window keeps refusing chats.

## Scope

In: truthful signed-out state and message for Claude, the start gate quoting it, no caching of a signed-out probe. Out: changing credential storage, plan recognition (fixed in #1104), download pins (specweave PR #2222).

## Acceptance Criteria

- [ ] AC-01: When `claude auth status` reports `loggedIn: false` (any exit code) and no token override is set, the snapshot is `status: "error"`, `auth.status: "unauthenticated"`, with a message naming the CLI path and config folder that were checked.
- [ ] AC-02: On Windows that message says a sign-in inside WSL or under another Windows user does not count.
- [ ] AC-03: The start gate refuses with that message instead of "authorization is unverified".
- [ ] AC-04: A signed-out probe result is not kept in the capabilities cache; a signed-in one still is.
- [ ] AC-05: Signed in, API key, Console, unreadable-status and token-override reads keep their current results.
- [ ] AC-06: On `windows-latest` the real CLI and product code read signed out with the new message, for the native and npm installs, and the native install reads ready after credentials appear. The npm install rejects a fixture token after init, and a real login is not testable on a hosted runner, so its ready read is not proved there.

## Approach

`apps/server/src/provider/ClaudeProvider.ts`: read the signed-out answer from the existing `auth status` calls and include `tokenSource: "none"` in the status read. `apps/server/src/provider/Drivers/ClaudeHome.ts`: message builder. `apps/server/src/provider/Drivers/ClaudeDriver.ts`: zero TTL for a signed-out probe. `apps/server/src/studio/Capacity.ts`: deny with the provider's message when it is unauthenticated. Rejected: forcing a fresh refresh on every denied start, since dropping the signed-out entry covers it and also clears the banner on the next periodic check.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A successful probe gets the zero TTL only when `tokenSource` is `"none"` with no plan and no paying API key (`apiKeySource` absent or `"none"`), so plan reads, key reads and Console sign-ins (no token source reported) keep their cache → reversible.
### Open
- none

## Tasks

### T-01 Signed-out state, message and cache
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: apps/server/src/provider/ClaudeProvider.ts, apps/server/src/provider/Drivers/ClaudeHome.ts, apps/server/src/provider/Drivers/ClaudeDriver.ts, apps/server/src/studio/Capacity.ts | Test: `pnpm exec vp test run src/provider/ClaudeProvider.test.ts src/studio/Capacity.test.ts`

### T-02 Windows check, review and merge
- AC: AC-06 | Files: throwaway workflow on `probe/windows-claude-cli` | Test: Windows run reads signed out for both installs, then ready for native

### T-03 Verify and close 1171
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: `specweave verify 1171`
