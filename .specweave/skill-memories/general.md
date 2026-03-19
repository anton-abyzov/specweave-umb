# General Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-03-19**: Store project-specific custom skills in the project's `.claude/commands/` directory, not in the global user `.claude/commands/` folder
- **2026-03-19**: SpecWeave team cleanup: Phase 3 tmux pane kill script is MANDATORY (only mechanism to close orphaned panes showing 'Resume this session'). SendMessage shutdown_request does NOT close panes. Required for all team-lead modes (brainstorm/planning/research/testing) and team-merge. Script must run even if orchestrator not in tmux.
- **2026-03-19**: Avoid adding deprecation warnings or defensive code to legitimate utility tools when root cause is fixed elsewhere. If documentation misdirects usage and that documentation is being corrected, skip tool-level defenses—prefer fixing the source.
- **2026-03-19**: Explicit /sw:team-lead invocation = MUST create real teams via TeamCreate, not just print phase plans (exception: trivial work <3 tasks, single file)
- **2026-03-19**: Skill() tool expects bare skill identifiers without the `/` prefix — the slash is only a UI trigger character for CLI input, not part of the tool parameter. Use "sw:do" not "/sw:do" when invoking skills programmatically
- **2026-03-19**: sync-progress command's auto-create step duplicates JIRA/ADO issues already created by living-docs sync. Workaround: use --no-create or --no-jira --no-ado flags for GitHub-only sync
