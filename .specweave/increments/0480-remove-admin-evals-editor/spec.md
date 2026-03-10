---
increment: 0480-remove-admin-evals-editor
title: Remove Admin Evals Editor
type: feature
priority: P1
status: completed
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Remove Admin Evals Editor

## Overview

Remove the redundant web-based evals.json editor from the admin panel. Eval authoring belongs locally via `vskill studio` / `vskill eval` in the CLI. Authors manage `evals.json` in their repos; the platform discovers it via rescan and runs server-side benchmarks. The admin editor is dead weight -- it duplicates CLI functionality and introduces an unnecessary GitHub write-back surface.

This is a **deletion increment**: removing code, not adding it.

## User Stories

### US-001: Remove admin evals editor page and API routes (P1)
**Project**: vskill-platform

**As a** platform maintainer
**I want** the admin evals editor page and its supporting API routes removed
**So that** the codebase has no dead code for a feature superseded by the CLI workflow

**Acceptance Criteria**:
- [x] **AC-US1-01**: The `/admin/evals` page directory (`src/app/admin/evals/`) and all its contents are deleted
- [x] **AC-US1-02**: The API route `GET /api/v1/admin/evals/content` (`src/app/api/v1/admin/evals/content/route.ts`) is deleted
- [x] **AC-US1-03**: The API route `POST /api/v1/admin/evals/commit` (`src/app/api/v1/admin/evals/commit/route.ts`) is deleted
- [x] **AC-US1-04**: The API route `GET /api/v1/admin/evals/skills` (`src/app/api/v1/admin/evals/skills/route.ts`) is deleted
- [x] **AC-US1-05**: The shared library `src/lib/github/eval-content.ts` (only used by the deleted routes) is deleted
- [x] **AC-US1-06**: All associated test files are deleted: `src/app/admin/evals/__tests__/page.test.tsx`, `src/app/api/v1/admin/evals/__tests__/routes.test.ts`, `src/lib/github/__tests__/eval-content.test.ts`
- [x] **AC-US1-07**: The "Evals" entry is removed from `NAV_ITEMS` in `src/app/admin/layout.tsx`
- [x] **AC-US1-08**: The project builds successfully after deletion (`npm run build` passes)
- [x] **AC-US1-09**: Existing test suite passes after deletion (`npx vitest run` -- no test references the deleted code)

---

## Functional Requirements

### FR-001: Delete evals editor page
Delete the entire `src/app/admin/evals/` directory (page component and its tests).

### FR-002: Delete evals editor API routes
Delete the entire `src/app/api/v1/admin/evals/` directory (content, commit, skills routes and their tests).

### FR-003: Delete evals content library
Delete `src/lib/github/eval-content.ts` and `src/lib/github/__tests__/eval-content.test.ts`. This module (`fetchEvalsContent`, `commitEvalsContent`) is only imported by the deleted routes.

### FR-004: Remove navigation link
Remove the `{ label: "Evals", href: "/admin/evals", icon: "check-circle" }` entry from `NAV_ITEMS` in `src/app/admin/layout.tsx`.

## Success Criteria

- Zero references to `/admin/evals` or `eval-content` remain in source code (excluding git history)
- Build and test suite pass cleanly

## Out of Scope

- Eval runner endpoints: `/api/v1/admin/eval/trigger`, `purge`, `bulk`, `direct`, `reverify`
- Public eval results pages: `/skills/[owner]/[repo]/[skill]/evals`
- Queue-based eval workers and processing pipeline
- Database tables: `EvalRun`, `EvalCase`
- Any CLI-side eval tooling (`vskill studio`, `vskill eval`)

## Dependencies

None. This is a standalone deletion with no external dependencies.
