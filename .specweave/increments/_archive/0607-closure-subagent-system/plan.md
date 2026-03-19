# Architecture Plan: Closure Subagent System

## Decision

Create a `sw-closer` subagent that wraps `sw:done` in a fresh context, following the same pattern as `sw-pm` wrapping `sw:pm`. Update team-lead, team-merge, do, and auto skills to spawn sw-closer instead of invoking closure inline.

## Architecture

```
CURRENT (broken):
  team-lead/auto context (bloated) → sw:done (loads grill + judge-llm + PM) → CONTEXT OVERFLOW

NEW:
  team-lead/auto context → Agent(sw:sw-closer) → [FRESH CONTEXT] → sw:done → grill → judge-llm → PM → specweave complete
```

## Components

### sw-closer subagent (agents/sw-closer.md)
- Follows sw-pm.md pattern: frontmatter with name, model, memory, skills
- Preloads sw:done (which internally chains grill, judge-llm, sync-docs)
- Retry awareness for Gate 0 desync failures

### close-all skill (skills/close-all/SKILL.md)
- Discovery: scan metadata.json for active/in-progress/ready_for_review with 0 pending tasks
- Claude Code: spawn sw-closer subagents sequentially (dependency order)
- Non-cloud: invoke sw:done directly per increment

### SKILL.md updates
- team-lead Section 8c: sw-closer subagents replace sw:team-merge delegation
- team-merge Step 4: add 4a/4b pattern (subagent vs direct)
- do Step 9: add 9a/9b pattern (subagent vs direct)
- auto Step 3.5: spawn sw-closer on all_complete_needs_closure

## Key Constraints
- `specweave complete <id> --yes` is the ONLY path to status=completed
- Sequential closure for dependency order (shared → backend → frontend)
- sw-closer must NOT modify source code — only fix closure metadata
- Non-cloud tools fall back to direct sw:done invocation
