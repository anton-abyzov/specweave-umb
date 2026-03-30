---
increment: 0651-figma-connect-skill
title: Figma Connect Skill - Combined MCP + CLI
type: feature
priority: P1
status: ready_for_review
created: 2026-03-30T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Figma Connect Skill - Combined MCP + CLI

## Overview

A new vskill plugin skill that bridges Figma's MCP server (16 tools for reading designs, generating code, extracting tokens) with the Code Connect CLI (`@figma/code-connect` for publishing persistent component mappings to Dev Mode). Neither tool alone covers the full design-to-code lifecycle — this skill combines them into 5 unified workflow modes.

## User Stories

### US-001: Skill Setup and Category Scaffold (P1)
**Project**: vskill

**As a** skill developer
**I want** a new "frontend" plugin category with a figma-connect skill
**So that** the skill is discoverable and distributable via vskill platform

**Acceptance Criteria**:
- [x] **AC-US1-01**: `plugins/frontend/.claude-plugin/plugin.json` exists with valid metadata (name, description, version, author, keywords)
- [x] **AC-US1-02**: `plugins/frontend/skills/figma-connect/SKILL.md` exists with valid frontmatter (name, description, metadata.tags)
- [x] **AC-US1-03**: SKILL.md is under 500 lines with reference material in `references/` directory

---

### US-002: Design-to-Code Workflow (P1)
**Project**: vskill

**As a** frontend developer
**I want** to implement UI components from Figma design URLs
**So that** I can translate designs to production code using both MCP context and existing Code Connect mappings

**Acceptance Criteria**:
- [x] **AC-US2-01**: Skill correctly parses standard, branch, and Make Figma URL formats (extracts fileKey, nodeId)
- [x] **AC-US2-02**: Skill checks existing Code Connect mappings (MCP `get_code_connect_map`) before generating new code
- [x] **AC-US2-03**: Skill uses MCP `get_design_context` with correct framework/language params for code generation
- [x] **AC-US2-04**: Skill adapts generated code to project conventions (existing components, tokens, patterns)

---

### US-003: Code Connect Publishing (P1)
**Project**: vskill

**As a** design system maintainer
**I want** to publish Code Connect mappings from code components back to Figma Dev Mode
**So that** designers and developers see accurate code snippets when inspecting components

**Acceptance Criteria**:
- [x] **AC-US3-01**: Skill uses MCP `get_code_connect_suggestions` to identify unmapped components
- [x] **AC-US3-02**: Skill generates `.figma.tsx` files with proper Code Connect property mappings (figma.string, figma.boolean, figma.enum, figma.instance)
- [x] **AC-US3-03**: Skill validates with CLI (`npx figma connect parse`) before publishing
- [x] **AC-US3-04**: Skill publishes via CLI (`npx figma connect publish`) and verifies via MCP `get_code_connect_map`
- [x] **AC-US3-05**: Skill supports `--dry-run` mode for validation without publishing

---

### US-004: Token Extraction (P2)
**Project**: vskill

**As a** frontend developer
**I want** to extract design tokens from Figma variables and write them to my project's token format
**So that** design decisions are automatically synchronized to code

**Acceptance Criteria**:
- [x] **AC-US4-01**: Skill extracts Figma variables via MCP `get_variable_defs`
- [x] **AC-US4-02**: Skill detects project token format (CSS custom properties, Tailwind config, Style Dictionary)
- [x] **AC-US4-03**: Skill organizes tokens by category (colors, spacing, typography) in the output

---

### US-005: Eval Suite (P1)
**Project**: vskill

**As a** skill developer
**I want** comprehensive evals for all workflow modes
**So that** skill quality can be measured and regressions caught

**Acceptance Criteria**:
- [x] **AC-US5-01**: `evals/evals.json` contains 12 eval cases covering all 5 modes + error paths
- [x] **AC-US5-02**: Each eval has 3-5 specific, objectively checkable boolean assertions
- [x] **AC-US5-03**: `evals/activation-prompts.json` contains 20 prompts (10 should_activate, 10 should_not_activate)
- [ ] **AC-US5-04**: Benchmark achieves 83%+ pass rate (10/12 evals)

---

### US-006: Framework Detection and Dual Auth (P1)
**Project**: vskill

**As a** developer using React, Vue, SwiftUI, or Compose
**I want** the skill to auto-detect my framework and handle both MCP and CLI authentication
**So that** I don't have to manually configure framework labels or deal with auth confusion

**Acceptance Criteria**:
- [x] **AC-US6-01**: Skill detects framework from project files (package.json, Podfile, build.gradle) and maps to Code Connect labels
- [x] **AC-US6-02**: Skill checks MCP auth via `whoami` and guides setup if missing
- [x] **AC-US6-03**: Skill checks CLI auth (`FIGMA_ACCESS_TOKEN`) and guides setup if missing
- [x] **AC-US6-04**: Error handling table covers auth failures, missing CLI, parse errors, rate limits

## Out of Scope

- Figma plugin development (writing Figma plugins)
- FigJam diagram generation (use MCP tools directly)
- Figma file creation / write-to-canvas (use MCP `use_figma` directly)
- Storybook integration setup
- Custom Code Connect parser development

## Dependencies

- Figma MCP server installed and authenticated in Claude Code
- `@figma/code-connect` CLI (skill guides installation if missing)
- Node.js 18+ (for CLI)
- Organization/Enterprise Figma plan (for Code Connect features)
