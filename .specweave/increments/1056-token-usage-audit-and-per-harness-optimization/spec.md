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

## Acceptance Criteria

- [ ] AC-01: A measurement report covers at least 7 days of local Claude Code and Codex usage. Per harness it gives input, cache-write, cache-read and output tokens and the cache-hit ratio, separately per day and per workload type (coordinator, worker, subagent, routine, review). It lists telemetry that is unavailable by name. Overlapping diagnostics are never summed, and local session reuse is never reported as a provider cache hit.
- [ ] AC-02: An attribution table estimates each category's share of per-turn input: system and injected instructions, tool schemas and skill listings, SpecWithCode project context, SpecWeave hook output, spec, ledger and memory reads, tool output and history replay, compaction and handoff documents, routine prompts, subagent fan-out and retries or duplicate reviews. Each row names its method (measured bytes or tokens, or estimate) and source.
- [ ] AC-03: A research note cites current Anthropic and OpenAI documentation for prompt caching (prefix rules, TTLs, breakpoints, minimums), and the context and compaction features of Claude Code and Codex. It says which ones SpecWeave and SpecWithCode already use and which they could use.
- [ ] AC-04: Each implemented optimization names the AC-02 row it targets. Before/after measurements on a reproducible fixture or replay (bytes and tokens of the injected payload, or the cache-read ratio) are stored under `/Users/antonabyzov/.specwithcode/m4/evidence/token-usage-1056/`.
- [ ] AC-05: The optimizations keep task and AC traceability, ownership and claims, safety rules and handoff correctness. The existing tests for the touched code pass, plus new tests for each change. A continuity check shows that a resumed or handed-off session still gets the facts it needs: active increment, next task, claims and rules.
- [ ] AC-06: Stable prefixes come first. Injected context whose content does not change between turns is emitted in a byte-stable order, and volatile parts (timestamps, counters) move out of the cached prefix where the harness caches by prefix. A test asserts byte stability for unchanged inputs.
- [ ] AC-07: A fresh-context review returns SHIP, and the user-facing summary reports the measured savings and the remaining gates.

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

### T-04 Implement optimizations with before/after measurements
- AC: AC-04, AC-05, AC-06 | Files: per T-03 | Test: per T-03

### T-05 Fresh review and delivery
- AC: AC-07 | Files: .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/review.md | Test: test -s .specweave/increments/1056-token-usage-audit-and-per-harness-optimization/reports/review.md

### T-06 Verify and close 1056

## Decisions

### Defaulted

- D-01 Savings are reported only from AC-04 measurements, never from estimates.
- D-02 1055 keeps subscription and cross-account cache work; 1056 does not claim savings across accounts.
