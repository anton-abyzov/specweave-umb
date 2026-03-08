---
increment: 0453-unify-skill-page-badges
title: 'Unify skill page badges: remove redundant TierBadge'
type: feature
priority: P1
status: completed
created: 2026-03-07T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Unify skill page badges: remove redundant TierBadge

## Overview

The skill detail page renders TierBadge ("VERIFIED") and TrustBadge ("T3 VERIFIED") side-by-side. When `certTier=VERIFIED` maps to `trustTier=T3`, both say the same thing — redundant. TrustBadge is the richer composite signal (T0-T4). Remove TierBadge from the skill detail page, keep only TrustBadge.

## User Stories

### US-001: Remove redundant TierBadge from skill detail page (P1)
**Project**: vskill-platform

**As a** skill consumer
**I want** a single unified trust badge on the skill detail page
**So that** I'm not confused by redundant "VERIFIED" + "T3 VERIFIED" badges

**Acceptance Criteria**:
- [x] **AC-US1-01**: TierBadge component is not rendered on the skill detail page
- [x] **AC-US1-02**: TrustBadge remains visible with correct tier display
- [x] **AC-US1-03**: TierBadge import is removed from the skill detail page file

## Out of Scope

- TierBadge usage in other pages (skills list, search palette, trending, publisher)
- TrustBadge component changes
- Trust score computation logic
- SVG badge API endpoint

## Dependencies

- None — self-contained UI change
