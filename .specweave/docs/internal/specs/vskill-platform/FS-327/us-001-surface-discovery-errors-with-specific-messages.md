---
id: US-001
feature: FS-327
title: Surface discovery errors with specific messages
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
---
# US-001: Surface discovery errors with specific messages

**Feature**: [FS-327](./FEATURE.md)

skill author submitting a repo
**I want** to see a specific error message when GitHub API limits or auth issues prevent discovery
**So that** I understand the problem is temporary and not that my repo has no skills

---

## Acceptance Criteria

- [x] **AC-US1-01**: `DiscoveryResult` type gains an optional `error` field: `error?: { code: "rate_limited" | "auth_failed" | "api_error"; message: string }`
- [x] **AC-US1-02**: When GitHub API returns 403 (rate limit), `discoverSkillsEnhanced` returns `{ skills: [], error: { code: "rate_limited", message: "GitHub API rate limit exceeded. Please try again in a few minutes." }, ... }` instead of throwing or returning empty
- [x] **AC-US1-03**: When GitHub API returns 401, `discoverSkillsEnhanced` returns `{ skills: [], error: { code: "auth_failed", message: "GitHub authentication issue. Please try again later." }, ... }`
- [x] **AC-US1-04**: For other non-success GitHub responses, `discoverSkillsEnhanced` returns `{ skills: [], error: { code: "api_error", message: "<descriptive message>" }, ... }`
- [x] **AC-US1-05**: When `GITHUB_TOKEN` is missing, the discover route logs a server-side warning (`console.warn`) but proceeds with unauthenticated calls (existing behavior, now explicit)
- [x] **AC-US1-06**: The discover route (`/api/v1/submissions/discover`) inspects the `error` field and returns HTTP 502 with the user-friendly error message when present
- [x] **AC-US1-07**: Discovery with 0 skills and no error field still returns HTTP 200 (backward compatible)
- [x] **AC-US1-08**: The submit page displays the specific error message from the 502 response (not the generic "No SKILL.md files found")

---

## Implementation

**Increment**: [0327-submit-page-discovery-fix](../../../../../increments/0327-submit-page-discovery-fix/spec.md)

