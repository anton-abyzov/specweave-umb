# Handoff — 0992-usable-umbrella-handoff Usable umbrella handoff and unfinished work portability
agent: codex-0992-lead · 2026-10-22T11:48:34.884Z · branch codex/0992-handoff-flow @ 8e329fc20 · tree: 3 uncommitted · redactions: 2
active claims: T-05 (stale by codex-0992-lead)

## Where I left off
Why: Released and Linux verified; installed Mac and manual UI acceptance pending
PR590 merged33ac849865; official1.0.71 sourcefc11911064026247d7d476fac140134e65b13075 published, PR592merged1f13bb6afef9. Full umbrella transfer91079files9repos, dirty/internal/externalworktree and consolidation/Undo tests passed and scratchremoved. PublishedMacfrontend/signature/notarization verified; Ministorm71 installed and retentionverified. T01-T04done,T05pending. Fullreport reports/project-transfer-verification.html; reportagent finalrender/QA finishing.

Intent board: .specweave/intents/board.jsonl — 0 open intents (planning state, not verification).

[Open the intent board](../../intents/board.jsonl)
Increment 0992-usable-umbrella-handoff (active) · tasks 4/5 done · ACs 0/5
Gotcha: Do not pick up foreign0957/0967. Do not force/update/restart M4 or overwrite its handled70request. Preserve all foreign release lanes. Never publish private evidence/grants, directly read live SQLite, or weaken pending installed checks. Headless browser only. Reports are local/ignored; this handoff is not pushed.

## Done / Pending
| Task | State | By | Evidence / note |
|---|---|---|---|
| T-01 Keep copy actions in the dialog footer | done | codex-0992-ui | cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0992- |
| T-02 Resolve and validate umbrella copy scope | done | codex-0992-scope | cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0992- |
| T-03 Preserve portable Git worktrees and verify remote consolidation | done | codex-0992-git | python3 /Users/antonabyzov/Projects/github/specweave-handoff |
| T-04 Integrate source scope and verify complete UI | done | codex-0992-ui | cd /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0992- |
| T-05 Review, release and close | stale | codex-0992-lead |  |
4/5 done · 0 skipped · 0 claimed · 0 blocked · 1 stale · 0 open

## Decisions
_None recorded — see spec.md Approach._

## Files touched
UNCOMMITTED — commit or stash before anything destructive.
```
M .specweave/increments/0992-usable-umbrella-handoff/spec.md
 M .specweave/metrics/release-timings.jsonl
?? .specweave/increments/0992-usable-umbrella-handoff/evidence/
```
Full diff: `.specweave/increments/0992-usable-umbrella-handoff/handoff.diff`

## Next steps
In this exact ownedcheckout, read reports/root-checkpoint.json and canonical report. Keep M4 read-only while normal updater waitsquiet; after it installs71 run verify-installed-mac.py and officialrelease verify, then verify-delivery.py. Existing newUI acceptance question remains pending; do not repeat. Only complete0992 after actual gates pass.

## Resume
1. `specweave pickup` prints the next task with its acceptance criteria, claims and branch state.
2. `specweave task claim <T-id> 0992-usable-umbrella-handoff` → implement → `specweave task done <T-id> --run "<test>"`.
3. Original transcript (optional): Claude Code: `claude -r <uuid>` · Codex: `codex resume <uuid>` · OpenCode: `opencode -s <id>`.

---
<!-- Doc format v2 -->