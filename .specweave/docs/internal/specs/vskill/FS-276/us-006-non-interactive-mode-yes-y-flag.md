---
id: US-006
feature: FS-276
title: Non-Interactive Mode (`--yes` / `-y` flag)
status: complete
priority: P1
created: 2026-02-21
project: vskill
external:
  github:
    issue: 1207
    url: "https://github.com/anton-abyzov/specweave/issues/1207"
---
# US-006: Non-Interactive Mode (`--yes` / `-y` flag)

**Feature**: [FS-276](./FEATURE.md)

developer using vskill in CI pipelines or scripts
**I want** a `--yes` flag that skips all interactive prompts
**So that** installations can run unattended with sensible defaults

---

## Acceptance Criteria

- [x] **AC-US6-01**: `--yes` (or `-y`) flag is available on the `install`/`add` command
- [x] **AC-US6-02**: With `--yes`, defaults are: all skills, all detected agents, project scope, symlink method
- [x] **AC-US6-03**: `--yes` can be combined with `--agent`, `--global` to override specific defaults
- [x] **AC-US6-04**: When stdin is not a TTY (piped/CI), the CLI behaves as if `--yes` was specified

---

## Implementation

**Increment**: [0276-interactive-skill-installer](../../../../../increments/0276-interactive-skill-installer/spec.md)

