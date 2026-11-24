# Verify — 0933-task-cards-on-the-ledger

PASS · 2026-10-21T06:30:22.358Z · commands from explicit

## Commands

### `cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/node_modules/vitest/vitest.mjs run /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/tests/unit/core/tasks/cards.test.ts /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/tests/unit/core/tasks/ledger.test.ts --maxWorkers=1 --no-file-parallelism` → exit 0 (5s)

```

 RUN  v4.1.11 /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave

 ✓ tests/unit/core/tasks/cards.test.ts (20 tests) 6ms
 ✓ tests/unit/core/tasks/ledger.test.ts (7 tests) 32ms

 Test Files  2 passed (2)
      Tests  27 passed (27)
   Start at  02:28:58
   Duration  2.51s (transform 939ms, setup 594ms, import 559ms, tests 38ms, environment 0ms)
```

### `cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/node_modules/vitest/vitest.mjs run /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/tests/unit/cli/commands/card.test.ts /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/tests/unit/core/session/pickup.test.ts --maxWorkers=1 --no-file-parallelism` → exit 0 (42s)

```

 RUN  v4.1.11 /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave

 ✓ tests/unit/core/session/pickup.test.ts (19 tests) 26417ms
     ✓ prints the next task with its acceptance criteria, derived AC status and others' claims  9524ms
     ✓ shows the next task's AC text and the claim command  332ms
     ✓ shows the caller's own claims instead of a next task  765ms
     ✓ shows the last handoff event, notes and the memory index  596ms
     ✓ shows the newest local checkpoint only when it is newer than the last handoff  1141ms
     ✓ lists several open increments and asks for one  3279ms
     ✓ says how to start when nothing is open  675ms
     ✓ appends a note event that pickup shows  739ms
     ✓ snapshots a same-size edit made in the same second as the last commit  3269ms
     ✓ pushes the branch and a WIP snapshot without touching the index or branch  2985ms
     ✓ releases the agent's claims and records the handoff, which pickup then shows  590ms
     ✓ prints the checklist first, then the next task, then the notes  830ms
     ✓ prints branch cards when no increment is open  1167ms
 ✓ tests/unit/cli/commands/card.test.ts (8 tests) 1313ms
     ✓ stores line and link on the ledger events  352ms
     ✓ prints header, blank line, then one line per card in ledger order  321ms
     ✓ card add/start/done/wait write .specweave/cards/<branch-slug>.jsonl with C-NN ids  391ms

 Test Files  2 passed (2)
      Tests  27 passed (27)
   Start at  02:29:03
   Duration  39.31s (transform 10.25s, setup 1.24s, import 9.47s, tests 27.73s, environment 0ms)
```

### `cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/node_modules/vitest/vitest.mjs run /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/tests/unit/core/tasks/verify-runner.test.ts /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/tests/unit/core/lifecycle/LifecycleHookDispatcher.test.ts --maxWorkers=1 --no-file-parallelism` → exit 0 (7s)

```

 RUN  v4.1.11 /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave

 ✓ tests/unit/core/lifecycle/LifecycleHookDispatcher.test.ts (5 tests) 227ms
 ✓ tests/unit/core/tasks/verify-runner.test.ts (6 tests) 357ms

 Test Files  2 passed (2)
      Tests  11 passed (11)
   Start at  02:29:45
   Duration  4.36s (transform 1.87s, setup 365ms, import 1.79s, tests 584ms, environment 0ms)
```

### `cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && npm run lint:standalone-skills && npm run lint:docs-refs` → exit 0 (3s)

```

> specweave@3.1.4 lint:standalone-skills
> node scripts/lint-standalone-skills.mjs

lint-standalone-skills: OK

> specweave@3.1.4 lint:docs-refs
> node scripts/lint-docs-refs.mjs

docs-refs: OK — 97 pages, 6 skills, 60 CLI commands.
```

### `cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/node_modules/vite-plus/bin/vp test run /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/server/src/mods/__tests__/SpecweaveProgress.cards.test.ts /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/web/src/studio/threadPlanProgress.test.ts --maxWorkers=1 --no-file-parallelism` → exit 0 (14s)

