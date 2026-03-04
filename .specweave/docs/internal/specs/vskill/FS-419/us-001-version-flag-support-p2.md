---
id: US-001
feature: FS-419
title: Version Flag Support (P2)
status: completed
priority: P2
created: 2026-03-03
tldr: "**As a** vskill CLI user."
project: vskill
external:
  github:
    issue: 3
    url: https://github.com/anton-abyzov/vskill/issues/3
---

# US-001: Version Flag Support (P2)

**Feature**: [FS-419](./FEATURE.md)

**As a** vskill CLI user
**I want** to run `vskill --version` to see the current version
**So that** I can verify which version is installed

---

## Acceptance Criteria

- [x] **AC-US1-01**: Running `vskill --version` outputs the version from package.json
- [x] **AC-US1-02**: The version output format is just the version number (e.g., `0.2.20`)

---

## Implementation

**Increment**: [0419G-vskill-version-flag](../../../../../increments/0419G-vskill-version-flag/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add --version flag to CLI
