---
increment: 0289-skills-category-crash-homepage-verification
title: "Fix skills category crash and improve homepage verification section"
type: bug
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Fix skills category crash and improve homepage verification section

## Overview

The /skills page crashes with a 500 error because an `onClick` event handler is used inside a React Server Component (`src/app/skills/page.tsx` line 299). Server Components cannot have event handlers. Additionally, the homepage "How verification works" section uses a minimal TreeList that could be redesigned for better clarity and visual impact.

## Root Cause Analysis

### Skills Page Crash
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/skills/page.tsx`
- **Line**: 299 -- `onClick={(e) => { e.preventDefault(); ... }}`
- **Error**: `Event handlers cannot be passed to Client Component props`
- **Impact**: Every request to `/skills` or `/skills?category=X` returns HTTP 500 when skills with `repoUrl` exist
- **Fix**: Replace the inline `onClick` handler with a proper `<a>` link element, or extract the repo link into a small Client Component

### Homepage Verification Section
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/page.tsx`
- **Lines**: 352-363
- **Current**: Simple TreeList with 3 text items (Scanned/Verified/Certified)
- **Goal**: Redesigned section with better visual hierarchy, tier badges, link to /trust page

## User Stories

### US-001: Fix Skills Page Server Component Crash (P1)
**Project**: vskill-platform

**As a** visitor browsing the skills registry
**I want** the /skills page to load without errors when filtering by category or viewing all skills
**So that** I can discover and evaluate AI agent skills

**Acceptance Criteria**:
- [x] **AC-US1-01**: GET /skills returns HTTP 200 with correct HTML (no 500 error)
- [x] **AC-US1-02**: GET /skills?category=development returns HTTP 200 with filtered results
- [x] **AC-US1-03**: Repo URL links in the skills list open in a new tab when clicked
- [x] **AC-US1-04**: No `onClick` handlers exist in the Server Component `src/app/skills/page.tsx`
- [x] **AC-US1-05**: The page still functions correctly for all category, tier, sort, and extensibility filters

---

### US-002: Improve Homepage Verification Section Design (P2)
**Project**: vskill-platform

**As a** first-time visitor to verified-skill.com
**I want** to quickly understand the three-tier verification model
**So that** I trust the platform's security guarantees

**Acceptance Criteria**:
- [x] **AC-US2-01**: The verification section displays three distinct tiers (Scanned, Verified, Certified) with visual differentiation
- [x] **AC-US2-02**: Each tier shows its verification method summary
- [x] **AC-US2-03**: The section includes a link to the /trust page for full details
- [x] **AC-US2-04**: The design uses the existing design system (mono font, CSS variables, terminal aesthetic)

## Functional Requirements

### FR-001: Remove onClick from Server Component
Replace the `<span onClick={...}>` repo link pattern in `/skills/page.tsx` with a standard `<a href={...} target="_blank">` element that works in Server Components.

### FR-002: Redesign Verification Section
Replace the TreeList in the homepage verification section with a more visually distinct layout showing the three tiers with icons/badges, short descriptions, and a CTA to the trust page.

## Success Criteria

- /skills page loads without errors (HTTP 200) for all filter combinations
- Homepage verification section visually communicates the three-tier model
- All existing tests pass
- No new runtime errors in development or production builds

## Out of Scope

- Changing the verification logic itself
- Adding new categories or tiers
- Modifying the /trust page content
- Database changes

## Dependencies

- None -- both fixes are UI-only changes to existing components
