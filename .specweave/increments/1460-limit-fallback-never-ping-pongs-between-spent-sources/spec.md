# Limit fallback never ping-pongs between spent sources

## Problem

On November 24, 2026 a worker thread on m4 ("Usage-limit stall: fall back on track") ran 918 turns between 8:34 and 10:16 AM EST. Each turn failed within two seconds and the next started about seven seconds later, alternating two sources of one model:

- GitHub Copilot, Gemini 4 Neon: "You have exceeded your monthly quota" (classified `usage_limit`, "Monthly quota used up on this provider."; one stop named a reset, November 30, 7:00 PM).
- Cursor, Gemini 4 Neon: "Gemini 4 Neon is not included in your weekly usage Buy credits or switch to a Grok model to continue."

The project's Daily track had Claude Opus 5.5 with room, and the limit card said "Continuing with Claude by project rule", yet the thread only left the loop when a person pressed "Continue with Claude". The timeline showed dozens of "limit reached · continued on …", "Switched model" and "Usage limit resolved — chat continued." rows.

Cause, from the code at `origin/main` `29d788d8c` and a reproduction test (`ProviderFallbackWorker.pingPong.test.ts`):

1. The only memory of "this source just refused" is `unreportedLimitStops`, and it holds only providers that report no usage at all (`reportsNoUsage`). Copilot (via `copilot_internal/user`) and Cursor (with usage reading on) both publish usage windows, so a stop on them holds nothing, even when the stop names its reset.
2. A provider's own refusal is model-specific (Gemini 4 Neon is out; the account's premium-request or weekly window still shows room). `hasUsableFallbackCapacity` and `roomOn` trust the account read, so the source that just refused still reads as having room.
3. Tried targets (`failedTargets`) are keyed by the stopped run (`thread:latestRunId`). Every hop is a new run, so each stop starts with an empty tried set.
4. On a Tracks project `resolveSameModelElsewhere` runs first and always finds "the same model on the other source", so the track's next model (Claude Opus 5.5) is never reached. Nothing caps hops.
5. The web timeline marks a usage-limit row "resolved" when a later run wrote any assistant text. Copilot writes its refusal ("Error: You have exceeded your monthly quota") as assistant text, so every stop read as resolved.

With the read missing or unavailable, the reproduction reaches Claude; with a read showing room it alternates indefinitely. Proof limit: M5 cannot read m4's live provider state, so which read Copilot and Cursor published on m4 is inferred from the code path that alone reproduces the loop.

## Scope

In: hold the exact source (instance and model) a limit stop came from until its reset or a backoff, whatever its usage read says; skip held sources in every fallback step; cap automatic hops per chain and park after the cap; stop calling a run that itself failed on a limit "resolved"; collapse consecutive limit hops into one timeline line. Out: routing's learned preference picking a spent model at launch and the Tracks reset wait (owned by m4's thread "Usage-limit stall: fall back on track"); cross-machine handoff rules (unchanged, `MachineLimitHandoff`); persisting holds across a server restart.

## Acceptance Criteria

