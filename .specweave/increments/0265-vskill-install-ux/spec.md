---
increment: 0265-vskill-install-ux
title: "vskill install UX: smart directory resolution and agent selection"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: vskill install UX: smart directory resolution and agent selection

## Overview

Two UX improvements to `vskill install`:

1. **Smart directory resolution** -- walk up from cwd to find the project root (`.git/`, `package.json`, etc.) so skills install to the correct location regardless of which subdirectory the user is in.
2. **Agent selection** -- allow `--agent <id>` to install to a specific agent instead of blindly installing to all detected agents.

## User Stories

### US-001: Smart Project Root Detection (P1)
**Project**: vskill

**As a** developer running `vskill install` from a subdirectory
**I want** the CLI to automatically find my project root
**So that** skills are installed in the correct location (e.g., `.claude/commands/` at the project root) instead of relative to my current working directory

**Acceptance Criteria**:
- [ ] **AC-US1-01**: When running `vskill install` from a subdirectory (e.g., `src/components/`), the CLI walks up the directory tree to find the project root by looking for marker files (`.git/`, `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `.specweave/`, `vskill.lock`)
- [ ] **AC-US1-02**: When a project root is found, local skills install to `<project-root>/<agent.localSkillsDir>` instead of `<cwd>/<agent.localSkillsDir>`
- [ ] **AC-US1-03**: When no project root is found (walking up to filesystem root), fall back to `cwd` (current behavior) and print a warning
- [ ] **AC-US1-04**: A `--cwd` flag allows the user to override the auto-detected root and force install relative to cwd
- [ ] **AC-US1-05**: The detected project root is printed in the install output so the user can see where files were installed

---

### US-002: Per-Agent Targeting (P1)
**Project**: vskill

**As a** developer with multiple AI agents installed
**I want** to install a skill to only specific agents
**So that** I can keep my agents' skill sets separate and avoid polluting agents I don't use for a project

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `--agent <id>` flag limits installation to the specified agent only (e.g., `--agent claude-code`)
- [ ] **AC-US2-02**: `--agent` can be specified multiple times to target several agents (e.g., `--agent claude-code --agent cursor`)
- [ ] **AC-US2-03**: If a specified agent is not detected/installed, print an error listing available agents and exit with code 1
- [ ] **AC-US2-04**: Without `--agent`, default behavior is unchanged (install to all detected agents)
- [ ] **AC-US2-05**: `--agent` works with both GitHub installs, registry installs, and plugin installs

## Functional Requirements

### FR-001: Project Root Discovery
A new utility function `findProjectRoot(startDir: string): string | null` that walks up the directory tree checking for project marker files. Returns the first directory containing any marker, or null if none found up to filesystem root.

Markers (in priority order): `.git/`, `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `requirements.txt`, `pom.xml`, `*.csproj`, `.specweave/`, `vskill.lock`

### FR-002: Agent Filtering
A utility function `filterAgents(agents: AgentDefinition[], agentIds?: string[]): AgentDefinition[]` that returns only the requested agents from the detected list, or all agents if no filter is specified.

## Success Criteria

- Zero breaking changes to existing `vskill install` usage without new flags
- All existing tests continue to pass
- New test coverage for project root discovery (edge cases: symlinks, no markers, nested git repos)
- New test coverage for agent filtering (invalid IDs, multiple agents, single agent)

## Out of Scope

- Interactive agent selection (prompting the user to pick agents from a list)
- Config file-based agent preferences (e.g., `.vskillrc`)
- Monorepo workspace-aware resolution (install to each workspace root)

## Dependencies

- No external dependencies needed; all functionality uses `node:fs` and `node:path`
