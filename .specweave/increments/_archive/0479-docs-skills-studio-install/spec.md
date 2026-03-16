---
increment: 0479-docs-skills-studio-install
title: 'Documentation Update: Skills, Skill Studio, Installation'
type: feature
priority: P1
status: completed
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Documentation Update: Skills, Skill Studio, Installation

## Problem Statement

Installation information for vskill (the AI skill package manager) is scattered across 4+ docs pages with no single authoritative guide. Skill Studio, a local browser-based IDE for skill development, has zero documentation beyond a homepage section with a video. There is no CLI reference page for vskill's 12 commands. This fragmentation forces users to piece together information from multiple sources, increasing time-to-first-install and reducing Skill Studio adoption.

## Goals

- Create a single authoritative installation guide that replaces scattered install fragments
- Document Skill Studio so users can discover and use the local skill development IDE
- Provide a complete CLI reference for all 12 vskill commands
- Update existing pages to cross-reference new content and eliminate duplication
- Maintain consistent navigation via sidebar and internal linking

## User Stories

### US-001: Skill Installation Guide (P1)
**Project**: specweave

**As a** developer new to AI skills
**I want** a single guide that covers all ways to install skills with vskill
**So that** I can install my first skill without visiting multiple pages

**Acceptance Criteria**:
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

### US-002: Skill Studio Documentation (P1)
**Project**: specweave

**As a** skill author
**I want** documentation for the Skill Studio IDE
**So that** I can use it to develop, test, and improve my skills locally

**Acceptance Criteria**:
- [x] **AC-US2-01**: Page exists at `docs/skills/skill-studio.md` with frontmatter
- [x] **AC-US2-02**: Documents quick start: `npx vskill studio` launches the local Vite React UI
- [x] **AC-US2-03**: Documents all 6 workspace panels: Editor, Tests, Run, Activation, History, Dependencies
- [x] **AC-US2-04**: Documents A/B benchmarking and model comparison features
- [x] **AC-US2-05**: Documents the skill improvement workflow (iterate, test, compare)
- [x] **AC-US2-06**: Documents creating skills inline within the Studio
- [x] **AC-US2-07**: Includes keyboard shortcuts reference
- [x] **AC-US2-08**: Lists relevant CLI commands (`vskill studio`, `vskill eval`)
- [x] **AC-US2-09**: Docusaurus build passes with the new page included

---

### US-003: vskill CLI Reference (P2)
**Project**: specweave

**As a** developer using vskill
**I want** a complete CLI reference page
**So that** I can look up exact command syntax and flags without reading `--help`

**Acceptance Criteria**:
- [x] **AC-US3-01**: Page exists at `docs/skills/vskill-cli.md` with frontmatter
- [x] **AC-US3-02**: Documents all 12 vskill commands with syntax, flags, and examples
- [x] **AC-US3-03**: Each command entry includes: name, description, usage syntax, flags/options table, and at least one example
- [x] **AC-US3-04**: Commands are organized by category (install, discover, develop, manage)
- [x] **AC-US3-05**: Docusaurus build passes with the new page included

---

### US-004: Sidebar and Navigation Updates (P1)
**Project**: specweave

**As a** docs site visitor
**I want** the new pages to appear in the sidebar navigation
**So that** I can find them through browsing, not just search

**Acceptance Criteria**:
- [x] **AC-US4-01**: `sidebars.ts` updated to include `skills/installation` in the Skills sidebar, positioned early (before the standards sections)
- [x] **AC-US4-02**: `sidebars.ts` updated to include `skills/skill-studio` in the Skills sidebar
- [x] **AC-US4-03**: `sidebars.ts` updated to include `skills/vskill-cli` in the Skills sidebar (under Ecosystem or Reference category)
- [x] **AC-US4-04**: `docusaurus.config.ts` updated if any navbar items need adjustment for new pages
- [x] **AC-US4-05**: All sidebar links resolve correctly (no 404s from sidebar navigation)

---

### US-005: Existing Page Cross-Reference Updates (P2)
**Project**: specweave

**As a** docs site visitor reading existing skills pages
**I want** links to the new installation, Studio, and CLI pages where contextually relevant
**So that** I discover related content naturally while reading

**Acceptance Criteria**:
- [x] **AC-US5-01**: `skills/index.md` updated with links to installation guide, Skill Studio, and CLI reference in the "Explore Further" section
- [x] **AC-US5-02**: `getting-started/index.md` updated to reference the vskill installation guide where skill/plugin installation is mentioned
- [x] **AC-US5-03**: `overview/plugins-ecosystem.md` updated to link to the installation guide and CLI reference where relevant
- [x] **AC-US5-04**: `skills/fundamentals.md` updated to cross-reference installation guide (where "install" is discussed) and CLI reference
- [x] **AC-US5-05**: `skills/skill-discovery-evaluation.md` updated to reference installation guide and vskill CLI in the SpecWeave Approach section
- [x] **AC-US5-06**: No broken internal links introduced by changes (`npm run build` exits 0)

## Functional Requirements

### FR-001: Content Accuracy
All vskill command syntax, flags, and behavior descriptions must match the actual vskill CLI implementation. Verify against `vskill --help` and subcommand help output.

### FR-002: Docusaurus Compatibility
All new markdown files must use valid Docusaurus 3.9 frontmatter and MDX-compatible syntax. Admonitions (:::tip, :::warning) follow Docusaurus conventions.

### FR-003: Consolidation Over Duplication
The installation guide becomes the single source of truth for "how to install skills." Existing pages that have install snippets should link to the guide rather than duplicating content.

## Success Criteria

- All 3 new pages render correctly in Docusaurus build
- `npm run build` passes with 0 errors in docs-site
- No broken internal links across the skills section
- Installation guide covers all 3 install sources (registry, GitHub, local)
- Skill Studio page documents all 6 workspace panels

## Out of Scope

- Video/animation content creation (reference existing videos only)
- Changes to vskill CLI source code
- Changes to verifiedskill.com platform
- Translations or i18n
- New Docusaurus plugins or theme customizations
- Performance benchmarks or load testing of docs site

## Dependencies

- Access to `vskill --help` output for accurate CLI reference
- Existing docs-site Docusaurus build must be working
- Current sidebars.ts structure (Skills sidebar already exists)

## Technical Notes

- Docs site is Docusaurus 3.9 at `repositories/anton-abyzov/specweave/docs-site/`
- All new files go under `docs/skills/` directory
- Sidebar config is in `sidebars.ts` (TypeScript, not JSON)
- Existing Skills sidebar has categories: Overview, Why Skills Matter, Fundamentals, Extensible Standard, Verified Standard, Ecosystem, Reference
- New pages should slot in logically: Installation near top, Studio under Ecosystem or its own section, CLI under Reference