```
note: You are running `vp test` as a Vite+ built-in command. If you meant to run the test npm script, use `vpr test` instead.

 RUN  v5.0.1 /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio


 Test Files  2 passed (2)
      Tests  41 passed (41)
   Start at  02:29:59
   Duration  7.03s (transform 69%, import 26%, tests 3%, setup 1%)

  Transform  transforming modules took 4.46s · 69% of tracked time, re-done on every run
             persist transforms across runs with fsModuleCache: true
             learn more: https://vitest.dev/guide/improving-performance#caching-between-reruns
```

### `/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /opt/homebrew/lib/node_modules/specweave/bin/specweave.js cards 0930 --md | grep -q 'pull/348' && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /opt/homebrew/lib/node_modules/specweave/bin/specweave.js cards 0931 --md | grep -q 'pull/2081'` → exit 0 (8s)

```
(no output)
```

### `cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/node_modules/vitest/vitest.mjs run /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/src/core/tasks/verify-and-gate.test.ts --maxWorkers=1 --no-file-parallelism` → exit 0 (2s)

```

 RUN  v4.1.11 /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave

 ✓ src/core/tasks/verify-and-gate.test.ts (5 tests) 196ms

 Test Files  1 passed (1)
      Tests  5 passed (5)
   Start at  02:30:21
   Duration  590ms (transform 206ms, setup 71ms, import 167ms, tests 196ms, environment 0ms)
```

## Acceptance criteria

11/11 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | A ledger event may carry `line` (max 100 chars) and `link`; `formatLedgerLine` and `parseLedger` keep them, older lines without them still parse, and an unknown key is still ignored. |
| AC-02 | x (tasks) | `foldLedger` exposes per task `card: { state: todo\|doing\|waiting\|done\|skipped, line, link }` where line falls back to the task title and link falls back to a PR URL, `log:` path or `HEAD <sha>` found in the evidence, in that order. |
| AC-03 | x (tasks) | `specweave task claim\|done\|block` accept `--line` and `--link`; `specweave card add\|start\|done\|wait\|list` exist as thin aliases; `specweave cards --md` prints a header line, a blank line, then one `✓ / ✱ / ○ text (link)` line per card in ledger order. |
| AC-04 | x (tasks) | `specweave pickup` prints the card checklist before the next task; the latest notes follow it. |
| AC-05 | x (tasks) | `specweave verify` exits 1 with "no test commands configured" when the command list is empty, unless `--reason` is given; the umbrella `.specweave/config.json` has `testing.commands` from its Commands table. |
| AC-06 | x (tasks) | `specweave card add "<text>"` on a branch with no bound increment appends to `.specweave/cards/<branch-slug>.jsonl` with ids `C-NN`; `specweave complete` refuses an increment whose spec.md has no ACs unless `--reason` is given. |
| AC-07 | x (tasks) | `onIncrementDone` runs the GitHub and ADO closure even when living docs sync is skipped; living docs sync is skipped with one log line when the spec has no user stories. |
| AC-08 | x (tasks) | SpecWithCode `ThreadIncrementTask` carries `line` and `link` (https URLs, or paths inside the increment directory after realpath), the server fold fills them, StepRow renders the line as a link, done rows read in the past tense and the current row is emphasised; a done row without a link shows "unverified". |
| AC-09 | x (tasks) | A thread whose worktree branch matches an increment's `inc/NNNN` branch or whose ledger names the branch is bound to it without a claim file. |
| AC-10 | x (tasks) | One JSON fixture of ledger lines and expected cards is run by specweave's ledger tests and by SpecWithCode's SpecweaveProgress tests. |
| AC-11 | x (tasks) | 0930 and 0931 have ledger lines whose cards link PR #348 and PR #2081. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | HEAD 98e4326a0 on https://github.com/anton-abyzov/specweave… |  |
| T-02 | done | claude@antons-macbook-m4max | HEAD 72ed4b5cf (+d4dfb8900 completions, dfb35fd78 unborn br… |  |
| T-03 | done | claude@antons-macbook-m4max | HEAD e760f2fc6 (+8e748b997 e2e fixtures) on https://github.… |  |
| T-04 | done | claude@antons-macbook-m4max | HEAD 025e6211b on https://github.com/anton-abyzov/specweave… |  |
| T-05 | done | claude@antons-macbook-m4max | HEAD 79a011c39 on https://github.com/anton-abyzov/specwithc… |  |
| T-06 | done | claude@antons-macbook-m4max | node /Users/antonabyzov/Projects/github/wt-0932-0934/specwe… |  |

6/6 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
