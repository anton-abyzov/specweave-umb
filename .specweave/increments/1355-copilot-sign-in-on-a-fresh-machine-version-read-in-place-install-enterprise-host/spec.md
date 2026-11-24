# Copilot sign-in on a fresh machine: version read, in-place install, enterprise host

## Problem

On M5, set up from scratch on November 18, 2026, the Add provider dialog's Sign in step for GitHub Copilot fails with "Could not read which Copilot CLI version is installed. Sign-in needs Copilot CLI 1.0.95 or newer." Copilot CLI 1.0.104 (current) prints `GitHub Copilot CLI 1.0.104.` with a trailing period, and `readCopilotVersion` (apps/server/src/provider/acp/CopilotDeviceAuthentication.ts) only accepts a version followed by whitespace or the end of the output. Every machine with a current Copilot CLI fails the same way, including linux-mini. The dialog then sends the user to Settings > Providers to install or update instead of offering the action in place. A Copilot Enterprise seat on a GHE.com host can only be reached when `gh` is signed in to that host alone; with a personal github.com sign-in too, there is no way to pick the host.

## Scope

In: tolerant version read; Install / update agent button in the sign-in step when the CLI is missing, too old or unreadable; a GitHub host choice for Copilot sign-in (github.com, enterprise hosts gh knows, or a typed GHE.com host); COPILOT_GH_HOST / GH_HOST in the sign-in environment honored. Out: copying any other app's credentials; GitHub Enterprise Server hosts beyond what Copilot CLI `--host` accepts; a release.

## Acceptance Criteria

- [ ] AC-01: `GitHub Copilot CLI 1.0.104.` (and `v1.0.104`, `1.0.104,`) reads as 1.0.104; preview and unrelated text still do not.
- [ ] AC-02: When sign-in fails because Copilot CLI is missing, too old or its version cannot be read, the sign-in step shows Install / update agent and the message points there.
- [ ] AC-03: The Copilot sign-in step lets the user pick github.com or an enterprise host (listed from gh or typed), and device sign-in starts with `--host <host>` for an enterprise host; github.com uses the default host.
- [ ] AC-04: Without a picked host, a COPILOT_GH_HOST or GH_HOST set for the instance decides the host before the single-gh-enterprise-host rule, and the device code is read for that host.
- [ ] AC-05: An older server ignores the new optional `host` field; an invalid host is rejected with a plain message.

## Approach

Server: CopilotDeviceAuthentication.ts (version regex, host normalization, host precedence), AcpRegistryAuth.ts (pass the chosen host), ProviderAuthFlow.ts and ProviderAuthService.ts (carry `host` into the flow context), contracts providerSetup.ts (optional `host` on ProviderAuthStartInput). Web: CopilotSignInHints.tsx (install button, host picker), ProviderAuthenticationSection.tsx (send host). Tests under apps/server and apps/web.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Host choice lives in the sign-in step, not in provider settings: the host follows the account, and Copilot CLI keeps the sign-in per host in its own store.
- D-02 github.com is passed as no `--host`, so the CLI's own default stays in charge.
### Open
- none

## Tasks

### T-01 Version read and host precedence on the server
- AC: AC-01, AC-03, AC-04, AC-05 | Files: apps/server/src/provider/acp/CopilotDeviceAuthentication.ts, apps/server/src/provider/acp/AcpRegistryAuth.ts, apps/server/src/provider/ProviderAuthFlow.ts, apps/server/src/provider/ProviderAuthService.ts, packages/contracts/src/providerSetup.ts | Test: cd apps/server && bun run test src/provider/acp/CopilotDeviceAuthentication.test.ts src/provider/acp/AcpRegistryAuth.test.ts

### T-02 Install button and host picker in the sign-in step
- AC: AC-02, AC-03 | Files: apps/web/src/components/settings/CopilotSignInHints.tsx, apps/web/src/components/settings/ProviderAuthenticationSection.tsx | Test: cd apps/web && bun run test src/components/settings/CopilotSignInHints.test.tsx
