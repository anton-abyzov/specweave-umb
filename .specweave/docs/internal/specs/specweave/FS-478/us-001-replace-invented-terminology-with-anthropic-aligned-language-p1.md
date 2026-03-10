---
id: US-001
feature: FS-478
title: "Replace invented terminology with Anthropic-aligned language (P1)"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** developer reading SpecWeave's skills documentation."
project: specweave
---

# US-001: Replace invented terminology with Anthropic-aligned language (P1)

**Feature**: [FS-478](./FEATURE.md)

**As a** developer reading SpecWeave's skills documentation
**I want** terminology that aligns with Anthropic's official Claude Code concepts
**So that** I can trust the documentation is accurate and not inflating SpecWeave's contributions

---

## Acceptance Criteria

- [ ] **AC-US1-01**: All occurrences of "Dynamic Context Injection (DCI)" and standalone "DCI" across the docs-site are replaced with lowercase "dynamic context injection"; first occurrence on each page notes it is "Claude Code's built-in `!command` syntax"
- [ ] **AC-US1-02**: All occurrences of "Extensible Skills Standard" are replaced with "Extensible Skills" (filenames remain unchanged)
- [ ] **AC-US1-03**: The "programs written in English" tagline in skills/index.md and any other files is replaced with "Skills extend what AI coding agents can do -- structured markdown files that define how an agent behaves in specific domains" (shorter form "structured markdown instructions" or "detailed playbooks" where space is limited)
- [ ] **AC-US1-04**: The incorrect glossary entry "Direct Command Injection" in skills-ecosystem-security.md is corrected to "dynamic context injection"
- [ ] **AC-US1-05**: Zero occurrences of uppercase "DCI" as an acronym remain in any docs-site markdown file (excluding code fences showing filenames or CLI output)

---

## Implementation

**Increment**: [0478-skills-docs-rhetoric-alignment](../../../../../increments/0478-skills-docs-rhetoric-alignment/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
