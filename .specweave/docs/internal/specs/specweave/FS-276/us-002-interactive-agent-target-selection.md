---
id: US-002
feature: FS-276
title: Interactive Agent Target Selection
status: complete
priority: P1
created: 2026-02-21
project: vskill
external:
  github:
    issue: 1203
    url: https://github.com/anton-abyzov/specweave/issues/1203
---
# US-002: Interactive Agent Target Selection

**Feature**: [FS-276](./FEATURE.md)

developer with multiple AI agents installed
**I want** to interactively choose which agents receive the skills
**So that** I can install skills only to the agents I actively use

---

## Acceptance Criteria

- [x] **AC-US2-01**: After skill selection, the CLI shows all detected agents with checkboxes (pre-checked)
- [x] **AC-US2-02**: User can toggle individual agents by entering their number
- [x] **AC-US2-03**: An "all" option selects or deselects every detected agent
- [x] **AC-US2-04**: When only 1 agent is detected, the agent selection step is skipped (auto-selected)
- [x] **AC-US2-05**: When `--agent <id>` flag(s) are provided, agent selection step is skipped (use specified agents)
- [x] **AC-US2-06**: When `--yes` flag is provided, all detected agents are auto-selected (no prompt)

---

## Implementation

**Increment**: [0276-interactive-skill-installer](../../../../../increments/0276-interactive-skill-installer/spec.md)

