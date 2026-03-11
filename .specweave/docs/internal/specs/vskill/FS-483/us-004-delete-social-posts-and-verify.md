---
id: US-004
feature: FS-483
title: "Delete social-posts and Verify"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill maintainer."
project: vskill
---

# US-004: Delete social-posts and Verify

**Feature**: [FS-483](./FEATURE.md)

**As a** skill maintainer
**I want** the `social-posts/` directory deleted after the merge is complete
**So that** only one social media skill exists and there is no residual confusion

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given the merge is complete, then the entire `social-posts/` directory (SKILL.md, evals/, evals/evals.json, evals/benchmark.json, evals/history/) is deleted
- [x] **AC-US4-02**: Given the deletion, then `social-media-posting/references/platform-posting.md` and `social-media-posting/references/engagement-playbook.md` remain unchanged
- [x] **AC-US4-03**: Given the merged skill, then the `description` field in the SKILL.md frontmatter includes trigger phrases from both original skills (covers "post about", "social media blast", "cross-post", "share on socials", "engage", "reply to threads", etc.)
- [x] **AC-US4-04**: Given the merged skill, then the "Related Skills" section no longer references `social-posts` and does not create a circular self-reference

---

## Implementation

**Increment**: [0483-merge-social-skills](../../../../../increments/0483-merge-social-skills/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-015**: Delete social-posts directory
- [x] **T-016**: Verify no remaining references to social-posts in codebase
