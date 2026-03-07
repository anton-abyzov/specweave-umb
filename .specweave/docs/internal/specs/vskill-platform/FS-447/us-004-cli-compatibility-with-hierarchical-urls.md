---
id: US-004
feature: FS-447
title: CLI Compatibility with Hierarchical URLs
status: complete
priority: P1
created: 2026-03-07
project: vskill
---
# US-004: CLI Compatibility with Hierarchical URLs

**Feature**: [FS-447](./FEATURE.md)

CLI user
**I want** `vskill find`, `vskill add`, and `vskill submit` to work with the new hierarchical skill names
**So that** I can search, install, and submit skills using the updated URL scheme

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given `vskill find react`, when the API returns skills with hierarchical names (e.g., `facebook/react/react-hooks`), then the CLI displays the name in `owner/repo/skill-slug` format and the URL as `https://verified-skill.com/skills/facebook/react/react-hooks`
- [x] **AC-US4-02**: Given the lockfile (`vskill.lock`), when a skill is installed, then the lockfile key uses the hierarchical name `owner/repo/skillSlug` instead of the flat slug
- [x] **AC-US4-03**: Given backward compatibility, when a lockfile contains old flat-slug keys, then `vskill list` and `vskill update` still read them correctly (graceful degradation)
- [x] **AC-US4-04**: Given the `vskill info <name>` command, when the user provides a hierarchical name like `acme/tools/linter`, then the CLI fetches and displays the skill detail
- [x] **AC-US4-05**: Given the blocklist check, when comparing skill names, then the check uses the hierarchical name format and the API endpoint accepts hierarchical names in the `name` query parameter

---

## Implementation

**Increment**: [0447-hierarchical-skill-urls](../../../../../increments/0447-hierarchical-skill-urls/spec.md)

