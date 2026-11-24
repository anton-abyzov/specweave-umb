---
title: "M3 thread stuck on Muse while Copilot Enterprise fallback has room"
thread: "thread:delegated-task:command%3Amcp%3Ad5782804-af62-4854-93c6-fba0973b4e9b%3Adelegate-task%3Aec1d8186-34a1-4d5a-968c-dddeb219cbd6"
threadTitle: "Review track fallback"
savedAt: "2026-11-20T15:33:30.083Z"
date: November 20, 2026
investigated-on: M5
evidence: two M3 photos (IMG_0197, IMG_0198, taken 15:28 UTC) plus code at v1.0.404 and a synthetic unit test. M3's app version is unknown; code findings are for 1.0.404
scope: read-only; no settings changed, no paid calls
---

# M3 thread stuck on Muse while Copilot Enterprise fallback has room

**Short answer:** M3 did fall back automatically from Opus 5.5 to the first entry in its fallback order, Muse `muse-wonder-1.0`. Muse then fails every turn with a generic "sent no details" error. The automatic fallback only moves a thread again after a usage-limit stop, or before a turn when a usage reading reaches the threshold. Muse gives neither: its errors are `provider_error`, and it has no usage reading. Continue resends on the thread's current model, which is Muse again. The thread can never reach Fallback 2, Claude Opus 5.5 on GitHub Copilot Enterprise (48% left), on its own.

## What the M3 photos show (observation)

| Item | Seen on M3 |
|---|---|
| Thread | "EU1 migration and…", Increment 0030 (Datadog EU migration), PR #29410, runs on m3 |
| Track banner | "Running on a fallback". Now: `muse-wonder-1.0 · Muse Code`. Meant for: `Opus 5.5 · Claude Code · Neared its usage limit.` Return: AUTOMATIC, "Goes back on its own once it has room." |
| Switch | Timeline line "Switched model Claude Opus 5.5 → muse-wonder-1.0" |
| Failures | "Provider error · earlier turn" at 9:47 AM. "Continue where you left off." sent at 10:28 AM on `m3 · Muse Code · muse-wonder-1.0`, then Provider error at 10:28: "The provider ended this turn with an error but sent no details…". Thread status "Failed · <1m elapsed" |
| Restart action | The **Continue** button on the error card, next to **Switch model**. The photo shows one Continue press ("Continue where you left off." at 10:28 on Muse) and two errors (9:47 and 10:28). I did not read the Continue handler; the photo alone shows the retry ran on Muse |
| Picker | GH Copilot Enterprise on m3: "Premium req… 48% left · 10d 8h", "Billing not reported". Claude Opus 5.5 marked **Fallback 2**. Other providers: Codex (3), Claude (15), Gemini CLI (1), GH Copilot E… (28), GitHub Copilot (2), Muse Code (5). No Devin. Cursor and Grok are "ready on m4", not on m3 |

What this implies about M3's fallback order (inference): Muse is entry 1 and Copilot Enterprise Opus 5.5 is entry 2, because the automatic switch landed on Muse and the picker labels Copilot Opus "Fallback 2". I did not find the badge's source code. The photos can't show whether the project runs Tracks (Daily) or a saved fallback order. Either way, plain `muse-wonder-1.0` ahead of Opus 5.5 on another source conflicts with the owner rules in `decision_model_tracks` (November 17 and 18: regular work stays on Daily; Muse Wonder Full only as the last resort; the same model on another source comes before a different model).

