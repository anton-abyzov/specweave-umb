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
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-google/verify.mjs, repositories/anton-abyzov/specweave-studio/docs/studio/google-account.md, .specweave/increments/0901-aide-google-health/reports | Test: focused coverage, production builds, headless Google proof, independent review, artifact verification and both-feed readback
