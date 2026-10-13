# 0901 Aide Google diagnostics and verified release

## Problem
Aide's October calendar worker could not open because its saved Claude profile was exhausted. The failure was classified as provider_error, preventing usage-limit recovery. Google is separately disconnected on the selected M4 host. Native Google tools are omitted from coordinator connection discovery guidance, and their status conflates missing sign-in with missing project grants. The installed service is 1.0.5 while desktop remains 1.0.4 because public 1.0.5 is still a draft.

## Scope
Actionable private Google diagnostics and minimal read-only API health probes; coordinator discovery guidance; integration of committed 0899 quota classification fix; focused regressions, builds, independent review, and matching newer service/desktop release. Preserve live work, account permissions and other owners. OAuth consent remains the user's action.

## Acceptance Criteria
- [ ] AC-01: Google status distinguishes missing sign-in, missing project authorization and failed API access without leaking ungranted account identity or personal data.
- [ ] AC-02: Authorized health checks probe Gmail, Calendar and Drive with content-free field projections; revoked credentials and API/network failures remain explicit.
- [ ] AC-03: Coordinators discover native Google tools and check readiness before delegating Google-only reads.
- [ ] AC-04: Exhausted provider admission retains usage_limit and reset metadata so existing recovery can act, reusing completed 0899 work.
- [ ] AC-05: Focused tests, builds and independent review pass; matching newer artifacts and update plans are published to both feeds and read back.
- [ ] AC-06: The coordinated guarded updater installs 1.0.7 on M4 with preserved state, passing health, exact source/version readback, and matching desktop version.
- [ ] AC-07: Aide completes real read-only Gmail, Calendar and Drive requests through its native Google tools after account consent and project authorization, with exact evidence and no fabricated success.
- [ ] AC-08: Cancel, X, Escape and backdrop dismissal of Morning briefing return to its originating screen including settings scope and hash; direct links safely fall back to Scheduled tasks, successful saves remain there, and other Settings cancellation paths are audited and regression checked.
- [ ] AC-09: The remaining chat-linked editor dismissal fixes are included in the coordinated follow-up release, with published and installed exact-source evidence; preserve the sole installer and the completed real Google proof.

## Approach
Isolated umbrella and source worktrees from main ed78ddc47; installed c95d3fd7 inspected read-only. Add diagnostics through existing studio_google_status, preserving fields and project gates; avoid unrelated UI/auth changes. Tests use fake Google and isolated homes. Reuse cc6be54fc from 0899 without changing its worktrees or ledgers. No live restart while other work runs. Node22 runtime and scoped Node24 build tools where required; headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never.

## Tasks

### T-01 Add private Google status and live health diagnostics
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/integrations/google/GoogleAccountService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/integrations/google/GoogleAccountService.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/integrations/google/googleAccountHealth.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/integrations/google/googleAccountHealth.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/google/tools.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/google/handlers.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/google/handlers.test.ts | Test: focused Google service and MCP regression tests

### T-02 Teach coordinator native Google discovery
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectWorkspaceService.test.ts | Test: focused project workspace prompt tests

### T-03 Integrate reviewed quota classification dependency
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/studio/Capacity.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/studio/Capacity.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderAdapter.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderAdapter.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderFailure.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderFailure.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderTurnStartService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProviderTurnStartService.test.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/providerSetup.ts | Test: focused quota admission and failure regressions on release base

### T-04 Verify and publish matching desktop and service release
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-google/verify.mjs, repositories/anton-abyzov/specweave-studio/docs/studio/releasing.md, repositories/anton-abyzov/specweave-studio/scripts/studio-projects/release-version.test.mjs, repositories/anton-abyzov/specweave-studio/CHANGELOG.md, repositories/anton-abyzov/specweave-studio/apps/server/package.json, repositories/anton-abyzov/specweave-studio/apps/desktop/package.json, repositories/anton-abyzov/specweave-studio/apps/web/package.json, repositories/anton-abyzov/specweave-studio/packages/contracts/package.json, repositories/anton-abyzov/specweave-studio/docs/studio/google-account.md, .specweave/increments/0901-aide-google-health/reports | Test: focused coverage, production builds, headless Google proof, independent review, artifact verification and both-feed readback

### T-05 Finish guarded M4 service and desktop installation
- AC: AC-06 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet, .specweave/increments/0901-aide-google-health/reports | Test: focused installer regression tests for any repair, independent review, guarded update receipt and live installed version/source/health readback

### T-06 Verify real Google service reads in Aide
- AC: AC-07 | Files: .specweave/increments/0901-aide-google-health/reports | Test: live authorized Gmail, Calendar and Drive tool results plus Aide coordinator completion evidence

### T-07 Restore consistent cancellation destinations
- AC: AC-08 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/GoogleAccountSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ScheduledTasksSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/scheduledTasksSettings.logic.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/scheduledTasksSettings.logic.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ThemeSettings.tsx, repositories/anton-abyzov/specweave-studio/scripts/studio-google/verify.mjs, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ThreadAutomationsPanel.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ScheduledTaskLink.tsx, .specweave/increments/0901-aide-google-health/reports/navigation | Test: focused scheduled-task navigation tests, web and server builds, isolated headless cancellation checks and independent review

### T-08 Verify coordinated shipment of the remaining cancellation fixes
- AC: AC-09 | Files: .specweave/increments/0901-aide-google-health/reports | Test: verify exact candidate inclusion, public release assets and installed version/source against the coordinated publisher's receipts

## Verified Google and remaining release boundary, 2026-10-13

Installed 1.0.8 source 291f919c24b600e400b8c64e9f3dd383795f33a6 passed one actual Aide native run at 12:13:39Z: all three health probes verified, Gmail/Calendar/Drive each returned one item, no other tools/delegation/provider errors, temporary auth revoked and existing sessions preserved. Independent receipt review passed. The earlier failed runs remain retained. Anton's Connected response supplied the manual Google consent step; no permissions or defaults were changed by the verification.

Morning briefing and Theme fixes are installed in 1.0.8. The separately coordinated 1.0.9 candidate contains the chat-linked editor fix and expanded navigation runner. T-08 retains that shipping boundary so completing code/tests is not mistaken for installing all requested fixes. The next release owner is chat 01a133f7-afb4-7771-8e87-55cfabfd6858; do not create a competing installer.

## Cancellation follow-up 2026-10-13

Anton reports Morning briefing cancellation returning home and requests consistent return behavior throughout Settings. Preserve full validated local origin for the routed template editor; consume its one-shot query on dismissal or save, with separate outcomes. Preserve intentional Settings exit behavior and existing Base UI overlay handling; consume Escape in the custom theme variant picker. The 0904 coordinator QA owner remains the sole publisher and installer for the next 1.0.8 release; send this reviewed source commit for integration. Browser proof remains isolated and headless.

## Resumed scope 2026-10-13

Anton explicitly requested completion of the 1.0.7 update, real Google verification through Aide, coordination with the existing installer and fixes for remaining blockers. The maintenance chat remains read-only while 0901 owns repair and coordination. Preserve the live automatic updater attempt and all quiescence/state/authentication guards. Avoid test listeners during preflight. Google sign-in and consent are still required if absent; never transfer another app's tokens or fabricate account verification.
