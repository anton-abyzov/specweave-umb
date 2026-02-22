---
increment: 0249-skill-detail-repo-link-extensibility
title: "Skill detail page: repo link + extensibility auto-detection"
type: feature
priority: P1
status: active
created: 2026-02-20
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Skill detail page: repo link + extensibility auto-detection

## Overview

Two gaps on the skill detail page: `repoUrl` is never rendered (no clickable source link), and extensibility is hardcoded in seed data with no auto-detection for community-submitted skills.

## User Stories

### US-001: Clickable repository link on skill detail page
**Project**: vskill-platform

**As a** visitor viewing a skill detail page
**I want** a clickable link to the skill's source repository
**So that** I can inspect the code, contribute, or verify the skill myself

**Acceptance Criteria**:
- [x] **AC-US1-01**: Skill detail Meta section includes a "Repository" row with a clickable link to `repoUrl`
- [x] **AC-US1-02**: Link displays the org/repo name (not the full URL) and opens in a new tab

---

### US-002: Auto-detect extensibility during submission scanning
**Project**: vskill-platform

**As a** skill author submitting a community skill
**I want** the platform to automatically detect if my skill supports extensibility
**So that** visitors see the "Extensible" badge and extension points without manual curation

**Acceptance Criteria**:
- [x] **AC-US2-01**: `detectExtensibility(skillMd)` returns `{ extensible, extensionPoints }` based on content analysis
- [x] **AC-US2-02**: Detects template, hook, config, plugin, and context extension point types
- [x] **AC-US2-03**: Returns `extensible: false` for skills with no extensibility signals
- [x] **AC-US2-04**: Extensibility result is stored in KV when a skill is published
- [x] **AC-US2-05**: Published skills surface `extensible` and `extensionPoints` in the data layer

## Out of Scope

- Modifying SKILL.md frontmatter format to declare extensibility
- Retroactively scanning existing seed-data skills (they already have hardcoded values)
