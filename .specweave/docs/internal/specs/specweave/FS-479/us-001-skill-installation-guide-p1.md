---
id: US-001
feature: FS-479
title: "Skill Installation Guide (P1)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** developer new to AI skills."
project: specweave
---

# US-001: Skill Installation Guide (P1)

**Feature**: [FS-479](./FEATURE.md)

**As a** developer new to AI skills
**I want** a single guide that covers all ways to install skills with vskill
**So that** I can install my first skill without visiting multiple pages

---

## Acceptance Criteria

- [x] **AC-US1-01**: Page exists at `docs/skills/installation.md` with frontmatter (title, description, keywords, sidebar_position)
- [x] **AC-US1-02**: Covers installing from registry (`vskill install <name>`), GitHub (`vskill install --repo`), and local directory (`vskill install --dir`)
- [x] **AC-US1-03**: Covers installing plugins (bundles of skills) with reference to the 13 available plugins
- [x] **AC-US1-04**: Documents the security scan pipeline (38 patterns + blocklist + optional LLM verify) that runs before install
- [x] **AC-US1-05**: Documents multi-agent install (auto-detects 49 AI coding agents including Claude Code, Cursor, Copilot)
- [x] **AC-US1-06**: Covers skill management: list, update, remove, blocklist commands
- [x] **AC-US1-07**: Explains global vs project scope for installations
- [x] **AC-US1-08**: Documents SpecWeave plugin auto-loading and how it relates to vskill
- [x] **AC-US1-09**: Includes a troubleshooting section for common installation issues
- [x] **AC-US1-10**: Docusaurus build passes with the new page included (`npm run build` exits 0)

---

## Implementation

**Increment**: [0479-docs-skills-studio-install](../../../../../increments/0479-docs-skills-studio-install/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Read vskill source and create installation.md
- [x] **T-002**: Verify Phase 1 build passes
