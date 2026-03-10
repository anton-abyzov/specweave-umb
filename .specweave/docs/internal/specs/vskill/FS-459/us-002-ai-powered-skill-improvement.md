---
id: US-002
feature: FS-459
title: "AI-Powered Skill Improvement"
status: completed
priority: P1
created: 2026-03-09T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 37
    url: https://github.com/anton-abyzov/vskill/issues/37
---

# US-002: AI-Powered Skill Improvement

**Feature**: [FS-459](./FEATURE.md)

**As a** skill developer
**I want** to send my SKILL.md and benchmark failures to an LLM and receive a suggested improved version with a visual diff
**So that** I can iterate on skill quality using AI assistance without manually analyzing failures

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the SkillDetailPage, when the user clicks "Improve Skill", then a panel appears with a model picker (supporting all configured providers: claude-cli, anthropic, ollama) and an "Improve" action button
- [x] **AC-US2-02**: Given the improvement is requested, when the backend processes it, then `POST /api/skills/:plugin/:skill/improve` reads the current SKILL.md, auto-includes up to 10 most recently failed assertions from the latest benchmark, constructs an improvement prompt, calls the selected LLM, and returns `{ original, improved, reasoning }`
- [x] **AC-US2-03**: Given the improvement response is received, when displayed, then a unified diff view shows line-by-line changes (green for added lines, red for removed lines) computed on the frontend without external diff libraries
- [x] **AC-US2-04**: Given the diff is displayed, when the user clicks "Apply", then `POST /api/skills/:plugin/:skill/apply-improvement` writes the improved content back to SKILL.md on disk, the viewer updates to reflect the new content, and a success confirmation is shown
- [x] **AC-US2-05**: Given the diff is displayed, when the user clicks "Discard", then the improvement panel closes and no changes are written to disk

---

## Implementation

**Increment**: [0459-skill-eval-enhancements](../../../../../increments/0459-skill-eval-enhancements/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
