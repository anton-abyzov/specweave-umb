---
increment: 0851-cli-install-migration-audit
title: "CLI install and migration audit"
type: feature
priority: P1
status: planned
created: 2026-05-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: CLI Install And Migration Audit

## Overview

Audit and harden the SpecWeave CLI path a new user hits first: install the command, initialize an empty folder, handle a non-empty/simple folder, copy or move repositories into `repositories/{org}/{repo}/`, migrate legacy config, configure git repositories, and verify the released/latest behavior.

## User Stories

### US-001: Installable CLI Starts Clean Workspaces
**Project**: specweave

**As a** new SpecWeave user
**I want** the CLI to install and initialize a clean folder predictably
**So that** I can start using SpecWeave without source-checkout assumptions or broken command paths

**Acceptance Criteria**:
- [x] **AC-US1-01**: An isolated npm-prefix install from the packed local package exposes `specweave --version`, `specweave --help`, and `specweave init --help` without missing dependency or missing `dist/` failures.
- [x] **AC-US1-02**: `specweave init . --quick --adapter generic` in an empty temp folder creates `.specweave/`, `repositories/`, instruction files, a valid config using the current workspace schema, and a git repository when git is available.
- [x] **AC-US1-03**: Command help, generated next steps, and skill-facing command references match real CLI commands or provide compatibility aliases.

### US-002: Existing Folder Migration Preserves User Code
**Project**: specweave

**As a** user starting from a simple folder with code already inside
**I want** clear copy, restructure, and continue-in-place paths
**So that** SpecWeave can adopt my code without surprise deletion or broken repository layout

**Acceptance Criteria**:
- [x] **AC-US2-01**: The local-copy path copies an existing local git repository into `repositories/{org}/{repo}/`, excludes `.git` and symlinks, rejects path traversal, and reports copied/skipped/errors deterministically.
- [x] **AC-US2-02**: The restructure path moves only safe top-level entries into `repositories/{org}/{repo}/`, skips `.git`, `.specweave`, `node_modules`, `repositories`, hidden files, and symlinks, and preserves clear warnings for CI/import breakage.
- [x] **AC-US2-03**: The non-interactive/quick path never restructures or copies implicitly; it leaves existing files in place and creates a usable workspace.

### US-003: Repository Registration Matches Current Config
**Project**: specweave

**As a** user adding repositories after init
**I want** `specweave get` and migration helpers to register repositories in the active config schema
**So that** child repositories are discoverable, initialized, and ready for future sync

**Acceptance Criteria**:
- [x] **AC-US3-01**: `specweave get <local-path>` registers a local repo from a temp fixture in a current `workspace` config and remains idempotent on repeated runs.
- [x] **AC-US3-02**: `specweave get owner/repo --no-init` targets `repositories/{owner}/{repo}/`, registers metadata without requiring external sync setup, and keeps `--no-init` honored.
- [x] **AC-US3-03**: Legacy `umbrella`/`multiProject` config migrates to the current workspace schema once, persists the result, and does not print repeated migration messages on unrelated commands.
- [x] **AC-US3-04**: Root and child git repository metadata use normalized repo-name project IDs and preserve optional root repository connection separately from child repo registrations.

### US-004: Fixes Ship And Verify Against Latest
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the audit fixes tested, reported, pushed, deployed or published, and verified against the newest version
**So that** the public CLI path is proven, not just locally patched

**Acceptance Criteria**:
- [x] **AC-US4-01**: A report at `reports/test-report.md` records every local command run, temp workspace used, failures found, fixes applied, and final pass/fail status.
- [x] **AC-US4-02**: Targeted unit/integration tests, `npm run build`, smoke tests, and the pack-install CLI matrix pass before marking implementation tasks complete.
- [ ] **AC-US4-03**: The fix branch is pushed, the deploy/publish path available in this repo is run, and the latest published/deployed SpecWeave version is verified with a fresh temp install.
- [ ] **AC-US4-04**: Optional steps are documented as optional in CLI output or docs: external issue sync, repo import, living docs background build, plugin refresh, and deploy/publish credential setup.

## Out of Scope

- Replacing the repository layout model.
- Changing external tracker semantics beyond making setup optional and non-blocking.
- Running destructive migrations against real user repositories.
- Forcing global npm installs outside an isolated test prefix.

## Dependencies

- Node.js >= 20.12.0, git, npm.
- Existing SpecWeave CLI source in `repositories/anton-abyzov/specweave`.
- Release credentials only for the deploy/publish task; local verification must work without them.
