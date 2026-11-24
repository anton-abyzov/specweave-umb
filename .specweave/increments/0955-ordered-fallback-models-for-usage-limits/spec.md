# Ordered fallback models for usage limits

## Problem

On October 19, 2026 the user asked to pick, on this machine, the models a limited thread continues on, best first: for example Codex GPT-6 Astra, then GPT-6.1 Sol. The same order should cover the reverse direction, so a limited Codex thread continues on Claude, and other models should work when they are available. The continued work should stay visibly paired with the stopped work.

Today SpecWithCode holds a single `providerLimitFallbackModelSelection`. The planner (`resolveProviderFallback`, packages/shared/src/providerFallback.ts:364) tries the current model on another provider before the user's fallback. The limit banner offers only one "Continue with …" target.

Audit evidence: ~/.specwithcode/m4/scratch/limit-audit-report/README.md. It found three defects that break continuation:
- A Claude `success` result with `api_error_status` 429 is classed `usage_limit` (ClaudeAdapterV2.ts:2766). With no reset time, the thread is switched away and never auto-resumed.
- Threads moved early at the switch threshold never return, because the return path matches only `limit-fallback:` runs (ProviderFallbackWorker.ts:244-251, 507-511, 913).
- A failed fallback dispatch is marked sent first and never retried for that run (ProviderFallbackWorker.ts:1304-1323).

## Scope

In, all in SpecWithCode (`anton-abyzov/specwithcode-dev`):
- the settings contract (global and project);
- the shared planner;
- ProviderFallbackWorker;
- the Providers settings page;
- the limit banner;
- the timeline continuation note;
- the Claude 429 classification.

Out:
- moving work to another machine (no automatic remote fallback);
- switching the signed-in account;
- spending options (credits, API keys), which keep their own opt-in;
- a separate linked thread per continuation (D-01).

## Acceptance Criteria

- [ ] AC-01: Settings hold `providerLimitFallbackModels`, an ordered list of up to 8 unique `{instanceId, model}` entries, globally and per project. The default is empty. When it is empty, a set legacy `providerLimitFallbackModelSelection` acts as a one-entry list. Saving the list also writes its first entry to the legacy key. Project overrides and machine-handoff resets cover the new key.
- [ ] AC-02: With a non-empty list, a limited thread continues on the first entry that is:
  - not the thread's current instance;
  - not limited;
  - signed in and able to take a turn;
  - holding a live listed model;
  - and has room, read the same way as today (a usage read under 5 minutes old and below the switch threshold, or a provider that reports no usage).

  The list goes before the same-model-elsewhere, project default, coordinator and any-ready steps, which still apply when no entry qualifies. One list serves both directions: for a Claude thread, `[Codex GPT-6 Astra, Codex GPT-6.1 Sol, Claude Opus 5.5]` gives Astra, then Sol; for a limited Codex thread it gives Claude Opus 5.5. A model-scoped window (Astra full, Sol not) gives Sol. Per-token instances in the list are skipped, unless the API-credit rule applies on its own terms.
- [ ] AC-03: The Providers page shows "Fallback order": numbered rows with provider and model, move up, move down, remove, and "Add model" (the existing provider-model picker, which refuses duplicates). It also shows "Any ready provider after these" and a reset. A project override page row exists.
- [ ] AC-04: The limit banner's primary button names the first eligible entry, e.g. "Continue with Codex · GPT-6 Astra". A menu lists the other entries in order, each either choosable or shown with a reason it is not available now ("full until 11:19 PM", "signed out", "limited"). Choosing one continues the stopped run on it through the same server path as the automatic switch.
- [ ] AC-05: The continuation stays paired in the same thread:
  - the timeline note reads "Claude limit reached · continued on Codex · GPT-6 Astra" (existing note, now also for early moves: "Switched before the Claude limit · continued on …");
  - while a thread runs on a fallback, its header shows "On Codex · GPT-6 Astra for Claude Opus 5.5" with the original's reset time when known, and a "Back to Claude Opus 5.5" action that is enabled when that provider has room.
- [ ] AC-06 (moved to 1075 on October 25, 2026; D-04): A thread moved early at the switch threshold returns to its original model like a limit continuation, once that provider has room or its reset passes.
- [ ] AC-07: A fallback dispatch that fails is retried, at most 3 attempts per run with backoff. Persisted command receipts still prevent a duplicate continuation after a restart.
- [ ] AC-08: A Claude `success` result with `api_error_status` 429 is `usage_limit` only when a window was rejected, the assistant reported `rate_limit`, or the terminal reason is `blocking_limit`. Otherwise it is `provider_error` with "Claude API rate limit reached. Try again later." and no switch.

## Decisions

### Asked
- none

### Defaulted
- D-01: Continue in the same thread, as today. The provider session is new, and another driver gets the handoff summary. It is paired by the timeline note and header chip, not by a new thread. This keeps one conversation, its history, queue and owner, and the return path. The user said "nested or new session… pair them… or name it appropriately", and the same thread with labelled segments satisfies that without duplicating threads.
- D-02: The user's explicit order beats same-model-elsewhere, because it is the stronger intent. Users who set no list keep today's order exactly.
- D-03: There is one ordered list, not a list per provider. The current instance and limited instances are skipped, so the reverse direction needs no second setting.
- D-04: AC-06 needs a persisted record of the early move's origin, because nothing in runs, handoffs or receipts identifies the target. That is a new thread field or a server-local store, so it gets its own increment. Meanwhile, the header chip (AC-05) gives a manual way back for limit continuations.

## Tasks

### T-01 Contract and planner
- AC: AC-01, AC-02 | Files: packages/contracts/src/settings.ts, packages/shared/src/providerFallback.ts, apps/server/src/fleet/MachineHandoff.ts | Test: vp test run packages/shared/src/providerFallback.test.ts packages/contracts/src/settings.test.ts

### T-02 Worker: ordered list, early-move return, dispatch retry
- AC: AC-02, AC-07 | Files: apps/server/src/orchestration-v2/ProviderFallbackWorker.ts | Test: vp test run apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts apps/server/src/orchestration-v2/ProviderFallbackWorker.policy.test.ts

### T-03 Claude 429 classification
- AC: AC-08 | Files: apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts | Test: vp test run apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts

### T-04 Settings UI, banner choices, pairing chip
- AC: AC-03, AC-04, AC-05 | Files: apps/web/src/components/settings/ProviderLimitSettings.tsx, apps/web/src/components/settings/projectOverrideRows.ts, apps/web/src/components/chat/UsageLimitRecoveryBanner.tsx, apps/web/src/components/ChatView.tsx, apps/web/src/studio/runIdentity.ts | Test: vp test run apps/web/src/components/chat/UsageLimitRecoveryBanner.test.tsx apps/web/src/studio/runIdentity.test.ts

### T-05 Headless visual evidence, PR, release queue
- AC: AC-03, AC-04, AC-05 | Files: none | Test: headless screenshots of the settings list, banner menu and header chip saved under ~/.specwithcode/m4/scratch/fallback-order-evidence

### T-06 Verify and close 0955
