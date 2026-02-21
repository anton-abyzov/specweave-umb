---
id: US-001
feature: FS-276
title: Interactive Skill Selection
status: complete
priority: P1
created: 2026-02-21
project: vskill
external:
  github:
    issue: 1202
    url: "https://github.com/anton-abyzov/specweave/issues/1202"
---
# US-001: Interactive Skill Selection

**Feature**: [FS-276](./FEATURE.md)

developer installing skills from a multi-skill repository
**I want** an interactive prompt listing all discovered skills with toggle selection
**So that** I can pick exactly which skills to install instead of getting all of them automatically

---

## Acceptance Criteria

- [x] **AC-US1-01**: When a repo contains 2+ skills, the CLI displays a numbered list with checkboxes showing each skill name and description
- [x] **AC-US1-02**: User can toggle individual skills on/off by entering their number
- [x] **AC-US1-03**: An "all" option selects or deselects every skill at once
- [x] **AC-US1-04**: Pressing Enter/Return confirms the current selection and proceeds to the next step
- [x] **AC-US1-05**: When a repo contains exactly 1 skill, the skill selection step is skipped (auto-selected)
- [x] **AC-US1-06**: When `--yes` flag is provided, all skills are auto-selected (no prompt)

---

## Implementation

**Increment**: [0276-interactive-skill-installer](../../../../../increments/0276-interactive-skill-installer/spec.md)

