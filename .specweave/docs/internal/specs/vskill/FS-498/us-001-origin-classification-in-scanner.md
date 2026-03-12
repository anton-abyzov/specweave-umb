---
id: US-001
feature: FS-498
title: "Origin Classification in Scanner"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 91
    url: https://github.com/anton-abyzov/vskill/issues/91
---

# US-001: Origin Classification in Scanner

**Feature**: [FS-498](./FEATURE.md)

**As a** skill developer
**I want** the skill scanner to classify each discovered skill as "source" or "installed"
**So that** downstream consumers (UI, CLI) know which skills are editable vs consumed copies

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a skill whose `dir` relative to `root` starts with any `localSkillsDir` prefix from `AGENTS_REGISTRY` (e.g., `.claude/`, `.cursor/`, `.amp/`), when the scanner returns results, then that skill has `origin: "installed"`
- [x] **AC-US1-02**: Given a skill whose `dir` relative to `root` starts with any hardcoded extra prefix (`.specweave/`, `.vscode/`, `.idea/`, `.zed/`, `.devcontainer/`, `.github/`, `.agents/`, `.agent/`), when the scanner returns results, then that skill has `origin: "installed"`
- [x] **AC-US1-03**: Given a skill whose `dir` relative path contains `plugins/cache/`, when the scanner returns results, then that skill has `origin: "installed"`
- [x] **AC-US1-04**: Given a skill that does not match any installed pattern, when the scanner returns results, then that skill has `origin: "source"`
- [x] **AC-US1-05**: Given a skill that exists as both a source copy and an installed copy, when the scanner returns results, then both copies appear in the list with their respective origin values

---

## Implementation

**Increment**: [0498-studio-skill-origin-classification](../../../../../increments/0498-studio-skill-origin-classification/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement `classifyOrigin` function and add `origin` to `SkillInfo`
- [x] **T-002**: Wire `origin` into all `skills.push()` call sites in `scanSkills`
