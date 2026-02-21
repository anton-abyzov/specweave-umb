---
increment: 0303-simplify-extensibility-standard
title: "Simplify Extensible Skills Standard — 3 Clear Categories"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Simplify Extensible Skills Standard — 3 Clear Categories

## Overview

Replace over-engineered E0-E4 five-tier model with 3 clear categories: extensible, semi-extensible, not-extensible. Remove unused frontmatter detection and portability matrix.

### Problem

The current Extensible Skills Standard (v3.0.0) defines 5 tiers (E0-E4) but is over-engineered:

- **E0** (not extensible): 68+ skills — fine, maps to `not-extensible`
- **E1** (keyword-detected): 20 skills — **misleading**. Regex-matching "custom templates" in prose doesn't make a skill genuinely extensible. k8s-manifests mentioning "custom manifest templates" in its description is NOT the same as having a discoverable, standard memory file.
- **E2** (frontmatter-declared): **0 skills** — unused, theoretical
- **E3** (DCI-verified): **0 skills** in seed data
- **E4** (DCI + auto-learning): **1 skill** (specweave itself)

The distinction between E3 and E4 is artificial — Reflect (auto-learning) is an optional feature, not a classification tier. The "portability matrix" is academic since only Claude Code executes skills today. The frontmatter extensibility schema (E2) has zero adoption.

### Solution

Replace E0-E4 with three clear categories:

| Category | Meaning | Detection |
|---|---|---|
| **Extensible** | Has a DCI block loading from `skill-memories/`. Users KNOW there's a standard, discoverable file to customize behavior. | DCI block with `skill-memories` reference |
| **Semi-Extensible** | Mentions customization mechanisms but NOT through the standardized skill-memories system. Skill-specific knowledge required. | Keyword signals in prose |
| **Not Extensible** | No customization mechanism. Fork SKILL.md to change behavior. | No signals |

## User Stories

### US-001: Simplify ExtensibilityTier Type and Detector (P1)
**Project**: specweave

**As a** platform developer
**I want** the extensibility system to use 3 clear categories instead of 5 confusing tiers
**So that** the codebase is simpler and the classification is honest about what "extensible" actually means

**Acceptance Criteria**:
- [x] **AC-US1-01**: `ExtensibilityTier` type in `types.ts` is `"extensible" | "semi-extensible" | "not-extensible"`
- [x] **AC-US1-02**: `detectExtensibility()` classifies skills with DCI blocks referencing `skill-memories` as `extensible`
- [x] **AC-US1-03**: `detectExtensibility()` classifies skills with keyword signals (template, hook, config, plugin, context) as `semi-extensible`
- [x] **AC-US1-04**: `detectExtensibility()` classifies skills with no signals as `not-extensible`
- [x] **AC-US1-05**: Frontmatter extensibility detection (E2) is removed — zero skills use it
- [x] **AC-US1-06**: Portability matrix is removed from `ExtensibilityResult` — only Claude Code runs skills today
- [x] **AC-US1-07**: `extensible: boolean` backward-compat field preserved: `true` for both `extensible` and `semi-extensible`, `false` for `not-extensible`
- [x] **AC-US1-08**: All extensibility-detector tests rewritten covering all 3 tiers plus edge cases
- [x] **AC-US1-09**: `getExtensibilityStats()` in `data.ts` returns counts for 3 categories instead of 5 tiers
- [x] **AC-US1-10**: Fenced code block stripping still works (DCI patterns inside ``` blocks are ignored)

---

### US-002: Update Seed Data and Platform UI (P1)
**Project**: specweave

**As a** marketplace user
**I want** skills to be honestly classified as extensible, semi-extensible, or not extensible
**So that** I can quickly understand which skills I can customize via skill-memories vs which require skill-specific knowledge

**Acceptance Criteria**:
- [x] **AC-US2-01**: All 20 former-E1 skills in `seed-data.ts` are reclassified as `semi-extensible` with existing extension points preserved
- [x] **AC-US2-02**: The 1 former-E4 skill (specweave) is reclassified as `extensible`
- [x] **AC-US2-03**: Skills list page filter shows 3 categories (Extensible / Semi-Extensible / Not Extensible) instead of E0-E4 sub-filters
- [x] **AC-US2-04**: Skill detail page shows new tier label with appropriate styling (green=extensible, yellow=semi-extensible, gray=not-extensible)
- [x] **AC-US2-05**: `ext=true` URL query param still works (returns both extensible and semi-extensible skills)
- [x] **AC-US2-06**: New URL params `ext=extensible` and `ext=semi-extensible` filter to specific tiers

---

### US-003: Rewrite Extensibility Documentation (P2)
**Project**: specweave

**As a** skill author or user
**I want** the extensibility docs to clearly explain the 3 categories without academic jargon
**So that** I understand exactly what "extensible" means and how to make my skill extensible

**Acceptance Criteria**:
- [x] **AC-US3-01**: `extensible-skills-standard.md` defines 3 categories with clear definitions
- [x] **AC-US3-02**: `extensible-skills-guide.md` simplified — removes E0-E4 tier table, portability matrix, frontmatter schema section
- [x] **AC-US3-03**: `extensible-skills.md` landing page uses 3-category quick reference table
- [x] **AC-US3-04**: DCI block documentation preserved and still accurate
- [x] **AC-US3-05**: Skill memories documentation preserved and still accurate
- [x] **AC-US3-06**: Docs clearly state Reflect/auto-learning is an optional feature orthogonal to extensibility classification

## Functional Requirements

### FR-001: Backward Compatibility
The `extensible: boolean` field on `SkillData` must remain. Both `extensible` and `semi-extensible` tiers map to `extensible: true`. This ensures existing API consumers and filtered views continue working.

### FR-002: Clean Removal of Unused Concepts
Frontmatter extensibility detection, portability matrix, and E0-E4 tier naming are fully removed from code and docs. No deprecated stubs or backward-compat shims.

## Success Criteria

- ExtensibilityTier type has exactly 3 values
- Zero references to E0/E1/E2/E3/E4 remain in platform code
- All extensibility-detector tests pass
- Platform builds and deploys successfully
- Docs site builds successfully

## Out of Scope

- Changes to DCI blocks or how they execute
- Changes to skill-memories system or cascading lookup
- Changes to Reflect auto-learning system
- Changes to the specweave CLI
- New extensibility features

## Dependencies

- None — this is a simplification/refactor of existing code
