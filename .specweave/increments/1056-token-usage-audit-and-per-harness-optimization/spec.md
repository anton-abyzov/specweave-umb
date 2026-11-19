---
increment: 1056-token-usage-audit-and-per-harness-optimization
title: Token usage audit and per-harness optimization
type: improvement
priority: P1
---

# Token usage audit and per-harness optimization

## Problem

Anton (October 24, 2026): token usage has risen sharply and "must be reviewed and optimized", possibly because of SpecWeave tasks and acceptance criteria, possibly fixable with cache reuse or other per-harness changes for Claude and Codex. Nobody has measured where the tokens go. Candidate sources include injected instructions (CLAUDE.md, AGENTS.md, SpecWithCode project context, memory index), tool schemas and skill listings, SpecWeave hook output, spec and ledger reads, tool output and history replay, compaction and handoff documents, repeated routine prompts, subagent fan-out, retries and duplicate reviews. Blaming any one of them before measuring would optimize the wrong thing.

## Scope

In scope:

- Measure real per-harness usage (Claude Code, Codex; other harnesses where telemetry exists) from local transcripts and supported `specweave-studio db query` reads: input, cache write, cache read, output, per turn and per session.
- Attribute cost to the categories above, with representative Claude and Codex workloads.
- Research current harness-specific caching and context features from authoritative sources (Anthropic docs for Claude and Claude Code, OpenAI docs for Codex).
- Implement the optimizations the evidence supports, in SpecWeave (this CLI and its hooks and templates) and the SpecWithCode app.
- Reproducible before/after measurements plus quality and continuity checks.

Out of scope:

- Subscription rotation and cross-account cache behavior (owned by 1055).
- Subagent continuity across switches (owned by 1053).
- macOS, Windows and Linux releases (release owner "Complete screenshot sessions").
- Truncating context blindly, lossy summaries, or any artificial token use to inflate numbers.
- Ranks 6 to 11 of `reports/plan.md` (dropped by Anton, November 19, 2026). Ranks 1 to 5 are built as T-04 to T-08.
- The plan's "Needs a user decision" rows other than "Routine changes": fan-out volume, long-lived sessions, `omitClaudeMd` for read-only subagents, Codex default effort and `MEMORY.md` size. "Routine changes" (rank 4) was approved by Anton on November 19, 2026, including deleting the duplicate routines.

## Acceptance Criteria

- [ ] AC-01: A measurement report covers at least 7 days of local Claude Code and Codex usage. Per harness it gives input, cache-write, cache-read and output tokens and the cache-hit ratio, separately per day and per workload type (coordinator, worker, subagent, routine, review). It lists telemetry that is unavailable by name. Overlapping diagnostics are never summed, and local session reuse is never reported as a provider cache hit.
- [ ] AC-02: An attribution table estimates each category's share of per-turn input: system and injected instructions, tool schemas and skill listings, SpecWithCode project context, SpecWeave hook output, spec, ledger and memory reads, tool output and history replay, compaction and handoff documents, routine prompts, subagent fan-out and retries or duplicate reviews. Each row names its method (measured bytes or tokens, or estimate) and source.
- [ ] AC-03: A research note cites current Anthropic and OpenAI documentation for prompt caching (prefix rules, TTLs, breakpoints, minimums), and the context and compaction features of Claude Code and Codex. It says which ones SpecWeave and SpecWithCode already use and which they could use.
- [ ] AC-04: Each implemented optimization names the AC-02 row it targets. Before/after measurements on a reproducible fixture or replay (bytes and tokens of the injected payload, or the cache-read ratio) are stored under `/Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/`.
- [ ] AC-05: The optimizations keep task and AC traceability, ownership and claims, safety rules and handoff correctness. The existing tests for the touched code pass, plus new tests for each change. A continuity check shows that a resumed or handed-off session still gets the facts it needs: active increment, next task, claims and rules.
- [ ] AC-06: Stable prefixes come first. Injected context whose content does not change between turns is emitted in a byte-stable order, and volatile parts (timestamps, counters) move out of the cached prefix where the harness caches by prefix. A test asserts byte stability for unchanged inputs.
- [ ] AC-07: A fresh-context review returns SHIP, and the user-facing summary reports the measured savings and the remaining gates.
- [ ] AC-08: (rank 1) For an ACP agent that reports session-cumulative totals (GitHub Copilot), each turn stores the increase since the previous prompt of the same live session; the first prompt of a session, and a prompt whose totals fall below the previous ones (counters reset), store the totals as reported. Agents that report per-turn usage (Devin, whose output resets every turn, Grok, Gemini) are unchanged. Before/after: the November Copilot total on the `measurement.md` basis (`app-db/cumulative_check.py` method), raw against corrected, plus a replay of a recorded cumulative sequence through the old and new code.
- [ ] AC-09: (rank 2) A project-context delta sends `memory_index` as a line diff against the acknowledged revision when the diff is smaller than the section, omits the inventory revision hash and unchanged per-file revisions, and emits sections in a byte-stable order. A full snapshot stays complete (after compaction and on an unacknowledged receipt), applying the diff to the previous index reproduces the new index, and a continuity test shows a resumed thread still sees role, environment, memory index and knowledge. Before/after: delta bytes on replayed section revisions.
- [ ] AC-10: (rank 3) Delegated-task threads and app-owned Claude subagents launch with `excludeDynamicSections`, so sibling workers with the same configuration share the system-prompt cache; auto memory and CLAUDE.md still load. Before/after: request-1 `cache_creation_input_tokens` against `cache_read_input_tokens` for two identical workers.
- [ ] AC-11: (rank 4) The disk-space and cleanup routines have a shell `check` that wakes the model only when a threshold trips, and each true duplicate routine pair is reduced to one routine (a pair whose members run at different times is one job and stays), changed through the app's routine tools or RPCs, never the state database. The report lists every deleted routine by name and id. Before/after: `routine_run_tokens` over comparable windows.
- [ ] AC-12: (rank 5) After 3 consecutive failed runs in one thread, the app stops automatic re-runs (routine fires and the provider-open retry and fallback; usage-limit fallback and resume stay with 1055) for that thread and reports why; a user message or a successful run resets the count. Before/after: runs started for a replayed failure streak.

