# Subagent continuity across model, subscription and machine handoffs

## Problem

On October 24, 2026, Anton reported threads stuck on "Working" after a model switch. His screenshots are at `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-57e1abac-cd06-4e9d-830e-29c63318dbd6.png` and `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-1b4c7025-5a0e-4111-ab92-123ca79fe91e.png`.

- "Independent review light theme PR", a Claude Code Opus 5.5 subagent of the EasyChamp thread "Console, Arena, UIKit feature PRs", has shown "Working for 9h 57m" with "No activity 9h". It was a read-only review of `/Volumes/Work/EasyChamp-code/w26-console/ec-console-ui`, branch `fix/match-center-facts-light-theme`, commit `644f4fa4` on top of `d830084e`.
- Five EasyChamp parents read "Working · N subagents": Daily SEO watch (on a "Fallback for Claude Op…" model), Remove sync unverified badge from CMS, Console/Arena/UIKit feature PRs, Club payment confirmation emails and 0952 PremierLiga import unblock.

Anton asked:

- Why do these threads show "Working"? He believes subagents get stuck when the model switches.
- Do handoff documents work, for example "after 95%", or is there a better strategy?
- How should subagents be handed off? Should they be restarted, and do they need extra instructions?
- Does the answer differ on the same machine and across machines?

Installed app 1.0.75 has no stranded-subagent settlement. Increment 1048 (in review, unreleased) settles stranded native subagents when the process that owned them is gone. This increment covers what 1048 does not: model, subscription and machine transitions; delegated and nested children; handoff documents and their threshold; and the display.

## Scope

In:

- Root cause for each row in the screenshots, from thread reads and source (never the database directly).
- Settlement and continuation of native, delegated and nested children when the parent switches model or provider (A→B→A), switches subscription, or moves or hands off to another machine.
- Process and lease liveness, including unavailable hosts, which stay "unknown" and are never settled as dead.
- The handoff document strategy and its threshold.
- Instructions given to a resumed or replacement child.
- Headless UI evidence.

Out:

- Editing EasyChamp features or taking over EasyChamp worktrees.
- Changing machine grants, billing choices or credentials.
- Merge, release and live restarts.

## Acceptance Criteria

- [ ] AC-01: A root-cause report covers every screenshot row and gives actual execution against display, citing thread reads and source lines. It also covers this owner's own failed status.
- [ ] AC-02: When a parent switches model or provider, native children of the old provider session are settled. Finished children are settled from evidence (their result delivered once). Unfinished ones are marked interrupted, and the parent gets one note naming what to rerun. Delegated (app-owned) children keep running on their own thread and stay linked. Nested children follow the same rules. Proven by fault and transition tests for A→B, A→B→A, and a subscription switch on the same provider.
- [ ] AC-03: Liveness is decided by evidence: a live process, a fresh lease or a heartbeat. On another machine, an unreachable host leaves its children "unknown", never cancelled. When a machine handoff moves a thread, its children are either moved with a lease or settled with a note, never duplicated. Proven by tests with two simulated hosts.
- [ ] AC-04: A resumed or replacement child gets the canonical context: the original brief, what it already did (tool calls with irreversible effects are listed, never replayed), the increment, tasks, ACs, evidence paths and the parent's instructions. A person's Stop, approval and billing boundaries and machine grants still hold.
- [ ] AC-05: A handoff document strategy based on research. It states what "95%" refers to (context-window use or provider quota) and recommends thresholds or triggers backed by current provider behaviour (auto-compact points, limit warnings) and our own data, not a fixed number. It is implemented where the current code is wrong, with tests.
- [ ] AC-06: The parent and child rows show the truth: "Working" only when a turn or a live child is really running. Otherwise they show "Stopped", "Interrupted, rerun pending" or "Unknown (machine unreachable)". Headless captures at 390 and 1280 px in light and dark.
- [ ] AC-07: Fresh-context review, routed delivery, and the EasyChamp owners and the handoff owner told what changes for their threads.

## Approach

1. Investigate first (T-01, research role): read the screenshot threads through `studio_thread_read`, map them to 1048's settlement code, and research handoff thresholds.
2. Build on `fix/core-failure-recovery-1048` (scratch worktree `/tmp/core-recovery/tree`) so settlement has one path.
3. Coordinate with the handoff owner ("Project setup and handoff review", 1006) and the EasyChamp coordinator instead of editing their work.

## Tasks

### T-01 Root cause and handoff research
- AC: AC-01, AC-05 | Files: .specweave/increments/1053-subagent-handoff-continuity/reports/root-cause.md, .specweave/increments/1053-subagent-handoff-continuity/reports/handoff-strategy.md | Test: test -s .specweave/increments/1053-subagent-handoff-continuity/reports/root-cause.md

### T-02 Settlement on model, provider and subscription switches
- AC: AC-02, AC-04 | Files: apps/server/src/orchestration-v2/ (app repo, scratch worktree) | Test: npx vp test run apps/server/src/orchestration-v2/SubagentHandoffContinuity.test.ts

### T-03 Cross-machine liveness and handoff
- AC: AC-03 | Files: apps/server/src/orchestration-v2/, apps/server/src/fleet/ | Test: npx vp test run apps/server/src/orchestration-v2/SubagentMachineHandoff.test.ts

### T-04 Handoff document threshold
- AC: AC-05 | Files: per T-01 findings | Test: per T-01 findings

### T-05 Row status truth and headless evidence
- AC: AC-06 | Files: apps/web/src/studio/, apps/web/tests/ | Test: headless fixture, captures under /Users/antonabyzov/.specwithcode/m4/evidence/subagent-handoff-1053/

### T-08 Resolve PR conflicts and continuity CI regressions
- AC: AC-02, AC-04, AC-06, AC-07 | Files: /tmp/core-recovery/h1053/apps/server/src/orchestration-v2/, /tmp/core-recovery/h1053/apps/web/src/components/studio/shell/SubagentPeek.tsx, /tmp/core-recovery/h1053/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, /tmp/core-recovery/h1053/apps/mobile/src/features/threads/ProviderSubagentBar.tsx | Test: server orchestration-v2 suites, affected web suites, repository typecheck gate and exact-head fresh review

### T-06 Fresh review, routed delivery and owner notes
- AC: AC-07 | Files: .specweave/increments/1053-subagent-handoff-continuity/reports/review.md | Test: test -s .specweave/increments/1053-subagent-handoff-continuity/reports/review.md

### T-07 Verify and close 1053

## Decisions

### Asked
- D-01: Anton asked for a complete core remedy for subagents stuck after model switches, covering handoff documents and cross-machine moves.

### Defaulted
- D-02: Builds on 1048's single settlement path. It adds no new interrupt `cause` literals, because older fleet peers decode `cause` as a closed set.
- D-03: Claude workers are rate-limited until 1:10 PM EDT on October 24. Work runs on Codex (ChatGPT subscription, not a paid fallback) until then.

### Open
- None.
