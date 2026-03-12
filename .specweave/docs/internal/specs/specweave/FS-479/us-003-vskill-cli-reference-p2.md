---
id: US-003
feature: FS-479
title: "vskill CLI Reference (P2)"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** developer using vskill."
project: specweave
---

# US-003: vskill CLI Reference (P2)

**Feature**: [FS-479](./FEATURE.md)

**As a** developer using vskill
**I want** a complete CLI reference page
**So that** I can look up exact command syntax and flags without reading `--help`

---

## Acceptance Criteria

- [x] **AC-US3-01**: Page exists at `docs/skills/vskill-cli.md` with frontmatter
- [x] **AC-US3-02**: Documents all 12 vskill commands with syntax, flags, and examples
- [x] **AC-US3-03**: Each command entry includes: name, description, usage syntax, flags/options table, and at least one example
- [x] **AC-US3-04**: Commands are organized by category (install, discover, develop, manage)
- [x] **AC-US3-05**: Docusaurus build passes with the new page included

---

## Implementation

**Increment**: [0479-docs-skills-studio-install](../../../../../increments/0479-docs-skills-studio-install/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: [P] Read vskill index.ts and create vskill-cli.md
