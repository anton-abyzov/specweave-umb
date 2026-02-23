---
id: US-007
feature: FS-325
title: Remove Fabricated vskillInstalls from Skill Detail Pages
status: not-started
priority: P1
created: 2026-02-22
project: vskill-platform
---
# US-007: Remove Fabricated vskillInstalls from Skill Detail Pages

**Feature**: [FS-325](./FEATURE.md)

visitor viewing a skill detail page or the verified skills table
**I want** to no longer see fabricated install counts
**So that** per-skill metrics are trustworthy and consistent with the homepage (which already shows "Unique Repos")

---

## Acceptance Criteria

- [ ] **AC-US7-01**: The skill detail page (`/skills/[name]/page.tsx`) Popularity section no longer shows the "Installs" StatCard
- [ ] **AC-US7-02**: The VerifiedSkillsTab table replaces the "Installs" column with "Trust" column showing `trustScore`
- [ ] **AC-US7-03**: The VerifiedSkillsTab sort option "Installs" is replaced with "Trust" (sorting by `trustScore`)

---

## Implementation

**Increment**: [0325-homepage-metrics-accuracy](../../../../../increments/0325-homepage-metrics-accuracy/spec.md)

