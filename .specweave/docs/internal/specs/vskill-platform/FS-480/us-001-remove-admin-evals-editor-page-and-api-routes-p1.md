---
id: US-001
feature: FS-480
title: "Remove admin evals editor page and API routes (P1)"
status: completed
priority: P1
created: 2026-03-10
tldr: "**As a** platform maintainer."
project: vskill-platform
---

# US-001: Remove admin evals editor page and API routes (P1)

**Feature**: [FS-480](./FEATURE.md)

**As a** platform maintainer
**I want** the admin evals editor page and its supporting API routes removed
**So that** the codebase has no dead code for a feature superseded by the CLI workflow

---

## Acceptance Criteria

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

## Implementation

**Increment**: [0480-remove-admin-evals-editor](../../../../../increments/0480-remove-admin-evals-editor/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Delete evals editor files and remove nav entry
- [x] **T-002**: Verify build and test suite pass