- [ ] AC-01: A thread stopped on a usage limit holds its source (instance and model) until the reset the stop names, or for 60 minutes when it names none. The hold applies whether or not the provider reports usage, and other models on the same instance stay usable.
- [ ] AC-02: No automatic limit fallback, for any thread on the machine, moves onto a held source. With two spent sources of one model on a Tracks project, the second stop moves the thread to the track's next model with room (reproduction: Copilot → Cursor → Claude Opus 5.5, never back to Copilot).
- [ ] AC-03: A hold ends early only when a run on that same source starts after the stop and completes, or, for a maker's own harness whose read covers each model (Claude, Codex), when a usage read taken after the stop shows room for that model.
- [ ] AC-04: Automatic limit fallback makes at most 4 hops in one chain (each stop on a run the sweep's own continuation of the previous stop started). After the cap the thread parks: no further automatic switch, and the existing limit card stays the one place to act.
- [ ] AC-05: A usage-limit row reads "resolved" only when a later run completed or did tool work; a later run that itself failed (its text is the provider's refusal) does not resolve it.
- [ ] AC-06: Consecutive limit hops in the timeline show as one collapsed line naming the hop count and the sources tried, expandable to the individual rows.

## Approach

1. `apps/server/src/orchestration-v2/limitSourceHolds.ts` (new, pure): `limitSourceHolds(previous, stoppedThreads, nowMs)` learns holds keyed by `fallbackSelectionKey`, `releaseCompletedSourceHolds` drops one when a later run on that source completes, and `limitFallbackChains` counts hops per thread.
2. `ProviderFallbackWorker.ts`: the sweep keeps both in `Ref`s next to `unreportedStops`, and passes held keys into `providerLimitStep` as part of `failedTargets` (already `excludedSelections` all the way down to `resolveSameModelElsewhere` and the track chain). A thread at the hop cap gets no `switch` step.
3. `apps/web/src/components/chat/usageWarningResolution.ts`: a failed later run counts only for tool work.
4. Web timeline grouping in a new module beside `MessagesTimeline.logic.ts` (that file and `MessagesTimeline.tsx` are already over the line limit).

Rejected: holding the whole instance (blocks Cursor's other models that still have room); trusting the usage read over the refusal (the cause); deriving chains from persisted runs (reading up to 900 runs per thread per sweep; after a restart the in-memory hold is relearned in one hop per source, at most 4 hops).

Risk: a source whose refusal was transient now waits up to 60 minutes. A completed run on it releases it sooner, and a person's pick is never blocked.

## Decisions

### Asked
- none (owner brief on November 24, 2026 named the behaviour: hold until reset or backoff, never switch back, cap hops, one action, one collapsed line)
### Defaulted (change any before sw-do)
- D-01 Unknown-reset backoff 60 minutes (owner asked for "a backoff"; the old no-usage hold used 5 hours, which parks a transient refusal too long).
- D-02 Hop cap 4 per chain; after it the thread parks on the existing card instead of a new one.
- D-03 Holds are per instance and model, not per instance.
- D-04 (review round 2, replaces round 1's) A parked chain makes no automatic move of any kind, including a handoff to another machine. The card's "Continue on …" is the one way to another machine. Round 1 allowed one handoff after parking, but the chain lives on one machine and the arrived thread is a new thread there, so "once" could not be enforced across machines.
- D-05 (review round 1) A fresh usage read releases a hold only on Claude and Codex, whose reads cover each model. Resellers (Copilot, Cursor, ACP agents) are released only by a completed run or the hold's end.
- D-06 (review round 1) The holds are shared process-wide, so a coordinator turn and a worker launch skip a held source too, not only the fallback sweep.
- D-07 (review round 2) A hop counts when the stopped run was started by the sweep's continuation of the previous stop, directly or as `limit-fallback:<thread>:hop-N:<stop>` after a target that could not open (parsed with `fallbackMove`).
- D-08 (review round 2) A read releases a Claude or Codex hold only if it is a usage read (not unavailable) taken after the stop that reads that model's percent. The release is recorded, so the old stop never holds again.
- D-09 (review round 2) The web names a refusal with the server's own rule (`isUsageLimitReply`, `packages/shared/src/usageLimitReply.ts`). For "resolved", text from a run that itself stopped on a limit counts only when it is longer than any notice (400 characters), or when the run did tool work.
- D-10 (review round 3) A parked chain sends no way back home either, even once the home's hold runs out; the card is the one place to act.
- D-11 (review round 3) The last check before a handoff applies D-08's read release to the providers it reads again, so a usage read that came in while the other machine answered keeps the thread here.
- D-12 (review round 3) Text from a stopped run also folds as a refusal when it repeats that run's own recorded limit failure (Cursor's refusal arrives as the run's error).
- D-13 (review round 4) A refusal must equal the run's whole recorded failure once normalized (lower case, single spaces, no `Error:` opening, request id or closing punctuation). Part of it, or the failure inside an answer, is an answer.
### Open
- none

## Tasks

### T-01 Hold the refusing source and cap hops in the fallback sweep
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/limitSourceHolds.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/limitSourceHolds.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.pingPong.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFallbackWorker.pingPongSweep.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/UnopenableHolds.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/limitHandoffTrack.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectCoordinatorService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/WorkerLaunchRoom.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/ProviderFallbackWorker.pingPong.test.ts apps/server/src/orchestration-v2/ProviderFallbackWorker.pingPongSweep.test.ts apps/server/src/orchestration-v2/limitSourceHolds.test.ts packages/shared/src/providerFallback.heldSources.test.ts

### T-02 A failed later run never resolves a limit row
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/usageWarningResolution.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/usageWarningResolution.test.ts | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/usageWarningResolution.test.ts

### T-03 Collapse consecutive limit hops into one timeline line
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/limitHopGroups.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/limitHopGroups.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/limitHopGroups.test.ts

## Review

Adversarial review on GPT-6.2 Sol (Codex). Never Grok; Gemini 4 Neon is out of quota.

Result: 5 rounds on m4. Round 5 was CLEAN at `dad226959`. PR #875 merged as `525b3b2c0` on November 24, 2026.
