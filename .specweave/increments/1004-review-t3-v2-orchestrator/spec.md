# Review T3 v2 orchestrator

## Problem

SpecWithCode (anton-abyzov/specwithcode-dev) is a fork of T3 Code pinned to upstream nightly `10f39eb9ac` (October 7, 2026) and never synced. Upstream has since landed 2,472 commits on main (v0.1.2 stable October 22, v0.1.3 nightly October 23), 447 of them in `apps/server/src/orchestration-v2` and `packages/contracts`. This week we hit three orchestrator defects that upstream may already solve differently: limit fallback moving threads onto exhausted or unprepared providers, the "Insufficient context allowance" dead end on context handoff, and turns refused while background agents run. Nobody has compared the two orchestrators since the fork.

## Scope

In: a read-only comparison of upstream T3 Code orchestration-v2 (latest main and v0.1.2) against our `apps/server/src/orchestration-v2` and related shared packages, covering turn and run lifecycle, provider adapters, queueing and steering, limits and fallback, context handoff and compaction, subagents, persistence and recovery; a written report with cited improvements, the upstream fixes for our three bugs, and a ranked adoption plan; an adversarial review of the report on Codex GPT-6.1 Sol.

Out: code changes, ports, merges, releases in the app repo; any access to `statev2.sqlite*`.

## Acceptance Criteria

- [ ] AC-01: `~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/REPORT.md` lists concrete improvements, each with an upstream file:line (or commit/PR) reference, our file:line reference, benefit, effort and risk.
- [ ] AC-02: The report states, for each of the three bugs (exhausted-provider fallback, "Insufficient context allowance", turns refused during background agents), the upstream mechanism or fix with commit/PR and file references, our current code path, and whether upstream solves it.
- [ ] AC-03: The report ends with a ranked adoption plan (priority, effort, dependencies, migration-number caveat).
- [ ] AC-04: A Codex GPT-6.1 Sol adversarial review of the report is saved next to it, and every challenged claim is marked kept, corrected or dropped in the final report.
- [ ] AC-05: No file in the app repo or its worktrees changed and no `statev2.sqlite*` file was opened; sources were read from scratch copies.
- [ ] AC-06: A focused context-switch audit distinguishes T3 Chat from the authoritative open-source T3 Code repository, records the latest upstream SHA/time, traces payload ordering/dedup/tools/attachments/budget/pending actions/children/source ownership and recovery paths, and reports meaningful test evidence plus installed continuation coverage and unresolved gates without claiming perfection.

## Approach

Sources: upstream cloned blobless to `~/Projects/scratch/t3-v2-orchestrator-review/upstream-t3code` (main `18e2742519`); our main exported with `git archive` to `~/Projects/scratch/t3-v2-orchestrator-review/ours-main` (`ab96f4d1c`). A multi-agent workflow splits the review by area (lifecycle and queue/steer, provider adapters and sessions, limits and fallback, context handoff and compaction, subagents and background work, persistence/projection/recovery), each agent writing a section file with upstream vs ours citations; a second pass verifies citations and produces the three bug analyses. The lead synthesizes REPORT.md and the ranked plan. Then a Codex GPT-6.1 Sol worker challenges the report; confirmed corrections are folded in.

Risk: upstream and our orchestration-v2 diverged heavily (406 files, +66K/-91K lines), so "port" often means "adapt"; citations must name exact commits so a later sync can trace them.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Compare against upstream `origin/main` as of October 23, 2026 and note when a change is only in nightly versus v0.1.2 stable.
- D-02: Report-only; any adoption becomes its own increment later.
### Open
- none

## Tasks

### T-01 Prepare scratch sources
- AC: AC-05 | Files: /Users/antonabyzov/Projects/scratch/t3-v2-orchestrator-review | Test: git -C ~/Projects/scratch/t3-v2-orchestrator-review/upstream-t3code rev-parse origin/main && cat ~/Projects/scratch/t3-v2-orchestrator-review/ours-main/.SOURCE_COMMIT

### T-02 Multi-agent area review with verified citations
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/Projects/github/studio-research-notes/t3-v2-orchestrator-review/sections | Test: ls ~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/sections/*.md

### T-03 Synthesize REPORT.md with bug analyses and ranked plan
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/Projects/github/studio-research-notes/t3-v2-orchestrator-review/REPORT.md | Test: grep -c "Insufficient context allowance" ~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/REPORT.md

### T-04 Adversarial review on Codex GPT-6.1 Sol
- AC: AC-04 | Files: /Users/antonabyzov/Projects/github/studio-research-notes/t3-v2-orchestrator-review/adversarial-review-sol.md | Test: test -s ~/Projects/github/studio-research-notes/t3-v2-orchestrator-review/adversarial-review-sol.md

### T-06 Context-switch assurance and installed evidence
- AC: AC-06 | Files: /Users/antonabyzov/Projects/github/studio-research-notes/t3-v2-orchestrator-review | Test: focused context-switch test receipts, source trace and installed read-only evidence with explicit limits

### T-05 Verify and close 1004
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1004-review-t3-v2-orchestrator | Test: specweave verify 1004 and fresh-context review
