---
id: US-002
feature: FS-525
title: "Remove zombie-prone background sync from hook"
status: completed
priority: P1
created: 2026-03-14T00:00:00.000Z
tldr: "**As a** developer running SpecWeave in automated environments."
project: specweave-umb
related_projects: [specweave]
---

# US-002: Remove zombie-prone background sync from hook

**Feature**: [FS-525](./FEATURE.md)

**As a** developer running SpecWeave in automated environments
**I want** the PostToolUse hook to not spawn background processes
**So that** zombie sync processes do not exhaust GitHub API rate limits

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the `close-completed-issues.sh` hook file, when inspected, then it contains no `&` backgrounding operators and no `disown` calls for sync operations
- [x] **AC-US2-02**: Given the hook runs in an environment with a `.env` file at PROJECT_ROOT containing GITHUB_TOKEN, when the hook executes gh CLI commands, then it sources GITHUB_TOKEN from `.env` and exports it as GH_TOKEN
- [x] **AC-US2-03**: Given stale `sync-*.lock` files (>60 minutes old) exist in `.specweave/state/`, when the hook starts execution, then those stale lock files are deleted before any other operations

---

## Implementation

**Increment**: [0525-fix-living-docs-sync-architecture](../../../../../increments/0525-fix-living-docs-sync-architecture/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
