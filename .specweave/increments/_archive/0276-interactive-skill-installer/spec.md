---
increment: 0276-interactive-skill-installer
title: "Interactive Skill Installation Wizard"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Interactive Skill Installation Wizard

## Overview

Add a multi-step interactive installation wizard to the vskill CLI that matches the UX of `npx skills` (vercel-labs/skills). When a user runs `vskill install owner/repo` (or `vskill install owner/repo`) and the repo contains multiple skills, the CLI presents an interactive flow with:

1. **Skill selection** -- toggle individual skills or select all
2. **Agent detection** -- show all 39 agents with installed status
3. **Install target** -- choose all detected agents vs specific agents
4. **Installation scope** -- project-level vs global
5. **Installation method** -- symlink (recommended) vs copy

Non-interactive bypass via `--yes` flag for CI/scripting. All existing non-interactive single-skill installs continue to work unchanged.

## User Stories

### US-001: Interactive Skill Selection (P1)
**Project**: vskill

**As a** developer installing skills from a multi-skill repository
**I want** an interactive prompt listing all discovered skills with toggle selection
**So that** I can pick exactly which skills to install instead of getting all of them automatically

**Acceptance Criteria**:
- [x] **AC-US1-01**: When a repo contains 2+ skills, the CLI displays a numbered list with checkboxes showing each skill name and description
- [x] **AC-US1-02**: User can toggle individual skills on/off by entering their number
- [x] **AC-US1-03**: An "all" option selects or deselects every skill at once
- [x] **AC-US1-04**: Pressing Enter/Return confirms the current selection and proceeds to the next step
- [x] **AC-US1-05**: When a repo contains exactly 1 skill, the skill selection step is skipped (auto-selected)
- [x] **AC-US1-06**: When `--yes` flag is provided, all skills are auto-selected (no prompt)

---

### US-002: Interactive Agent Target Selection (P1)
**Project**: vskill

**As a** developer with multiple AI agents installed
**I want** to interactively choose which agents receive the skills
**So that** I can install skills only to the agents I actively use

**Acceptance Criteria**:
- [x] **AC-US2-01**: After skill selection, the CLI shows all detected agents with checkboxes (pre-checked)
- [x] **AC-US2-02**: User can toggle individual agents by entering their number
- [x] **AC-US2-03**: An "all" option selects or deselects every detected agent
- [x] **AC-US2-04**: When only 1 agent is detected, the agent selection step is skipped (auto-selected)
- [x] **AC-US2-05**: When `--agent <id>` flag(s) are provided, agent selection step is skipped (use specified agents)
- [x] **AC-US2-06**: When `--yes` flag is provided, all detected agents are auto-selected (no prompt)

---

### US-003: Interactive Scope Selection (P1)
**Project**: vskill

**As a** developer choosing between project-level and global skill installation
**I want** a prompt asking whether to install to the current project or globally
**So that** I can make an informed decision about where skills live

**Acceptance Criteria**:
- [x] **AC-US3-01**: After agent selection, the CLI prompts "Install scope: (1) Project [recommended] or (2) Global?"
- [x] **AC-US3-02**: Project scope installs to `<project-root>/<agent.localSkillsDir>/`
- [x] **AC-US3-03**: Global scope installs to `<agent.globalSkillsDir>/`
- [x] **AC-US3-04**: When `--global` flag is provided, scope selection is skipped (global)
- [x] **AC-US3-05**: When `--yes` flag is provided, defaults to project scope (no prompt)

---

### US-004: Interactive Install Method Selection (P1)
**Project**: vskill

**As a** developer installing skills to multiple agents
**I want** to choose between symlink and copy installation methods
**So that** I can use symlinks for deduplication or copies for portability

