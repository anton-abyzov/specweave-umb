---
increment: 0382-marketplace-install-mode
title: "Claude Code Plugin Marketplace Install Mode"
type: feature
priority: P1
status: planned
created: 2026-02-27
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Claude Code Plugin Marketplace Install Mode

## Overview

When `npx vskill install <owner/repo>` targets a GitHub repository that contains `.claude-plugin/marketplace.json` at root level, the install flow should auto-detect this and switch to a "marketplace add" mode. Instead of the current skill-discovery and extraction flow, it lists all available plugins from marketplace.json with a toggleable checkbox UI (all unselected by default), lets the user select which plugins they want, and installs each selected plugin via native `claude plugin marketplace add` + `claude plugin install` commands.

This is distinct from the existing `--plugin` flag flow (which names a specific plugin) and the `--all` flag (which installs everything). The detection happens automatically based on repo structure.

## User Stories

### US-001: Auto-detect marketplace repo during install (P1)
**Project**: vskill

**As a** developer running `vskill install owner/repo`
**I want** vskill to automatically detect that the target repo is a Claude Code plugin marketplace
**So that** I get routed to the correct installation flow without needing to know about `--plugin` or `--repo` flags

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `vskill install owner/repo` is run and the repo has `.claude-plugin/marketplace.json` at root, the marketplace install flow is triggered automatically
- [x] **AC-US1-02**: Detection uses the GitHub Contents API to check for `.claude-plugin/marketplace.json` existence before falling back to skill discovery
- [x] **AC-US1-03**: When the repo does NOT have `.claude-plugin/marketplace.json`, the existing skill-discovery flow continues unchanged
- [x] **AC-US1-04**: The `--plugin` flag still works as before and is NOT affected by auto-detection (explicit flag takes precedence)

---

### US-002: Interactive plugin selection UI (P1)
**Project**: vskill

**As a** developer installing from a marketplace repo
**I want** to see all available plugins with a toggleable checkbox list (all unchecked by default)
**So that** I can choose exactly which plugins I want without installing everything

**Acceptance Criteria**:
- [x] **AC-US2-01**: All plugins from marketplace.json are listed with name and description
- [x] **AC-US2-02**: All checkboxes are unchecked by default (opt-in, not opt-out)
- [x] **AC-US2-07**: Already-installed plugins are visually marked with "(installed)" in the selection list
- [x] **AC-US2-03**: The existing `promptCheckboxList` UI is used for plugin selection
- [x] **AC-US2-04**: If no plugins are selected, the install aborts with a message
- [x] **AC-US2-05**: In non-TTY mode (CI/piped), the install aborts with an error suggesting `--plugin` or `--all` flags
- [x] **AC-US2-06**: The `--yes` flag selects all plugins (same as `--all` behavior)

---

### US-003: Native Claude Code plugin installation (P1)
**Project**: vskill

**As a** developer who selected plugins from the marketplace
**I want** each plugin installed via `claude plugin marketplace add` and `claude plugin install`
**So that** plugins are managed by Claude Code's native plugin system with proper namespacing

**Acceptance Criteria**:
- [x] **AC-US3-01**: The marketplace is registered via `claude plugin marketplace add <repo-path>` (using a temporary clone or the raw GitHub URL)
- [x] **AC-US3-02**: Each selected plugin is installed via `claude plugin install <plugin>@<marketplace-name>`
- [x] **AC-US3-03**: If `claude` CLI is not available, fall back to the existing extraction-based install per plugin
- [x] **AC-US3-04**: Installation progress is shown for each plugin (spinner + success/failure status)
- [x] **AC-US3-05**: A summary is printed showing which plugins were installed and which failed

---

### US-004: Lockfile and telemetry integration (P2)
**Project**: vskill

**As a** developer using vskill's tracking features
**I want** marketplace-installed plugins to be recorded in the lockfile
**So that** `vskill list` and `vskill update` work correctly for marketplace-installed plugins

**Acceptance Criteria**:
- [x] **AC-US4-01**: Each installed plugin is recorded in the lockfile with source `marketplace:<owner>/<repo>#<plugin-name>`
- [x] **AC-US4-02**: Install telemetry is reported for each plugin (fire-and-forget)

## Functional Requirements

### FR-001: Marketplace Detection
When `addCommand` is called with a 2-part `owner/repo` source (and no `--plugin`/`--repo` flags), before running skill discovery, check if the repo has `.claude-plugin/marketplace.json` by fetching `https://api.github.com/repos/{owner}/{repo}/contents/.claude-plugin/marketplace.json`. If it exists, route to the new marketplace install flow.

### FR-002: Plugin Selection
Fetch and parse marketplace.json. Present all plugins via `promptCheckboxList` with items unchecked by default. Support `--yes` (select all) and `--all` (select all) flags to skip the prompt.

### FR-003: Installation via Claude CLI
For each selected plugin:
1. Clone/download the repo to a temp directory (or use GitHub raw content)
2. Register marketplace via `claude plugin marketplace add`
3. Install plugin via `claude plugin install <plugin>@<marketplace>`
4. If native install fails, fall back to the existing `installRepoPlugin` extraction path

### FR-004: Non-TTY Behavior
In non-interactive mode without `--yes`/`--all`, print available plugins and exit with error code, directing the user to use explicit flags.

## Success Criteria

- `vskill install owner/repo` seamlessly detects marketplace repos and presents plugin selection
- All existing install flows (skill, --plugin, --repo, registry) remain unchanged
- Test coverage for new marketplace detection and install paths

## Out of Scope

- Modifying Claude Code's native plugin system
- Supporting non-GitHub marketplaces
- Auto-update of marketplace-installed plugins (handled by existing `vskill update`)
- Security scanning of marketplace plugins (already handled by existing scan infrastructure)

## Dependencies

- `claude` CLI binary must be installed for native plugin install (graceful fallback if absent)
- GitHub API access for marketplace.json detection
- Existing `marketplace/marketplace.ts` parser
- Existing `utils/claude-cli.ts` native install functions
