---
increment: 0294-skill-page-agent-pills
title: "Skill page Works-with colorful agent pills"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Skill page Works-with colorful agent pills

## Overview

The homepage "Works with N agents" section displays rich, brand-colored pill badges with vendor icons for each agent. The skill detail page's "Works with" section currently shows plain grey square badges with no icons and no brand colors. This increment extracts `AGENT_COLORS` and `AGENT_ICONS` into a shared lib file and updates the skill detail page to use the same colorful, icon-rich pill badges as the homepage.

## User Stories

### US-001: Shared agent branding constants (P1)
**Project**: specweave

**As a** developer
**I want** AGENT_COLORS and AGENT_ICONS to live in a single shared lib file
**So that** both the homepage and skill detail page can import them without duplication

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new shared file `src/lib/agent-branding.ts` exports `AGENT_COLORS` and `AGENT_ICONS` with the same data currently in `src/app/page.tsx`
- [x] **AC-US1-02**: `src/app/page.tsx` imports `AGENT_COLORS` and `AGENT_ICONS` from the shared file instead of defining them inline
- [x] **AC-US1-03**: No duplicate definitions of `AGENT_COLORS` or `AGENT_ICONS` exist in the codebase

---

### US-002: Brand-colored agent pills on skill detail page (P1)
**Project**: specweave

**As a** user viewing a skill detail page
**I want** the "Works with" section to show brand-colored pill badges with icons
**So that** the agent compatibility section looks consistent with the homepage and is easier to scan

**Acceptance Criteria**:
- [x] **AC-US2-01**: Each agent in the "Works with" section renders as a rounded pill with the agent's brand color (from `AGENT_COLORS`) as a tinted background and border
- [x] **AC-US2-02**: Agents that have an entry in `AGENT_ICONS` show the brand icon (13x13px) to the left of the name
- [x] **AC-US2-03**: Agents without an icon entry but with a color entry show a small colored dot indicator
- [x] **AC-US2-04**: Agents without any branding data render a plain pill (no crash, graceful fallback)
- [x] **AC-US2-05**: The visual style matches the homepage featured agents section (rounded pills, mono font, icon + name)

## Functional Requirements

### FR-001: Extract shared constants
Create `src/lib/agent-branding.ts` that exports `AGENT_COLORS: Record<string, string>` and `AGENT_ICONS: Record<string, string>` with the exact same data currently hardcoded in `src/app/page.tsx`.

### FR-002: Update homepage imports
Replace the inline `AGENT_COLORS` and `AGENT_ICONS` definitions in `src/app/page.tsx` with imports from the shared file.

### FR-003: Update skill detail page
Replace the plain grey square badges in `src/app/skills/[name]/page.tsx` with colorful pill badges using data from the shared branding file.

## Success Criteria

- Both pages render identically to before (homepage) or better (skill page) with no visual regressions
- Zero duplication of agent branding data
- Build passes with no errors

## Out of Scope

- Adding new agents to the branding maps
- Changing the homepage layout or badge styling
- Adding interactivity (links, tooltips) to agent pills
- Database-driven agent branding

## Dependencies

- None -- purely frontend refactoring within existing pages
