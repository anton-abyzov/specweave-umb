---
id: US-001
feature: FS-482
title: "Simplified Init Command (P1)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1528
    url: https://github.com/anton-abyzov/specweave/issues/1528
---

# US-001: Simplified Init Command (P1)

**Feature**: [FS-482](./FEATURE.md)

**As a** developer
**I want** `specweave init` to quickly scaffold the project structure without asking about external tools
**So that** I can start using SpecWeave immediately without a lengthy wizard

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a directory without `.specweave/`, when running `specweave init`, then `.specweave/` directory, config.json, CLAUDE.md, AGENTS.md, and .gitignore are created in < 10 seconds
- [x] **AC-US1-02**: Given any init invocation, when the command runs, then no prompts appear about greenfield/brownfield, repository hosting, issue trackers, or repo cloning
- [x] **AC-US1-03**: Given a directory with a `.git/config` containing a remote URL, when running init, then the adapter (Claude/Cursor/Generic) and git provider (GitHub/ADO/Bitbucket) are auto-detected silently without prompting
- [x] **AC-US1-04**: Given the `--quick` flag, when running init, then zero interactive prompts are shown
- [x] **AC-US1-05**: Given interactive mode (no `--quick`), when running init, then at most 2 prompts appear: language selection (if non-English locale detected) and adapter confirmation
- [x] **AC-US1-06**: Given the generated config.json, when inspecting its contents, then it contains only core fields: project name, adapter, repository.provider, language, hooks, auto, lsp, and testing defaults -- no multiProject, issueTracker, projectMaturity, or structureDeferred fields

---

## Implementation

**Increment**: [0482-simplify-init](../../../../../increments/0482-simplify-init/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Simplify `createConfigFile()` in directory-structure.ts
- [x] **T-002**: Rewrite next-steps.ts with guided follow-up commands
- [x] **T-003**: Simplify summary-banner.ts interface
- [x] **T-004**: Rewrite init.ts — main rewrite (remove 70% of code)
- [x] **T-005**: Export `detectProvider` from provider-detection.ts and barrel
