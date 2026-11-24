# Chaos rig: usage-limit fallback and subagent storm on fake providers

## Problem

Usage-limit fallback and subagent fan-out keep shipping races: queued sends racing a pre-switch (`31bfb2911`, `611fa65a6`), a coordinator stuck after a subscription change (1301), a subagent "Working 9h 57m" (1053), a dead background workflow that left its thread waiting forever (1302), and on November 24, 2026 a 918-turn Copilot/Cursor ping-pong on m4 (fixed in 1460, PR #875). Every fix got unit tests; none got a recurring run where limits change during the run. `STUDIO_SIMULATE_USAGE_LIMIT` is read at process start and stops a turn before it starts, so today no check can flip a limit mid-run.

Source: `.specweave/reports/threads/2026-11-24-chaos-loop-methodology-and-specwithcode-16f346-d9d984.md`, candidate 1.

**Spike findings (November 24, 2026, scratch server from source on M5):**

- A local ACP agent that answers `Error: You've hit your usage limit.` is classified as a usage limit with no reset (`packages/shared/src/usageLimitReply.ts`), the same path as Copilot's spent quota.
- The fallback only moves to a source whose sign-in is confirmed (`hasUsableFallbackCapacity` needs `auth.status: "authenticated"`), so the fake must advertise an auth method and the rig signs in through `provider.auth.start`.
- With three fakes a, b, c reporting 10% used (`STUDIO_SIMULATE_PROVIDER_USAGE`) and a and b answering with the limit notice, `main` at `f3ce25682` ping-pongs a→b→a→b (18 failed runs in 90 s) and never reaches c. That is the m4 incident, reproduced with no model tokens.
- The first fallback run carries the original message in its context handoff; later continuations send "Continue where you left off." Agent sessions map to threads through `providerThreads[].nativeThreadRef.nativeId`.

## Scope

In: a model-free fake ACP agent driven by a control file; a runner that boots one scratch server (from source, or the built entry), flips limits on a seeded schedule, fans out workers through `delegate_task`, and queues messages; a pure checker for three invariants with self-tests in PR CI; a report-only nightly workflow.

Out: real subscriptions and the live M4/M5 homes; changing fallback or recovery behaviour (`UsageLimitRecoveryWorker.ts`, `ProviderFallbackWorker.ts` and what PR #875 touches belong to 1460; failing seeds go to that owner); observing a limit clear within a run (fake notices name no reset and 1460 holds a source 60 minutes, so a return after a real reset needs a test-only clock seam near the ping-pong code, a follow-up to agree with 1460's owner); kill and restart of the server mid-run (later scenario); the agent triage loop.

## Acceptance Criteria

- [x] AC-01: `scripts/studio-chaos/chaos-agent.mjs` is a model-free ACP agent that reads its control file at every prompt (limited, work-then-limit, delay, crash), advertises a sign-in method, runs any number of `MCP-CALL` lines in order, and appends every prompt and outcome to a per-instance log.
- [x] AC-02: `scripts/studio-chaos/fallback-storm.mjs` boots a scratch server on a private home under the OS temp folder, signs the fakes in, runs a named scenario under a wall-clock cap, writes `receipt.json` with the seed, the fault schedule, turn counts and a verdict of `pass`, `violated` or `stalled`, and stops only the processes it started (the server and its own process tree). The same seed yields the same planned fault schedule; the receipt records when each fault was applied. Exact fault placement against prompts can still move with machine load (proof limit).
- [x] AC-03: Invariant "runs once and in order": per thread, every accepted user message ends in exactly one completed run in its continuation chain, or the thread shows a visible stop (its latest run failed with a usage limit and nothing is running); completed runs follow dispatch order; the fakes' answered turns per thread equal the server's completed runs.
- [x] AC-04: Invariant "every result reaches its launcher": every app-owned subagent that ended has `completionDelivery.state` `delivered` or `acknowledged`, or `disposed` with a reason, and the launcher received a message carrying that child's completion.
- [x] AC-05: Invariant "one switch per limit, no return before reset": after a run on source S stops on a usage limit, no later automatic fallback (in any thread) runs on S before that stop's reset (or 60 minutes when it names none) unless a run that started after the stop completed on S, and each limit stop is followed by at most one automatic fallback before a run completes or the thread stops.
- [x] AC-06: The checker goes red on the bug: the `ping-pong` scenario is `violated` (AC-05) on `main` before PR #875 and `pass` on #875's head, both receipts saved in this increment's `reports/`.
- [x] AC-07: `scripts/studio-chaos/check.test.mjs` exercises each invariant on synthetic good and bad fixtures and runs in the scripts suite (`node --test 'studio-*/**/*.test.mjs'`).
- [x] AC-08: `.github/workflows/chaos-nightly.yml` runs the scenarios nightly and on demand as report-only (`continue-on-error`), uploads receipts, and prints each failing seed's replay command in the job summary.

## Approach

Real-server pattern from `scripts/studio-limit-handoff/verify.mjs`: the fallback and recovery workers are wired only in `runtimeLayer.ts`, so an in-process harness would not exercise them. New files under `scripts/studio-chaos/` only; `verify.mjs` (1,564 lines) and `link-launch-agent.mjs` (hashed into other verifiers' receipts) stay untouched.

1. `chaos-agent.mjs`: control file per prompt; limit as a notice reply; witness log.
2. `lib/scratch-server.mjs`: home layout, start from `apps/server/dist/bin.mjs` or `src/bin.ts`, token exchange, WebSocket RPC, sign-in, seeded PRNG (mulberry32).
3. `check.mjs`: a pure function over thread projections, the fakes' turn logs and the fault schedule; returns violations with thread, run and rule. No I/O, so the self-test feeds it fixtures.
4. `fallback-storm.mjs`: scenarios `ping-pong` (a and b spent, c free; fallback order a, b, c) and `storm` (a coordinator on a delegates N workers to a worker source with seeded delays, queues follow-ups while limits flip on a, b, c on a seeded schedule). Reads state only through `orchestration.getThreadProjection`, never the scratch database file.
5. `chaos-nightly.yml`: build the server, run `ping-pong` and `storm` over a few seeds, upload receipts, summary table.

Risks: shared runners are slower, so timing caps are generous and a cap hit is `stalled`, not `violated`. A fake models only what it emits: background work (1306) and real Copilot quirks are out.

## Decisions

### Asked
- none (owner approved the report's recommendation on November 24, 2026)
### Defaulted (change any before sw-do)
- D-01 Report-only nightly; no merge gate until three clean nightly runs → default (reversible).
- D-02 Limit notice reply rather than `STUDIO_SIMULATE_USAGE_LIMIT`, because the reply can flip mid-run and follows the Copilot path that ping-ponged → default.
- D-03 Hold window for AC-05 is the stop's reset, else 60 minutes, per exact source (instance and model) across all threads, ended by a run that starts after the stop and completes; matching 1460's rule → default.
### Open
- none

## Tasks

### T-01 Fake agent and scratch-server helpers
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/chaos-agent.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-chaos/lib/scratch-server.mjs | Test: node repositories/anton-abyzov/specwithcode/scripts/studio-chaos/fallback-storm.mjs --scenario ping-pong --seed 1 (fakes sign in and the first limit stop is logged)

### T-02 Invariant checker with self-tests
- AC: AC-03, AC-04, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/check.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-chaos/check.test.mjs | Test: node --test repositories/anton-abyzov/specwithcode/scripts/studio-chaos/check.test.mjs

### T-03 Runner with ping-pong and storm scenarios
- AC: AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/fallback-storm.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-chaos/README.md | Test: node repositories/anton-abyzov/specwithcode/scripts/studio-chaos/fallback-storm.mjs --scenario storm --seed 7

### T-04 Red on main, green on #875
- AC: AC-06 | Files: .specweave/increments/1465-chaos-rig-usage-limit-fallback-and-subagent-storm-on-fake-providers/reports/ping-pong-main.json, .specweave/increments/1465-chaos-rig-usage-limit-fallback-and-subagent-storm-on-fake-providers/reports/ping-pong-875.json | Test: compare the two receipts' verdicts (violated, pass)

### T-05 Nightly report-only workflow
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/.github/workflows/chaos-nightly.yml | Test: gh workflow run chaos-nightly.yml after merge and confirm the receipt artifact and summary
