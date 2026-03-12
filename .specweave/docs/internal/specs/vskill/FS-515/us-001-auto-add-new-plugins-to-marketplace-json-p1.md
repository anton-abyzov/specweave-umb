---
id: US-001
feature: FS-515
title: "Auto-add new plugins to marketplace.json (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** vskill plugin author."
project: vskill
---

# US-001: Auto-add new plugins to marketplace.json (P1)

**Feature**: [FS-515](./FEATURE.md)

**As a** vskill plugin author
**I want** to run `vskill marketplace sync` to automatically add my new plugin to marketplace.json
**So that** it appears in Claude Code's `/plugin Discover` tab without manual file editing

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a plugin directory `plugins/foo/` with a valid `.claude-plugin/plugin.json` that is not listed in marketplace.json, when the user runs `vskill marketplace sync`, then a new entry is added to the `plugins` array in marketplace.json with `name`, `source` (`./plugins/foo`), `version`, and `description` from plugin.json
- [x] **AC-US1-02**: Given a plugin directory `plugins/bar/` with no `.claude-plugin/plugin.json`, when the user runs `vskill marketplace sync`, then the directory is skipped and a warning is printed to stderr naming the skipped directory
- [x] **AC-US1-03**: Given marketplace.json does not exist at `.claude-plugin/marketplace.json`, when the user runs `vskill marketplace sync`, then the command prints an error message and exits with code 1

---

## Implementation

**Increment**: [0515-vskill-marketplace-sync](../../../../../increments/0515-vskill-marketplace-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Write failing tests for `syncMarketplace()` pure function (TDD RED)
- [x] **T-002**: Implement `syncMarketplace()` and new types in `src/marketplace/marketplace.ts` (TDD GREEN)
- [x] **T-005**: TDD REFACTOR -- full suite, build, smoke test
