# 1306 Background work never leaves a thread stuck on a settings change

## Problem

In the "Cross-account machine connect" thread (Claude on the M4) the owner changed effort from high to xhigh while a background subagent ("Build redesigned Machines join card") was running. Every message after that failed within 2 seconds with a red "Provider error: Claude is still running background agents or commands, and this model change would end them." Runs 55 to 61 were marked Failed. Setting effort back did not help, the error named nothing, and its buttons (Continue, Switch model) could not fix it. He could not tell why the thread was stuck or what to press.

PR #177 (`8a7b500f66`, unreleased) makes a model, effort, Fast Mode or thinking change wait for the background work, with a quiet note. It leaves these gaps:

- A change that narrows access (a removed folder, a permission or tool change) is still refused with the generic "Provider error" card. It names no work, Continue fails again while the work runs, and Switch model is irrelevant.
- Nothing says up front, where the choice is made, that a change will wait.
- The quiet note says "background work" without naming it.
- A prompt-injected effort (Ultrathink) applies on the waiting turn although the note says the change waits (#177 review item).

## Scope

In: the Claude adapter's refusal and deferral text, a failure code for the refusal, its card in the timeline and the thread banner, a note in the composer's model picker, the prompt effort on a waiting turn.

Out: holding a refused message in the queue until the work ends; a pending-setting marker on the model chip (needs the live selection in the thread projection); automatic stuck-subagent detection (the composer strip already names the work and has Stop); the automatic model switch that gets one attempt on the old model (#177 review item, limit-fallback machinery); other providers.

## Acceptance Criteria

- [ ] AC-01: A turn refused because background work blocks a folder, permission or tool change fails with code `background_work_blocks_change`, and its message names the work, for example: Claude is still running subagent "Build redesigned Machines join card".
- [ ] AC-02: That failure's card is titled "Background work is still running", never "Provider error", in the timeline and in the thread banner.
- [ ] AC-03: While the work runs, the card offers one action, "Stop background work and continue", which stops the work and then continues the failed run. It shows no Switch model. Once the work has ended the action is Continue.
- [ ] AC-04: The quiet note for a waiting model or effort change names the work: Effort xhigh applies when subagent "Build redesigned Machines join card" finishes.
- [ ] AC-05: The model picker of a settled Claude thread that still hosts background work shows a note naming the work and saying that a model or effort change applies when it finishes. Threads without such work, and other providers, show none.
- [ ] AC-06: On a turn whose selection waits, the prompt keeps the effort keyword the live process opened with; the new one is sent with the first prompt of the next process.

## Approach

One rule: a settings change during background work either waits and says so where it is made, or is one click from applying. Nothing fails silently or generically.

Server (`apps/server`):

- `ClaudeAdapterV2.ts`: `liveProcessBackgroundWork(live)` beside `liveProcessRunsBackgroundWork` reads the same roster and subagent registry and returns a label and a count (kind noun plus quoted description, at most 3, then "and N more"). `ClaudeBackgroundWorkBlocksQueryReplacementError` gains `blockedBy` and words its message with it. The deferral note takes the same names. `ClaudeLiveQueryContext` remembers `openedPromptEffort`; `startTurn` and `steerTurn` use the opened prompt effort while a selection waits (the prompt is still built before the query opens, so an unsendable prompt opens no process; it is rebuilt only when the keyword differs).
- `claudeModelOptions.ts`: `describeDeferredClaudeSelection` takes an optional work label.
- `ProviderFailure.ts`: `classifiedFailureCode` returns the new code for that error tag.
- `packages/shared/src/orchestrationV2ThreadError.ts`: `BACKGROUND_WORK_BLOCKS_CHANGE_FAILURE_CODE`, its title in `providerFailureDisplayTitle`, and continuable in `isContinuableProviderFailure`.

Web (`apps/web`):

- `chat/BackgroundWorkBlockRecovery.tsx` (new): the single action. `FailureRecovery.tsx` and `ThreadErrorBanner.tsx` render it instead of Continue and Switch model for that code, following the existing workspace-missing precedent.
- `ChatView.tsx`: wires the action. Stop reuses `handleStopBackgroundWork`; the continue fires when the pending work list empties, or after 8 seconds, so the interrupt has closed the process first.
- `chat/ModelPickerBackgroundWorkNote.tsx` (new), passed through `ChatComposer.tsx`, `ProviderModelPicker.tsx` and `ModelPickerContent.tsx`, shown above the effort strip.

Rejected: holding the refused run in a held queue and starting it when the work ends. It is the stronger fix, but it changes run lifecycle and queue semantics and needs the orchestrator to learn about adapter-side background work; too much for one PR. Letting a narrowing change wait like a model change is rejected for good: the process would keep more access than granted.

Risk: the names come from provider-supplied descriptions. `liveProcessBackgroundWork` passes each through `redactProviderFailureText` before it reaches the note or the error, and `describeBackgroundWork` keeps the first line, drops control characters and cuts it to 80 characters.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Refused narrowing change stays a failed run with a one-click card, not a held queue (smaller, reversible).
- D-02 The picker note shows only on a settled thread; during a running turn the client cannot tell foreground from background subagents.
- D-03 No chip marker and no stuck-subagent timer in this increment.

### Open
- none

## Tasks

### T-01 Name the blocking work, classify the refusal, keep the prompt effort
- AC: AC-01, AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/claudeModelOptions.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/claudeModelOptions.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProviderFailure.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProviderFailure.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/orchestrationV2ThreadError.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/orchestrationV2ThreadError.test.ts | Test: cd ~/.specwithcode/m4/scratch/2026-11-11-background-work-settings/repo && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts apps/server/src/claudeModelOptions.test.ts apps/server/src/orchestration-v2/ProviderFailure.test.ts packages/shared/src/orchestrationV2ThreadError.test.ts

### T-02 One-action card for the refusal
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/BackgroundWorkBlockRecovery.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/BackgroundWorkBlockRecovery.dom.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/FailureRecovery.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ThreadErrorBanner.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ThreadErrorBanner.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/MessagesTimeline.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/provider-errors/main.tsx, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/orchestrationV2PendingBackgroundWork.ts | Test: cd ~/.specwithcode/m4/scratch/2026-11-11-background-work-settings/repo && node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/ThreadErrorBanner.test.tsx apps/web/src/components/chat/MessagesTimeline.test.tsx
- **Dependencies**: T-01

### T-03 Picker note while background work runs
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ModelPickerBackgroundWorkNote.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ModelPickerBackgroundWorkNote.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ModelPickerContent.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ProviderModelPicker.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ChatComposer.tsx | Test: cd ~/.specwithcode/m4/scratch/2026-11-11-background-work-settings/repo && node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/ModelPickerBackgroundWorkNote.test.tsx apps/web/src/components/chat/ModelPickerContent.test.tsx apps/web/src/components/chat/ProviderModelPicker.test.tsx
- **Dependencies**: T-02

### T-04 Changelog, pull request, SHIP review on the exact head, merge, release handoff
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/CHANGELOG.md | Test: cd ~/.specwithcode/m4/scratch/2026-11-11-background-work-settings/repo && gh pr view --json state --jq .state | grep -qx MERGED
- **Dependencies**: T-03

### T-05 Verify and close 1306
- AC: AC-01 | Files: .specweave/increments/1306-background-work-never-leaves-a-thread-stuck-on-a-settings-change/reports/closure.md | Test: specweave verify 1306-background-work-never-leaves-a-thread-stuck-on-a-settings-change
- **Dependencies**: T-04
