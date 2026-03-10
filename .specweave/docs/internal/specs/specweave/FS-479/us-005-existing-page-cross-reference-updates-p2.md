---
id: US-005
feature: FS-479
title: "Existing Page Cross-Reference Updates (P2)"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** docs site visitor reading existing skills pages."
project: specweave
---

# US-005: Existing Page Cross-Reference Updates (P2)

**Feature**: [FS-479](./FEATURE.md)

**As a** docs site visitor reading existing skills pages
**I want** links to the new installation, Studio, and CLI pages where contextually relevant
**So that** I discover related content naturally while reading

---

## Acceptance Criteria

- [ ] **AC-US5-01**: `skills/index.md` updated with links to installation guide, Skill Studio, and CLI reference in the "Explore Further" section
- [ ] **AC-US5-02**: `getting-started/index.md` updated to reference the vskill installation guide where skill/plugin installation is mentioned
- [ ] **AC-US5-03**: `overview/plugins-ecosystem.md` updated to link to the installation guide and CLI reference where relevant
- [ ] **AC-US5-04**: `skills/fundamentals.md` updated to cross-reference installation guide (where "install" is discussed) and CLI reference
- [ ] **AC-US5-05**: `skills/skill-discovery-evaluation.md` updated to reference installation guide and vskill CLI in the SpecWeave Approach section
- [ ] **AC-US5-06**: No broken internal links introduced by changes (`npm run build` exits 0)

---

## Implementation

**Increment**: [0479-docs-skills-studio-install](../../../../../increments/0479-docs-skills-studio-install/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-006**: Add cross-reference links to skills/index.md, getting-started/index.md, overview/plugins-ecosystem.md
- [ ] **T-007**: Add cross-reference links to fundamentals.md and skill-discovery-evaluation.md; final build verification
