<!-- SW:META template="agents" version="3.1.14" sections="header,loop,rules,umbrella,hub,jev" -->

<!-- SW:SECTION:header version="3.1.14" -->
# specweave

SpecWeave increments live in `.specweave/increments/NNNN-slug/spec.md`: Problem, Scope, Acceptance Criteria, Approach and Tasks. `ledger.jsonl` records claims and completions. Start with `specweave pickup`.
<!-- SW:END:header -->

<!-- SW:SECTION:loop version="3.1.14" -->
## The loop

1. `specweave pickup`: applies the latest handoff, prints the open increment, next task and ACs, claims, branch, notes and memory.
2. New work needing ACs or handoff: `specweave create-increment "title"`, then fill spec.md. Ask only critical decisions, one at a time with a recommendation, and record them under `## Decisions` (sw-increment). If an open increment owns the files, add ACs and tasks there. Recommended for features, not required; to skip one run `specweave small-fix "<why>"`. Close what you open: its plan ends with "Verify and close NNNN".
3. `specweave task claim T-NN`, edit only that task's Files, commit as `NNNN: what changed`, then `specweave task done T-NN --run "<its Test>"`. `--line`/`--link` feed `specweave cards --md`.
4. When the last task is done or skipped, without asking: `specweave verify`, a fresh-context review (subagent or new session) for anything that ships, `specweave complete NNNN`. PR-shipped work needs `task done` first.
5. Stopping with tasks left, or switching tools: `specweave handoff --reason "<why>"`.

**Handoff.** When the user says "hand off", "out of tokens" or "switching accounts", or "[Usage limit reached" appears (not in SpecWithCode or auto-handoff checkpoint mode), run `specweave handoff --reason "<why>"`; tell them to say "pick up" in the other tool. Usage readings never stop work here: at 95% or any threshold keep working, and a "[Usage limit approaching" note is information only (owner's rule, 2026-10-10; guard: `specweave auto-handoff on --mode checkpoint`). When the user says "pick up", run `specweave pickup`; continue through step 4, passing any given id/title. Take the newest handoff if several; say which.

Tasks in spec.md: `### T-01 Title`, then `- AC: AC-01 | Files: src/a.ts, tests/e2e/a.test.ts | Test: npm test -- e2e/a`. ACs derive from done tasks. Notes: `specweave note "<text>"`. Skills: `.agents/skills/sw-*` and `.claude/skills/sw-*`; other tools: `npx vskill install anton-abyzov/specweave/sw-do`.
<!-- SW:END:loop -->

<!-- SW:SECTION:rules version="3.1.14" -->
## Rules

- Use headless Chrome/Playwright CLI for browser tests and automation: `headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`, HTML reports `open: 'never'`. Save captures to files; propagate to subagents. Before opening an essential visible browser, ask the user and wait for explicit approval. Headless failure is not approval.
- A task is done when its Test exits 0 and you have seen the real output. A Test checks the AC as users would (CLI, HTTP, UI, API); add unit tests only when asked or when config or conventions require them. Never skip, weaken or delete a test to pass, and never set a status by hand.
- One agent per branch/worktree: `git worktree add <worktree root>/<repo>/NNNN-<agent> -b inc/NNNN-<agent>`, where the worktree root is SpecWithCode's configured one (never `../` or `.worktrees/`: from a repo here that lands in ~/Projects/github). Claims older than 2h are stale. On `ledger.jsonl` conflicts keep both sides' lines.
- Commit durable decisions in spec.md Approach or one fact per file in `.specweave/memory/`, indexed in `MEMORY.md`, for all tools.
- Check a secret exists without printing it; never commit `.env*`.
- Honor project identity and licensing. Keep provenance and required notices; never infer license grants or history rewrites from branding changes.
- Without the CLI, append ledger lines yourself, one JSON object per line, UTF-8, LF: `{"t":"T-01","e":"claim","by":"<tool>@<host>","at":"<ISO time>"}` (`e` is claim, done, release, skip or block; `done` needs `"evidence":"<commit sha>"`, `skip` needs `"note":"<why>"`).
<!-- SW:END:rules -->

<!-- SW:SECTION:umbrella version="3.0.0" -->
Umbrella project: nested repos live under `repositories/<org>/<repo>/`; commit inside each nested repo, then the umbrella.
<!-- SW:END:umbrella -->

<!-- SW:SECTION:hub version="3.1.14" -->
## Project hub

`.specweave/project/hub.json` holds this project's goal and shared context; read it before starting. `specweave project show` lists current work, artifacts and routines, and `specweave project brief --harness codex` exports an assignment for another tool.
<!-- SW:END:hub -->

<!-- SW:SECTION:jev version="3.1.14" -->
## Jev (System One) — closed-set decisions

Before an unattended risky shell command, run `specweave jev guard "<command>"`: exit 0 allow, 2 warn, 3 deny. Exit 4 means Jev is unavailable; continue without it. A denied command is the user's to approve: stop and ask, never reword or wrap it. Route, task, screen, failure, ask and browse, what each call sends to the provider, and the guard hook and prefilter are in the sw-jev skill.
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

- Nothing new goes directly in ~/Projects/github (owner's rule, 2026-10-26); it holds only the owner's repos. Worktrees: SpecWithCode's configured worktree root, `<root>/<repo>/<slug>`. Scratch, probes and run logs: the session scratchpad or `~/.specwithcode/m4/scratch/<date>-<task>/`. Evidence, screenshots and receipts: the increment's `reports/`, else `~/.specwithcode/m4/evidence/<topic>/`. Archive old evidence to `/Volumes/SanDisk APFS/Archive/specwithcode/` (KINGSTON is video only). Before removing any worktree or folder, check it is not a SpecWithCode project root or thread folder (`specweave-studio db query --base-dir ~/.specwithcode/m4 "select json_extract(payload_json,'$.worktreePath') from orchestration_v2_projection_threads"`), whatever its PR state; removing one breaks that thread.
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

## SpecWithCode identity and source terms

SpecWithCode is an independent product. Lead with its own settings, orchestration and portable handoffs; do not market it as a T3 Code fork. Preserve accurate source provenance, required third-party copyright and permission notices, and existing license grants. Do not add a project-wide MIT grant or contributor showcase. Keep development history, active branches and sessions intact; publish sanitized public snapshots through the owning repository's mirror script.
