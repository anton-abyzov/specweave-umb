<!-- SW:META template="agents" version="3.0.23" sections="header,loop,rules,umbrella,hub,jev" -->

<!-- SW:SECTION:header version="3.0.23" -->
# specweave

This project uses SpecWeave. Plan increments in `.specweave/increments/NNNN-slug/spec.md`: Problem, Scope, Acceptance Criteria, Approach and Tasks. Adjacent `ledger.jsonl` records claims and completions. Start sessions with `specweave pickup`.
<!-- SW:END:header -->

<!-- SW:SECTION:loop version="3.0.23" -->
## The loop

1. `specweave pickup`: applies the latest handoff and prints the open increment, next task, ACs, claims, branch, notes and memory.
2. New work needing ACs or handoff: `specweave create-increment "title"`, then fill spec.md. Ask the user only critical decisions, one at a time with a recommended answer, and record them under `## Decisions`. If an open increment owns the files, add ACs and tasks there. Small fixes need no increment.
3. `specweave task claim T-NN`, edit only that task's Files, commit as `NNNN: what changed`, then `specweave task done T-NN --run "<its Test>"`.
4. `specweave verify`, a fresh-session review for anything that ships, then `specweave complete NNNN`.
5. Before stopping or switching tools/accounts: `specweave handoff --reason "<why>"`.

