---
id: US-001
feature: FS-514
title: "Working sync-setup CLI command"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer who just ran `specweave init` on a brownfield project,."
---

# US-001: Working sync-setup CLI command

**Feature**: [FS-514](./FEATURE.md)

**As a** developer who just ran `specweave init` on a brownfield project,
**I want** to run `specweave sync-setup` in my terminal to connect GitHub Issues, JIRA, or ADO,
**So that** the "next steps" guidance actually works and I can connect external tools without needing Claude Code open.

---

## Acceptance Criteria

- [x] **AC-US1-01**: `specweave sync-setup` exists and runs without "unknown command" error
- [x] **AC-US1-02**: Command shows interactive provider selection (GitHub / JIRA / ADO) via checkbox prompt
- [x] **AC-US1-03**: Command collects credentials per selected provider (token, domain, project key)
- [x] **AC-US1-04**: Command asks for permission preset: read-only | push-only | bidirectional | full-control
- [x] **AC-US1-05**: For umbrella projects, command offers global or per-repo sync target assignment
- [x] **AC-US1-06**: Credentials written to `.env`, sync config written to `.specweave/config.json`
- [x] **AC-US1-07**: `--quick` flag skips interactive prompts gracefully (exits 0 with hint message)
- [x] **AC-US1-08**: `--provider <github|jira|ado>` flag pre-selects provider, skipping selection prompt

---

## Implementation

**Increment**: [0514-init-sync-setup-brownfield](../../../../../increments/0514-init-sync-setup-brownfield/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: Build, verify CLI works, commit and push