**Expected behavior (Anton's):** when the fallback fails, the next entry (Copilot Enterprise Opus 5.5) should take the thread.

## What M5 can and cannot see about M3

M3 is not in M5's fleet. `studio_machine_list` on M5 lists win, m4 and linux-mini only, and `studio_thread_list {machine: "m3"}` returns `unknown_machine`: "No machine named \"m3\". studio_machine_list shows the machines this one can use." So M5 has no authorized access to M3's database, settings, logs or provider identities. Everything about M3 below is either from the photos or inferred from the code, and labelled that way. The same Muse failure pattern does appear on M5 (9 of 9 Muse turns failed since November 19; see the earlier 1362 report). Muse is signed in with no usage reading on M5, m4 and win alike.

## Configured, eligible, attempted (M3, inferred from photos + code)

| Candidate | Configured | Eligible to the fallback code | Attempted |
|---|---|---|---|
| Opus 5.5 · Claude Code | home model | No: neared its limit (pre-switch threshold) | Yes, earlier, until the pre-switch |
| muse-wonder-1.0 · Muse Code | fallback entry 1 (inferred) | Yes: a named entry that reports no usage is allowed | Yes: the automatic pre-switch, then the 10:28 Continue. Both errors in the photos are Muse's |
| Claude Opus 5.5 · GH Copilot Enterprise | fallback entry 2 ("Fallback 2") | Yes: usage read 52% used, under a 90% style threshold | **Never**: nothing moves the thread off Muse |
| Gemini CLI | in picker (1 model); not seen in the order | Probably not: earlier today the 1362 investigation found Gemini CLI on m3 rejected its own sign-in after Google login (an auth failure, not quota). Separately, `isGeminiSpendProvider` keeps Gemini out of every automatic step except a named order entry | No |
| Devin | not on M3 (absent from picker) | n/a on M3. On m4 and linux-mini, `acpRegistry_devin` models are listed as `heldModels` (I didn't verify the reason), so only a named entry could take a thread | No |
| Codex, Claude Code (other models), GitHub Copilot (personal) | in picker; Codex and Claude carry red dots | Unknown from the photos: no order position shown. The red dots likely mean limit or attention | No |

## Why the next entry is never reached (code at v1.0.404)

`apps/server/src/orchestration-v2/ProviderFallbackWorker.ts` moves a thread in three cases. `providerFallbackCommand` has the first two:

1. `thread.status === "failed" && thread.lastErrorClass === "usage_limit"`: continue on the next order entry (`message.dispatch`, "Continue where you left off.").
2. `shouldSwitchBeforeTurn`: the current provider's usage reading is at or over the threshold. This is how Opus moved to Muse.

3. The "target that cannot open" path (`unopenableFallback.ts`; its test reads "moves on to the next provider and keeps everyone off the broken one"). It fires only when `isOpenFailure` (`providerOpenFailure.ts`) sees code `provider_unavailable` or `provider_open_failed`, or a null code with the legacy message "Failed to open … provider session".

Muse on M3 meets none of them. The photo's message is the generic "sent no details" text, which is neither an open-failure code nor the legacy message. Its failure class is `provider_error`, and the generic ACP adapter that runs Muse never emits `usage_limit`. With no usage reading, trigger 2 can never fire. Continue starts a new turn on the thread's saved model, so it retries Muse. No failure count or hold marks Muse as broken for this stop.

## Synthetic check (no paid calls, no settings changes)

A focused unit test called `providerFallbackCommand` with M3's shape. Providers: Claude at 95%, Muse signed in with no usage reading, Copilot Enterprise at 52%. Order: [Muse, Copilot Enterprise Opus 5.5]. It ran in a git-ignored folder of an existing M5 scratch checkout, whose fallback files are identical to v1.0.404. All 4 cases passed:

| Case | Result |
|---|---|
| 1. Opus idle at 95% | `thread.model-selection.set` → `muse / muse-wonder-1.0` (matches the M3 switch) |
| 2. On Muse, failed `provider_error` | `null`: no move (matches M3) |
| 3. On Muse, idle after the failure | `null`: no usage reading, no pre-switch |
| 4. On Muse, failed `usage_limit` | `message.dispatch` → `acpRegistry_github_copilot_2 / claude-opus-5.5`, "Continue where you left off." |

Case 4 shows the chain works once the failure is classed as a limit. Copilot Enterprise is reachable; the trigger is what's missing. The test used an explicit fallback list, so cases 1 and 4 illustrate the mechanism rather than M3's exact configuration. Cases 2 and 3 hold for any configuration. Test source, config and output: `~/.specwithcode/m5/scratch/2026-11-20-m3-fallback/m3Fallback.test.ts`, `~/.specwithcode/m5/scratch/2026-11-20-m3-fallback/vite.config.ts`, `~/.specwithcode/m5/scratch/2026-11-20-m3-fallback/result.txt`. To rerun: copy the test and config into `<checkout>/.artifacts/m3-fallback/` (git-ignored), then from the checkout run `ROOT=$PWD node node_modules/vite-plus/bin/vp test run --config .artifacts/m3-fallback/vite.config.ts --root $PWD`.

## Quota versus auth versus generic errors

- **Copilot Enterprise on M3:** the photo shows a quota reading (48% left, resets in 10 days 8 hours), so it is signed in and has room. "Billing not reported" means only that the billing tier is unknown. M5 cannot read M3's Copilot account identity.
- **Muse:** no quota signal and no auth signal reach the app, only the generic error. Muse stays "signed in", so the app has nothing that would mark it unusable. Whether Muse is out of quota or its sign-in is broken can only be seen in Muse Code itself.
- **Gemini:** never an automatic target unless named in the fallback order (deliberate spend guard).
- **Devin:** not set up on M3.

## Practical next step

1. **On M3 now:** press **Switch model** on the error card and pick Claude Opus 5.5 under GH Copilot Enterprise. Or, in Fallback order, move Copilot Enterprise Opus 5.5 above Muse, or remove Muse until it works. This changes M3's own settings, so it is Anton's call. I did not change anything.
2. **On M3:** open Muse Code's own account or usage page to see whether it is out of quota or signed out. The same failure has been seen on M5 since November 18.
3. **Product fix:** Anton already decided this today (`decision_model_tracks` revision 12, November 20, 15:12): "A provider turn that ends with no work, class `provider_error` or `unknown`, and a session id that still contains `native-thread:pending`, counts as a session that never opened. The second such failure on the same instance can move the thread when switching is on." It isn't in 1.0.404 or on `origin/main`, and no increment covers it. M5's identical Muse failures do carry a `native-thread:pending` provider thread id, so the rule would cover them. M3's ids are unverified. Plan it as an increment that extends `isOpenFailure` and the unopenable path. Beyond that rule: while a thread is on a fallback, treat a failure with no output from the fallback (`provider_error` or `unknown`, no tokens produced, or 2 such in a row) as a stop. Continue on the next order entry, and mark the failed entry tried for this stop (`excludedSelections`). Make Continue on such a thread advance instead of retrying the same broken fallback. Teach the Muse/ACP adapter to recognise usage-limit errors.