## Approach

1. Measure first (AC-01, AC-02). Claude Code transcripts under `~/.claude/projects/*/*.jsonl` carry per-message usage. Codex rollouts under `~/.codex/sessions/` carry token_count events. App turn usage comes from `specweave-studio db query` (never the SQLite file). Reuse the 1055 scan pattern (`/Users/antonabyzov/.specwithcode/m4/scratch/1055-usage-scan/scan.py`). Measure the injected payloads directly: hook stdout, the SpecWithCode project-context block, the memory index, tool and skill listings.
2. Research (AC-03) runs in parallel.
3. Pick optimizations by measured share times feasibility. Implement them in the owning repo with tests.
4. Measure again on the same fixture (AC-04), check continuity (AC-05), then a fresh review (AC-07).

## Tasks

### T-01 Measure per-harness usage and attribute cost
- AC: AC-01, AC-02 | Files: .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/measurement.md, /Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/ | Test: test -s .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/measurement.md

### T-02 Research harness caching and context features
- AC: AC-03 | Files: .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/research.md | Test: test -s .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/research.md

### T-03 Optimization plan from evidence
- AC: AC-02, AC-04 | Files: .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/plan.md | Test: test -s .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/plan.md

### T-04 Rank 1: store ACP cumulative usage as deltas
- AC: AC-04, AC-05, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/AcpTurnTokenUsage.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/AcpTurnTokenUsage.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.ts, /Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/rank1/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/provider/AcpTurnTokenUsage.test.ts apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.test.ts

### T-05 Rank 2: project context deltas
- AC: AC-04, AC-05, AC-06, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectContextLineDiff.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectContextLineDiff.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectContextSnapshot.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectContextDelivery.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectContextDelivery.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectContextRuntime.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectContextAdapters.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, /Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/rank2/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectContextLineDiff.test.ts apps/server/src/project/ProjectContextDelivery.test.ts apps/server/src/project/ProjectContextBudget.test.ts apps/server/src/project/ProjectContextAdapters.test.ts

### T-06 Rank 3: share the system-prompt cache across workers
- AC: AC-04, AC-05, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts, /Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/rank3/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts

### T-07 Rank 4: routine gates and duplicate routines
- AC: AC-04, AC-11 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/rank4/ | Test: test -s /Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/rank4/routines-after.json

### T-08 Rank 5: stop failed-run loops
- AC: AC-04, AC-05, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/RunFailureBreaker.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/RunFailureBreaker.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/RunFailureBreaker.dispatch.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, /Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/rank5/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/RunFailureBreaker.test.ts apps/server/src/orchestration-v2/RunFailureBreaker.dispatch.test.ts

### T-09 Fresh review and delivery
- AC: AC-07 | Files: .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/review.md | Test: test -s .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/review.md

### T-10 Verify and close 1056

## Review

- Reviewer: openai (gpt-6.1-sol)
- Depth: standard
- Required: yes

Muse and Codex are out on November 19, 2026, so reviews run on Copilot Enterprise (`acpRegistry_copilot`) with `gpt-6.1-sol`, per Anton's standing rule of November 18, 2026. One review per app PR; reviewers read with `git show` and `git diff` only.

## Decisions

### Defaulted

- D-01 Savings are reported only from AC-04 measurements, never from estimates.
- D-02 1055 keeps subscription and cross-account cache work; 1056 does not claim savings across accounts.
- D-03 Rank 1 applies to GitHub Copilot only. A November 2026 recheck (`rank1/recheck-since-2026-10-10.txt`) shows Copilot input and output both rise on 72% of consecutive turns (Claude 43%), while Devin's output resets every turn (53%), so Devin's input is not a session total and stays per-turn.

### Made by Anton

- D-04 November 19, 2026: build ranks 1 to 5, drop ranks 6 to 11; rank 4 approved, including deleting the duplicate routines.
