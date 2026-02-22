---
increment: 0279-extensible-skills-standard-spec
title: "Extensible Skills Standard Formalization"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Extensible Skills Standard Formalization

## Overview

Formalize the Extensible Skills Standard with tiered definitions (E0-E4), structured frontmatter declaration format, an enhanced detector that checks DCI blocks (not just keyword patterns), platform statistics (extensibility counts on `/api/v1/stats` and `/skills` page filtering by tier), and documentation restructure from the current how-to guide into a formal standard plus implementation guide.

### Problem Statement

The current extensibility system has three gaps:

1. **Binary classification**: Skills are either "extensible" or not. The detector pattern-matches prose keywords ("custom templates", "lifecycle hooks") but cannot distinguish between a skill that *mentions* extension in its description vs. one that has a verified DCI block with working `skill-memories` lookup. Example: `k8s-manifests` is flagged extensible because its description mentions "custom manifest templates", but it has no DCI shell block -- users cannot actually customize it without forking SKILL.md.

2. **No tier model**: All 21/89 extensible skills (24%) are effectively E1 (keyword-detected). There is no distinction between declarative config extensibility and runtime DCI-based extensibility. DCI is Claude Code-only (1/39 agents) -- a portability matrix is needed so skill authors and consumers understand what works where.

3. **Documentation gap**: The current `extensible-skills.md` is a how-to guide mixing the standard definition, architecture, getting started, and FAQ. It needs to be split into a formal standard (normative) and an implementation guide (informative).

### Key Scenarios

- **k8s-manifests**: Has keyword-detected extension points (template, config) but no DCI block. Under the new standard, this is E1 (declarative -- documents extension points in prose) vs. E2+ (verified DCI block present).
- **specweave**: Has DCI blocks + `skill-memories` lookup + auto-learning via Reflect. This is E3/E4 (runtime-extensible with verified mechanism).
- **eslint-config**: Has `config` and `plugin` extension points detected by keywords. Actual extensibility depends on whether SKILL.md has a DCI one-liner.

## User Stories

### US-001: Extensibility Tier Model (P1)
**Project**: vskill-platform

**As a** skill registry maintainer
**I want** a formal E0-E4 tier classification for skill extensibility
**So that** I can accurately represent the extensibility level of each skill and users can distinguish "mentions extension" from "has verified DCI block"

**Acceptance Criteria**:
- [x] **AC-US1-01**: The `ExtensibilityResult` type includes a `tier` field with values E0 (not extensible), E1 (declarative/keyword-detected), E2 (frontmatter-declared), E3 (DCI-verified), E4 (DCI + auto-learning/Reflect)
- [x] **AC-US1-02**: The `detectExtensibility` function returns the correct tier based on signals found (keywords only = E1, frontmatter `extensibility:` block = E2, DCI shell block detected = E3, DCI + reflect/auto-learn reference = E4)
- [x] **AC-US1-03**: Existing keyword-only detection continues to work and is classified as E1
- [x] **AC-US1-04**: Backward compatibility: `extensible: boolean` remains derived (true when tier >= E1) so existing consumers are unaffected

---

### US-002: Enhanced Detector with DCI Block Detection (P1)
**Project**: vskill-platform

**As a** skill registry maintainer
**I want** the extensibility detector to parse DCI shell blocks (`!` backtick commands) and structured frontmatter in SKILL.md content
**So that** I can distinguish keyword-mentioned extensibility (E1) from verified DCI-based extensibility (E3+)

**Acceptance Criteria**:
- [x] **AC-US2-01**: The detector identifies DCI shell blocks matching the pattern `` !`...skill-memories...` `` or `` !`...` `` within SKILL.md content and classifies as E3+
- [x] **AC-US2-02**: The detector parses YAML frontmatter for an `extensibility:` key with structured tier declaration (e.g., `extensibility: { tier: E2, points: [...] }`) and classifies accordingly
- [x] **AC-US2-03**: When both keyword signals AND DCI blocks are found, the highest tier wins (DCI > frontmatter > keywords)
- [x] **AC-US2-04**: A SKILL.md with DCI block referencing `skill-memories` AND a `reflect` or `auto-learn` reference is classified as E4
- [x] **AC-US2-05**: Test coverage for all tier transitions: plain text (E0), keyword-only (E1), frontmatter-declared (E2), DCI-block (E3), DCI + reflect (E4)

---

### US-003: Portability Matrix (P1)
**Project**: vskill-platform

**As a** skill author
**I want** a portability matrix showing which extensibility mechanisms work with which agents
**So that** I can make informed decisions about which extensibility tier to target

**Acceptance Criteria**:
- [x] **AC-US3-01**: The `ExtensibilityResult` includes a `portability` field mapping mechanism names to arrays of compatible agent slugs (e.g., `{ "DCI": ["claude-code"], "frontmatter": ["claude-code", "cursor", ...], "keyword": ["*"] }`)
- [x] **AC-US3-02**: DCI (shell-based `!` backtick execution) is mapped exclusively to `claude-code` agent
- [x] **AC-US3-03**: Frontmatter-declared extensibility is portable to any agent that reads YAML frontmatter
- [x] **AC-US3-04**: The skill detail page displays the portability information for extensible skills

