# Handoff — 0992-usable-umbrella-handoff Usable umbrella handoff and unfinished work portability
agent: codex-0992-lead · 2026-10-22T11:53:54.109Z · branch codex/0992-handoff-flow @ a35d9f6e8 · tree: 2 uncommitted · redactions: 2
active claims: T-05 (claimed by codex-0992-lead)

## Where I left off
Why: Release and Linux verification complete; Mac rollout and UI acceptance pending
PR #590 is merged. Version 1.0.71 is published from fc11911064026247d7d476fac140134e65b13075; release PR #592 is merged. The full umbrella and dirty/internal/external worktree transfer scenarios passed, including consolidation, Undo and scratch cleanup. Ministorm runs 1.0.71 with 24 guards and 13 retention checks passing. The published Mac package contains the tested UI and passes signature/notarization checks. The installed Mac remains on 1.0.69 while its normal updater waits for quiet. The final illustrated report is reports/project-transfer-verification.html; final headless report QA passed four cases and 16 screenshots. T-01 through T-04 are done; T-05 remains open.

Intent board: .specweave/intents/board.jsonl — 0 open intents (planning state, not verification).

[Open the intent board](../../intents/board.jsonl)
Increment 0992-usable-umbrella-handoff (active) · tasks 4/5 done · ACs 0/5
Gotcha: Do not take over 0957 or 0967, force a Mac update, restart active services, or replace another owner installation request. Browser automation must be headless. Never access live SQLite directly. Reports and private evidence remain local; this checkpoint is not pushed. SpecWeave owns handoff-report.html; preserve project-transfer-verification.html.

## Done / Pending
| Task | State | By | Evidence / note |
|---|---|---|---|
| T-01 Keep copy actions in the dialog footer | done | codex-0992-ui | cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0992- |
| T-02 Resolve and validate umbrella copy scope | done | codex-0992-scope | cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0992- |
| T-03 Preserve portable Git worktrees and verify remote consolidation | done | codex-0992-git | python3 /Users/antonabyzov/Projects/github/specweave-handoff |
| T-04 Integrate source scope and verify complete UI | done | codex-0992-ui | cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0992- |
| T-05 Review, release and close | claimed | codex-0992-lead |  |
4/5 done · 0 skipped · 1 claimed · 0 blocked · 0 stale · 0 open

## Decisions
_None recorded — see spec.md Approach._

## Files touched
UNCOMMITTED — commit or stash before anything destructive.
```
M .specweave/metrics/release-timings.jsonl
?? .specweave/increments/0992-usable-umbrella-handoff/evidence/
```
Full diff: `.specweave/increments/0992-usable-umbrella-handoff/handoff.diff`

## Next steps
Read reports/root-checkpoint.json in this exact checkout. Keep M4 read-only until its normal updater installs 1.0.71; then run verify-installed-mac.py, official release verification and verify-delivery.py with the exact release source. The existing UI acceptance question remains pending; do not repeat it. Complete 0992 only after actual verification and acceptance gates pass.

## Resume
1. `specweave pickup` prints the next task with its acceptance criteria, claims and branch state.
2. `specweave task claim <T-id> 0992-usable-umbrella-handoff` → implement → `specweave task done <T-id> --run "<test>"`.
3. Original transcript (optional): Claude Code: `claude -r <uuid>` · Codex: `codex resume <uuid>` · OpenCode: `opencode -s <id>`.

---
<!-- Doc format v2 -->