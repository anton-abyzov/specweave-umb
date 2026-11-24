<!-- SW:META template="agents" version="3.1.24" sections="header" -->

<!-- SW:SECTION:header version="3.1.24" -->
# specweave

This project plans work with SpecWeave: `specweave pickup` prints the open increment, the next task and its acceptance criteria. The sw-* skills in `.agents/skills/` and `.claude/skills/` carry the rest (plan, do, review, done, handoff).
<!-- SW:END:header -->

## Commands

| Action | Command |
|---|---|
| Build | TODO: not detected — fill in the build command |
| Test | TODO: not detected — fill in the test command |
| Lint | TODO: not detected — fill in the lint command |

If a cell still says TODO, fill it in from `package.json`/`Makefile` and commit; `specweave verify` runs these rows.

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
