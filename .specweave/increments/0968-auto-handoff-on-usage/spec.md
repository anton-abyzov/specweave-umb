# Automatic handoff when a provider nears its usage limit

## Problem

0955 switches a thread to an ordered fallback model on the same machine when the provider hits its usage limit. The user wants the switch to happen earlier, at an adjustable threshold (default 95%), and to be able to continue on another machine, whose provider account may have room, so the thread can still finish.

## Scope

In: an adjustable threshold, fallback targets of the form "Machine · Provider · Model", usage shared across the fleet so targets can be judged, picking the first qualifying target, handing off through 0967 at a turn boundary or from the last checkpoint on a hard limit, and a thread notice.

Out: the handoff mechanism itself (0967), and buying more usage.

## Acceptance Criteria

- [ ] AC-01: Settings → Providers has "Switch at" with a default of 95% used (choices 50 to 95% used, shown as the share left, or Off), stored as providerLimitSwitchAtPercent (null is Off).
- [ ] AC-02: The ordered fallback list accepts "Machine · Provider · Model" targets as well as same-machine models.
- [ ] AC-03: Each machine shares its provider usage percent and account identity with paired machines in the logical project (no secrets, no tokens). A target is skipped when its usage is at or above the threshold, when it uses the same account as the current provider, or when its machine is offline.
- [ ] AC-04: When no machine target qualifies, a same-machine fallback model is used; when none qualifies either, the thread waits and says why.
- [ ] AC-05: At or above the threshold the switch happens at the next turn boundary (shouldSwitchBeforeTurn); on a hard limit mid-turn it continues from the last checkpoint.
- [ ] AC-06: The thread shows a notice, for example "Hit 95% of Claude on M4 · continued on Minis with Claude Opus 5.5", linking both threads.
- [ ] AC-07: Two-server test with stubbed usage proves threshold, skip rules, fallback and the notice.
- [ ] AC-08: Eligible capacity. Each machine shares, per provider instance, a non-secret account fingerprint (a sha256 of the driver and the account id, org or email, never a token), its usage percent, reset time, sign-in state and when it was read. A machine target is eligible only when its account pool differs from the exhausted one, its usage is below the threshold, its machine is online, the project's work grant allows it (project and sign-in), and the provider is signed in. Unknown usage is not eligible unless the policy "Use targets with unknown usage" is on.
- [ ] AC-09: Safe resume on the target. A limit-triggered machine handoff resumes only threads whose latest run is running or was stopped by the usage limit, as a fresh provider session on the target seeded from 0967's portable checkpoint (hidden ref, transcript delta, handoff note), never by live process migration. Completed, cancelled, user-stopped and user-failed runs are never restarted. One idempotency key per stopped run and 0967's lease epoch keep the source from running the turn again, so side effects are not repeated.
- [ ] AC-10: Explicit policy. The ordered fallback list is visible in Settings; a setting chooses "Same machine first" or "Other machine first"; when nothing qualifies the thread waits and names the reason per candidate, for example "Minis: same Claude account as M4", "M3: offline", "Minis: no work grant for EasyChamp", "Minis: Solo isn't linked there".
- [ ] AC-11: Per-thread errors. When files, secrets, grants or sign-in are missing on the target (0967's preflight), the thread stays on its source with the exact reason; nothing half-moves.
- [ ] AC-12: Fault tests in the two-server script: the limit hits mid-turn and then the source goes offline, the target goes offline during the resume, a same-account target is skipped, a stopped thread is never resumed, and no turn runs twice.

## Approach

Extend packages/shared/src/providerFallback.ts and apps/server/src/orchestration-v2/ProviderFallbackWorker.ts. Check first whether provider usage is already shared over the fleet; add a small usage summary to the fleet presence payload if not. Call 0967's Hand off to… API for machine targets.

## Decisions

### Asked

- None.

### Defaulted

- D-01: 95% default, adjustable, per the user.
- D-02: Same-account targets are skipped because they share the same limit.
- D-03: "Other machine first" is the default order, matching AC-04 (a same-machine fallback model is used when no machine target qualifies). Nothing leaves the machine until the user adds a machine target, because the machine target list starts empty.
- D-06: A machine target takes a thread only at a real boundary: when the thread's turn stops on the usage limit (resume from the checkpoint), or when the thread is idle at the threshold and its latest turn finished within the last 10 minutes (a move with no resume message, once per thread per usage window). Older idle threads move when their next turn stops on the limit. This avoids copying checkpoints for threads nobody returns to and stops idle threads from moving back and forth.
- D-07: An unknown account (no fingerprint) on the same driver as the exhausted provider counts like unknown usage; different drivers are always different pools. Usage older than 15 minutes counts as unknown. The fingerprint is "sha256:" plus the hex sha256 of "specwithcode-account-pool:v1:" and the pool key, which is "<driver>:<email>" when the provider reports an email, else "<driver>:pool:<quota pool id>"; no account id, org or token leaves the machine.
- D-08: A project that has no linked copy on the target machine reads "<machine>: <project> isn't linked there", separate from a linked project the work grant leaves out ("no work grant for <project>"), because the fixes differ (link the project, or widen the grant).
- D-04: Targets with unknown usage are not eligible by default (user, October 20, 2026).
- D-05: An older peer that does not report usage reads as unknown usage, not as room.

## Tasks

### T-01 Threshold setting
- AC: AC-01 | Files: providerFallback.ts, settings UI | Test: unit tests

### T-02 Machine targets in the fallback list
- AC: AC-02 | Files: contracts, settings UI | Test: unit tests

### T-03 Fleet usage summary
- AC: AC-03 | Files: fleet presence payload | Test: server tests

### T-04 Target selection and handoff
- AC: AC-04, AC-05 | Files: ProviderFallbackWorker.ts | Test: server tests

### T-05 Notice
- AC: AC-06 | Files: thread timeline | Test: component tests

### T-06 Two-server test
- AC: AC-07 | Files: verification script | Test: the script

### T-07 Account fingerprint and fleet usage share
- AC: AC-08 | Files: contracts orchestratorMcp.ts, OrchestratorMcpService capabilities, RemoteWorkers.ts | Test: unit and server tests

### T-08 Eligibility with per-candidate reasons and target order
- AC: AC-08, AC-10 | Files: packages/shared machine fallback module, settings contract and UI | Test: unit tests

### T-09 Safe resume and lease fence
- AC: AC-09 | Files: server machine limit handoff module, ProviderFallbackWorker.ts | Test: server tests

### T-10 Per-thread preflight errors
- AC: AC-11 | Files: server machine limit handoff module | Test: server tests

### T-11 Fault tests
- AC: AC-12 | Files: two-server verification script | Test: the script

### T-13 Verify recovery after the target reconnects
- AC: AC-12 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/0968-closure/scripts/studio-limit-handoff/verify.mjs | Test: two-server verification script with simulated usage and headless screenshots
- Review finding, October 22, 2026: #550 retries the pending takeover when the target returns. Require exactly one target continuation, no source retry, and preserve the offline hold checks. The previous assertion that the thread remains stuck is obsolete.

### T-14 Prove a running turn hits the limit
- AC: AC-09, AC-12 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/0968-closure/scripts/studio-limit-handoff/verify.mjs, /Users/antonabyzov/.specwithcode/m4/worktrees/0968-closure/scripts/studio-logical-projects/link-launch-agent.mjs | Test: two-server verification script with a model-free provider writing partial work before returning a usage-limit error
- Review finding, October 22, 2026: the existing simulation rejects the turn before a provider starts. Make the fixture execute a turn and preserve its partial output and file through the portable checkpoint before the source-offline fault. Never invoke a paid provider.

### T-12 Verify and close 0968
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
