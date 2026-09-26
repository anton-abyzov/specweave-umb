<!-- SW:META template="agents" version="3.0.0" sections="header,loop,rules,umbrella,hub,jev" -->

<!-- SW:SECTION:header version="3.0.0" -->
# specweave

This project uses SpecWeave. Work is planned in increments: `.specweave/increments/NNNN-slug/spec.md` holds Problem, Scope, Acceptance Criteria, Approach and Tasks, and `ledger.jsonl` beside it records who claimed and finished what. Start every session with `specweave pickup`.
<!-- SW:END:header -->

<!-- SW:SECTION:loop version="3.0.0" -->
## The loop

1. `specweave pickup`: brings in the latest handoff, then prints the open increment, the next task with its acceptance criteria, claims held by others, branch state, notes and project memory.
2. New work that needs acceptance criteria or a handoff: `specweave create-increment "title"`, then fill in spec.md. If an open increment already owns the files, add ACs and tasks to it instead of opening another. Small self-contained fixes need no increment.
3. `specweave task claim T-NN`, edit only that task's Files, commit as `NNNN: what changed`, then `specweave task done T-NN --run "<its Test>"`.
4. `specweave verify`, a review in a fresh session for anything that ships, then `specweave complete NNNN`.
5. Stopping for any reason (out of tokens, switching tool or account): `specweave handoff --reason "<why>"`.

**Handoff in two words.** When the user says "hand off", "I'm out of tokens" or "switching accounts", or a "[Usage limit approaching" or "[Usage limit reached" note asks you to checkpoint, run `specweave handoff --reason "<why>"` and tell the user to say "pick up" in the other tool. When the user says "pick up" or "continue from the other account", run `specweave pickup` and carry on with the task it names. `specweave report` writes an HTML timeline; `specweave auto-handoff on` hands off by itself at 90% of the limit.

Tasks live in spec.md as `### T-01 Title` followed by `- AC: AC-01 | Files: src/a.ts, src/a.test.ts | Test: npm test -- a`. An AC is met when the tasks covering it are done. Leave a message for whoever works on an increment next with `specweave note "<text>"`. Each step is a skill in `.agents/skills/sw-*` and `.claude/skills/sw-*`; other tools: `npx vskill install anton-abyzov/specweave/sw-do`.
<!-- SW:END:loop -->

<!-- SW:SECTION:rules version="3.0.0" -->
## Rules

- A task is done when its Test exits 0 and you have seen the real output. Never skip, weaken or delete a test to pass, and never set a status by hand.
- One agent per branch and worktree: `git worktree add ../NNNN-<agent> -b inc/NNNN-<agent>`. A claim older than 2h is stale. On a merge conflict in `ledger.jsonl` keep every line from both sides.
- Decisions that must outlive this session go in spec.md Approach, or as one file per fact in `.specweave/memory/` with a line in its `MEMORY.md` index. Memory is committed, so every tool and account sees it.
- Check a secret exists without printing it; never commit `.env*`.
- Without the CLI, append ledger lines yourself, one JSON object per line, UTF-8, LF: `{"t":"T-01","e":"claim","by":"<tool>@<host>","at":"<ISO time>"}` (`e` is claim, done, release, skip or block; `done` needs `"evidence":"<commit sha>"`, `skip` needs `"note":"<why>"`).
<!-- SW:END:rules -->

<!-- SW:SECTION:umbrella version="3.0.0" -->
Umbrella project: nested repos live under `repositories/<org>/<repo>/`; commit inside each nested repo, then the umbrella.
<!-- SW:END:umbrella -->

<!-- SW:SECTION:hub version="3.0.0" -->
## Project hub

`.specweave/project/hub.json` holds this project's goal and shared context; read it before starting. `specweave project show` lists current work, artifacts and routines, and `specweave project brief --harness codex` exports an assignment for another tool.
<!-- SW:END:hub -->

<!-- SW:SECTION:jev version="2.2.0" -->
## Jev (System One) — closed-set decisions

Jev answers questions whose every possible answer can be written down in advance: about 250 ms, about $0.00002, calibrated probabilities, no generation. Delegate the decision, then act on it yourself.

