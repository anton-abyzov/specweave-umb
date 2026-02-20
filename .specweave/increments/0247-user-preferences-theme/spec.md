---
increment: 0247-user-preferences-theme
title: "Server-Persisted User Preferences (Theme)"
type: feature
priority: P1
status: planned
created: 2026-02-19
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Server-Persisted User Preferences (Theme)

## Overview

Add server-side persistence for user preferences, starting with theme (light/dark/system). Currently the theme toggle stores the choice in localStorage only — logged-in users lose their preference when switching devices. This increment adds a `preferences` JSON field to the User model, API endpoints for reading/updating preferences, and syncs the ThemeToggle component with the server.

## User Stories

### US-001: Server-Persisted Theme Preference (P1)
**Project**: vskill-platform

**As a** logged-in user
**I want** my theme preference to persist across devices
**So that** I see my preferred theme on any device I log into

**Acceptance Criteria**:
- [x] **AC-US1-01**: User model has a `preferences` JSON field with default `{}`
- [x] **AC-US1-02**: `GET /api/v1/user/preferences` returns user preferences (401 if not authenticated)
- [x] **AC-US1-03**: `PATCH /api/v1/user/preferences` updates theme with shallow merge and Zod `.strict()` validation
- [x] **AC-US1-04**: ThemeToggle syncs preference to server via debounced PATCH when user is authenticated
- [x] **AC-US1-05**: On page load, authenticated users' server preferences override localStorage
- [x] **AC-US1-06**: Unauthenticated users continue to use localStorage-only theme (no API calls)
- [x] **AC-US1-07**: Network failures on PATCH do not break theme toggling

## Functional Requirements

### FR-001: Preferences JSON Column
`preferences Json @default("{}")` on User model. Extensible for future preferences (notifications, language, etc.) without new migrations.

### FR-002: Preferences API
- `GET /api/v1/user/preferences` — returns parsed preferences
- `PATCH /api/v1/user/preferences` — shallow merge with Zod validation, rejects unknown keys

### FR-003: Client-Server Sync
localStorage = fast read cache (FOUC prevention). Server = cross-device source of truth. 500ms debounced PATCH on toggle. Fire-and-forget fetch on mount to reconcile.

## Success Criteria

- All existing tests pass (zero regressions)
- New preferences module and route tests pass
- Theme persists across devices for logged-in users

## Out of Scope

- Settings page UI (future increment)
- Additional preferences beyond theme (future increment)
- Admin preferences (admins have separate auth system)

## Dependencies

- Existing GitHub OAuth auth system (`requireUser`)
- Existing ThemeToggle component and CSS variable system
