---
id: US-002
feature: FS-265
title: Per-Agent Targeting
status: not-started
priority: P1
created: 2026-02-21
project: vskill
---
# US-002: Per-Agent Targeting

**Feature**: [FS-265](./FEATURE.md)

developer with multiple AI agents installed
**I want** to install a skill to only specific agents
**So that** I can keep my agents' skill sets separate and avoid polluting agents I don't use for a project

---

## Acceptance Criteria

- [ ] **AC-US2-01**: `--agent <id>` flag limits installation to the specified agent only (e.g., `--agent claude-code`)
- [ ] **AC-US2-02**: `--agent` can be specified multiple times to target several agents (e.g., `--agent claude-code --agent cursor`)
- [ ] **AC-US2-03**: If a specified agent is not detected/installed, print an error listing available agents and exit with code 1
- [ ] **AC-US2-04**: Without `--agent`, default behavior is unchanged (install to all detected agents)
- [ ] **AC-US2-05**: `--agent` works with both GitHub installs, registry installs, and plugin installs

---

## Implementation

**Increment**: [0265-vskill-install-ux](../../../../../increments/0265-vskill-install-ux/spec.md)

