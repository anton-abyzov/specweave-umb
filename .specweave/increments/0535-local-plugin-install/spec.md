# Spec: Local Plugin Installation

## Problem
Running `frontend @ vskill` fails with "Plugin 'frontend' not found in marketplace 'vskill'" because the current system relies on on-demand marketplace lookups via LLM detection in user-prompt-submit.sh. This is fragile and installs to global `~/.claude/plugins/cache/` instead of project-local `.claude/skills/`.

## User Stories

### US-001: As a developer, I want plugins installed locally so they are always available
**ACs:**
- [x] AC-US1-01: `specweave init` copies all plugin skills into `.claude/skills/` at init time
- [x] AC-US1-02: No `claude plugin install` calls for sw-* plugins
- [x] AC-US1-03: Skills are in project `.claude/skills/`, not `~/.claude/skills/`

### US-002: As a developer, I want no on-demand marketplace lookups
**ACs:**
- [x] AC-US2-01: user-prompt-submit.sh does not call `claude plugin install` for plugins
- [x] AC-US2-02: LLM-based plugin detection no longer triggers installation
- [x] AC-US2-03: Increment detection still works in the hook
