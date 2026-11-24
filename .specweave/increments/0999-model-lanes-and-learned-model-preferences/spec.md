# Model lanes and learned model preferences

## Problem
Picker favorites are an unordered, per-device star set. The server cannot see them, so they cannot choose a worker's model. The user wants two ordered default lists instead: one of frontier models for complex or creative work, one for routine work led by Opus 5.5. The coordinator judges which kind each task is and starts it on the first model in that list that can run now, skipping a provider that is limited or exhausted (Copilot's monthly quota). Each project also remembers what the user said about which model suits which kind of task.

## Scope
In: two ordered lane lists as a project-scoped server setting; lane classification (coordinator hint first, then learned rules, then deterministic rules); lane-first worker routing in delegate_task, create_threads and studio_thread_launch; per-project learned preferences with an MCP tool for the coordinator and a feedback control on the routing chip; Settings UI (Settings > Providers and Project settings) with the learned list; tests, headless screenshots, a real routing check, PR, release.
Out: mid-run usage-limit continuation (ProviderFallbackWorker keeps the Fallback order; open PRs #593, #599, #612 own that code); removing picker favorites (they stay as picker shortcuts and can seed a lane).

## Acceptance Criteria
- [x] AC-01: Settings has an ordered "Complex and creative" list and an ordered "Routine" list (max 8 each, reorder, remove, add from any provider's catalog, seed from favorites), saved machine-wide with per-project override.
- [x] AC-02: A worker whose model nobody named starts on the first entry of its lane that is installed, signed in, below the switch threshold and not usage-limit held (Copilot monthly quota); skipped entries and the reason are recorded on the routing decision. With both lists empty, behaviour is unchanged.
- [x] AC-03: The lane comes from the caller's `taskLane` hint, else a matching learned preference, else deterministic rules (complexity and creativity markers, size of the brief, task class); a named model, a restricted work grant and Opus-only pinned lanes are never overridden.
- [x] AC-04: Each project keeps learned preferences (prefer a model, avoid a model, or set the lane, for tasks matching keywords or a task class). The coordinator records them with an MCP tool when the user gives feedback; the routing chip offers the same capture; Settings lists and deletes them. A matching prefer rule is tried first, an avoid rule is skipped.
- [x] AC-05: Unit tests for classification, selection, skipping and learned rules; settings and chip component tests; headless screenshots of the new settings; a real routing check on the installed build where a complex task and a routine task land on the right models and an exhausted provider is skipped.
- [x] AC-06: PR merged with CI green; a signed and notarized macOS release ships through the documented process after checking no other release is in flight; this Mac updates to it.

## Approach
New shared module `packages/shared/src/modelLanes.ts` holds the lane classifier, learned-rule matching and `resolveLaneRouting`, reusing `canTakeTurn`, `providerUsedPercent` and `isGeminiSpendProvider` from providerFallback. Server `project/TaskRouting.ts` tries lanes before the existing tier router; lanes are active whenever the lane's list is non-empty (configuring them is the opt-in). Lane entries are explicit user choices, so a per-token instance in a list is allowed and labelled; Gemini spend stays excluded as in #603. Contracts gain `ModelLanes`, `LearnedModelPreference`, two project-scoped keys (`modelLanes`, `learnedModelPreferences`), an optional `taskLane` hint on worker-launch inputs and optional `lane`/`skipped`/`preferenceId` fields on `TaskRoutingDecision`. A project MCP tool `studio_model_preference` records, lists and deletes learned rules. Web gets `ModelLanesSettings` and a feedback popover on `RoutingDecisionChip`.

## Decisions
### Defaulted
- Lanes apply without the Auto switch once a list has an entry; empty lists keep today's behaviour.
- Unclassified work goes to Routine; complexity needs a marker, a large brief or a design/creative class.
- Per-token entries a person put in a lane are allowed (explicit choice) and labelled "billed per token"; Gemini/Vertex spend is never chosen automatically.
- Learned preferences are written to the project override, never machine-wide, so one project's feedback does not leak into another.
- Picker favorites stay; the lanes card offers "Add favorites" to seed a list.
### Open
- none

## Tasks
### T-01 Contracts: lanes, learned preferences, taskLane hint, decision fields
- AC: AC-01, AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/packages/contracts/src/taskRouting.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/packages/contracts/src/settings.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/packages/contracts/src/orchestratorMcp.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/packages/shared/src/serverSettings.ts | Test: contracts typecheck and settings decode tests

### T-02 Shared lane router and learned-rule matching
- AC: AC-02, AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/packages/shared/src/modelLanes.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/packages/shared/src/modelLanes.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/packages/shared/package.json | Test: vitest modelLanes.test.ts

### T-03 Server: lane-first routing in worker launches and the preference MCP tool
- AC: AC-02, AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/server/src/project/TaskRouting.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/server/src/mcp/OrchestratorMcpService.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/server/src/mcp/toolkits/project/tools.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/server/src/mcp/toolkits/project/handlers.ts | Test: server routing and MCP tool tests

### T-04 Web: lanes settings, learned list, chip feedback
- AC: AC-01, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/web/src/components/settings/ModelLanesSettings.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/web/src/components/settings/ProjectDefaultsSettings.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/web/src/components/studio/shell/RoutingDecisionChip.tsx | Test: component tests and headless screenshots

### T-05 PR, CI, merge, release and installed routing check
- AC: AC-05, AC-06 | Files: PR, release run, evidence under /Users/antonabyzov/.specwithcode/m4/evidence/model-lanes-20261022 | Test: CI green, release verified, installed routing check

### T-06 Verify and close 0999
- AC: AC-05, AC-06 | Files: verification evidence | Test: specweave verify, fresh-context review, specweave complete
