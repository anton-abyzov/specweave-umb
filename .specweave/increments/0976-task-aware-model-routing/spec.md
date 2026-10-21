# Task-aware Auto model routing

## Problem

Every SpecWithCode worker starts on the project's worker model (Opus 5.5 by default) or the caller's model, whatever the task. Translations, processing an hour of transcript and first animation drafts run fine on Sonnet 5.5, but they spend Opus quota today. No part of the app knows which model fits a task. The only automatic move is the usage-limit fallback (0955).

The user asked on October 20, 2026 for deliberate, opt-in routing that weighs provider availability and entitlement, task difficulty and risk, modality, context and tool support, and cost or quota. It must never treat the cheapest model as the default for final or high-risk work.

## Scope

In:
- One pure router in packages/shared.
- A deterministic classifier with optional `taskClass` hints on delegate_task, create_threads and studio_thread_launch.
- The `taskRouting` setting (project-overridable), with policy precedence, floors, exclusions and a paid-API cap.
- Persisting the decision on the delegated task and the thread.
- At most one escalation after a failure.
- A long-audio pipeline (ASR first, then chunking).
- A Settings panel, a decision chip, tests and headless evidence.

Out:
- Server-side speech-to-text.
- An LLM classification call.
- Price tables for money estimates.
- Cross-machine routing (0968).
- Changing the usage-limit fallback.

## Acceptance Criteria

- [ ] AC-01: `classifyTask` labels each task with a class (translation, transcript, summary, research, animation-draft, animation-final, code, review, design, general), a confidence and its signals, without any model call. Risk markers move a cheap class to its final/high-risk form. Ties or no signal count as uncertain.
- [ ] AC-02: `routeTask` follows the precedence in the design. An explicit model or provider pin wins. Auto is off by default. The minimum tier and the exclusions always hold. Auto moves only below the baseline, never above it. Unknown tiers and per-token providers are never picked unless the paid-API cap allows. An unavailable or limited provider is skipped. When no model is eligible, the baseline stays and the reason is given.
- [ ] AC-03: Model tiers come from the live catalog, via the slug or name. Sonnet 5.5 resolves to `claude-sonnet-5-5` on claudeAgent and to `claude-sonnet-5.5` on each Copilot instance, and the two Copilot instances stay distinct.
- [ ] AC-04: A long-audio or transcript task gets a decision with an explicit ASR → chunk → process pipeline and a chunk plan sized to the routed model's context window. The worker prompt says that the text model does not transcribe the audio.
- [ ] AC-05: Server: delegate_task, create_threads and studio_thread_launch apply the router where the app picks the model: a coordinator worker with no model named, or a caller that passes `taskClass`. The decision is persisted on the task and thread records and returned in the tool result. Explicit pins and inherited non-coordinator models are unchanged.
- [ ] AC-06: Escalation runs at most once per thread. A routed thread whose run failed with a non-limit error continues once, in the same thread, on the baseline model. It never escalates mid-turn, never on a usage limit, and never twice.
- [ ] AC-07: The `taskRouting` setting persists: mode, quality, per-class tiers, minimum tier, excluded providers, paid-API cap and escalation. The project override works. Decode defaults keep older settings files valid.
- [ ] AC-08: The Settings panel edits the policy and lists conflicts. The decision chip shows the provider (display name), model, class, reason, billing and escalation. Headless screenshots are saved.
- [x] AC-09: Tests cover:
  - task classes
  - pins
  - floors
  - exclusions
  - an unavailable provider
  - no eligible model
  - long audio
  - translation
  - animation draft vs final
  - cost opt-in
  - persistence
  - fallback interplay
  - escalation

  Some of these tests fail before the change.

## Approach

Design: ~/.specwithcode/m4/scratch/task-aware-routing/design.md.

Changed files, in order:
1. packages/contracts/src/taskRouting.ts: the schemas.
2. settings.ts: the setting, patch and project key.
3. orchestrationV2.ts: optional `routing` on the subagent, thread, shell and commands.
4. orchestratorMcp.ts: the `taskClass` hint and the `routing` result.
5. packages/shared/src/taskRouting.ts: the router.
6. apps/server/src/project/TaskRouting.ts: the single server helper.
7. OrchestratorMcpService.ts and project/handlers.ts: call sites.
8. Orchestrator.ts and ProjectionStore.ts: persistence.
9. orchestration-v2/TaskRoutingEscalationWorker.ts: escalation.
10. apps/web: TaskRoutingSettings, RoutingDecisionChip, header and peek, and the fixture.

Rejected:
- An LLM classifier: it spends tokens on trivial decisions.
- Routing inside ProviderFallbackWorker: it owns limits only, and this keeps one router.
- Syncing the setting across machines: provider ids are per machine.

## Decisions

### Asked
- D-01: Model for this work → local Claude Code Opus 5.5 high only (user).
### Defaulted (change any before sw-do)
- D-02: Auto is off by default. It applies only to coordinator workers with no model named, or to callers that pass `taskClass`.
- D-03: The default class tiers are standard (Sonnet) for translation, transcript, summary, research and animation-draft, and frontier (no change) for everything else. Economy (Haiku) is used only when the user turns it on.
- D-04: code, review, design and animation-final never go below standard.
- D-05: Paid API is never used by default. The cap allows at most the tier the user picks, and the app never activates credentials or credits.
- D-06: The setting is per machine (not shared) and can be overridden per project.
### Open
- none

## Tasks

### T-01 Contracts: routing schemas, setting, hints and record fields
- AC: AC-05, AC-07 | Files: packages/contracts/src/taskRouting.ts, settings.ts, orchestrationV2.ts, orchestratorMcp.ts | Test: contracts unit tests

### T-02 Shared router: classifier, tiers, policy, chunk plan, conflicts
- AC: AC-01, AC-02, AC-03, AC-04 | Files: packages/shared/src/taskRouting.ts | Test: packages/shared/src/taskRouting.test.ts

### T-03 Server: apply the router at the three launch sites and persist
- AC: AC-05 | Files: apps/server/src/project/TaskRouting.ts, OrchestratorMcpService.ts, project/handlers.ts, Orchestrator.ts, ProjectionStore.ts | Test: server unit tests

### T-04 Escalation worker
- AC: AC-06 | Files: apps/server/src/orchestration-v2/TaskRoutingEscalationWorker.ts, runtimeLayer.ts | Test: worker unit tests

### T-05 Web: settings panel and decision chip
- AC: AC-08 | Files: apps/web/src/components/settings/TaskRoutingSettings.tsx, studio/shell/RoutingDecisionChip.tsx, ProjectThreadHeader.tsx, SubagentPeek.tsx | Test: web unit tests

### T-06 Headless evidence
- AC: AC-08 | Files: apps/web/tests/task-routing/ | Test: verify.mjs headless

### T-07 PR, memory and coordination
- AC: all | Files: none | Test: gh pr view

### T-08 Verify and close 0976
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