---

### US-004: Platform Statistics for Extensibility (P2)
**Project**: vskill-platform

**As a** platform user
**I want** the `/api/v1/stats` endpoint to include extensibility counts broken down by tier
**So that** I can see the ecosystem's extensibility distribution at a glance

**Acceptance Criteria**:
- [x] **AC-US4-01**: `/api/v1/stats` response includes an `extensibility` object with `total` count and per-tier counts (`e0`, `e1`, `e2`, `e3`, `e4`)
- [x] **AC-US4-02**: The `/skills` page extensible filter toggle shows the tier breakdown (not just a total count)
- [x] **AC-US4-03**: The `/skills` page supports filtering by extensibility tier via `?ext=E2` (or higher) query parameter, replacing the current boolean `?ext=true`

---

### US-005: Documentation Restructure (P2)
**Project**: specweave (docs-site)

**As a** skill author or consumer
**I want** the extensible skills documentation split into a formal standard (normative) and an implementation guide (informative)
**So that** I can reference the standard for tier definitions and the guide for practical how-to steps

**Acceptance Criteria**:
- [x] **AC-US5-01**: The current `extensible-skills.md` is restructured into two documents: `extensible-skills-standard.md` (formal tier definitions E0-E4, DCI specification, frontmatter schema, portability matrix) and `extensible-skills-guide.md` (getting started, examples, FAQ)
- [x] **AC-US5-02**: The standard document uses RFC-style normative language (MUST, SHOULD, MAY) for tier requirements
- [x] **AC-US5-03**: The index page and sidebar reflect the new structure
- [x] **AC-US5-04**: All internal cross-references and the vskill-platform UI links are updated to point to the new URLs

---

### US-006: Seed Data and Existing Skills Migration (P2)
**Project**: vskill-platform

**As a** platform maintainer
**I want** the seed data updated with accurate extensibility tiers for all 89 skills
**So that** the platform reflects the new tier model from launch

**Acceptance Criteria**:
- [x] **AC-US6-01**: Each skill in `seed-data.ts` has an `extensibilityTier` field (E0-E4) in addition to the existing `extensible` boolean
- [x] **AC-US6-02**: Skills currently flagged `extensible: true` with keyword-only detection are assigned E1
- [x] **AC-US6-03**: Skills with known DCI blocks (e.g., SpecWeave's own skills) are assigned E3 or E4
- [x] **AC-US6-04**: The `SkillData` type is updated with `extensibilityTier?: 'E0' | 'E1' | 'E2' | 'E3' | 'E4'`

## Functional Requirements

### FR-001: Extensibility Tier Enum
Define `ExtensibilityTier` as `'E0' | 'E1' | 'E2' | 'E3' | 'E4'` with the following semantics:
- **E0**: Not extensible. No extension points detected.
- **E1**: Declarative. Keywords in prose mention extension points (templates, hooks, config overrides). No verified mechanism.
- **E2**: Frontmatter-declared. SKILL.md YAML frontmatter contains `extensibility:` block with structured declaration.
- **E3**: DCI-verified. SKILL.md contains a working DCI shell block (`` !`...` ``) that loads skill-memories.
- **E4**: DCI + Auto-Learning. E3 plus evidence of Reflect/auto-learning integration.

### FR-002: Enhanced Detector Signals
The detector MUST check these signals in order of strength:
1. DCI block with `skill-memories` reference + `reflect` reference -> E4
2. DCI block with `skill-memories` reference -> E3
3. YAML frontmatter `extensibility:` key -> E2
4. Keyword pattern matches (existing SIGNALS array) -> E1
5. None of the above -> E0

### FR-003: Backward Compatibility
The `extensible: boolean` field MUST remain on `SkillData` and be derived from `tier >= E1`. All existing API consumers using `?ext=true` MUST continue to work.

## Success Criteria

- All 89 seed data skills have accurate extensibility tiers assigned
- The extensibility detector correctly classifies sample SKILL.md content across all 5 tiers with test coverage
- `/api/v1/stats` returns tier-level extensibility breakdown
- Documentation is split into standard + guide with no broken links
- Zero breaking changes to existing API consumers

## Out of Scope

- Automated scanning of actual SKILL.md files from GitHub repos (uses seed data + manual classification)
- Runtime validation that DCI blocks actually execute correctly
- Agent-specific extension mechanisms beyond DCI (e.g., Cursor's `.cursorrules` injection)
- Prisma schema changes (extensibility data stays in KV/seed layer)

## Dependencies

- Existing extensibility detector at `src/lib/scanner/extensibility-detector.ts`
- Existing seed data at `src/lib/seed-data.ts`
- Existing types at `src/lib/types.ts`
- Existing docs at `docs-site/docs/skills/extensible/`
