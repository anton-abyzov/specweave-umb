# Verify — 1145-hand-off-the-coordinator-of-a-large-project

PASS · 2026-11-02T03:32:06.616Z · commands from explicit

## Commands

### `gh pr checks 1171 -R anton-abyzov/specwithcode-dev --required` → exit 0 (1s)

```
Changed paths	pass	7s	https://github.com/anton-abyzov/specwithcode-dev/actions/runs/41381984122/job/125074654957	
PR Gate	pass	6s	https://github.com/anton-abyzov/specwithcode-dev/actions/runs/41381984122/job/125079159263	
PR Gate (typecheck)	pass	13m17s	https://github.com/anton-abyzov/specwithcode-dev/actions/runs/41381984122/job/125074760128	
```

## Acceptance criteria

5/5 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x | A coordinator handoff of a project with more than 100 threads and more than 2 MB of history succeeds; the bundle stays within MACHINE_HANDOFF_MAX_BYTES. |
| AC-02 | x | The destination coordinator receives its own recent history and a summary list of the workers, and says how many older messages and threads stayed on the source. |
| AC-03 | x | A small project still carries full transcripts as before; older peers still accept the bundle. |
| AC-04 | x | The user docs describe what a coordinator handoff carries. |
| AC-05 | x | Past the worker cap, the summaries name threads that need the person, run or are pinned before open, resolved and archived ones; a resolved thread's old flags do not count. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | gh pr view 1055 -R anton-abyzov/specwithcode-dev --json sta… |  |
| T-02 | done | claude@antons-macbook-m4max | git -C repositories/anton-abyzov/specweave-studio show orig… |  |
| T-03 | claimed | claude@antons-macbook-m4max |  |  |
| T-04 | done | claude@antons-macbook-m4max | gh pr checks 1171 -R anton-abyzov/specwithcode-dev --requir… |  |

3/4 done · 0 skipped · 1 claimed · 0 blocked · 0 stale · 0 open
