# Review: 1354 Coordinator context continuity across model switches (PR 521, round 3)
Verdict: ship · risk: medium · 6 runtime/contract files in delta a5abee45..23657666 · 2 findings (2 low)
Reviewer context: new session, Claude Opus 5.5 reviewing OpenAI-written code (GPT-6-Astra). Reviewed heads `6382a0967f6216be6869aeac32cc4c1f20b8efed` and final exact head `23657666cdd2c3dcf37722784e08fd36e847edfb`.

## Scope

Round 3 covers the round 2 high (hard eight-worker cap) fix in `6382a096`, plus the later test-only delta `6382a096..23657666`. Full PR diff `cb61c42b..23657666` was re-read for the changed selection, delivery, preparation and contract paths. No code was edited.

## Prior findings

- Round 1 high, lifecycle refs evicting first-user and latest assistant anchors: still fixed. Anchors are added before workers in `apps/server/src/orchestration-v2/ContextHandoffBudget.ts:313-315`; my probe keeps all three anchors at 2,048, 4,096, 8,000, 16,000 and 64,000 bytes.
- Round 1 high, tools/questions counted as assistant answers: still fixed (`findLastIndex(kind === "assistant_message")`, line 314).
- Round 1 low, interrupted tool-only recovery: covered by the ProviderSwitch integration test, which passes.
- Round 2 high, eight-worker cap omitting 4 of 12 active app-owned workers at 64,000 bytes: fixed. Eight is now only the priority pass (line 338); `rankedWorkers.slice(8)` runs after prose and before tool pointers (line 344). Probe: 12/12 workers and 30 tools at 64,000; 40/40 workers at 64,000; 12/12 at 16,000.

## Omission accounting and bounds

`omittedWorkers` counts unique unselected worker keys (line 349-350), is reserved at its maximum width in the wrapper (lines 285-294), persists through all three preparation sites in `ContextHandoffService.ts:293,407,487`, is summed into delivery (`ContextHandoffDelivery.ts:120-129`) and is recomputed for the pointer-only fallback by unique key (lines 141-147). Re-selecting a 64,000-byte preparation at a 4,096-byte delivery budget reported 9 omitted workers with 3 selected, the correct total. Every probe case kept `historyCost <= budget`. The contract field is `Schema.optional(NonNegativeInt)`, so older persisted handoffs still decode.

Security: the new field is a non-negative integer rendered into fixed text; no user-controlled strings, paths or commands are added.

## [low] apps/server/src/orchestration-v2/ContextHandoffDelivery.ts:120 omitted-worker total can double-count across pending handoffs

`omittedWorkersBefore` sums each pending handoff's own count. A worker whose launch falls in one handoff's runs and whose state record falls in another, both omitted at preparation, is counted twice. A worker omitted in handoff A but carried by handoff B is also reported omitted while present. Probe: one 12-worker history omitting 9 at 4,096 yields 18 when two handoffs omit the same set. The number is advisory and the recovery route is printed with it, so nothing is lost; the count can only overstate.

## [low] apps/server/src/orchestration-v2/ContextHandoffBudget.ts:343 older assistant prose outranks active workers beyond the first eight

The prose pass (all non-worker, non-tool records, newest first) runs before `rankedWorkers.slice(8)`. With 12 running app-owned workers plus 40 older 800-byte assistant messages at 16,000 bytes, 8 workers survive and 4 active app-owned workers are omitted while old prose is kept. This is the author's stated ordering, the omission is counted and recovery is named, and at 64,000 all 12 survive, so it does not block. If the incident class recurs with long coordinator transcripts, rank active app-owned workers ahead of non-anchor prose.

## Verification

- Delta `6382a096..23657666`: only `ContextHandoffLifecycle.test.ts` (`TurnItemId.make` on three assertion IDs) and `testkit/ProviderSwitch.integration.test.ts` (one type-narrowing guard). No runtime change; confirmed with `git diff --stat`.
- Focused tests at head `23657666` in the implementation checkout (read-only run): ContextHandoff*, TurnStartReads, ProjectionStore*, ProviderSwitch integration, 16 files, 173 passed, 1 failed. Log `/srv/work/scratch/r3-pr521/focused-tests.log`.
- The one failure is `ProjectionStore.slowQueries.test.ts:496`: the SQLite query plan for `PREVIOUS_BACKGROUND_BUSY_SQL` does not use `orchestration_v2_projection_nodes_live_subagent_idx`. It fails deterministically here (3 of 3 runs). The PR does not touch that statement, that index, migrations or the test; its only ProjectionStore change widens the turn-item type list in the history read (`ProjectionStore.ts:4742`). I attribute it to the base or this machine, not the PR, but did not run it on the base commit; CI decides.
- Independent probe: `/srv/work/scratch/r3-pr521/probe4.mts`, output `/srv/work/scratch/r3-pr521/probe4.log`.
- Owner evidence reviewed: typecheck gate passed with 0 new diagnostics at `23657666` (`/srv/specwithcode/minisforum/evidence/1354-context-continuity/typecheck-23657666.log`); 77 affected tests passed (`/srv/specwithcode/minisforum/evidence/1354-context-continuity/r3-ci-fixture-tests.log`); clean supported checks copy (`/srv/specwithcode/minisforum/evidence/1354-context-continuity/checks-copy-r3.log`).

## Not covered by this review

Required CI, merge, release and installed-app verification remain separate gates owned by the delegated owner thread. Attribution of the original m3 incident is unverified. Scope delivery is not independently recorded here: the code meets the stated behaviour in tests and probes, but installed behaviour is unverified.

Nits: wrapper sentence "Counts cover eligible records only" is now terse enough to be ambiguous about whether worker counts include tool records.
