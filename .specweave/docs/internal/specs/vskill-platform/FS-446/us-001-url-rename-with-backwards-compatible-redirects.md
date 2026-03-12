---
id: US-001
feature: FS-446
title: "URL Rename with Backwards-Compatible Redirects"
status: not_started
priority: P1
created: "2026-03-07T00:00:00.000Z"
tldr: "**As a** site visitor."
project: vskill-platform
---

# US-001: URL Rename with Backwards-Compatible Redirects

**Feature**: [FS-446](./FEATURE.md)

**As a** site visitor
**I want** publisher pages served at `/publishers` and `/publishers/[name]`
**So that** the URL structure reflects the new terminology while old bookmarks still work

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a request to `/publishers`, when the page loads, then the publishers listing page renders with correct data
- [ ] **AC-US1-02**: Given a request to `/publishers/[name]`, when the page loads, then the individual publisher detail page renders with that publisher's skills and stats
- [ ] **AC-US1-03**: Given a request to `/authors`, when the server responds, then a 301 redirect is issued to `/publishers`
- [ ] **AC-US1-04**: Given a request to `/authors/[name]`, when the server responds, then a 301 redirect is issued to `/publishers/[name]`
- [ ] **AC-US1-05**: Given the Next.js app directory, when inspecting `src/app/`, then `src/app/authors/` no longer exists and all pages live under `src/app/publishers/`

---

## Implementation

**Increment**: [0446-rename-authors-to-publishers](../../../../../increments/0446-rename-authors-to-publishers/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: Move src/app/authors/ directory to src/app/publishers/ and rename internal components
- [x] **T-008**: Add 301 redirects for /authors and /authors/:path* in next.config.ts
