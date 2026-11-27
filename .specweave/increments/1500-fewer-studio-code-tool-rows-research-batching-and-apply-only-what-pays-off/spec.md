# Fewer studio-code tool rows: research batching and apply only what pays off

## Problem

The owner asked whether one model call should run several studio-code tools, so threads show far fewer tool rows on desktop and mobile (coordinator question, answered November 27, 2026: "apply it when it's really necessary", full research first, adversarial review on Muse Wonder Full at Extra High).

Nothing like batching exists. Increment 1483 (1.0.443) loads 6 core studio-code tools up front. Upstream T3 adapted to the Codex and OpenCode "Code Mode" host features; we skipped those commits (`.specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/all-changes.md:392`).

Measured on M5's database on November 27, 2026 (report `reports/research-batching.md`):

- studio-code calls are 4,489 of 37,976 worker tool rows (11.8%) and 526 of 790 coordinator tool rows (66.6%).
- At least 766 studio-code calls (2.0% of tool rows) ran in the same model step as the call before them (a lower bound: 1,368 at a 10 s start gap), so a static batch or composite tool could merge them. The other adjacent pairs have reasoning or another tool between them.
- Run through the real row builders (`deriveMessagesTimelineRows` for desktop, `buildThreadFeed` + `deriveThreadFeedPresentation` for mobile), the 40 threads with the most studio-code calls since November 20 show 1,330 tool rows on desktop today. A same-step batch would show 1,321 (-0.7%); a script that merges every adjacent call would show about 1,308 (-1.7%, a bound biased both ways). Mobile: 1,402, 1,393, 1,381.
- Desktop and mobile already fold every run of adjacent tool calls into one row with a studio-aware summary ("Read 3 threads and sent 2 messages"), and fold each settled turn into one row.
- Of the 1,300 single rows still visible on desktop, 785 are wake notifications (background task, command and monitor finishes) and 149 are system notices. About 60 are studio-code calls.

## Scope

In: the research, the measurement scripts and their numbers, the option analysis with security and per-tool consent, a recommendation, and the Muse review rounds of that research and plan.

Out: any code change unless the review or the owner reverses the recommendation. Wake-notification rows, `task_status` polling, nameless "Tool" rows and ToolSearch rows are recorded as separate follow-ups, not fixed here.

## Acceptance Criteria

- [ ] AC-01: A research report in this increment's `reports/` gives per-thread and total studio-code call counts, same-step versus sequential splits, and desktop and mobile row counts from the real row builders for today, a same-step batch and an adjacent-merge bound.
- [ ] AC-02: The report weighs a sandboxed JS batch tool, composite tools and UI-only collapsing against prior art (Anthropic programmatic tool calling and code execution with MCP, Cloudflare Code Mode, Codex/OpenCode Code Mode as T3 met it), including where per-tool approval is enforced today and how each option keeps or loses it.
- [ ] AC-03: The report recommends the smallest change that pays off, or no change, with the numbers that decide it.
- [ ] AC-04: Muse Wonder Full 1.0 at Extra High reviews the research and plan; every finding is answered in the report and the review ends with no open blocking finding.
- [ ] AC-05: If any code ships, a batch never bypasses per-tool approval: each inner call is checked by the same host and server gates as a direct call, proven by a test of the refusal.

## Approach

1. Export tool rows and full turn items for the 40 busiest threads with `specwithcode db query` (never the database file). Scripts and data live in `~/.specwithcode/m4/scratch/2026-11-27-tool-batching/`.
2. Feed them through the real desktop and mobile row builders in throwaway Vitest files (not committed), with three inputs: as stored, with same-step studio calls merged, and with every adjacent studio call merged.
3. Read where approval happens: Claude `allowedTools` and `canUseTool` keyed on `mcp__studio-code__*` names (`apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts:1359`, `claudeReadOnlyMcpTools.ts`), and the server gates in `apps/server/src/mcp/McpToolAccess.ts`.
4. Compare options and recommend. Review on Muse; fix findings; re-review.

Rejected for now, with numbers in the report: a sandboxed JS batch tool (about 1.7% fewer rows; consent is keepable only with work on both sides, each inner call through its server `Declaration` and through the host's per-tool settings ask/deny and read-only list, and it needs a sandbox); composite tools (0.7%); further UI collapsing of studio-code rows (they are already folded).

Review: Muse Wonder Full 1.0 at Extra High, round 1 "agree with changes", round 2 "fix first" on R2-1 and R2-2 (reports/muse-review.md); all round 1 and round 2 findings answered in the report and spec.

## Decisions

### Asked
- D-01 Should batching be planned? → "Yes, apply it when it's really necessary", full research, Muse Wonder Full at Extra High review (owner via coordinator, November 27, 2026).
### Defaulted (change any before sw-do)
- D-02 Muse effort is Extra High for this increment, as the owner said on November 27, 2026. This overrides `decision_muse_effort_high.md` (High since November 18) for this review only.
- D-03 Ship no batching code → accepted by the owner, November 27, 2026 ("Yes, accept it. I agree."). Follow-ups go to a new increment.
### Open
- D-04 Whether to fold wake-notification rows (785 of 1,300 visible single rows) is a separate increment, if the owner wants it.

## Tasks

### T-01 Measure studio-code calls and rendered rows
- AC: AC-01 | Files: .specweave/increments/1500-fewer-studio-code-tool-rows-research-batching-and-apply-only-what-pays-off/reports/research-batching.md | Test: test -s .specweave/increments/1500-fewer-studio-code-tool-rows-research-batching-and-apply-only-what-pays-off/reports/research-batching.md

### T-02 Weigh options against prior art and consent, recommend
- AC: AC-02, AC-03 | Files: .specweave/increments/1500-fewer-studio-code-tool-rows-research-batching-and-apply-only-what-pays-off/reports/research-batching.md | Test: grep -q "## Recommendation" .specweave/increments/1500-fewer-studio-code-tool-rows-research-batching-and-apply-only-what-pays-off/reports/research-batching.md

### T-03 Muse Wonder Full review of research and plan
- AC: AC-04 | Files: .specweave/increments/1500-fewer-studio-code-tool-rows-research-batching-and-apply-only-what-pays-off/reports/muse-review.md | Test: grep -q "Verdict" .specweave/increments/1500-fewer-studio-code-tool-rows-research-batching-and-apply-only-what-pays-off/reports/muse-review.md

### T-04 Implement only if the decision reverses
- AC: AC-05 | Files: none unless reversed | Test: skipped unless code ships
