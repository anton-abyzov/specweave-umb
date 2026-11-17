# Coordinator delegates real work to threads

## Problem

Work runs inside the project coordinator thread instead of a worker thread. Evidence: photo `/Users/antonabyzov/Downloads/IMG_0186.HEIC` shows the coordinator (m3, Muse, muse-wonder-1.0) running the "Complete EU1 AKS agent migration" as a workflow inside the coordinator thread, then telling the user it has no clickable thread link because the run is a workflow inside the coordinator. The user asked for thread links and got none.

Causes found in `repositories/anton-abyzov/specwithcode`:

- Prompt conflict. The coordinator role in [ProjectWorkspaceService.ts](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts:193) says the coordinator does no work itself and routes at once with `delegate_task`. But the orchestration instructions given to every agent, including the coordinator, in [StudioOrchestrationInstructions.ts](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.ts:15) say to use the native subagent tool and to start top-level threads only when the user asks. For a coordinator that reads as: do the work with native subagents or a workflow, in this thread.
- No mechanism. The only coordinator guard, `toWorkerLayer` in [McpToolAccess.ts](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/mcp/McpToolAccess.ts:362), refuses Studio MCP hands-on toolkits (preview, Chrome, computer, device) for coordinators. Native provider tools (Agent, Workflow, Bash, Read, Edit) are not Studio MCP tools, so nothing stops a coordinator from using them. Claude workflows stay enabled in a coordinator thread because [ClaudeWorkflowPolicy.ts](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeWorkflowPolicy.ts:192) enables them unless the project mode is disabled.

## Scope

In: role-aware orchestration instructions for coordinator threads on every provider path; runtime policy carries whether the thread is its project's coordinator; Claude coordinator sessions get workflows disabled and native subagent, hands-on file, shell and web tools disallowed; tests proving a coordinator prompt routes work to `delegate_task` and does not carry the native-subagent instruction, and that a Claude coordinator session cannot start a workflow or subagent.

Out: machine placement and worker machine defaults (owned by the running thread "Why M5 cannot start work"); weakening the coordinator role text; changing worker threads.

## Acceptance Criteria

- [x] AC-01: A coordinator thread's orchestration instructions say real work goes to a worker with `delegate_task` in async mode, never to native subagents or workflows, and keep the simple, summarizing, forwarding, delivery-recording and one-line acknowledgement exceptions.
- [x] AC-02: A worker thread's orchestration instructions are unchanged.
- [x] AC-03: A Claude coordinator session has workflows disabled and Agent, Task, Workflow, Bash, Read, Edit, Write, Glob, Grep and web tools disallowed, while Studio MCP routing tools stay available.
- [x] AC-04: Existing orchestration, workflow-policy, runtime-policy and MCP access tests pass.

## Approach

1. `StudioOrchestrationInstructions.ts`: add a coordinator variant and a selector `studioOrchestrationInstructionsForRole`; thread it through `studioOrchestrationSystemPrompt`, `studioOrchestrationPromptForFirstRun` and `studioAcpPromptWithInstructions` (role change reinjects on ACP).
2. `ProviderAdapter.ts` and `RuntimePolicy.ts`: add `isCoordinator` to the runtime policy, resolved from the project's `coordinatorThreadId`.
3. Adapters (Claude, Codex, ACP, Cursor, OpenCode, OpenCode2, Pi): pass the role to the instruction selector. Claude also forces workflow mode disabled for coordinators in `compileClaudeWorkflowPolicy` via a new `coordinator` flag that disallows native hands-on tools.
4. Tests in `StudioOrchestrationInstructions.test.ts`, `ClaudeWorkflowPolicy.test.ts` and `RuntimePolicy` coverage.

Rejected: stronger coordinator prose only. The prose already says it and the work still landed in the coordinator, because the system-level orchestration text contradicted it and no tool was refused.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Claude coordinator disallows native hands-on tools instead of only Agent and Workflow, because research and verification in the coordinator are done with Bash and Read. Studio MCP tools (thread list, send, memory, ask) stay available so routing, forwarding and delivery recording keep working.
### Open
- none

## Tasks

### T-01 Coordinator orchestration instructions
- AC: AC-01, AC-02 | Files: apps/server/src/provider/StudioOrchestrationInstructions.ts, apps/server/src/provider/CodexDeveloperInstructions.ts, adapter call sites | Test: StudioOrchestrationInstructions.test.ts

### T-02 Runtime policy carries coordinator role
- AC: AC-01 | Files: apps/server/src/orchestration-v2/ProviderAdapter.ts, apps/server/src/orchestration-v2/RuntimePolicy.ts | Test: RuntimePolicy tests

### T-03 Claude coordinator tool enforcement
- AC: AC-03 | Files: apps/server/src/provider/ClaudeWorkflowPolicy.ts, apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts | Test: ClaudeWorkflowPolicy.test.ts

### T-04 Release
- AC: AC-04 | Files: none | Test: specweave-studio checks run for server tests, then PR and release through the dispatcher per reference_release_and_merge_protocol

### T-05 Post-merge review follow-ups
- AC: AC-01, AC-03 | Files: apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, apps/server/src/provider/StudioOrchestrationInstructions.ts, apps/server/src/orchestration-v2/Adapters/piStudioMcpInjection.ts | Test: ClaudeAdapterV2.test.ts, StudioOrchestrationInstructions.test.ts, piStudioMcpInjection.test.ts
- A post-merge review of PR #522 confirmed three gaps: the Claude live-query reuse key ignored the role, Cursor got the routing line on run 1 only, and Pi workers could inherit `STUDIO_PI_COORDINATOR`. Fixed in PR #523.
