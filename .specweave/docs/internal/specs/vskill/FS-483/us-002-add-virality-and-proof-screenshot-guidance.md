---
id: US-002
feature: FS-483
title: "Add Virality and Proof Screenshot Guidance"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill user."
project: vskill
---

# US-002: Add Virality and Proof Screenshot Guidance

**Feature**: [FS-483](./FEATURE.md)

**As a** skill user
**I want** the merged skill to prioritize proof screenshots for X/Twitter and Threads
**So that** posts on high-virality platforms lead with authentic evidence rather than generic AI art

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the merged SKILL.md, when I read the image generation section for X/Twitter and Threads, then it states the first image MUST be a proof screenshot (terminal output, metrics dashboard, before/after comparison, code with results, error stories) rather than generic AI-generated art
- [x] **AC-US2-02**: Given the merged SKILL.md, when the user has no proof screenshot available, then the skill instructs asking the user to provide one first; if the topic is abstract (opinion/thought leadership), fall back to data visualization or infographic-style AI art
- [x] **AC-US2-03**: Given the merged SKILL.md proof screenshot section, then it explicitly states to NEVER generate mock or fake terminal screenshots, and to never block the posting workflow over the absence of a proof screenshot
- [x] **AC-US2-04**: Given the merged SKILL.md, when I read the proof screenshot creation section, then it provides specific guidance on creating good proof screenshots (clean terminal with visible output, cropped metrics dashboards, annotated before/after comparisons)

---

## Implementation

**Increment**: [0483-merge-social-skills](../../../../../increments/0483-merge-social-skills/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Add Proof Screenshots section (X/Twitter and Threads first-image requirement)
