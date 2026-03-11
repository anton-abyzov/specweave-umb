---
id: US-001
feature: FS-483
title: "Merge SKILL.md Content"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** skill user."
project: vskill
---

# US-001: Merge SKILL.md Content

**Feature**: [FS-483](./FEATURE.md)

**As a** skill user
**I want** the `social-media-posting` SKILL.md to contain all capabilities from both skills
**So that** I have a single comprehensive social media orchestrator without needing to know about two separate skills

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the merged SKILL.md, when I read the workflow section, then a "Strategic Thinking" phase appears before content writing that includes hook formulas (curiosity gaps, contrarian takes, story hooks, value hooks), psychological angles (social proof, curiosity gap, loss aversion, authority, reciprocity), copy principles, and content pillar guidance
- [x] **AC-US1-02**: Given the merged SKILL.md, when I read the "Before Starting" section, then it instructs checking for `product-marketing-context.md` in the `.claude/` directory first, project root as secondary fallback, and describes product integration ratios (60/20/15/5%)
- [x] **AC-US1-03**: Given the merged SKILL.md, when I read the video generation section, then Veo 3.1 (Option A) is documented with full API details, Ken Burns fallback (Option B), and UGC script (Option C), matching the content from `social-posts`
- [x] **AC-US1-04**: Given the merged SKILL.md, when I read the copy output section, then per-platform copy files are saved to `generated-assets/copy/*.txt` for all 11 platforms (linkedin.txt, twitter.txt, instagram.txt, tiktok.txt, facebook.txt, threads.txt, reddit.txt, devto.txt, discord.txt, telegram.txt, youtube.txt)
- [x] **AC-US1-05**: Given the merged SKILL.md tool priority table, then Chrome-open appears as a last-resort fallback column for all browser-based platforms (Instagram, LinkedIn, Threads, YouTube, Reddit, TikTok, dev.to, Facebook) but not for Telegram (API-only) or platforms with dedicated CLI tools as first choice

---

## Implementation

**Increment**: [0483-merge-social-skills](../../../../../increments/0483-merge-social-skills/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Merge SKILL.md frontmatter (description + triggers + tags)
- [x] **T-002**: Insert "Before Starting" section (product context file check)
- [x] **T-003**: Insert Strategic Thinking phase section
- [x] **T-004**: Update Workflow Overview (add CONTEXT, STRATEGY, VIDEO steps)
- [x] **T-005**: Update Tool Priority table (add Chrome-open fallback column)
- [x] **T-006**: Add direct Gemini API as image generation fallback
- [x] **T-007**: Add Pillow carousel compositing technique
- [x] **T-009**: Insert Video Generation section (Veo 3.1 + Ken Burns + UGC)
- [x] **T-010**: Add per-platform copy file output subsection (all 11 platforms)
- [x] **T-011**: Add Review & Publish Chrome-open workflow section
- [x] **T-012**: Add Error Handling ("When Things Go Wrong") section
- [x] **T-013**: Update Related Skills (remove social-posts ref, add SP skills)
