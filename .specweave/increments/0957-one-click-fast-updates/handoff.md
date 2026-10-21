# Handoff — 0957-one-click-fast-updates One-click fast updates
agent: claude@antons-macbook-m4max · 2026-10-20T22:34:14.692Z · branch main @ 9af60665f · tree: 18 uncommitted · redactions: 0
active claims: none

## Where I left off
Why: usage limit again. 1.0.63 shipped by someone else with #473's first version (no review fixes) and #466 minus 4 commits; #497 then landed those 4. M1/M3 on 1.0.63; M4 on 1.0.62 (lost SQLite lock, 8 jobs running) - asked user: wait for 1.0.64 (recommended) or now. One-press fixes on branch fix/one-press-update-gaps (pushed); verify loop workflow wf_0017e08b-e6a (task w2hrflrqw) running there - read its journal, then add coordinator's UI follow-ups (a) offer Update now on service status error with newer downloaded release, (b) clear installingSince when agent leaves installing; skip (c) ws.ts markConnected (auth, needs user ok). Speed work rebased on main fe842153c2 (incl #497) at 64a3750a44, pushed as perf/update-install-speed-v2; workflow wf_86fe9b4c-254 done - read round 1/2 verifier findings in its journal (one low: prestate refusal during staging leaves release published), fix, open PR. Then PRs green+merge, cut 1.0.64 (proper release notes), roll fleet, verify; close 0957 (T-06 should say 1.0.64).
Intent board: .specweave/intents/board.jsonl — 0 open intents (planning state, not verification).

[Open the intent board](../../intents/board.jsonl)
Increment 0957-one-click-fast-updates (active) · tasks 1/6 done · ACs 1/7

## Done / Pending
| Task | State | By | Evidence / note |
|---|---|---|---|
| T-01 One press: service first, then the app, with a visible clock | open |  | handoff |
| T-02 Desktop: pending request, no downgrade, one download clock | open |  | handoff |
| T-03 The service catches up to the app's release | open |  | handoff |
| T-04 Release follow-ups: M4 hold, own-request cancel, retry cap, ShipIt, partial app | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/studio-release-followu |
| T-05 Faster service install with per-phase timings | open |  |  |
| T-06 Release 1.0.63 and check one press on the fleet | open |  |  |
1/6 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 5 open

## Decisions
_None recorded — see spec.md Approach._

## Files touched
UNCOMMITTED — commit or stash before anything destructive.
```
M .specweave/increments/0854-source-link-deprecation-pipeline/tasks.md
 M .specweave/increments/0948-link-projects-across-machines/spec.md
 M .specweave/metrics/release-timings.jsonl
?? .specweave/increments/0958-brace-shorthand-report-links-name-real-files/
?? .specweave/increments/0959-rename-sidebar-chats-by-double-click/
?? .specweave/increments/0960-follow-the-latest-until-the-reader-scrolls-up/
?? .specweave/increments/0961-thread-plan-umbrella-root/
?? .specweave/increments/0962-ac-traceability/
?? .specweave/increments/0963-paginated-increment-index/
?? .specweave/increments/0964-layout-discovery-root-impact/
?? .specweave/increments/0965-crafted-glyphs-no-brain-lock/
?? .specweave/increments/0966-run-on-add-to-machine/
?? .specweave/increments/0967-thread-handoff-mode/
?? .specweave/increments/0969-orchestrator-per-machine/
?? .specweave/increments/0970-phone-fleet-failover/
?? .specweave/increments/0971-one-issue-per-increment-sync/
?? .specweave/increments/0976-task-aware-model-routing/
?? .specweave/increments/0979-provision-fleet-machines/
```
Full diff: `.specweave/increments/0957-one-click-fast-updates/handoff.diff`

## Next steps
`specweave task claim T-01 0957-one-click-fast-updates` — One press: service first, then the app, with a visible clock

## Resume
1. `specweave pickup` prints the next task with its acceptance criteria, claims and branch state.
2. `specweave task claim <T-id> 0957-one-click-fast-updates` → implement → `specweave task done <T-id> --run "<test>"`.
3. Original transcript (optional): Claude Code: `claude -r <uuid>`.

---
<!-- Doc format v2 -->