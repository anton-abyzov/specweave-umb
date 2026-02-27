---
increment: 0320-search-palette-github-stars
title: Display GitHub Stars in SearchPalette
type: feature
priority: P2
status: completed
created: 2026-02-22T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Display GitHub Stars in SearchPalette

## Overview

Add GitHub star counts to the Cmd+K search palette results. The search API `/api/v1/skills/search` currently returns `name`, `author`, `certTier`, `repoUrl` -- needs to also return `githubStars`. The SearchPalette component displays a star icon with formatted count (e.g., "3.2k") next to each skill result.

## User Stories

### US-001: GitHub Stars in Search Results (P2)
**Project**: vskill-platform

**As a** developer browsing skills via the Cmd+K palette
**I want** to see GitHub star counts for each skill result
**So that** I can quickly gauge a skill's popularity without opening its detail page

**Acceptance Criteria**:
- [x] **AC-US1-01**: Search API `/api/v1/skills/search` returns `githubStars` (number) alongside existing fields
- [x] **AC-US1-02**: SearchPalette displays a star icon with formatted count for each skill result where `githubStars > 0`
- [x] **AC-US1-03**: Star count is formatted as compact notation -- raw number below 1000, "X.Xk" for 1000+
- [x] **AC-US1-04**: Star display does not appear when `githubStars` is 0 or missing
- [x] **AC-US1-05**: Star icon and count positioned between repo URL and cert tier badge in result row

## Out of Scope

- Extracting `formatNumber` into a shared utility (follow-up refactor)
- Real-time star count fetching (uses existing stored value)
- Star counts for non-skill items (categories, actions)
