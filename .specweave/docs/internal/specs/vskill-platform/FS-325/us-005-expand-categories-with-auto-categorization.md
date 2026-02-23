---
id: US-005
feature: FS-325
title: Expand Categories with Auto-Categorization
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1291
    url: https://github.com/anton-abyzov/specweave/issues/1291
---
# US-005: Expand Categories with Auto-Categorization

**Feature**: [FS-325](./FEATURE.md)

platform maintainer
**I want** more skill categories and automatic categorization based on skill content
**So that** discovered skills get meaningful categories instead of all defaulting to "development"

---

## Acceptance Criteria

- [x] **AC-US5-01**: The `SkillCategory` type is expanded with new categories: `"ai-ml"`, `"infrastructure"`, `"productivity"`, `"communication"`, `"finance"`, `"education"`, `"analytics"`
- [x] **AC-US5-02**: `CATEGORY_LABELS` on the homepage maps all new categories to display labels
- [x] **AC-US5-03**: A `categorizeSkill(name: string, description: string, labels: string[]): SkillCategory` function is created that assigns categories based on keyword matching
- [x] **AC-US5-04**: The rebuild-index route (`/api/v1/admin/rebuild-index`) uses `categorizeSkill()` instead of hardcoding `"development"`
- [x] **AC-US5-05**: The publish pipeline in `submission-store.ts` uses `categorizeSkill()` when creating new skills
- [x] **AC-US5-06**: Existing seed data skills are re-reviewed: any miscategorized skills are corrected
- [x] **AC-US5-07**: The keyword mapping is tested with at least 10 representative skill names/descriptions

---

## Implementation

**Increment**: [0325-homepage-metrics-accuracy](../../../../../increments/0325-homepage-metrics-accuracy/spec.md)

