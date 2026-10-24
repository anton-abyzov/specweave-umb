# Resume limit-paused Claude threads after an account change

## Problem

Anton switched the Claude CLI login to another subscription on October 24, 2026, between 11:49 PM and 12:30 AM EDT. Threads stopped with "Claude usage limit reached" stayed stopped until coordinators sent them messages by hand. Root cause, with live evidence and a probe test: `/Users/antonabyzov/.specwithcode/m4/evidence/claude-account-switch-20261024/root-cause.md` (source `origin/main` `2e95e09ae3`, installed 1.0.75).

1. A Claude stop with a reported reset resumes only when the clock reaches that reset, here the old account's 06:50 UTC. The only early path, `hasFreshLimitPermission`, needs a Codex `quotaPoolId` (`apps/server/src/orchestration-v2/usageLimitRecovery.ts:148`, `:204-236`; `UsageLimitRecoveryWorker.ts:101-103`; `Orchestrator.ts:480-483`).
2. The Claude login watcher only refreshes the usage meter (`apps/server/src/provider/Drivers/ClaudeDriver.ts:330-344`). Nothing stores which account a stop happened on, and recovery gets no signal.
3. PR-watch wakes and delegated results start turns on a limit-paused thread (`Orchestrator.ts:2747-2761`). They fail at the start gate and move the re-arm chain forward (`usageLimitRecovery.ts:107-119`). Four of them before the reset turn auto-resume off for good (`LIMIT_REARM_MAX = 3`).

Composer notices also overlap. The watcher card always sits in front, the limit card is collapsed to a 12px sliver behind it, and the watcher tucks 17px under the composer. Audit and screenshots: `/Users/antonabyzov/.specwithcode/m4/evidence/claude-account-switch-20261024/layout/composer-stack-audit.md`.

## Scope

In:
- Claude account identity on the usage snapshot.
- Early resume of eligible limit-paused threads when a fresh read on a different account shows room, with dedup and a stagger.
- Holding automatic wakes on a limit-paused thread.
- A truthful account-change notice with recovery actions.
- The composer notice stack: complete cards, no overlap, and an accessible overflow pill.

Out:
- 529 overload recovery (separate, waiting for approval).
- Changing a login, provider or identity.
- Reading credential files beyond the identity fields the login watcher already reads.
- Inferring approval for API billing.
- Prompt-cache guarantees.
- `#654` and `#662` scope.

## Acceptance Criteria

