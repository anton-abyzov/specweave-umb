---
id: US-003
feature: FS-504
title: "Non-TTY Disambiguation (P1)"
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** CI pipeline or script author."
project: vskill
---

# US-003: Non-TTY Disambiguation (P1)

**Feature**: [FS-504](./FEATURE.md)

**As a** CI pipeline or script author
**I want** clear output and a non-zero exit code when a flat name is ambiguous
**So that** my automation fails explicitly instead of installing the wrong skill

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given multiple results and a non-TTY environment, then the CLI prints the ranked result list (same display format as `vskill find`) and exits with code 1
- [ ] **AC-US3-02**: Given a non-TTY environment, then the error message instructs the user to specify the exact `owner/repo/skill` path

---

## Implementation

**Increment**: [0504-install-skill-discovery](../../../../../increments/0504-install-skill-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-005**: Non-TTY exit with ranked list and actionable error
