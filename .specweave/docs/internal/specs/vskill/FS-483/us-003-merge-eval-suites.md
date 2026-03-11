---
id: US-003
feature: FS-483
title: "Merge Eval Suites"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill maintainer."
project: vskill
---

# US-003: Merge Eval Suites

**Feature**: [FS-483](./FEATURE.md)

**As a** skill maintainer
**I want** the merged `evals.json` to contain all 8 test cases with updated assertions
**So that** the combined skill is fully tested including Veo video generation and proof screenshot behavior

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given the merged evals.json, then it contains 8 eval entries: the original 4 from `social-media-posting` (IDs 1-4) plus the 4 from `social-posts` renumbered to IDs 5-8
- [x] **AC-US3-02**: Given the renumbered social-posts evals (5-8), then the `skill_name` field is `social-media-posting` and any references to `nanobanana` skill are updated to `nano-banana-pro`
- [x] **AC-US3-03**: Given eval ID 5 (topic-to-all-platforms, originally social-posts eval 1), then its assertions include a check for strategic thinking phase and a check for saving copy files to `generated-assets/copy/`
- [x] **AC-US3-04**: Given the merged evals, then at least one eval assertion validates Veo 3.1 video generation or fallback behavior, and at least one assertion validates proof screenshot preference for X/Twitter or Threads

---

## Implementation

**Increment**: [0483-merge-social-skills](../../../../../increments/0483-merge-social-skills/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-014**: Merge evals.json (renumber 5-8, update skill_name, add assertions)