- [x] AC-01: An account change is detected and published. The managed provider remembers the last authenticated account email in server memory only. When a probe authenticates as a different email (a sign-out in between still counts), the published `usageLimits.accountChangedAt` is set to that probe's `checkedAt`; later reads on the same account carry it. The first read after start and signing back in to the same account set nothing. No new identity field leaves the server.
- [x] AC-02: An early resume happens once. A Claude stop armed for a later reset, followed by `accountChangedAt` after the stop and a complete read (`nativeAllowanceObservedAt`) at or after the change, at most 5 minutes old (`LIMIT_CHECK_INTERVAL_MS`; a staler read gets one refresh per interval), with no unavailable state and `limitReadShowsRoom` "room", produces exactly one `limit-resume:` command carrying `:acct:<changedMs>:` before the reset. It continues "Continue where you left off." in the same native session. A repeated sweep or a restart builds the same command id. The orchestrator accepts the mark only when `changedMs` is after the stopped run's `completedAt` and not in the future.
- [x] AC-03: Stale or partial reads change nothing. The same account, a change before the stop, no complete read, a complete read from before the change, a failed read, a new account that is also spent, or one that refused a turn gives no early resume. The thread keeps today's reset-time behaviour.
- [x] AC-04: Stop intent is kept. The early path goes through the same gates as the reset-time resume, so nothing resumes for auto-continue off, a person's snooze, a settled thread, a blocking request, a machine handoff hold, a paused or archived project, or a thread moved to another instance. Pins and the thread's selection are unchanged.
- [x] AC-05: Resumes are staggered. With several paused threads on one instance, at most one account-change resume is sent per instance every 5 seconds (`ACCOUNT_RESUME_SPACING_MS`), in sweep order. A thread that hits a new limit after its resume re-arms through the existing path.
- [x] AC-06: Wakes do not burn retries. An automatic delivery (notification, delegated result or scheduled task, including one a person scheduled) queued after the active run, on an idle thread whose limit stop has a future or unknown reset, is queued without a person-hold and does not start: `startNextQueuedRun` leaves the queue alone while the limit stop is the latest executed run. It keeps the `usage_limit` state and its arm, so it cannot add a failed run to the re-arm chain. It runs after the `limit-resume` continuation, a person's send or any later turn. Past the reset, a wake starts normally. (Changed from a held queue by review r1: a held wake could be stranded behind a later one.)
- [x] AC-07: The account-change notice is truthful. When the stopped run ended before `accountChangedAt` and a complete read of the new account shows room, the limit notice is replaced by "Claude account changed": "The limit was on the previous account. This thread continues on the new one shortly." when recovery is armed, or "The limit was on the previous account, and the new one has room." with a "Continue now" button that continues the thread and shows a failure inline with `role="alert"`. It never mentions cache, cost or billing, and it has an accessible close button ("Dismiss account change notice").
- [x] AC-08: Composer notices never overlap. The notices are complete floating cards in a column with a 6px gap, ordered urgent (account change, limit), then errors, warnings and running work. More than two fold behind a keyboard-reachable "N more notices" pill with `aria-expanded` and `aria-controls`, and Escape folds them back. The queue, approval and question drawers stay attached. Headless proof at 360, 800 and 1280 px in light and dark, including pending question + watcher + quota, shows 1px borders on all four sides, equal corners, no overlap, no horizontal overflow and 44px touch targets at 360.
- [x] AC-09: Review r1 fixes hold. A wake queued behind a limit is queued without a person-hold, so it runs after the resume and is never stranded behind a later wake. The "continues shortly" copy shows only for a Claude stop that is armed, auto-resuming, not settled and not snoozed. An account-change resume the orchestrator refuses never uses up the instance's 5-second slot. The `:acct:` mark is read only from a `limit-resume:` command id.
- [x] AC-10: A→B→A continuity. A thread on Claude that hits the limit, continues on Codex, and returns to Claude after the subscription changes resumes the same native Claude session. The return receives exactly one `delta_since_target_last_seen` handoff covering only the Codex runs. Runs already in the Claude session, including the limit stop, are not replayed, and the next Claude turn carries no handoff.
- [x] AC-11: A model-free runtime demonstration (orchestrator, worker and test adapters, no provider calls) writes a receipt under `/Users/antonabyzov/.specwithcode/m4/evidence/claude-account-switch-20261024/` that records the suites, counts and source head for AC-01..AC-10.

## Approach

Server (`apps/server/src`):
- `provider/makeManagedServerProvider.ts` tracks the authenticated email in its state and stamps `accountChangedAt` (`withAccountChange`); `provider/providerUsageLimits.ts` carries it across updates; `packages/contracts/src/providerUsageLimits.ts` adds the field.
- `orchestration-v2/usageLimitRecovery.ts` adds `accountChangeShowsRoom` and the `:acct:<ms>:` mark helpers.
- `UsageLimitRecoveryWorker.ts` passes the proven change into `limitRecoveryCommand`, refreshes a stale read through the shared refresh gate, and spaces account resumes per instance.
- `Orchestrator.ts` accepts the mark in `limitRecoveryResumeAllowed` and holds automatic deliveries behind a limit stop.

Web (`apps/web/src`):
- `components/chat/AccountChangedBanner.tsx` and its wiring in `components/ChatView.tsx`.
- `components/chat/ComposerBannerStack.tsx` floats notices as whole cards in severity order with the overflow pill; `ComposerBanner.tsx` drops the peek sliver; `ComposerSurface.tsx` boxes the composer under any banner surface.
- `apps/web/tests/composer-stack/` is the headless fixture and checker.
- `ChatComposer.tsx` is not touched, so `#662` does not conflict.

Delivery: this thread has no worktree binding. Code is written in a scratch export of `origin/main` under `/tmp` and reviewed in a fresh context. The reviewed patch goes to the bound delivery owner `mcp:0ccf0bb8-12f0-47d6-bea0-6586c83aa37d`. No merge, release or service restart from this lane.

## Decisions

