# Resolve workflow capabilities on the execution machine

## Problem
A configured skill or plugin does not establish usable tools or destination readiness. Audit 1110 corrected configuration copy; users still need scoped runtime evidence and dependency checks before invocation.

## Scope
In: declarative workflow dependencies; destination-local platform and binary checks; scoped native session tool inventories; independent configured/discovered/registered/checked evidence; Skills UI; invocation checks for every app-managed provider session; backward-compatible snapshots; focused tests and documentation.
Out: credential copying, new auth/grants, remote installs or test runs, migration changes, provider connector emulation, live restarts and releases. Existing account and OS permission boundaries remain authoritative.

## Acceptance Criteria
- [ ] AC-01: A skill can declare bounded tool ids, binary names and supported platforms under metadata.specwithcode.requires. Invalid declarations fail visibly; declarations cannot execute commands or export credentials.
- [ ] AC-02: Capability evidence is scoped to the execution environment, provider instance, exact workspace and native session/thread. Different scopes never satisfy a dependency. Missing, denied, unsupported, stale, error and unknown states remain distinguishable with observation times and reasons.
- [ ] AC-03: Live Codex and Claude sessions report their own registered tools through native read-only session introspection. Unsupported providers and absent sessions report unknown/unsupported; configuration never fabricates registration or service authentication. Released/replaced sessions lose their evidence.
- [ ] AC-04: Skill picker discovery preflights platform/binary requirements on its host, and actual turn submission rechecks declared dependencies against its execution context. Proven blockers stop dispatch with actionable errors; unknown tool/auth states are disclosed without silently granting access or breaking undeclared legacy workflows.
- [ ] AC-05: Project Skills exposes dependency checks and the four evidence stages, scoped to its selected machine and provider. Remote or older-server snapshots lacking evidence show unknown. UI distinguishes discovery from instructions actually loaded and never labels discovery as operational success.
- [ ] AC-06: Focused contract, service, invocation and UI tests pass, including scope isolation, stale/partial inventory, session release, malformed declarations, safe binary checks and unavailable hosts. Production web/server builds and fresh review pass. Installed/manual acceptance remains a separate gate.

## Approach
Extend contracts and the existing Skills service; add a pure evaluator plus bounded local filesystem checks. Extend the adapter runtime with optional read-only tool inspection, using Codex mcpServerStatus/list with the exact native thread id and Claude init/tool-status evidence. Extend the session manager with a read-only scoped inventory and invocation preflight. Enrich provider workspace skills with portable dependency summaries for composers. Reuse the existing machine-routed Skills RPC and environment identity; no cross-machine credential or executable synchronization. Carry 1110 configuration wording in the same branch.

## Decisions
### Asked
- D-01: User approved the recommended capability and dependency model, fully implemented.
### Defaulted
- D-02: Requirements live under metadata.specwithcode.requires, keeping native skill formats portable and legacy skills unchanged.
- D-03: Unknown observations never become missing or ready. Tools whose native inventories are partial stay unknown when absent. Registration never proves service authentication.
- D-04: Safe checks inspect local files and existing session metadata only. No arbitrary probe command or external action is accepted from skill metadata.
### Open
- None.

## Tasks
### T-01 Implement scoped capability contracts, native evidence and dependency preflight
- AC: AC-01, AC-02, AC-03, AC-04 | Files: packages/contracts/src/workflowCapabilities.ts, packages/contracts/src/projectSkills.ts, packages/contracts/src/server.ts, packages/contracts/src/index.ts, packages/client-runtime/src/providerSkills.ts, apps/server/src/project/workflowCapabilities.ts, apps/server/src/project/ProjectSkillsService.ts, apps/server/src/mcp/toolkits/projectConnections/tools.ts, apps/server/src/mcp/toolkits/projectConnections/handlers.ts, apps/server/src/provider/ProviderRegistry.ts, apps/server/src/provider/ProviderDriver.ts, apps/server/src/provider/Drivers/CodexDriver.ts, apps/server/src/provider/Drivers/ClaudeDriver.ts, apps/server/src/provider/Drivers/CodexManagedProvider.ts, apps/server/src/orchestration-v2/ProviderAdapter.ts, apps/server/src/orchestration-v2/ProviderSessionManager.ts, apps/server/src/orchestration-v2/runtimeLayer.ts, apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts | Test: focused contract, service and adapter tests in T-03

### T-02 Expose capability evidence and document portable workflows
- AC: AC-05 | Files: apps/web/src/components/settings/ProjectSkillsSettings.tsx, apps/web/src/components/settings/WorkflowCapabilities.tsx, apps/web/tests/connections-library/mocks.tsx, apps/web/tests/connections-library/main.tsx, docs/user/workflow-capabilities.md | Test: focused UI tests and headless fixture

### T-03 Verify and close 1111
- AC: AC-06 | Files: packages/contracts/src/workflowCapabilities.test.ts, apps/server/src/project/workflowCapabilities.test.ts, apps/server/src/project/ProjectSkillsService.test.ts, apps/server/src/mcp/toolkits/projectConnections/handlers.test.ts, apps/server/src/orchestration-v2/ProviderSessionManager.test.ts, apps/server/src/provider/ProviderRegistry.test.ts, apps/web/src/components/settings/WorkflowCapabilities.test.tsx, reports/validation.md, reports/review.md | Test: focused suites, production web/server builds, specweave verify 1111, fresh review, specweave complete 1111 subject to manual acceptance gate
