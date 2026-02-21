---
id: US-004
feature: FS-296
title: Baseline Trending Scores for Published Skills
status: complete
priority: P2
created: 2026-02-21
project: vskill-platform
---
# US-004: Baseline Trending Scores for Published Skills

**Feature**: [FS-296](./FEATURE.md)

platform user browsing the trending section
**I want** newly published community skills to have a non-zero baseline trending score
**So that** they appear in trending lists instead of being permanently buried at the bottom

---

## Acceptance Criteria

- [x] **AC-US4-01**: KV-published skills in `getSkills()` receive a baseline `trendingScore7d` value (e.g., 1) instead of hardcoded 0
- [x] **AC-US4-02**: KV-published skills in `getSkillByName()` also receive the same baseline score
- [x] **AC-US4-03**: Skills enriched with live metrics (`ENABLE_LIVE_METRICS=true`) override the baseline with real values

---

## Implementation

**Increment**: [0296-strip-prefix-rollout-fixes](../../../../../increments/0296-strip-prefix-rollout-fixes/spec.md)