### Asked
- D-01 Resume on an account change automatically → yes. Anton: "I believe we should be triggering", with a notice to the user.
### Defaulted (change any before sw-do)
- D-02 The early resume follows the existing auto-continue setting. With it off, the notice offers a one-click continue instead.
- D-03 Identity is the authenticated email the probe already reports, compared in server memory only. Nothing new is published except the change time.
- D-04 Stagger is one account resume per instance per 5 seconds, in sweep order.
- D-05 The notice names no plan and never promises cache reuse; a continued native session may or may not reuse cache on the new account.
- D-06 Subagent continuity across a limit stop belongs to 1048 AC-03 (the parent is told which subagents were stopped and reruns only the missing ones). 1047 adds no separate subagent logic.
- D-07 Detection stays the probe's authenticated email (D-03). The app never reads credential files and never switches to API billing on an account change.
- D-08 Source acceptance is proven by tests, three fresh reviews (r3 SHIP, r4 delta SHIP) and the model-free runtime receipt. Delivered as PR #673, green at head 2fcfce2fc2 (checks 40094957936, October 24, 2026; receipt /Users/antonabyzov/.specwithcode/m4/evidence/claude-account-switch-20261024/delivery-receipt-673.md). T-07 closes after #673 merges through the release owner ("Complete screenshot sessions", 1.0.77 candidate); installed acceptance is recorded then.
### Open
- none

## Tasks

### T-01 Account change on the Claude usage snapshot
- AC: AC-01 | Files: apps/server/src/provider/makeManagedServerProvider.ts, apps/server/src/provider/providerUsageLimits.ts, packages/contracts/src/providerUsageLimits.ts | Test: vp test run apps/server/src/provider/makeManagedServerProvider.test.ts

### T-02 Early resume on account room with dedup and stagger
- AC: AC-02, AC-03, AC-04, AC-05 | Files: apps/server/src/orchestration-v2/usageLimitRecovery.ts, apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.ts, apps/server/src/orchestration-v2/Orchestrator.ts | Test: vp test run apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.accountChange.test.ts apps/server/src/orchestration-v2/Orchestrator.accountChangeResume.test.ts

### T-03 Hold wakes on a limit-paused thread
- AC: AC-06 | Files: apps/server/src/orchestration-v2/Orchestrator.ts | Test: vp test run apps/server/src/orchestration-v2/Orchestrator.accountChangeResume.test.ts

### T-04 Account-change notice and composer notice stack
- AC: AC-07, AC-08 | Files: apps/web/src/components/chat/AccountChangedBanner.tsx, apps/web/src/components/chat/ComposerBannerStack.tsx, apps/web/src/components/chat/ComposerBanner.tsx, apps/web/src/components/chat/ComposerSurface.tsx, apps/web/src/components/ChatView.tsx, apps/web/tests/composer-stack/verify.mjs | Test: vp test run apps/web/src/components/chat/AccountChangedBanner.test.tsx apps/web/src/components/chat/ComposerBannerStack.test.tsx; headless 360/800/1280 light/dark with question + watcher + quota, headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never

### T-05 A→B→A continuity test and runtime receipt
- AC: AC-09, AC-10, AC-11 | Files: apps/server/src/orchestration-v2/testkit/ProviderSwitch.integration.test.ts, /Users/antonabyzov/.specwithcode/m4/evidence/claude-account-switch-20261024/runtime-receipt.json | Test: vp test run apps/server/src/orchestration-v2/testkit/ProviderSwitch.integration.test.ts apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.accountChange.test.ts apps/server/src/orchestration-v2/Orchestrator.accountChangeResume.test.ts apps/server/src/orchestration-v2/usageLimitRecovery.accountMark.test.ts

### T-06 Fresh review and routed delivery
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/claude-account-switch-20261024/ | Test: fresh-context review verdict SHIP; patch routed to mcp:0ccf0bb8-12f0-47d6-bea0-6586c83aa37d; no merge or release from this lane

### T-07 Verify and close 1047
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1047-claude-account-change-resume/ledger.jsonl | Test: specweave verify 1047; fresh-context review; specweave complete 1047

Implementation paths are relative to the app repository and are replaced with the bound worktree path before tasks are claimed.
