# Implementation Plan: Server-Persisted User Preferences (Theme)

## Overview

JSON column on User model + GET/PATCH API endpoints + ThemeToggle server sync. localStorage remains fast path for FOUC prevention; server is source of truth for cross-device persistence.

## Architecture

### Components
- `src/lib/preferences.ts`: Type definitions, parse function, Zod validation
- `src/app/api/v1/user/preferences/route.ts`: GET + PATCH endpoints
- `src/app/components/ThemeToggle.tsx`: Enhanced with server sync

### Data Model
- User: Add `preferences Json @default("{}")` — stores `{ theme?: "light" | "dark" | "system" }`

### API Contracts
- `GET /api/v1/user/preferences`: Returns `{ preferences: { theme: "dark" } }` (401 if unauth)
- `PATCH /api/v1/user/preferences`: Body `{ theme: "light" }`, shallow merge, returns updated preferences

## Architecture Decisions

- **JSON vs column**: JSON column — extensible for future preferences without migrations
- **Shallow merge**: PATCH merges top-level keys only — predictable, deletable via explicit values
- **Fire-and-forget sync**: ThemeToggle fetches preferences on mount; if 401, ignores (no React context needed)
- **500ms debounce**: Prevents rapid-toggle flooding server with PATCH requests

## Implementation Phases

### Phase 1: Foundation (TDD)
- Preferences type module with parsePreferences and Zod schema
- Prisma schema migration

### Phase 2: Core API (TDD)
- GET/PATCH route handlers following auth/me pattern

### Phase 3: Client Integration
- ThemeToggle server sync with debounced writes

## Testing Strategy

- Unit tests for `parsePreferences()` and Zod schema
- Route tests for GET/PATCH (auth, validation, merge, error cases)
- Manual verification for ThemeToggle sync behavior
