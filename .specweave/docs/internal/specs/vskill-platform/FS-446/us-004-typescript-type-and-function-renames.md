---
id: US-004
feature: FS-446
title: "TypeScript Type and Function Renames"
status: not_started
priority: P1
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** developer maintaining the codebase."
project: vskill-platform
---

# US-004: TypeScript Type and Function Renames

**Feature**: [FS-446](./FEATURE.md)

**As a** developer maintaining the codebase
**I want** all author-related TypeScript types, interfaces, and functions renamed to use "publisher" terminology
**So that** the code is internally consistent with the UI terminology

---

## Acceptance Criteria

- [ ] **AC-US4-01**: Given `src/lib/types.ts`, when inspected, then `AuthorSummary` is renamed to `PublisherSummary`, `AuthorFilters` to `PublisherFilters`, and `AuthorRepo` to `PublisherRepo`
- [ ] **AC-US4-02**: Given `src/lib/data.ts`, when inspected, then `getAuthors` is renamed to `getPublishers`, `getAuthorCount` to `getPublisherCount`, `getAuthorStats` to `getPublisherStats`, `getAuthorBlockedSkills` to `getPublisherBlockedSkills`, and `getAuthorRepos` to `getPublisherRepos`
- [ ] **AC-US4-03**: Given all files importing renamed types or functions, when the codebase compiles, then zero TypeScript errors related to missing author-named exports
- [ ] **AC-US4-04**: Given the Prisma schema, when inspected, then the `author` column name is unchanged (backwards compatibility)
- [ ] **AC-US4-05**: Given `src/lib/cron/authors-cache-refresh.ts`, when inspected, then the file is renamed to `publishers-cache-refresh.ts` with updated function names and all imports updated

---

## Implementation

**Increment**: [0446-rename-authors-to-publishers](../../../../../increments/0446-rename-authors-to-publishers/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Rename types in src/lib/types.ts
- [x] **T-002**: Rename functions in src/lib/data.ts
- [x] **T-003**: Rename cache/cron utility files and update all importers
