---
increment: 0514-init-sync-setup-brownfield
title: Fix init sync-setup command + brownfield repo onboarding
type: feature
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix init sync-setup command + brownfield repo onboarding

## Overview

Two broken first-run experiences for brownfield projects:

1. `specweave init` shows `specweave sync-setup` in "next steps" — but this command doesn't exist as a CLI command (only as a Claude skill). Running it gives `error: unknown command 'sync-setup'`.

2. When repos exist at `repositories/{name}/.git` (1-level, missing org subfolder), `scanUmbrellaRepos()` silently returns null with no warning or guidance. Users don't know their repos weren't recognized.

---

## User Stories

### US-001: Working sync-setup CLI command

**Project**: specweave

**As a** developer who just ran `specweave init` on a brownfield project,
**I want** to run `specweave sync-setup` in my terminal to connect GitHub Issues, JIRA, or ADO,
**So that** the "next steps" guidance actually works and I can connect external tools without needing Claude Code open.

**Acceptance Criteria**:
- [x] AC-US1-01: `specweave sync-setup` exists and runs without "unknown command" error
- [x] AC-US1-02: Command shows interactive provider selection (GitHub / JIRA / ADO) via checkbox prompt
- [x] AC-US1-03: Command collects credentials per selected provider (token, domain, project key)
- [x] AC-US1-04: Command asks for permission preset: read-only | push-only | bidirectional | full-control
- [x] AC-US1-05: For umbrella projects, command offers global or per-repo sync target assignment
- [x] AC-US1-06: Credentials written to `.env`, sync config written to `.specweave/config.json`
- [x] AC-US1-07: `--quick` flag skips interactive prompts gracefully (exits 0 with hint message)
- [x] AC-US1-08: `--provider <github|jira|ado>` flag pre-selects provider, skipping selection prompt

### US-002: Brownfield repo layout detection

**Project**: specweave

**As a** developer with repositories in a non-standard layout (missing org subfolder),
**I want** `specweave init` to detect this and show me exactly how to fix it,
**So that** I understand why my repos aren't being recognized and can follow a clear path to fix it.

**Acceptance Criteria**:
- [x] AC-US2-01: After `specweave init`, when repos exist at `repositories/{name}/.git` (1-level), a warning is displayed
- [x] AC-US2-02: Warning lists the affected repository names
- [x] AC-US2-03: Warning shows the exact `mkdir` + `mv` fix command with the first affected repo as example
- [x] AC-US2-04: When repos follow the standard 2-level `{org}/{repo}` pattern, no warning is shown
- [x] AC-US2-05: When no `repositories/` directory exists, no warning is shown
- [x] AC-US2-06: Warning does not appear when `scanUmbrellaRepos()` already found valid repos

---

## Out of Scope

- Full credential validation / connection testing (handled by existing `setupIssueTracker` internals)
- Migrating repos from 1-level to 2-level layout automatically (too destructive for init)
- ADO multi-project configuration (covered by existing sync skill)
