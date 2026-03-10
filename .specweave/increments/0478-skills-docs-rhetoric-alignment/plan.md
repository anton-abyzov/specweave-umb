# Plan: Align skills documentation rhetoric with Anthropic official terminology

## Overview

Copy-editing pass across 20 markdown files in `repositories/anton-abyzov/specweave/docs-site/docs/`. No code, no file renames, no structural reorganization. Total: ~97 occurrences of banned terminology to replace across four categories. The plan defines the editing strategy: file grouping, replacement rules, execution order, and verification.

## Editing Strategy: Batch by file, prioritize by terminology category

Each file gets a single editing pass that applies all applicable replacements at once. The terminology categories below define replacement rules and priority (which phrasing decisions to make first), not separate file-revisit passes.

## Replacement Rules

### R1: DCI / Dynamic Context Injection (51 occurrences, 9 files)

- First occurrence on each page: `dynamic context injection (Claude Code's built-in !command syntax)`
- Subsequent on same page: `dynamic context injection` or `injection block` for brevity
- Standalone uppercase `DCI`: always expand to `dynamic context injection`
- Never capitalize unless start of sentence

### R2: Extensible Skills Standard (21 occurrences, 12 files)

- Simple find-replace: `Extensible Skills Standard` -> `Extensible Skills`
- No context variation needed

### R3: SOLID / Open-Closed Principle (25 occurrences, 12 files)

- Replace with plain language: "core skill logic stays stable; your project-specific customizations layer on top" or contextually appropriate equivalent
- Remove standalone SOLID mentions without replacement where they add no meaning

### R4: Tagline + Glossary fix + Additive framing (3 files, targeted edits)

- `skills/index.md`: Replace "programs written in English" with spec-defined framing (AC-US1-03); add additive-value note acknowledging Claude Code's native skill system (AC-US3-01/02)
- `guides/youtube-tutorial-script.md`: Replace "programs written in English"
- `skills/verified/skills-ecosystem-security.md`: Fix "Direct Command Injection" -> "dynamic context injection"

## File Inventory

### High-density files (need R1 + R2 + R3 -- edit these first)

| # | File (relative to docs-site/docs/) | R1 | R2 | R3 | R4 |
|---|-----------------------------------|----|----|----|-----|
| 1 | `skills/extensible/extensible-skills-standard.md` | 17 | 2 | 1 | -- |
| 2 | `skills/extensible/extensible-skills-guide.md` | 15 | 3 | 2 | -- |
| 3 | `skills/extensible/extensible-skills.md` | 5 | 2 | 4 | -- |
| 4 | `skills/extensible/index.md` | 4 | 3 | 4 | -- |
| 5 | `skills/index.md` | 3 | 3 | 1 | tagline + additive framing |

### Medium-density files (need R1 or R2 + other)

| # | File | R1 | R2 | R3 | R4 |
|---|------|----|----|----|-----|
| 6 | `skills/verified/skills-ecosystem-security.md` | 4 | -- | -- | glossary fix |
| 7 | `skills/verified/verified-skills.md` | 1 | 2 | -- | -- |
| 8 | `skills/fundamentals.md` | 1 | 1 | -- | -- |
| 9 | `skills/extensible/skill-development-guidelines.md` | -- | 1 | 4 | -- |
| 10 | `skills/skill-discovery-evaluation.md` | 1 | -- | -- | -- |

### Single-category files

| # | File | Category |
|---|------|----------|
| 11 | `skills/verified/index.md` | R2 (1) |
| 12 | `academy/talks/skills-plugins-marketplaces.md` | R2 (1) |
| 13 | `guides/core-concepts/skills-first-architecture.md` | R2 (1) |
| 14 | `glossary/terms/skills-vs-agents.md` | R2 (1) |
| 15 | `overview/skills-as-programs.md` | R3 (2) |
| 16 | `quick-start.md` | R3 (2) |
| 17 | `guides/youtube-tutorial-script.md` | R3 (2) + R4 tagline |
| 18 | `glossary/categories/architecture.md` | R3 (1) |
| 19 | `glossary/index-by-category.md` | R3 (1) |
| 20 | `academy/fundamentals/software-engineering-roles.md` | R3 (1) |

## Execution Order

1. Files 1-5 (high-density, all categories intersect)
2. Files 6-10 (medium-density)
3. Files 11-20 (single-category, can all be done in parallel)
4. Verification grep sweep

Files within each group are independent and can be edited in parallel.

## Verification

After all edits, run these grep checks against `repositories/anton-abyzov/specweave/docs-site/docs/` (excluding `drafts/`). All must return zero results:

- `DCI` as standalone acronym (exclude code fences)
- `Dynamic Context Injection` (capitalized)
- `Extensible Skills Standard`
- `Open/Closed Principle` or `Open-Closed Principle`
- `SOLID` (as design principle reference)
- `Direct Command Injection`
- `programs written in English`

## Constraints

- No file renames (FR-002)
- No structural/nav/sidebar changes
- `drafts/` excluded from scope
- No CLI source or SKILL.md edits
- Collaborative/additive tone throughout

## Risk

Low. All changes are in-text markdown edits. Only risk is missing an occurrence, mitigated by grep verification. DCI inside code fences showing filenames/CLI output is allowed per spec (AC-US1-05).

## No ADR or Domain Delegation Needed

No architectural decisions to record. No frontend/backend/testing domain skills apply -- this is a markdown editing task.
