# Delegated workers say when their provider cannot run the asked mode

## Problem

On November 17, 2026 the 1327 thread (Claude, Full access) delegated an adversarial review to Muse Code with `runtimeMode: "auto"`. Muse Code offers only Supervised and Full access (`apps/server/src/provider/Drivers/MuseDriver.ts:171`), so every turn ran Supervised (`apps/server/src/orchestration-v2/RuntimePolicy.ts:99-108`, `apps/server/src/provider/muse/MuseRuntime.ts:104-106`). Each shell command, even `git show`, became an approval card for Anton. The worker showed "Needs you · Approval requested" while its parent believed it ran unattended. `delegate_task` checks the child mode only against the parent (`apps/server/src/mcp/OrchestratorMcpService.ts:3672`), never against the target provider, and says nothing.

Evidence: `~/.specwithcode/m4/scratch/2026-11-17-needs-you-muse-auto/findings.md`.

## Scope

In: `delegate_task` returns a `warning` naming the mode the worker will really run, why each command will wait for a person, and how to get unattended work. Out: changing what any mode auto-approves, mapping Auto to Muse's own `:auto-review` profile, refusing the launch, the read-only subagent peek having no Approve button, `create_threads` and `studio_thread_launch`.

## Acceptance Criteria

- [x] AC-01: `delegate_task` to a provider whose `supportedRuntimeModes` lacks the resolved mode returns `warning` that names the provider, the asked mode and the mode it runs (Supervised), and says each command waits for a person.
- [x] AC-02: The warning suggests `runtimeMode "full-access"` only when the parent runs Full access and the provider offers it; otherwise it suggests a provider that offers the asked mode.
- [x] AC-03: No warning when the provider offers the mode or lists no modes; an existing increment warning is kept alongside.
- [x] AC-04: The dispatched thread keeps the asked runtime mode (no permission change).

## Approach

New `apps/server/src/mcp/delegatedRuntimeMode.ts` reuses `providerRuntimeMode` so the warning matches what turns really run. `OrchestratorMcpService.delegateTask` looks up the target's snapshot in the providers it already loaded and joins the warning into the result's existing `warning` field. Rejected: refusing the launch (breaks attended Muse work); silently clamping the stored mode (a later provider switch would lose Auto); auto-approving under Muse (a permission change for the owner).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 warn, do not refuse or clamp (reversible)
### Open
- none

## Tasks

### T-01 Warn on delegate_task when the provider lacks the asked mode
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/delegatedRuntimeMode.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/delegatedRuntimeMode.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.delegateMode.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/delegatedRuntimeMode.test.ts apps/server/src/mcp/OrchestratorMcpService.delegateMode.test.ts
