---
title: What the app does when a thread hits a usage limit
increment: 1460
date: November 24, 2026
---

# What the app does when a thread hits a usage limit

Case: the m4 worker thread "Usage-limit stall: fall back on track", on a Tracks project. It ran on GitHub Copilot with Gemini 4 Neon. Copilot (both accounts) and Cursor had both used up their Gemini 4 Neon quota, and the Daily track had Claude Opus 5.5 with room.

Evidence: 918 runs between 8:34 and 10:16 AM EST, November 24, 2026 (runs 1 to 918 failed, run 919 on Claude Opus 5.5 started after a person pressed "Continue with Claude"). Each run failed about 2 seconds after it started, and the next started about 7 seconds later.

## Before the fix (app on `origin/main` `29d788d8c`)

1. **The run fails.** Copilot answers "Error: You have exceeded your monthly quota". The adapter classifies it `usage_limit` ("Monthly quota used up on this provider."). Cursor answers "Gemini 4 Neon is not included in your weekly usage…", also `usage_limit`. One stop names a reset (November 30, 7:00 PM); most name none.
2. **The fallback sweep wakes** (`ProviderFallbackWorker` sweep; a failure wakes it at once, otherwise every 30 seconds).
3. **It decides which providers are held.** `unreportedLimitStops` holds a provider only when it reports no usage at all. Copilot (read through `copilot_internal/user`) and Cursor (with usage reading on) both publish usage windows, so **neither is held**. Not even the stop with a known reset holds Copilot.
4. **It looks for a target.** On a Tracks project, `resolveProviderFallback` tries "the same model on another source" first (`resolveSameModelElsewhere`). Cursor lists Gemini 4 Neon, and its account read still shows room, because the refusal covers one model while the read covers the account. **Cursor is picked.**
5. **Tried targets are forgotten.** The list of sources already tried is keyed by the stopped run. The next stop is a new run, so the list starts empty again.
6. **Repeat.** On Cursor's stop, step 4 finds Copilot with room, and so on. The track's next model (Claude Opus 5.5) is never reached, because "same model elsewhere" always answers first. **Nothing caps the hops.**
7. **The recovery worker** (`UsageLimitRecoveryWorker`) never got involved: the fallback moved the thread before any reset wait. The card's "Continuing with Claude by project rule" describes the rule, not what the sweep was doing.
8. **The timeline.** Each hop added a failure row, a "Switched model" row and a "limit reached · continued on" note. The failure row read "Usage limit resolved — chat continued." because the next run had written assistant text, and Copilot writes its refusal as assistant text.
9. **Side effect.** Each hop wrote a context handoff and started a provider session, which also explains load such as the "linux-mini is slow to answer" toast.

## After the fix (PR #875)

1. **The run fails**, as before.
2. **The source is held.** Its exact instance and model (Copilot / Gemini 4 Neon) are held until the reset the stop names, or for 60 minutes when it names none, **whatever a reseller's usage read says**. The hold covers every thread on the machine, including coordinator turns and new worker launches, so other threads stay off it. Other models on that instance (Cursor's Grok, Claude's other models) stay usable.
3. **Held sources are skipped** in every limit fallback step, including "same model elsewhere" and the track chain.
4. **Second stop** (Cursor): both Gemini 4 Neon sources are held, so the track's next model with room takes the thread. In the reproduction that is Claude Opus 5.5. Copilot is never tried again.
5. **Hop cap.** A chain gets at most 4 automatic hops. A hop counts only when the stopped run was started by the sweep's own continuation of the previous stop, including the replacement sent after a target that could not open. On the next stop the thread **parks**: no more automatic switches and no automatic handoff to another machine. The existing limit card ("Continue with …", "Other models", "Continue on …") is the one place to act. A person's message or any run the sweep did not start begins a new chain.
6. **A hold ends early** only when a run on that same source starts after the stop and completes, or, on Claude and Codex, when a usage read taken after the stop shows room for that model. A status refresh or an unavailable read never ends a hold.
7. **The timeline.** A limit row reads "resolved" only after a later run that completed, did tool work, or wrote a real answer longer than any limit notice. Two or more consecutive hops fold into one line, such as "Usage limits · switched 14 times between Copilot and Cursor", which opens to the original rows. Only text the server's own rule calls a refusal folds; any other answer stays in view.

## Still open

- Before parking, the machine handoff still runs once the whole track is out here. A thread that arrives on another machine starts a new chain there. The existing guard (`reverseMoveSuppressed`, `apps/server/src/handoff/HandoffTransferStore.ts`) only stops a move straight back while the thread is on its first run there. The receiving machine's check (`providerFailures`) doesn't read its own usage holds. This PR leaves the handoff code unchanged.

- Holds and chains live in server memory. After a restart each spent source costs one hop to learn again, which the cap bounds.
- The other machine (handoff) is only taken when the project's usage-limit handoff is on and the whole track is out here. That rule (`MachineLimitHandoff`) is unchanged.
- At launch, routing can still pick a spent "learned preference". That gap, and the Tracks reset wait, belong to m4's thread "Usage-limit stall: fall back on track".
- Proof limit: M5 cannot read m4's live provider snapshot. That Copilot and Cursor published usage reads with room is inferred from the one code path that reproduces the loop (`ProviderFallbackWorker.pingPong.test.ts`, "room usage read" case). With no read, or an unavailable one, the old code already reached Claude.
