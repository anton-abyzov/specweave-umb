---
increment: 0478-skills-docs-rhetoric-alignment
title: Align skills documentation rhetoric with Anthropic official terminology
type: change-request
priority: P1
status: completed
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Align skills documentation rhetoric with Anthropic official terminology

## Problem Statement

SpecWeave's skills documentation currently frames several built-in Claude Code features as SpecWeave inventions. "Dynamic Context Injection (DCI)" is presented as a proprietary acronym when it is Claude Code's native `!command` syntax. "Extensible Skills Standard" implies a formal standard body when it is a SpecWeave convention. SOLID/Open-Closed Principle references position skill customization as software engineering architecture when the mechanism is simpler than that. The glossary contains an incorrect expansion ("Direct Command Injection" instead of "dynamic context injection"). These misalignments undermine credibility with developers who know Anthropic's official terminology.

## Goals

- Replace all invented acronyms and inflated terminology with Anthropic-aligned language
- Clearly communicate what Claude Code provides natively vs what SpecWeave adds on top
- Remove software engineering jargon (SOLID/OCP) that over-formalizes simple skill customization
- Fix factual errors in the glossary

## User Stories

### US-001: Replace invented terminology with Anthropic-aligned language (P1)
**Project**: specweave

**As a** developer reading SpecWeave's skills documentation
**I want** terminology that aligns with Anthropic's official Claude Code concepts
**So that** I can trust the documentation is accurate and not inflating SpecWeave's contributions

**Acceptance Criteria**:
- [x] **AC-US1-01**: All occurrences of "Dynamic Context Injection (DCI)" and standalone "DCI" across the docs-site are replaced with lowercase "dynamic context injection"; first occurrence on each page notes it is "Claude Code's built-in `!command` syntax"
- [x] **AC-US1-02**: All occurrences of "Extensible Skills Standard" are replaced with "Extensible Skills" (filenames remain unchanged)
- [x] **AC-US1-03**: The "programs written in English" tagline in skills/index.md and any other files is replaced with "Skills extend what AI coding agents can do -- structured markdown files that define how an agent behaves in specific domains" (shorter form "structured markdown instructions" or "detailed playbooks" where space is limited)
- [x] **AC-US1-04**: The incorrect glossary entry "Direct Command Injection" in skills-ecosystem-security.md is corrected to "dynamic context injection"
- [x] **AC-US1-05**: Zero occurrences of uppercase "DCI" as an acronym remain in any docs-site markdown file (excluding code fences showing filenames or CLI output)

---

### US-002: Remove SOLID/OCP references from skill customization docs (P1)
**Project**: specweave

**As a** developer evaluating SpecWeave's skill extensibility model
**I want** the docs to explain customization in plain terms without software engineering design pattern jargon
**So that** the mechanism feels approachable rather than over-engineered

**Acceptance Criteria**:
- [x] **AC-US2-01**: All references to "Open/Closed Principle" and "SOLID" are removed or replaced with plain-language explanations across ALL docs-site markdown files (not limited to the 15 initially listed files)
- [x] **AC-US2-02**: The replacement text explains the same concept without jargon -- e.g., "core skill logic stays stable; your project-specific customizations layer on top" or equivalent
- [x] **AC-US2-03**: No occurrences of "Open/Closed Principle" or "SOLID" remain in any docs-site markdown file (drafts/ excluded from this requirement)

---

### US-003: Clarify SpecWeave's additive value over Claude Code native features (P1)
**Project**: specweave

**As a** developer evaluating whether to adopt SpecWeave
**I want** clear communication about what Claude Code provides natively vs what SpecWeave builds on top
**So that** I understand the value proposition without feeling misled

**Acceptance Criteria**:
- [x] **AC-US3-01**: The skills landing page (skills/index.md) includes a brief section or inline note that acknowledges Claude Code's native skill system and positions SpecWeave's contributions (Verified Skills, vskill CLI, marketplace, extensibility conventions) as building on top of it
- [x] **AC-US3-02**: The additive framing uses collaborative tone ("SpecWeave builds on Claude Code's native skill system by adding...") rather than contrasting/delineation tone
- [x] **AC-US3-03**: Pages that describe dynamic context injection reference it as a Claude Code built-in capability that SpecWeave leverages, not a SpecWeave invention

## Functional Requirements

### FR-001: Scope includes all docs-site markdown files
All markdown files under `repositories/anton-abyzov/specweave/docs-site/docs/` are in scope for terminology replacement. The `drafts/` directory is excluded.

### FR-002: No file renames
Filenames (e.g., `extensible-skills-standard.md`) remain unchanged even when in-text references to "Extensible Skills Standard" are updated. URL stability takes priority.

### FR-003: Replacement patterns
| Find | Replace with |
|------|-------------|
| `Dynamic Context Injection (DCI)` | `dynamic context injection` (first on page: add "Claude Code's built-in `!command` syntax") |
| Standalone `DCI` (acronym usage) | `dynamic context injection` or `injection block` (when full phrase was recently used) |
| `Extensible Skills Standard` | `Extensible Skills` |
| `Open/Closed Principle` / `SOLID` references | Plain-language equivalent |
| `programs written in English` | Anthropic-aligned framing (see AC-US1-03) |
| `Direct Command Injection` (glossary) | `dynamic context injection` |

## Success Criteria

- Zero occurrences of uppercase "DCI" as an acronym in docs-site markdown (excluding drafts/)
- Zero occurrences of "Extensible Skills Standard" in docs-site markdown
- Zero occurrences of "Open/Closed Principle" or "SOLID" in docs-site markdown (excluding drafts/)
- All pages that discuss dynamic context injection credit it as a Claude Code built-in
- Documentation reads as collaborative/additive rather than claiming inventorship

## Out of Scope

- Renaming any files or changing URL slugs
- Changes to `drafts/` directory content
- Changes to non-docs-site files (CLI source, plugin SKILL.md files, etc.)
- Structural reorganization of docs pages
- Changes to the vskill README (deferred to a separate pass)
- Sidebar, navigation, or config file changes (unless required by in-text reference updates)

## Dependencies

- Access to `repositories/anton-abyzov/specweave/docs-site/docs/` directory
- Knowledge of Anthropic's official Claude Code terminology (current as of early 2026)
