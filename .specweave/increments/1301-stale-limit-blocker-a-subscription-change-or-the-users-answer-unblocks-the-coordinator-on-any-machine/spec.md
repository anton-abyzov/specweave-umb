# Stale limit blocker: a subscription change or the user's answer unblocks the coordinator on any machine

## Problem

Anton, November 11, 2026, with a screenshot of the fortnite-3js coordinator on linux-mini (the Minisforum): "Make sure that it's not staying as a blocked coordinator because we changed subscriptions in threads, and I believe they proceeded. For some reason, the coordinator stayed in blocked, so make sure we solve those situations properly."

What happened (times UTC, read from the threads on the Minisforum, `origin/main` at `c143906485`):

| Time | Event |
|---|---|
| 19:55:51 | The Fable build worker (Claude, `claude-fable-5-2`) fails: "You're out of usage credits." |
| 19:57:21 | The worker "reported back", which wakes the coordinator (Claude, `claude-opus-5-5`). Its run 8 is refused before the session opens: "Claude's weekly Fable limit is used up; it resets at 2026-11-13T02:00:00.000Z." |
| about 20:07 | Anton signs the Claude CLI on that machine into another subscription. He messages the worker by hand ("just continue on the same machine, i changed claude subscription") and it runs. |
| 20:08:25 | Anton presses "Retry last message" on the coordinator. It replays his original request, not the worker's wake. |
| 20:09:15 | The coordinator answers and ends with "**Blocker:** the weekly Fable 5.2 limit is used up and resets on November 13, 2026 at 02:00 UTC ... wait or move to another model?" The limit was already gone. |
| 20:43:15 | Anton replies "subscription is changed, just complete it". The Blocked state clears and the coordinator continues. |

Why, in the code:

1. **Nothing resumed after the account change.** `UsageLimitRecoveryWorker` resumes a limit-stopped thread on an account change only when the stop is armed with auto-continue (`autoResumeByDefault`, `UsageLimitRecoveryWorker.ts:53`). The project and the global setting were both off, so the worker took its "Nothing resumes by itself" branch (`:567-583`) and only refreshed the snapshot for a banner. That banner exists in thread chats only, not on the coordinator. The project setting `autoApproveSubscriptionChange` (default on, asked for on October 25, 2026) is read only after the stop is armed (`:643-648`).
2. **The wake was lost.** `LaunchedWorkerWake` sends "reported back" once. The run it started never opened a provider session, and a later resume says only "Continue where you left off." (`UsageLimitRecoveryWorker.ts:142`), so the coordinator never gets the worker's report.
3. **No agent is told the limit stopped applying.** The only limit text in the coordinator's context was the old run-8 error. Nothing in a resume or a turn says the account changed, so the model restated a dead limit as a blocker.
4. **A Blocked state clears only on a later message.** `shellReportedBlocker` (`ProjectionStore.ts:2018`) clears when a user-role message is newer than the report. An account change writes no thread event, so a thread blocked on a limit stays Blocked until someone writes to it. Anton's reply did clear it: that path works.

Also seen, not fixed here: the worker's Fable rejection fenced the whole Claude instance, so an Opus coordinator was refused for a Fable-only window (`Capacity.ts:640`, pinned as a stopgap by `ClaudeLimitReset.test.ts:310`).

## Scope

In: the server (`apps/server/src/orchestration-v2`), which runs on every machine, so a coordinator on Linux behaves like one on macOS. A limit-stopped thread continues by itself when its provider is signed in to another subscription with room. That resume carries the message the limit swallowed and says the limit no longer applies. A thread whose last report is blocked on a usage limit is continued once on the same event. Tests for each. In the web app, only what must stay true: the account-changed notice's "continues shortly" promise and the setting's description in the nine languages.

Out: scoping the Claude start gate to the model family (follow-up, see Problem). The coordinator's "Retry last message" replaying the original request instead of the wake. Relaying an account change between machines (each server watches its own CLIs). A note on messages the person types themselves. Mobile.

## Acceptance Criteria

