# Agent Execution Learnings

## Team Composition
- **2-3 agents optimal** for most features; 5+ agents increases coordination overhead significantly
- Contract-first spawning (shared/database → backend/frontend) prevents integration surprises
- Phase 1 (upstream) agents MUST complete before Phase 2 (downstream) agents start

## Spawning
- **Always use `mode: "bypassPermissions"`** — agents cannot handle interactive trust-folder prompts
- **Use Opus model** for implementation agents — Sonnet misses edge cases in complex codebases
- Agent files live in `agents/` subdirectory of skills — Read the file and pass content as Task() prompt

## Token Efficiency
- Skills with `context: fork` run in isolated context — use for non-interactive skills (architect, planner, grill)
- PM skill stays in shared context (needs user interaction for interviews)
- Forked skills: ~60% token savings in main conversation

## Communication Protocol
- Agents signal via SendMessage: PLAN_READY → PLAN_APPROVED/REJECTED → CONTRACT_READY → COMPLETION
- Team-lead reviews ALL plans before approving — never auto-approve
- BLOCKING_ISSUE messages require immediate team-lead attention
