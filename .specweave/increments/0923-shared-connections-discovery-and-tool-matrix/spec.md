# 0923 Shared connections discovery and tool matrix

## Problem
Project connection setup hides MCP declarations already present in native clients. Users cannot compare Codex and Claude Code on a selected execution machine or distinguish configuration from authenticated session availability.

## Scope
In: read-only shared library; bounded discovery of Codex user/project TOML and Claude user/private-project/shared-project JSON; per-machine typed RPC; project context and precedence; matrix with provenance, disabled/error/unknown states; existing Studio project grants retained. Out: importing credentials, launching MCP commands, network health probes, changing native config, new OAuth flows, managed/plugin inventory, release deployment. Native access remains managed by each client; first slice exposes project-specific configuration without pretending Studio grants control native sessions.

## Acceptance Criteria
- [ ] AC-01: Discovery reads only destination-host configuration and optional registered project roots, handles missing/malformed/oversized files, honors configured native home paths, returns bounded metadata without commands, arguments, URLs, headers, environment values or credentials, and starts no processes/network calls.
- [ ] AC-02: Codex and Claude declarations are separate per client, project overrides and explicit disables are shown with source/scope, and absent declarations are distinguished from unreadable/unsupported sources; authentication/session access remain explicitly unverified.
- [ ] AC-03: Settings Connections shows a machine-selectable tool matrix with refresh and source details; project Environment shows the same library in its exact environment/project context alongside existing Studio grants. Permission-denied/offline/loading/empty states never appear as successful zero results.
- [ ] AC-04: Focused discovery/service/authorization/UI tests, coverage, production web/server builds, headless browser checks, and fresh-context review pass. Manual UI acceptance remains required before closure.

## Approach
Product checkout /Users/antonabyzov/Projects/github/studio-connections-library, branch codex/connections-library, base origin/main b9e1029f4. Umbrella checkout has unrelated dirty work preserved. No matching owner found; 0921 owns ACP permissions, not these connections files. SpecWeave 3.0.15 matches npm; Jev unavailable. Follow Effect service boundaries and existing typed RPC authorization. Full TOML parser, allowlisted metadata projection, fixed/bounded sources, no probing. Matrix groups by display name only, retaining separate provider source identities. Native settings files are evidence of declaration, not proof of runtime admission or trust. Project settings remain authoritative only for Studio-managed calls. Relevant ADRs: 0170 test isolation; 0831 credential-storage boundary (no token copying). Headless Chrome only, PWDEBUG=0 and PLAYWRIGHT_HTML_OPEN=never. Node22 production; separately scoped build runtime if required.

## Tasks
### T-01 Implement discovery and typed read API
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/Projects/github/studio-connections-library/apps/server/src/project/, /Users/antonabyzov/Projects/github/studio-connections-library/packages/contracts/src/projectConnections.ts, /Users/antonabyzov/Projects/github/studio-connections-library/packages/contracts/src/nativeConnections.ts, /Users/antonabyzov/Projects/github/studio-connections-library/packages/contracts/src/projectConnectionRpc.ts, /Users/antonabyzov/Projects/github/studio-connections-library/packages/contracts/src/clientRpcPermissions.ts, /Users/antonabyzov/Projects/github/studio-connections-library/apps/server/src/auth/RpcAuthorization.test.ts, /Users/antonabyzov/Projects/github/studio-connections-library/apps/server/src/observability/RpcInstrumentation.ts, /Users/antonabyzov/Projects/github/studio-connections-library/apps/server/package.json, /Users/antonabyzov/Projects/github/studio-connections-library/pnpm-lock.yaml | Test: focused discovery and project connection service tests

### T-02 Integrate shared and project matrix views
- AC: AC-03 | Files: /Users/antonabyzov/Projects/github/studio-connections-library/packages/client-runtime/src/state/projectWorkspace.ts, /Users/antonabyzov/Projects/github/studio-connections-library/packages/client-runtime/src/state/runtime.ts, /Users/antonabyzov/Projects/github/studio-connections-library/packages/client-runtime/src/state/nativeConnections.test.ts, /Users/antonabyzov/Projects/github/studio-connections-library/apps/web/src/components/connections/, /Users/antonabyzov/Projects/github/studio-connections-library/apps/web/src/components/settings/ConnectionsLibrarySettings.tsx, /Users/antonabyzov/Projects/github/studio-connections-library/apps/web/src/routes/settings.connections.tsx, /Users/antonabyzov/Projects/github/studio-connections-library/apps/web/src/components/studio/ProjectConnections.tsx | Test: focused matrix component tests

### T-03 Verify and document
- AC: AC-04 | Files: /Users/antonabyzov/Projects/github/studio-connections-library/apps/web/tests/connections-library/, /Users/antonabyzov/Projects/github/studio-connections-library/scripts/studio-verify/connections-library.mjs, /Users/antonabyzov/Projects/github/studio-connections-library/reports/connections-library/, /Users/antonabyzov/Projects/github/studio-connections-library/docs/connections-library.md, /Users/antonabyzov/Projects/github/studio-connections-library/README.md, /Users/antonabyzov/Projects/github/studio-connections-library/CHANGELOG.md, /Users/antonabyzov/Projects/github/studio-connections-library/AGENTS.md | Test: focused coverage, web/server production builds, headless matrix checks

### T-04 Manual UI acceptance
- AC: AC-04 | Files: reports/connections-library/ | Test: Anton accepts the concrete matrix UI before increment closure

## Acceptance and merge receipt
Anton accepted the UI and authorized closure/main merge on 2026-10-14. PR #187 merged at 4f7c37b8a2f2ce7f7ef227519233610ae0fce54d; see reports/merge.md.
