---
increment: 0656-sw-umbrella-skill
title: 'sw:umbrella skill for automated workspace creation'
type: feature
priority: P1
status: completed
created: 2026-04-02T00:00:00.000Z
structure: user-stories
---

# Feature: sw:umbrella skill for automated workspace creation

## Overview

Automate the manual process of creating umbrella workspaces (directory structure, repo migration, symlinks, .env consolidation, specweave init). Two modes: `init` (from scratch) and `wrap` (existing repos).

## User Stories

### US-001: Create umbrella from scratch (P1)
**Project**: specweave

**As a** developer with multiple related repositories
**I want** to run `sw:umbrella init` with a name and list of repos
**So that** I get a fully configured umbrella workspace without manual setup

**Acceptance Criteria**:
- [x] **AC-US1-01**: Skill creates `{name}/repositories/{org}/{repo}/` directory structure
- [x] **AC-US1-02**: Remote repos are cloned via `specweave get`
- [x] **AC-US1-03**: Local repos are moved into structure with symlinks at original paths
- [x] **AC-US1-04**: `.env` files from repos are consolidated into umbrella root
- [x] **AC-US1-05**: `specweave init` runs at umbrella root, producing valid config
- [x] **AC-US1-06**: A `setup.sh` script is generated for fresh-machine bootstrap

---

### US-002: Wrap existing repo in umbrella (P2)
**Project**: specweave

**As a** developer working in a standalone repo
**I want** to run `sw:umbrella wrap` to restructure it into an umbrella
**So that** I can add more repos later without manual migration

**Acceptance Criteria**:
- [x] **AC-US2-01**: Skill detects org/repo from git remote
- [x] **AC-US2-02**: Repo is moved into `repositories/{org}/{repo}/` under new umbrella root
- [x] **AC-US2-03**: Symlink created at original repo location
- [x] **AC-US2-04**: `specweave init` and repo registration complete successfully

## Out of Scope

- CLI command implementation (`specweave umbrella create`) — future increment
- Bulk org cloning (already handled by `sw:get`)
- External sync setup (handled by `sw:sync-setup` post-creation)
