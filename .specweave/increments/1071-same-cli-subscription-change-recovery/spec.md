# Recover limit-held threads when the same CLI changes subscription

## Problem

On October 25, 2026, around 1:01 AM EDT, the specweave thread "Fix IDE zoom sh..." (PR #696) hit "You've hit your session limit · resets 2:50am". Anton then signed in to another Claude subscription in the same Claude Code CLI. The composer meter showed the new subscription (Opus 5.5, 99%), but the thread kept "Usage limit reached. Resets in 1 h 46 min (2:50 AM)" and waited for the old account's reset. Screenshots: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-6bb42e49-82fa-4848-adee-7142ce45b861.png` and `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-26d46d08-0318-4819-a914-11b173faf68d.png`.

Anton, verbatim: "When I see this message, then I go to my CLI console and I change from one subscription to another, meaning that we keep the same code harness, but just the subscription changed. It must be smart enough to do something with it, recognize this subscription, and maybe monitor this under the hood. I don't know how often, maybe every 1 or 2 minutes. It must then be able to switch to the subscription if a user confirms this. Probably there should be a message: 'Okay, we've identified that there was a switch of subscription. I do confirm this.' There must be a setting, of course, in the project setting: 'Do you want to automatically approve this or not?' I would keep this as true".

Cause:

1. Installed M4 is 1.0.76, source `4446ca4295`. It has none of 1047's account-change resume (#673, `aa9f2be63d`) and no Codex relogin restart (#689, `7c79180ee5`). Both shipped in 1.0.77 (tag `828a758d42`, published 05:00 UTC October 25), which is not installed yet. On 1.0.76 a Claude limit stop resumes only at the old account's reported reset.
2. 1047 on `origin/main` `bf8abcfca9` still misses the cases Anton describes:
   - Identity is the signed-in email only (`makeManagedServerProvider.ts` `loginEmail`). Two subscriptions on one email (another organization or plan) look like the same account.
   - The last account lives in server memory only, and the first read after a start sets nothing. A relogin that a restart, such as installing 1.0.77, follows is never detected.
   - Codex is excluded. The sweep runs `accountChange` only for non-Codex threads (`UsageLimitRecoveryWorker.ts`, `checked.codex ? null : ...`). A Codex pool change makes `UsageLimitAvailability` observe `changed`, which blocks every early resume. The running shared app-server also keeps the old sign-in until #689 sees a failed turn.
   - The account read is refreshed only when it is older than 5 minutes (`LIMIT_CHECK_INTERVAL_MS`), and the provider probe runs every 5 minutes (`DEFAULT_PROVIDER_HEALTH_REFRESH_INTERVAL`). A sign-in that does not touch the watched login file waits up to 10 minutes.
   - There is no way to require a confirmation. The early resume follows auto-continue only.

## Scope

In (app repo `anton-abyzov/specwithcode-dev`, branch `feat/subscription-change-recovery` from `origin/main` `bf8abcfca9`):
- An opaque account key per subscription for Claude and Codex, read through the provider's own status paths (Claude Agent SDK `initialize` account, Codex `account/rateLimits` account id).
- Change detection by key that survives a restart.
- Bounded monitoring while a limit-held thread exists.
- The `autoApproveSubscriptionChange` project setting (default on) and the confirmation notice.
- Codex support, including a safe replacement of the shared runtime.
- Tests, a headless UI fixture, delivery through the release owner, and installed verification.

Out:
- Changing provider or model.
- API keys, API credits or any paid spend.
- Switching logins for the user.
- Reading credential files beyond what the existing login watcher reads.
- Automatic rotation between subscriptions and cache-aware checkpoints (1055).
- The usage meter display (1054).

## Acceptance Criteria

- [ ] AC-01: Subscription key. A complete usage read on a subscription sign-in publishes `usageLimits.subscriptionKey`:
  - Claude: `claude:sha256:<64 hex>` of the lowercased email, organization and plan from the SDK `initialize` account.
  - Codex: the existing `quotaPoolId`, a hash of the ChatGPT account id.

  API-key billing, Claude Console, third-party backends, a failed read and a read with no email publish no key ("unknown"). No email, organization name or token is persisted.
- [ ] AC-02: Change detection. The server compares keys, and emails only when either key is unknown. A change sets `accountChangedAt` to the read that first saw the new identity. An unknown read in between never counts as a change, and returning to the same identity keeps the earlier stamp. The last identity and its stamp are stored per instance as a hash in `<providerStatusCacheDir>/<instanceId>.account.json`. After a restart, the first read compares against the stored identity, so a relogin before or during a restart is detected. Tests cover A→B, A→unknown→A, A→unknown→B, restart between A and B, same email with another organization, and API key added.
- [ ] AC-03: Bounded monitoring. While at least one thread on an instance is limit-held (`isLimitRecoveryCandidate`, recovery armed or confirmation pending), the sweep refreshes that instance's read at most once every 2 minutes (`SUBSCRIPTION_CHECK_INTERVAL_MS`). With no held thread there is no extra refresh. The login-file watcher still refreshes at once. A refresh never runs under the thread or project lock, and a refresh failure changes nothing.
- [ ] AC-04: Auto-approve setting. `autoApproveSubscriptionChange` is a project-scoped server setting, default `true`, with a switch "Continue on a new subscription automatically" in Settings → Providers → usage limits and a "This project" override row. On: an account-change resume is sent exactly once, under the existing gates (auto-continue armed, no person snooze, not settled, no blocking request, no machine hold, project not paused or archived, same instance), with the 5-second per-instance spacing. Off: no automatic resume. The notice asks for confirmation instead.
- [ ] AC-05: Confirmation notice. When the stop ended before `accountChangedAt` and the new subscription has room, the limit notice is replaced. The title is "<Provider> subscription changed". The body reads "We detected a sign-in to another subscription in the same <Provider> CLI. The limit was on the previous one, and the new one has room." Below it:
  - with auto-approve on and recovery armed: "This thread continues on the new subscription shortly.";
  - otherwise, a "Confirm and continue" button that sends one continuation and shows a failure inline (`role="alert"`).

  The notice never mentions API keys, billing, cache or switching models. Headless screenshots at 360 and 1280 px in light and dark cover both states.
- [ ] AC-06: Codex. An account-change resume works for a Codex stop:
  - An `availability` of `changed` no longer blocks it.
  - The orchestrator accepts the `:acct:` mark for Codex as for Claude.
  - The Codex runtime records the account key it opened with. When the instance's key has moved, the session manager replaces the runtime on the next open once no turn or background work runs on it. While it is busy, it keeps serving its turns without failing them.
  - The worker holds a Codex account-change resume while its instance has a runtime waiting for replacement, so the resume never runs on the old sign-in.
- [ ] AC-07: Exactly once and Stop intent. A restart, repeated sweeps or a confirmation click racing the automatic resume produce one continuation run (`limit-resume:...:acct:<changedMs>:...` command id, stable across restarts because `accountChangedAt` is persisted). A stopped (interrupted), settled, person-snoozed or archived thread never resumes. A→B→A (back to the spent account) does not resume early while its read shows no room.
- [ ] AC-08: Delivery. Focused server, contracts, shared and web tests pass, typecheck passes, and a fresh-context review returns SHIP. The PR merges green into main. The release owner ships it, and the installed M4 build is read back with version and source commit.

## Approach

Server (`apps/server/src`):
- `provider/subscriptionIdentity.ts` (new) hashes the SDK account (`claudeSubscriptionKey`) and reads Codex's `quotaPoolId` (`subscriptionKeyOf`). `ClaudeProvider.ts` attaches `subscriptionKey` to the usage it publishes.
- `provider/makeManagedServerProvider.ts` tracks `accountIdentity` (key or hashed email) and `accountChangedAt`, loading them from and saving them to an optional `subscriptionMemory` input. `makeSubscriptionMemory` in `provider/subscriptionIdentity.ts` is the file store. `Drivers/ClaudeDriver.ts` and `Drivers/CodexDriver.ts` pass it in.
- `orchestration-v2/UsageLimitRecoveryWorker.ts`:
  - per-instance 2-minute refresh;
  - Codex account change;
  - the `autoApproveSubscriptionChange` gate;
  - a hold while the Codex runtime awaits replacement.

  `usageLimitRecovery.ts` relaxes the `availability` block for a proven account change. `Orchestrator.ts` makes the same relaxation in `limitRecoveryResumeAllowed`.
- `Adapters/CodexAdapterV2.ts` adds `replaceWhenIdle` from the opening account key. `ProviderAdapter.ts` adds the optional field. `ProviderSessionManager.ts` replaces the runtime when idle and exposes `replacementPending(instanceId)`.

Contracts and shared: `providerUsageLimits.ts` `subscriptionKey`; `settings.ts` `autoApproveSubscriptionChange`.

Web:
- `components/chat/AccountChangedBanner.tsx`: copy, the Codex driver, and the setting-aware `accountChangeAutoContinues`.
- `components/ChatView.tsx`: pass the setting.
- `components/settings/ProviderLimitSettings.tsx` and `projectOverrideRows.ts`: the switch.
- `apps/web/tests/composer-stack/verify.mjs (account, account-manual cases)`: headless fixture.

## Decisions

### Asked
- D-01: Auto-approve a detected subscription change → yes by default, as a project setting (Anton, October 25, 2026).
### Defaulted (change any before sw-do)
- D-02: Monitoring cadence is 2 minutes per instance, only while a thread is limit-held. The login watcher stays instant. An agent schedule is never used.
- D-03: Identity is an opaque hash of what the provider's own status reports (email + organization + plan for Claude, account id for Codex). Plan changes count as a subscription change. The room check keeps a stale or wrong key from resuming onto a spent account.
- D-04: With auto-approve on, the early resume still needs the thread's auto-continue arm (1047 D-02). A thread with auto-continue off shows "Confirm and continue".
- D-05: Claude needs no runtime replacement, because each Claude turn reads the CLI's current sign-in (1047 evidence, October 24 recovery of 9 threads). Only Codex keeps a long-lived shared process.
- D-06: The notice says "subscription", never "account switch to another provider". It offers no API-key path.
### Open
- none

## Tasks

### T-01 Account key and persisted change detection
- AC: AC-01, AC-02 | Files: apps/server/src/provider/subscriptionIdentity.ts, apps/server/src/provider/ClaudeProvider.ts, apps/server/src/provider/makeManagedServerProvider.ts, apps/server/src/provider/Drivers/ClaudeDriver.ts, apps/server/src/provider/Drivers/CodexDriver.ts, packages/contracts/src/providerUsageLimits.ts | Test: vp test run apps/server/src/provider/makeManagedServerProvider.test.ts apps/server/src/provider/subscriptionIdentity.test.ts

### T-02 Bounded monitoring, setting gate and Codex resume in recovery
- AC: AC-03, AC-04, AC-06, AC-07 | Files: apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.ts, apps/server/src/orchestration-v2/usageLimitRecovery.ts, apps/server/src/orchestration-v2/Orchestrator.ts, packages/contracts/src/settings.ts | Test: vp test run apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.subscriptionChange.test.ts

### T-03 Codex runtime replacement when idle
- AC: AC-06 | Files: apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, apps/server/src/orchestration-v2/ProviderAdapter.ts, apps/server/src/orchestration-v2/ProviderSessionManager.ts | Test: vp test run apps/server/src/orchestration-v2/ProviderSessionManager.test.ts

### T-04 Confirmation notice and setting UI
- AC: AC-04, AC-05 | Files: apps/web/src/components/chat/AccountChangedBanner.tsx, apps/web/src/components/ChatView.tsx, apps/web/src/components/settings/ProviderLimitSettings.tsx, apps/web/src/components/settings/projectOverrideRows.ts, apps/web/tests/composer-stack/verify.mjs (account, account-manual cases) | Test: vp test run apps/web/src/components/chat/AccountChangedBanner.test.tsx; headless screenshots (headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never)

### T-05 Review, PR and delivery
- AC: AC-08 | Files: .specweave/increments/1071-same-cli-subscription-change-recovery/reports/ | Test: gh pr checks; fresh-context review SHIP; release owner readback

### T-06 Verify and close 1071
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: specweave verify 1071-same-cli-subscription-change-recovery

Implementation paths are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/.worktrees/failed-turn-recovery`.