- [ ] AC-01: A thread stopped on a usage limit, with auto-continue off for the project and globally, resumes by itself after its provider instance is signed in to another subscription and a full read of the new account shows room, when the project's `autoApproveSubscriptionChange` is on (the default). With that setting off nothing is armed or resumed. Such an arm resumes only while the change is still proven: if the new account fills up or the setting is turned off, the old reset passing resumes nothing.
- [ ] AC-02: That resume never overrides a person: a stop the person turned auto-continue off for, or stopped with Stop, is not armed, and a thread that moved off the stopped run's provider instance is not armed.
- [ ] AC-03: A resume sent because the account changed tells the agent, in the message it receives, that the usage limit no longer applies because the provider is signed in to another subscription with room, and not to wait for the old reset or report that limit as a blocker.
- [ ] AC-04: When the stopped run never reached the provider (refused before its session opened), the resume delivers that run's message text again, so a worker's "reported back" wake is not lost. A stopped run that did start gets no repeat of its message.
- [ ] AC-05: An idle thread whose last report names a usage limit as its blocker gets one server message when a provider instance on that machine changes to another subscription with room after the report. The message clears the Blocked state and starts a turn. It is sent once per thread and change, one message per changed instance and sweep with room proven again each time, not while a process of that instance still runs on the previous subscription, and never to a thread that is running, settled, archived, snoozed, waiting on a request, in a paused or archived project, or in a project with `autoApproveSubscriptionChange` off.
- [ ] AC-06: A blocker that does not name a usage limit is left alone by AC-05, and any later user-role message (the person's reply or a server continuation) clears a reported blocker.

## Approach

All server-side, so it holds on whichever machine runs the coordinator. New logic goes in a new module because `Orchestrator.ts` and `ProjectionStore.ts` are far over the 1,500-line limit; they get call sites only.

1. **`apps/server/src/orchestration-v2/limitLifted.ts`** (new, pure):
   - `accountChangeArmCommand(thread, changedMs)`: a policy arm `limit-arm:<thread>:<run>:<resetMs>:acct:<changedMs>` with `autoResume: true`, or null when the person owns the stop (a matching recovery with auto-continue off whose request id is not a `limit-arm:`), or the stop is already armed.
   - `accountChangeArmOf(requestId)`: the change time read back from that arm id.
   - `limitResumeText(...)`: the resume text with the "no longer applies" sentence and, for a run that never started, its message.
   - `blockerNamesUsageLimit(text)`: a closed match on usage-limit wording ("usage limit", "weekly limit", "limit is used up", "limit reached", "quota", "out of usage", "usage credits"; not "rate limit", which is usually an API's).
   - `limitBlockedContinuation(...)`: the `message.dispatch` for AC-05, id `limit-lifted:<thread>:<run>:<changedMs>`.
2. **`UsageLimitRecoveryWorker.ts`**: in the unarmed branch, an account change with room and `autoApproveSubscriptionChange` on sends the arm under the project admission lock, with the same project and instance checks the other arms use. The next sweep resumes through the existing armed path (`:acct:` mark, orchestrator checks unchanged). Before the per-thread loop, a scan compares each provider's `accountChangedAt` with the last one handled; a new change with room reads the shell snapshot once and sends AC-05's message to the threads that qualify.
3. **`Orchestrator.ts`** (`dispatchText`, about `:6184`): a limit-recovery resume whose command id or arm carries an account-change mark gets its text from `limitResumeText`.
4. **Web** (`apps/web`): `accountChangeAutoContinues` in `AccountChangedBanner.tsx` promises a continue for a stop the server arms itself (no recovery, or a rule's arm), and `limitSettings.subscription.description` says so in `en`, `de`, `es`, `fr`, `ja`, `ko`, `pt`, `ru`, `zh`.
5. Tests: `limitLifted.test.ts`, `UsageLimitRecoveryWorker.accountChange.test.ts` (the existing "auto-continue off arms nothing" case becomes the `autoApproveSubscriptionChange` off case, see D-01), a blocked-thread sweep test, an orchestrator resume-text test, and `ProjectionStore.reportedBlocker.test.ts` for a server-authored message.

Rejected: clearing Blocked without a message (the agent would still believe the limit holds, and the shell is derived from messages); a note injected into every turn from the provider registry (`ProviderTurnStartService.ts` joins notes in four places and has no registry); arming with auto-continue off to record the change (the same command id could never arm later).

Risks: D-01 changes a behavior a test pinned. A thread woken by AC-05 may answer that it is blocked on something else, which costs one turn. The AC-05 match is on model-written text; it is bounded by needing a real account change with room, a report older than the change and at most 7 days old, and one message per thread and change.

## Decisions

### Asked
- none (the owner's message and the October 25, 2026 request for `autoApproveSubscriptionChange`, default on, set the direction)

### Defaulted (change any before sw-do)
- D-01 A detected subscription change with room continues limit-stopped threads even when auto-continue at the reset is off, because signing in to another subscription is the person's own action and `autoApproveSubscriptionChange` (default on) is its switch. Turning that setting off restores "ask first". This replaces the pinned case "auto-continue off arms nothing and resumes nothing" for account changes only; a reset passing still resumes nothing with auto-continue off.
- D-02 AC-05 looks at every idle thread on the machine whose blocker names a usage limit, not only threads on the changed provider instance, because a coordinator reports its workers' limits. The message names the provider so the agent can tell whether it applies.

- D-04 From the review of the first head: the blocked-thread message names the provider that changed and leaves the agent to say if its limit was another one (D-02 stays); the wording match is closed to provider usage limits, so bare "quota", rate limits and size limits do not match; a failed send is tried three times.
- D-03 The code is read from `origin/main` of `anton-abyzov/specwithcode` and committed out of tree, because another session holds the shared checkout. Each task's Test runs in a plain export of the PR head at `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-11-stale-limit-blocker/app`; Files stay declared from the umbrella root.
- D-05 From the review of the second head: a blocked thread held for now (paused project, handoff in flight) is looked at again for up to five hours after the change; the message is decided under the settings snapshot and sent after it; an account-change arm that can no longer resume is taken back once the old reset passed, so the thread shows no resume that will not come; blocked-thread messages and armed resumes share one turn per instance every 5 s; the wording match works sentence by sentence and needs a spent or reset verb next to a provider or model name
- D-06 The review of the third head (`e33f694f`) said SHIP. Left as follow-ups, none of them a wrong resume: the taken-back arm is only reached when a resume is due, so a Codex stop without a permitted availability check, or a stop with no reset time and no room, can keep showing an armed resume; a blocked-thread message takes the instance's turn before an armed resume; the wording match still accepts a few sentences where the limit kind does not sit right before the word limit ("limit on file size", "max number of retries limit")

### Open
- none

## Tasks

### T-01 Pure rules for a lifted limit
- AC: AC-02, AC-03, AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/limitLifted.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/limitLifted.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProjectionStore.reportedBlocker.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-11-stale-limit-blocker/app/apps/server && PWDEBUG=0 CI=1 pnpm exec vp test run src/orchestration-v2/limitLifted.test.ts src/orchestration-v2/ProjectionStore.reportedBlocker.test.ts

### T-02 Account change arms and resumes a limit stop without auto-continue
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.accountChange.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/AccountChangedBanner.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/AccountChangedBanner.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/en.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/de.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/es.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/fr.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ja.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ko.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/pt.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ru.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/zh.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-11-stale-limit-blocker/app/apps/server && PWDEBUG=0 CI=1 pnpm exec vp test run src/orchestration-v2/UsageLimitRecoveryWorker && cd ../web && PWDEBUG=0 CI=1 pnpm exec vp test run src/components/chat/AccountChangedBanner.test.tsx

### T-03 The resume says the limit is gone and redelivers an undelivered message
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/Orchestrator.limitLiftedResume.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-11-stale-limit-blocker/app/apps/server && PWDEBUG=0 CI=1 pnpm exec vp test run src/orchestration-v2/Orchestrator.limitLiftedResume.test.ts src/orchestration-v2/limitLifted.test.ts

### T-04 A thread blocked on a limit report continues once on an account change
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.testkit.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.limitBlocked.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-11-stale-limit-blocker/app/apps/server && PWDEBUG=0 CI=1 pnpm exec vp test run src/orchestration-v2/UsageLimitRecoveryWorker.limitBlocked.test.ts

### T-05 Ship: PR, review on the exact head, required CI, merge, release request
- AC: AC-01, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/CHANGELOG.md | Test: test "$(gh pr view 160 --repo anton-abyzov/specwithcode --json state -q .state)" = MERGED

### T-06 Verify and close 1301
- AC: AC-01 | Files: .specweave/increments/1301-stale-limit-blocker-a-subscription-change-or-the-users-answer-unblocks-the-coordinator-on-any-machine/spec.md | Test: specweave verify 1301