| Moment | Command |
|---|---|
| Before choosing a skill or a subagent model tier | `specweave jev route "<prompt>"` |
| Picking the tier for one task already in the ledger | `specweave jev task T-NN` — a suggestion you act on; nothing re-routes models behind you |
| Before an unattended risky shell command | `specweave jev guard "<command>"` — exit 0 allow, 2 warn, 3 deny |
| Pulled issue / PR / web text, a red test run | `specweave jev screen <file>` · `specweave jev failure <file>` |
| Any other closed set of your own | `specweave jev ask --state @state.json --questions @q.json` |
| Mechanical browser navigation (headless only) | `specweave jev browse --goal "<goal>" --url "<url>"` |
| Is it configured here, what has it cost | `specweave jev doctor` · `specweave jev usage` |

Exit 4 means Jev is unavailable — continue without it. Never send Jev code, prose, compaction, counting or date maths, another model's free-text output, or a question whose answers you cannot enumerate. Below `jev.thresholds.route` treat the answer as no answer.

Every call sends its state — prompt text, task titles and ACs, the shell command, test-output tails, screened text, page text and element names — to the configured provider under the user's own key; secret-shaped values are masked heuristically first, best-effort only.

The Bash guard is per project (`specweave jev setup --guard-bash` writes the config flag, the `.specweave/state/jev-guard.enabled` marker and a project-level `PreToolUse` hook; `--no-guard-bash` removes all three). A regex prefilter skips Jev for `npm test`, `npm run build|test|lint`, `pnpm/yarn test`, `cargo test`, `go test` and plain read commands, so project-defined scripts are trusted by the guard. A denied command is the user's to approve — stop and ask; do not reword it, wrap it or edit config around it.
<!-- SW:END:jev -->

## Commands

| Action | Command |
|---|---|
| Build | `npm --prefix repositories/anton-abyzov/specweave run build && npm --prefix repositories/anton-abyzov/vskill run build && npm --prefix repositories/anton-abyzov/vskill-platform run build` |
| Test | `npm --prefix repositories/anton-abyzov/specweave run test:unit:fast && npm --prefix repositories/anton-abyzov/vskill test && npm --prefix repositories/anton-abyzov/vskill-platform test` |
| Lint | `npm --prefix repositories/anton-abyzov/specweave run lint:skills && npm --prefix repositories/anton-abyzov/specweave run lint:docs-refs && npm --prefix repositories/anton-abyzov/vskill run lint:skills-spec` |

Use Node 22. For isolated worktrees, pass their actual commands with `specweave verify --cmd`. The platform currently has no configured ESLint command; do not claim a clean platform lint run. UI changes also require their relevant headless browser checks and product builds.

## Project notes

(architecture map, things agents get wrong here, recurring mistakes — keep it short)

## Available Subagent Types

SpecWeave uses specialized subagents for different phases of the increment workflow. These run in isolated contexts to keep the main agent's context clean.

| Subagent | Purpose | When to Use |
|----------|---------|-------------|
| `sw:sw-closer` | Runs full `sw:done` closure pipeline in fresh context | After team-lead/team-merge completes, prevents context overflow |
| `sw:sw-pm` | Writes spec.md with user stories and acceptance criteria | During `sw:increment` planning phase |
| `sw:sw-architect` | Writes plan.md with architecture decisions | During `sw:increment` planning phase |
| `sw:sw-planner` | Writes tasks.md with BDD test plans | During `sw:increment` planning phase |

Agent definitions live in `plugins/specweave/agents/`. The team-lead orchestrator spawns these automatically when needed.

## Project Overview

Umbrella repo containing SpecWeave and related repositories under `repositories/anton-abyzov/`.

## Project-Specific Gates

### Closing Increment (additional steps)
Before `sw:done`, also run:
- Coverage check: `npx vitest run --coverage` (must meet targets in config.json)
- Ask user for manual acceptance: new UI, auth, payments, data migrations

### File Limits
- Max 1500 lines per file — extract before adding
- Check ADRs at `.specweave/docs/internal/architecture/adr/` before implementing changes

<!-- specweave:project-hub -->
## Shared project context
Read .specweave/project/hub.json for the project goal, shared context, artifacts and routine definitions. Run `specweave project show` for current work and `specweave project brief` for a fresh coordinator brief. Use native task tools only within user authorization. Routines are definitions until configured in the host scheduler.
<!-- /specweave:project-hub -->
