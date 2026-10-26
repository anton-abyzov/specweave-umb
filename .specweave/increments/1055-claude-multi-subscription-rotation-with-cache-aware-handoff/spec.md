# Claude multi-subscription rotation with cache-aware handoff

## Problem

On October 24, 2026, Anton asked that switching between two or three Claude subscriptions on one machine, for example after a 5-hour limit, use the prompt cache sensibly and hand off automatically, "so that it works perfectly fine and it saves the state, the token, and the context usage". His Claude CLI diagnostics showed: 5-hour window 84% used, weekly 31%, Fable 5%. Over the local 24 hours, 93% of usage came with 4+ parallel sessions, 91% was subagent-heavy and 62% ran above 150k context. These overlap and are not additive causes. Screenshot: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-62a71dbf-0261-4c6f-8744-26377cf97a9a.png`.

Research, measurements and sources: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1055-claude-multi-subscription-rotation-with-cache-aware-handoff/reports/research.md`. Code audit with citations: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1055-claude-multi-subscription-rotation-with-cache-aware-handoff/reports/code-audit.md`.

1. **A switch can never reuse another account's cache.** Caches are isolated per organization and, in Claude Code, per machine and directory. The first turn on an account that has not served this prefix within its TTL re-writes the whole prefix. Main conversations get a 1-hour TTL, subagents and compaction 5 minutes.
2. **The measured cost is the lapsed TTL, not the account.** In the October 23–24 switch, all 27 sessions active before and after had been idle at least 4,999 s while limit-parked. Their first requests re-wrote 5.11M tokens (median prompt 184k; only about 15.9k was warm). Over 7 days, cold misses re-wrote 171.8M tokens: 321 main-conversation misses after the 1-hour TTL lapsed and 429 subagent misses after the 5-minute TTL lapsed.
3. **No policy joins the pieces.** On `origin/main`, occupancy (`tokenUsage.usedTokens`, `autoCompactThreshold`) and quota (`usageLimits`, 95% switch default) are both measured. Nothing does any of the following:
   - checkpoint or compact before a switch;
   - compare a cold native resume with a fresh session from a checkpoint;
   - charge the cold write to the target's quota;
   - guard against two homes signed in to one account;
   - cap concurrency per account.

   Usage reads are per instance, and M4 rotates by re-login in one home (`claudeAgent`, 2,937 runs), so identity changes under the same instance id. No turn records its account.
4. **Mixed chains lose the target's own session.** In Claude A → Codex → Claude C → Claude A, A resumes C's copied session (which started from a summary), not A's own native session.
5. **Policy risk.** "Advertised usage limits for Pro and Max plans assume ordinary, individual usage". The Consumer Terms forbid "bypassing any of our systems or protective measures". No official source allows or forbids rotating subscriptions.

## Scope

In (app repo `anton-abyzov/specwithcode-dev`, after 1047 #673, 1048 #678, 1052 #672 and 1053 merge):

- An account fingerprint and a switch marker on every Claude run and turn, plus a cold-prefix measurement.
- Identity-scoped usage reads that survive a restart, with fresh eligibility and a same-account guard.
- An evidence-based continuity policy at a switch: resume warm, compact or checkpoint first, start fresh from a checkpoint, or resume cold. It replaces any fixed 95% context rule.
- Planned switches: checkpoint and warm compaction before quota runs out.
- A concurrency governor per account when quota is tight.
- An optional automatic rotation among authorized subscriptions, behind an explicit setting with consent, off by default.
- Exactly-once reconciliation for A→B→C→A, including mixed chains.
- Subagent settle or resume without duplicate tools, reusing 1053.
- Fault and identity-switch tests, measurement, and a runtime receipt.

Out:

- The usage meter and picker display (1054 owns it; 1055 only exposes data).
- Limit fallback ordering and exclusions (0955 and 1052), except adding the cost and identity inputs.
- Machine handoff transport, checkpoint seed and lease (0967 and 0968). Across machines the policy always picks a fresh session from the checkpoint.
- Account-change detection and early resume (1047).
- Changing logins, reading credentials beyond the identity fields the login watcher already reads, API-credit or Vertex/Gemini spend, and any promise of cache savings that is not measured.
- Changing the subagent cache TTL. Measured: a 1-hour subagent TTL costs more than it saves (research §1, finding 3).

## Acceptance Criteria

- [ ] AC-01: Each Claude run and turn records a salted account fingerprint, derived server-side from the identity fields the login watcher already reads (never an email or token in the projection). It also records a switch cause: `none`, `relogin`, `instance`, `model`, `ttl_lapsed`, `compaction` or `fresh_session`. The first turn after a switch records `coldPrefixTokens` (cache creation on its first request) and `warmPrefixTokens`. Aggregates are queryable through `specweave-studio db query`. A test covers relogin in one home, two homes, and a restart in between.
- [ ] AC-02: Usage reads are keyed by account fingerprint, not instance. A re-login under the same instance never inherits the previous account's windows. The last read per account persists across a restart, so 1047's account change is still detected after one. Rotation eligibility needs a complete read for that account at most 5 minutes old, with no denial after the read. Two instances on the same account count as one pool: the planner never "rotates" to the same account. Unknown or stale counts as ineligible.
- [ ] AC-03: A pure `switchContinuityPolicy` returns one of `resume_warm`, `compact_then_switch`, `fresh_from_checkpoint` or `resume_cold`, with its reason and estimate. Inputs:
  - prefix tokens P, from the last `tokenUsage`;
  - the last request time of this provider thread on the target account;
  - the TTL in force (1 hour main, 5 minutes subagent, 5 minutes on usage credits);
  - checkpoint size K;
  - the target account's fresh room;
  - model identity (a model change is always cold).

  Its weights are configuration seeded from the documented API ratios and replaced by AC-09's calibration. No fixed percentage of the context window triggers it. Table tests cover every branch, including "target served this prefix within TTL → resume_warm" and "P ≥ 100k, cold target → fresh_from_checkpoint, unless the user pinned native resume".
- [ ] AC-04: When the policy picks `compact_then_switch` or `fresh_from_checkpoint`, a structured checkpoint is written before the switch. It holds the increment, task, ACs, branch and head, next action, evidence paths, the side-effect journal (never replayed) and native transcript pointers. Compaction runs on the current account only while its cache is warm and its quota has room. Otherwise the checkpoint alone is used. A compaction that would land on a spent account is never sent.
- [ ] AC-05: Planned switch. When an account's fullest applicable window crosses the user's switch threshold (`providerLimitSwitchAtPercent`, default unchanged) and before it is exhausted, idle Claude threads on that account above `IDLE_COMPACT_MIN_TOKENS` are checkpointed and, by policy, warm-compacted. They go one at a time, within the existing idle-compaction concurrency. Limit-parked threads are covered too: a test proves H1 one way or the other (does `ClaudeIdleCompactionReactor` skip them today?) and the fix where it does.
- [ ] AC-06: Concurrency governor. While an account's 5-hour window is at or above a configurable tight level, with its reset more than `providerLimitWaitUnderMinutes` away, new Claude starts on that account follow these rules:
  - capped per account (default from AC-09's data, initially 2 concurrent runs);
  - automatic starts (delegated, scheduled, PR-watch) queue first;
  - a person's send is never blocked, only told;
  - resumes keep 1047's 5-second spacing.

  The cap lifts when a fresh read shows room. Tests cover cap, lift, person priority and restart.
- [ ] AC-07: Optional automatic rotation. A setting "Rotate between my Claude subscriptions automatically" is off by default. Turning it on shows a consent dialog quoting the "ordinary, individual usage" and "bypassing ... protective measures" texts with their links, and records who agreed and when. Only instances the user marked authorized for rotation are candidates. The target is chosen by fresh room first, then cache warmth, then fallback order. With the setting off, behaviour is unchanged: the existing fallback and 1047 rules apply, and the switch shows a one-click "Continue on <subscription>" instead.
- [ ] AC-08: Rotation keeps the boundaries:
  - a person's Stop is final and also disarms limit recovery on a limit-parked thread (fixes the probable gap in research §4);
  - per-token or API-billed Claude, Vertex and Gemini are never candidates;
  - pins, snooze, settle, paused or archived projects and machine-handoff holds are respected;
  - when the source and target instances resolve to different effective permission modes (`launchArgs` override), the switch is refused with a notice unless the user allowed it.
- [ ] AC-09: Measurement before claims. A runtime evidence task records, for at least 10 real switches or TTL-lapsed resumes across at least two accounts: `coldPrefixTokens`, `warmPrefixTokens`, policy choice, and the 5-hour `usedPercent` before and after the first turn. The calibration file reports the observed subscription cost of a cold write against a warm turn, with its uncertainty. The policy weights and the AC-06 default come from this file. UI copy and docs make no cache-savings claim beyond what it shows.
- [ ] AC-10: A→B→C→A reconciliation, exactly once.
  - Claude-only chain: one native session continues, with no handoff text.
  - Non-Claude B and C: A's own native session receives one `delta_since_target_last_seen` covering only B's and C's runs.
  - Mixed chain (Claude A → Codex B → Claude C → Claude A): A returns to its own native session with one delta covering B's and C's runs when the policy says `resume_warm` or `resume_cold`. Otherwise it gets a fresh session from the checkpoint. It never silently continues C's copy.

  No run is delivered twice, none is skipped, and the turn after a delivered delta carries none. Restart and failed-start cases keep 1048's rollback.
- [ ] AC-11: Subagents across a switch reuse 1053. Finished children are settled from receipts once. Unfinished native children are interrupted, with one note to the parent naming what to rerun. Delegated children keep running and stay linked. No tool call recorded in the side-effect journal is executed again by a resumed parent or replacement child. A fault test kills the process mid-child during a relogin and asserts zero duplicate tool executions.
- [ ] AC-12: Fault and identity-switch suite, model-free (orchestrator, workers and test adapters):
  - relogin mid-turn;
  - relogin while limit-parked;
  - two homes on one account;
  - A→B→C→A pure and mixed;
  - restart between hops;
  - stale and partial reads;
  - spent target;
  - permission mismatch;
  - Stop on a parked thread;
  - concurrency cap under tight quota;
  - rotation setting off and on.
- [ ] AC-13: A runtime receipt under `/Users/antonabyzov/.specwithcode/m4/evidence/claude-multi-subscription-1055/` records suites, counts, source head and the AC-09 calibration summary. Fresh-context review verdict SHIP.

## Approach

Paths are relative to the app repo and get replaced with the bound worktree path before tasks are claimed. Base: `origin/main` after #673, #678, #672 and the 1053 branch merge.

1. **Identity and markers (AC-01, AC-02).**
   - `apps/server/src/provider/loginWatch.ts` already reads `oauthAccount.{accountUuid, organizationUuid}`. Hash them with a per-install salt in `apps/server/src/provider/claudeAccountFingerprint.ts` (new).
   - Stamp the fingerprint on runs and turns from `ClaudeAdapterV2.ts` (`claudeProviderTurnTokenUsage`) into `turnTokenUsage`.
   - Key usage snapshots by fingerprint in `providerUsageLimits.ts`.
   - Persist the last read per fingerprint in server state (not the live DB from tools).
   - Same-account guard in `packages/shared/src/providerFallback.ts` `usable()`.
2. **Policy (AC-03).** `packages/shared/src/switchContinuityPolicy.ts` (new, pure), with weights in `packages/shared/src/switchContinuityWeights.ts`, calibrated later. Called from `ProviderSwitchService.ts` and `ProviderFallbackWorker.ts` before a switch, and from `Orchestrator.ts` dispatch on a return to a Claude home.
3. **Checkpoint and compaction (AC-04, AC-05).** Reuse 0967 `HandoffMode` checkpoints and the 1053 `ChildContinuationContext`/`ContextHandoffBudget`. Add `apps/server/src/orchestration-v2/PreSwitchCheckpoint.ts`. Extend `ClaudeIdleCompactionReactor.ts` with a quota-threshold trigger and the H1 fix. `compactThread` already exists.
4. **Governor (AC-06).** `apps/server/src/orchestration-v2/AccountConcurrencyGovernor.ts` (new), consulted by `startNextQueuedRun` and the delegated, scheduled and PR-watch start paths. Reuse 1047's `ACCOUNT_RESUME_SPACING_MS`.
5. **Rotation setting (AC-07, AC-08).**
   - `packages/contracts/src/settings.ts`: `claudeRotation.enabled`, `consentAt`, `authorizedInstanceIds`, `tightPercent`, `maxConcurrentPerAccount`.
   - Consent dialog and authorized toggles in the existing Usage limits settings panel, with headless checks.
   - Stop disarm in `Orchestrator.ts` `holdStoppedThread`.
   - Permission comparison through `RuntimePolicy.ts` plus the `launchArgs` resolution in `ClaudeAdapterV2.ts`.
6. **Reconciliation (AC-10).** `Orchestrator.ts` dispatch picks the target home's own root provider thread when the policy resumes. `canResumeAcrossInstances` copies only when the policy chooses the source's session.
7. **Measurement (AC-09).** A read-only script over `specweave-studio db query` aggregates plus usage-only transcript fields (pattern: `/Users/antonabyzov/.specwithcode/m4/scratch/1055-usage-scan/scan.py`). It writes the calibration JSON and markdown to the evidence folder.

Rejected:

- A fixed "switch at 95% context" rule. 95% is a quota setting, and Studio compacts at 400k, not near 1M.
- A 1-hour TTL for subagents (measured net loss).
- Moving native transcripts across machines (the cache is per machine anyway; 0967 owns transport).
- Automatic rotation on by default (policy risk, finding 5).

Risks:

- The transcript format is internal and unstable; use only usage fields, behind a version check.
- The subscription weighting of cache tokens is unverified, so AC-09 gates all claims.
- 1047, 1048 and 1053 are unmerged; rebase cost.
- Terms risk of rotation stays with the user's consent.

## Decisions

### Asked
- none (research and planning lane; no user questions were asked from it)
### Defaulted (change any before sw-do)
- D-02 Account identity is a salted hash of `accountUuid` and `organizationUuid` from fields the login watcher already reads. No email in projections or logs.
- D-03 Cache-savings numbers in UI or docs appear only after AC-09's calibration. Until then the policy uses documented API ratios internally and says "estimate".
- D-04 Across machines the policy always picks `fresh_from_checkpoint`; the 0967 seed and transport are unchanged.
- D-05 The subagent TTL stays at Claude Code's default (5 minutes); measured net loss otherwise.
- D-06 Usage meter display of switch cost or account belongs to 1054; 1055 only exposes fields.
- D-07 A person's send is never blocked by the governor; it only shows that the account is tight.
- D-08 (October 25, 2026) AC-01 and AC-02 build on the opaque `usageLimits.accountKey` and the persisted limit-stop key from the auth-recovery owner's branch `feat/subscription-change-recovery` (1063/1067 lane) once it merges, and do not add a second fingerprint. 1055 adds only what that branch leaves out: the key on each turn, switch causes, cold-prefix fields, the same-account guard and per-account pooling.
### Open
- D-01 Ship automatic rotation among Claude subscriptions at all (AC-07)? Recommendation: build it behind the off-by-default setting with the Terms consent dialog, and make the cache-aware policy (AC-01..AC-06, AC-10, AC-11) apply to every switch regardless. Alternative: drop AC-07 and keep only manual "Continue on <subscription>". This is Anton's decision because of the policy risk in finding 5.

## Tasks

### T-01 Account fingerprint, switch markers and H1 check
- AC: AC-01, AC-02 | Files: apps/server/src/provider/claudeAccountFingerprint.ts, apps/server/src/provider/loginWatch.ts, apps/server/src/provider/providerUsageLimits.ts, apps/server/src/provider/ClaudeTurnTokenUsage.ts, apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, packages/contracts/src/providerRuntime.ts, packages/shared/src/providerFallback.ts | Test: vp test run apps/server/src/provider/claudeAccountFingerprint.test.ts apps/server/src/provider/providerUsageLimits.accountKey.test.ts packages/shared/src/providerFallback.sameAccount.test.ts

### T-02 Switch continuity policy
- AC: AC-03 | Files: packages/shared/src/switchContinuityPolicy.ts, packages/shared/src/switchContinuityWeights.ts | Test: vp test run packages/shared/src/switchContinuityPolicy.test.ts

### T-03 Pre-switch checkpoint, warm compaction and planned switch
- AC: AC-04, AC-05 | Files: apps/server/src/orchestration-v2/PreSwitchCheckpoint.ts, apps/server/src/orchestration-v2/ClaudeIdleCompactionReactor.ts, apps/server/src/orchestration-v2/ProviderSwitchService.ts, apps/server/src/orchestration-v2/ProviderFallbackWorker.ts | Test: vp test run apps/server/src/orchestration-v2/PreSwitchCheckpoint.test.ts apps/server/src/orchestration-v2/ClaudeIdleCompactionReactor.limitParked.test.ts

### T-04 Concurrency governor under tight quota
- AC: AC-06 | Files: apps/server/src/orchestration-v2/AccountConcurrencyGovernor.ts, apps/server/src/orchestration-v2/Orchestrator.ts | Test: vp test run apps/server/src/orchestration-v2/AccountConcurrencyGovernor.test.ts

### T-05 Optional rotation setting, consent and boundaries
- AC: AC-07, AC-08 | Files: packages/contracts/src/settings.ts, apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/RuntimePolicy.ts, apps/web/src/components/settings/ (Usage limits panel), apps/web/tests/claude-rotation/verify.mjs | Test: vp test run apps/server/src/orchestration-v2/ClaudeRotation.test.ts apps/server/src/orchestration-v2/Orchestrator.stopDisarmsLimit.test.ts; headless consent and settings checks at 390 and 1280 px, light and dark (headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never, reporters open never)

### T-06 A→B→C→A reconciliation including mixed chains
- AC: AC-10 | Files: apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/ProviderSessionManager.ts, apps/server/src/orchestration-v2/testkit/ProviderSwitch.integration.test.ts | Test: vp test run apps/server/src/orchestration-v2/testkit/ProviderSwitch.integration.test.ts

### T-07 Subagents across a subscription switch (reuse 1053)
- AC: AC-11 | Files: apps/server/src/orchestration-v2/SubagentSettlement.ts, apps/server/src/orchestration-v2/ChildContinuationContext.ts, apps/server/src/orchestration-v2/testkit/SubagentRelogin.fault.test.ts | Test: vp test run apps/server/src/orchestration-v2/testkit/SubagentRelogin.fault.test.ts

### T-08 Fault and identity-switch suite
- AC: AC-12 | Files: apps/server/src/orchestration-v2/testkit/ClaudeRotation.fault.test.ts | Test: vp test run apps/server/src/orchestration-v2/testkit/ClaudeRotation.fault.test.ts

### T-09 Measurement, calibration and runtime evidence
- AC: AC-09, AC-13 | Files: scripts/measure/claude-switch-cost.mjs, /Users/antonabyzov/.specwithcode/m4/evidence/claude-multi-subscription-1055/calibration.json, /Users/antonabyzov/.specwithcode/m4/evidence/claude-multi-subscription-1055/runtime-receipt.json | Test: node scripts/measure/claude-switch-cost.mjs --check /Users/antonabyzov/.specwithcode/m4/evidence/claude-multi-subscription-1055/calibration.json (at least 10 switches, two accounts)

### T-10 Verify and close 1055
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1055-claude-multi-subscription-rotation-with-cache-aware-handoff/ledger.jsonl | Test: specweave verify 1055; fresh-context review verdict SHIP; specweave complete 1055
