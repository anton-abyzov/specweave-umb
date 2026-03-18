# General Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-03-18**: Store project-specific custom skills in the project's `.claude/commands/` directory, not in the global user `.claude/commands/` folder
- **2026-03-18**: SpecWeave team cleanup: Phase 3 tmux pane kill script is MANDATORY (only mechanism to close orphaned panes showing 'Resume this session'). SendMessage shutdown_request does NOT close panes. Required for all team-lead modes (brainstorm/planning/research/testing) and team-merge. Script must run even if orchestrator not in tmux.