**Acceptance Criteria**:
- [x] **AC-US4-01**: After scope selection, the CLI prompts "Install method: (1) Symlink [recommended] or (2) Copy?"
- [x] **AC-US4-02**: Symlink mode copies skills to a canonical `.agents/skills/<name>/` directory, then creates relative symlinks from each agent's skills directory
- [x] **AC-US4-03**: Copy mode copies skills directly to each agent's directory independently
- [x] **AC-US4-04**: If symlink creation fails (e.g., Windows without Dev Mode), falls back to copy with a warning
- [x] **AC-US4-05**: When `--yes` flag is provided, defaults to symlink (no prompt)

---

### US-005: Pre-Install Summary and Confirmation (P2)
**Project**: vskill

**As a** developer about to install skills
**I want** to see a summary of what will be installed before it happens
**So that** I can verify and abort if something looks wrong

**Acceptance Criteria**:
- [x] **AC-US5-01**: After all selections are made, display a summary showing: selected skills, target agents, scope, and method
- [x] **AC-US5-02**: Prompt "Proceed? (Y/n)" before starting installation
- [x] **AC-US5-03**: Entering "n" or "N" aborts the installation cleanly
- [x] **AC-US5-04**: When `--yes` flag is provided, the confirmation is skipped

---

### US-006: Non-Interactive Mode (`--yes` / `-y` flag) (P1)
**Project**: vskill

**As a** developer using vskill in CI pipelines or scripts
**I want** a `--yes` flag that skips all interactive prompts
**So that** installations can run unattended with sensible defaults

**Acceptance Criteria**:
- [x] **AC-US6-01**: `--yes` (or `-y`) flag is available on the `install`/`add` command
- [x] **AC-US6-02**: With `--yes`, defaults are: all skills, all detected agents, project scope, symlink method
- [x] **AC-US6-03**: `--yes` can be combined with `--agent`, `--global` to override specific defaults
- [x] **AC-US6-04**: When stdin is not a TTY (piped/CI), the CLI behaves as if `--yes` was specified

## Functional Requirements

### FR-001: Prompt Utilities Module
A new `src/utils/prompts.ts` module providing interactive prompt functions built on Node.js `readline`:
- `promptCheckboxList(items, options)`: Multi-select with toggle, "all" option
- `promptChoice(question, choices)`: Single choice from numbered options
- `promptConfirm(question, defaultYes)`: Yes/No confirmation
- `isTTY()`: Check if stdin/stdout are interactive terminals

No external dependencies (no `@clack/prompts`, `inquirer`, etc.). Uses only `node:readline`.

### FR-002: Canonical Skills Directory
For symlink mode, skills are stored in a canonical `.agents/skills/<name>/` directory (project-level) or `~/.agents/skills/<name>/` (global). Non-universal agents get symlinks pointing from `<agent-dir>/<name>/` to the canonical location. Universal agents read from the canonical directory directly.

### FR-003: Install Method Orchestration
A new `installWithMethod(skills, agents, opts)` function in the add command that:
1. Iterates selected skills
2. For each skill, runs security scan
3. For each passing skill, installs via the chosen method (symlink or copy)
4. Updates lockfile with all installed skills

## Success Criteria

- All existing non-interactive `vskill install` / `vskill install` usage continues to work unchanged
- When stdin is not a TTY, behaves identically to `--yes` mode
- All 39 agents display correctly in the agent selection prompt
- Symlink mode creates valid relative symlinks that work when cd'ing into the project
- All existing tests pass; new tests added for prompt utilities and install methods
- `--yes` flag documented in `--help` output

## Out of Scope

- Config file-based preferences (`.vskillrc`, persistent agent selection)
- Interactive search/browse of the registry (separate `vskill find` command)
- Rollback or undo after installation
- Telemetry/analytics for interactive choices
- Windows-specific junction/mklink support (symlink fallback to copy is sufficient)

## Dependencies

- No new external dependencies -- uses only `node:readline` (built-in)
- Depends on existing: `agents-registry.ts`, `agent-filter.ts`, `project-root.ts`, `output.ts`
- Increment 0265 (smart project root + per-agent targeting): completed
