---
id: US-004
feature: FS-276
title: Interactive Install Method Selection
status: complete
priority: P1
created: 2026-02-21
project: vskill
external:
  github:
    issue: 1205
    url: "https://github.com/anton-abyzov/specweave/issues/1205"
---
# US-004: Interactive Install Method Selection

**Feature**: [FS-276](./FEATURE.md)

developer installing skills to multiple agents
**I want** to choose between symlink and copy installation methods
**So that** I can use symlinks for deduplication or copies for portability

---

## Acceptance Criteria

- [x] **AC-US4-01**: After scope selection, the CLI prompts "Install method: (1) Symlink [recommended] or (2) Copy?"
- [x] **AC-US4-02**: Symlink mode copies skills to a canonical `.agents/skills/<name>/` directory, then creates relative symlinks from each agent's skills directory
- [x] **AC-US4-03**: Copy mode copies skills directly to each agent's directory independently
- [x] **AC-US4-04**: If symlink creation fails (e.g., Windows without Dev Mode), falls back to copy with a warning
- [x] **AC-US4-05**: When `--yes` flag is provided, defaults to symlink (no prompt)

---

## Implementation

**Increment**: [0276-interactive-skill-installer](../../../../../increments/0276-interactive-skill-installer/spec.md)