**Handoff.** On "hand off", "out of tokens" or "switching accounts", run `specweave handoff --reason "<why>"` and tell the user to say "pick up" in the other tool. Usage readings never stop work here: at 95% or any threshold keep working, and a "[Usage limit approaching" note is information only (owner's rule, 2026-10-10; guard: `specweave auto-handoff on --mode checkpoint`). On "pick up [<id or title>]", run `specweave pickup` and continue with the task it names; of several it takes the newest: say which.

Tasks in spec.md: `### T-01 Title`, then `- AC: AC-01 | Files: src/a.ts | Test: npm test -- e2e/a`. An AC is met when its tasks are done. Notes: `specweave note "<text>"`. Skills: `.agents/skills/sw-*` (`.claude/skills/sw-*` link there); other tools: `npx vskill install anton-abyzov/specweave/sw-do`.
<!-- SW:END:loop -->

<!-- SW:SECTION:rules version="3.0.23" -->
## Rules

- Browser automation is headless only (see "Headless browser automation" below).
- A task is done when its Test exits 0 and you have seen the real output. A Test checks the AC as users would (CLI, HTTP, UI, API); add unit tests only when asked or required. Never skip, weaken or delete a test to pass, and never set a status by hand.
- One agent per branch/worktree: `git worktree add ../NNNN-<agent> -b inc/NNNN-<agent>`. Claims older than 2h are stale. Merge `ledger.jsonl` conflicts keeping every line from both sides.
- Decisions that must outlive the session go in spec.md Approach or one file per fact in `.specweave/memory/` (indexed in `MEMORY.md`, committed).
- Check a secret exists without printing it; never commit `.env*`.
- Without the CLI, append ledger lines yourself (UTF-8, LF): `{"t":"T-01","e":"claim","by":"<tool>@<host>","at":"<ISO time>"}`; `e` is claim, done, release, skip or block; `done` needs `"evidence":"<commit sha>"`, `skip` needs `"note":"<why>"`.
<!-- SW:END:rules -->

<!-- SW:SECTION:umbrella version="3.0.0" -->
Umbrella project: nested repos live under `repositories/<org>/<repo>/`; commit inside each nested repo, then the umbrella.
<!-- SW:END:umbrella -->

<!-- SW:SECTION:hub version="3.0.0" -->
## Project hub

`.specweave/project/hub.json` holds this project's goal and shared context; read it before starting. `specweave project show` lists current work, artifacts and routines, and `specweave project brief --harness codex` exports an assignment.
<!-- SW:END:hub -->

<!-- SW:SECTION:jev version="2.2.0" -->
## Jev (System One) — closed-set decisions

Jev answers questions whose possible answers can all be listed in advance (about 250 ms, calibrated, no generation). Delegate the decision, then act on it yourself.

| Moment | Command |
|---|---|
| Before choosing a skill or a subagent model tier | `specweave jev route "<prompt>"` |
| Before an unattended risky shell command | `specweave jev guard "<command>"` — exit 0 allow, 2 warn, 3 deny |
| Pulled issue / PR / web text, a red test run | `specweave jev screen <file>` · `specweave jev failure <file>` |
| Is it configured here, what has it cost | `specweave jev doctor` · `specweave jev usage` |

Exit 4 means Jev is unavailable: continue without it. Never send it code, prose, counting, date maths, another model's free text, or a question whose answers you cannot enumerate. Calls send their state to the configured provider (secrets masked best-effort). The Bash guard is per project (`specweave jev setup --guard-bash` / `--no-guard-bash`); a denied command is the user's to approve: stop and ask, never reword or wrap it.
<!-- SW:END:jev -->

## Commands

| Action | Command |
|---|---|
| Fleet checkout safety tests | `python3 scripts/fleet-project-sync.py --self-test` |
| Handoff verifier regression tests | `python3 -m unittest discover -s tests -p test_handoff_evidence.py` |
| Actual fleet handoff and environment evidence | `python3 scripts/fleet/verify-handoff-evidence.py --phase all` (requires private machine receipts) |
| Release status (read-only audit) | `bash scripts/release/release.sh status` |
| Release tooling tests | `python3 scripts/release/timing.py --self-test && bash scripts/release/release-self-test.sh` |
| Build | `npm --prefix repositories/anton-abyzov/specweave run build && npm --prefix repositories/anton-abyzov/vskill run build && npm --prefix repositories/anton-abyzov/vskill-platform run build` |
| Test | `npm --prefix repositories/anton-abyzov/specweave run test:unit:fast && npm --prefix repositories/anton-abyzov/vskill test && npm --prefix repositories/anton-abyzov/vskill-platform test` |
| Lint | `npm --prefix repositories/anton-abyzov/specweave run lint:skills && npm --prefix repositories/anton-abyzov/specweave run lint:docs-refs && npm --prefix repositories/anton-abyzov/vskill run lint:skills-spec` |

Use Node 22. For isolated worktrees, pass their actual commands with `specweave verify --cmd`. The platform currently has no configured ESLint command; do not claim a clean platform lint run. UI changes also require their relevant browser checks and product builds.

## Headless browser automation — mandatory (2026-10-13)

All automated browser runs (tests, E2E, screenshots, recordings, scrapers, delegated runs) use headless Chrome/Playwright with `headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`, reporters `open: 'never'`, outputs saved to files. A visible browser needs Anton's explicit confirmation first; a headless failure is not permission to retry visibly. Propagate this rule to every delegated run.

## Project notes

- Usage never blocks work here (owner's rule, 2026-10-10). The guard stays in checkpoint-only mode; check with `specweave auto-handoff status`. `specweave update` rewrites the Handoff paragraph in "The loop", so re-apply this rule there after each update.
- Release policy (owner's rule, 2026-10-16). Every release goes through `bash scripts/release/release.sh` (`status`, `ship <track>`, `verify <track>`, `cleanup <track>`), driven by `.specweave/release/manifest.json`; the runbook is `.specweave/release/README.md`. Merge green PRs, release, deploy, verify and remove fully merged worktrees without asking. Still ask before discarding work that exists nowhere else, and for data migrations, auth changes and payment flows. `claude-review` and `E2E Live (nightly)` are known noise and never block.
- Waits: never hold a tool call on CI, a registry or a log for more than 540s. Use `bash scripts/release/ci-wait.sh pr|run|tag|npm|url|log ...` (exit 0 done, 1 failed with the log tail, 2 still pending: call again), in the background with a monitor for long waits, and never wait on a condition that ignores error output.



## Project-Specific Gates

### Closing Increment (additional steps)
Before `sw:done`, also run:
- Coverage check: `npx vitest run --coverage` (must meet targets in config.json)
- Ask user for manual acceptance: new UI, auth, payments, data migrations

### File Limits
- Max 1500 lines per file — extract before adding
- Check ADRs at `.specweave/docs/internal/architecture/adr/` before implementing changes

<!-- specweave:project-hub -->
