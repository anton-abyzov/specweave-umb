---
increment: 1174-windows-machine-publishes-to-connect
title: Windows machine publishes to Connect
---

# Windows machine publishes to Connect

## Problem

Publishing a fresh Windows install to SpecWithCode Connect fails with the bare message
`https://relay.spec-weave.com/v1/client/environment-links failed` and no reason.

Evidence from production on November 2, 2026, 16:10 UTC:

- Environment `6079479c` reserved an allocation at 16:10:07, its tunnel was created and configured by 16:10:09, no DNS record was recorded and `ready_at` stayed empty.
- The Worker's slowest invocation that minute took 9.015 s, matching `RELAY_REQUEST_DEADLINE_MS` (9,000 ms), which returns a 504 whose body is not in the API schema. The client cannot decode it, so it shows no detail.
- The account has an override of 1,000,000 tunnels and 4 active links, so `environment_link_limit_exceeded` is not the cause.
- The link path that creates a DNS record last ran on October 29. Existing machines only update their records, so only a new machine reaches this code. Nothing here depends on Windows.
- The Cloudflare client retries transient errors, including "Authentication error", inside each 8 s call timeout, so a persistent failure reads as a hang and the real error is lost.

## Scope

In: the first-link path on the relay, the shared relay client's link timeout, the message shown in the desktop and mobile apps, and relay logs that name the failing stage.

Out: the Windows Claude CLI sign-in (increment 1171), the Linux updater, and any release dispatch.

## Acceptance criteria

- [ ] AC-01 The relay gives `POST /v1/client/environment-links` a deadline long enough for a first provision, and other API routes keep 9 s.
- [ ] AC-02 The relay client waits longer than that deadline for the link call only, so the relay's answer arrives before the client gives up.
- [ ] AC-03 A failed Cloudflare tunnel or DNS call returns its real error within its call timeout, instead of timing out behind retries.
- [ ] AC-04 A provisioning failure writes a Worker log naming the stage, reason, environment and underlying error, with no tokens.
- [ ] AC-05 A link failure with no decoded relay error shows why in the app: HTTP status, timeout or network failure, plus a trace id when known. This holds on desktop and mobile.
- [ ] AC-06 The root cause of the stalled DNS step is identified from production logs and fixed.
- [ ] AC-07 The Windows machine publishes to Connect and appears in the fleet, reachable from M4.

## Approach

Add a per-route deadline next to the existing webhook deadline. Add a link-specific client timeout. Bound the retries on Cloudflare calls so the last real error survives. Log at the linker where stage and environment are known. Build the client detail in one shared function used by web and mobile.

Merging deploys the relay on its own, so server-side fixes reach the Windows install without a new app version. The client message and timeout need the next release.

## Tasks

### T-01 Relay deadline, bounded retries and provisioning log
- AC: AC-01, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/infra/relay/src/http/Api.ts, repositories/anton-abyzov/specwithcode-dev/infra/relay/src/environments/ManagedEndpointProvider.ts, repositories/anton-abyzov/specwithcode-dev/infra/relay/src/environments/EnvironmentLinker.ts | Test: cd infra/relay && pnpm exec vitest run src/http/Api.test.ts src/environments/EnvironmentLinker.test.ts src/environments/ManagedEndpointProvider.test.ts

### T-02 Client link timeout and useful message
- AC: AC-02, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/relay/managedRelay.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/cloud/linkEnvironment.ts, repositories/anton-abyzov/specwithcode-dev/apps/mobile/src/features/cloud/linkEnvironment.ts | Test: pnpm exec vitest run packages/client-runtime/src/relay apps/web/src/cloud/linkEnvironment.test.ts apps/mobile/src/features/cloud/linkEnvironment.test.ts

### T-03 Root cause from production and live proof
- AC: AC-06, AC-07 | Files: as the logs show | Test: production D1 shows `ready_at` set for environment `6079479c`, and `studio_machine_list` on M4 lists the Windows machine

### T-04 Verify and close 1174
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: specweave verify 1174-windows-machine-publishes-to-connect
