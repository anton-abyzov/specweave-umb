# Handoff — 0990-portable-project-copy Portable project copy with active work
agent: codex-copy-lead · 2026-10-22T00:48:17.485Z · branch codex/0990-portable-project-copy @ cb69ba08d · tree: 2 uncommitted · redactions: 0
active claims: T-04 (blocked by codex-copy-lead)

## Where I left off
Why: Manual UI acceptance pending; source implementation and isolated Linux proof are ready.
Product repo /Users/antonabyzov/.specwithcode/m4/worktrees/codex-0990-copy, branch codex/0990-portable-project-copy, HEAD 56b6cf73da758c9a76286c3272783151175d7eb4, PR https://github.com/anton-abyzov/specwithcode-dev/pull/586. 246 focused tests, coverage, web/server builds, four headless cases and independent review passed. Real ministorm transfer verified 6210 files, 878 MB, four repos, Git/content/Undo and unchanged live service. Increment 0990 verify commands passed; AC04 stays open for manual acceptance.

Intent board: .specweave/intents/board.jsonl — 0 open intents (planning state, not verification).

[Open the intent board](../../intents/board.jsonl)
Increment 0990-portable-project-copy (active) · tasks 4/5 done · ACs 3/4
Gotcha: Do not take over 0957/0988 or change their worktrees. Private raw evidence stays untracked. Source original worktrees are unchanged. No live coordinator migration, installed release or permanent full-umbrella copy is claimed.

## Done / Pending
| Task | State | By | Evidence / note |
|---|---|---|---|
| T-01 Active copy backend | done | codex-copy-backend | 4a655b3cf integrated backend;188 focused tests16files passed |
| T-02 Destination paths and clear copy flow | done | codex-copy-ui | cd /Users/antonabyzov/Projects/github/specweave-copy-ui && P |
| T-03 Real Linux transfer proof | done | codex-copy-remote | Production transfer code to ministorm Linux passed:6210 file |
| T-04 Documentation, integrated review and completion | blocked | codex-copy-lead | Source ready at specwithcode-dev PR586 HEAD56b6cf73d.246 foc |
| T-05 Recover a copied snapshot without losing an ownership fence | done | codex-copy-backend | Integrated f1b804483 at current cc04dfe68. Recovery proof: 2 |
4/5 done · 0 skipped · 0 claimed · 1 blocked · 0 stale · 0 open

## Decisions
_None recorded — see spec.md Approach._

## Files touched
UNCOMMITTED — commit or stash before anything destructive.
```
M .specweave/increments/0990-portable-project-copy/spec.md
?? .specweave/increments/0990-portable-project-copy/evidence/
```
Full diff: `.specweave/increments/0990-portable-project-copy/handoff.diff`

## Next steps
Obtain manual acceptance of the updated UI requested in this chat. Check PR586 exact-head CI; fix any failures, then use the umbrella release workflow after acceptance. Recheck owners before release. Complete T04 and verify/close 0990 only after its gates pass.

## Resume
1. `specweave pickup` prints the next task with its acceptance criteria, claims and branch state.
2. `specweave task claim <T-id> 0990-portable-project-copy` → implement → `specweave task done <T-id> --run "<test>"`.
3. Original transcript (optional): Claude Code: `claude -r <uuid>` · Codex: `codex resume <uuid>` · OpenCode: `opencode -s <id>`.

---
<!-- Doc format v2 -->