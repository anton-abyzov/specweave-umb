---
id: US-003
feature: FS-392
title: "Weekly Downloads in Skill Detail Page (P1)"
status: completed
priority: P1
created: "2026-03-01T00:00:00.000Z"
tldr: "**As a** developer browsing skills."
project: vskill-platform
---

# US-003: Weekly Downloads in Skill Detail Page (P1)

**Feature**: [FS-392](./FEATURE.md)

**As a** developer browsing skills
**I want** to see weekly download stats on the skill detail page
**So that** I can gauge recent adoption velocity beyond the monthly aggregate

---

## Acceptance Criteria

- [x] **AC-US3-01**: Skill detail page shows a "Weekly" StatCard when `npmDownloadsWeekly > 0`
- [x] **AC-US3-02**: The existing StatCard labeled "NPM" is relabeled to "Monthly" for clarity
- [x] **AC-US3-03**: Both monthly and weekly StatCards use the same `formatNumber` helper for consistent display
- [x] **AC-US3-04**: Data layer (`src/lib/data.ts`) includes `npmDownloadsWeekly` in the Prisma select for skill detail queries

---

## Implementation

**Increment**: [0392-npm-weekly-downloads](../../../../../increments/0392-npm-weekly-downloads/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Update data layer to include npmDownloadsWeekly in skill queries
- [x] **T-007**: Add Weekly StatCard and relabel Monthly on skill detail page
