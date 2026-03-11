---
increment: 0483-merge-social-skills
title: Merge social-posts into social-media-posting
status: completed
priority: P1
type: feature
created: 2026-03-11T00:00:00.000Z
---

# Merge social-posts into social-media-posting

## Problem Statement

Two overlapping social media skills exist in the marketing plugin: `social-media-posting` (11 platforms, automated posting, dedup, engagement, scheduling) and `social-posts` (6+1 platforms, strategic thinking, product context, video generation, per-platform copy files). This duplication causes confusion about which skill to invoke, splits capabilities across two SKILL.md files, and means neither skill alone delivers the full social media workflow. Merging them into one definitive orchestrator eliminates the overlap and creates a single, complete skill.

## Goals

- Consolidate all social media capabilities into `social-media-posting` as the single definitive skill
- Preserve every unique capability from both skills without loss
- Add virality-focused proof screenshot guidance for X/Twitter and Threads
- Produce a merged eval suite (8 test cases) covering all combined functionality
- Remove `social-posts/` directory cleanly after merge

## User Stories

### US-001: Merge SKILL.md Content
**Project**: vskill
**As a** skill user
**I want** the `social-media-posting` SKILL.md to contain all capabilities from both skills
**So that** I have a single comprehensive social media orchestrator without needing to know about two separate skills

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the merged SKILL.md, when I read the workflow section, then a "Strategic Thinking" phase appears before content writing that includes hook formulas (curiosity gaps, contrarian takes, story hooks, value hooks), psychological angles (social proof, curiosity gap, loss aversion, authority, reciprocity), copy principles, and content pillar guidance
- [x] **AC-US1-02**: Given the merged SKILL.md, when I read the "Before Starting" section, then it instructs checking for `product-marketing-context.md` in the `.claude/` directory first, project root as secondary fallback, and describes product integration ratios (60/20/15/5%)
- [x] **AC-US1-03**: Given the merged SKILL.md, when I read the video generation section, then Veo 3.1 (Option A) is documented with full API details, Ken Burns fallback (Option B), and UGC script (Option C), matching the content from `social-posts`
- [x] **AC-US1-04**: Given the merged SKILL.md, when I read the copy output section, then per-platform copy files are saved to `generated-assets/copy/*.txt` for all 11 platforms (linkedin.txt, twitter.txt, instagram.txt, tiktok.txt, facebook.txt, threads.txt, reddit.txt, devto.txt, discord.txt, telegram.txt, youtube.txt)
- [x] **AC-US1-05**: Given the merged SKILL.md tool priority table, then Chrome-open appears as a last-resort fallback column for all browser-based platforms (Instagram, LinkedIn, Threads, YouTube, Reddit, TikTok, dev.to, Facebook) but not for Telegram (API-only) or platforms with dedicated CLI tools as first choice

### US-002: Add Virality and Proof Screenshot Guidance
**Project**: vskill
**As a** skill user
**I want** the merged skill to prioritize proof screenshots for X/Twitter and Threads
**So that** posts on high-virality platforms lead with authentic evidence rather than generic AI art

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the merged SKILL.md, when I read the image generation section for X/Twitter and Threads, then it states the first image MUST be a proof screenshot (terminal output, metrics dashboard, before/after comparison, code with results, error stories) rather than generic AI-generated art
- [x] **AC-US2-02**: Given the merged SKILL.md, when the user has no proof screenshot available, then the skill instructs asking the user to provide one first; if the topic is abstract (opinion/thought leadership), fall back to data visualization or infographic-style AI art
- [x] **AC-US2-03**: Given the merged SKILL.md proof screenshot section, then it explicitly states to NEVER generate mock or fake terminal screenshots, and to never block the posting workflow over the absence of a proof screenshot
- [x] **AC-US2-04**: Given the merged SKILL.md, when I read the proof screenshot creation section, then it provides specific guidance on creating good proof screenshots (clean terminal with visible output, cropped metrics dashboards, annotated before/after comparisons)

### US-003: Merge Eval Suites
**Project**: vskill
**As a** skill maintainer
**I want** the merged `evals.json` to contain all 8 test cases with updated assertions
**So that** the combined skill is fully tested including Veo video generation and proof screenshot behavior

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the merged evals.json, then it contains 8 eval entries: the original 4 from `social-media-posting` (IDs 1-4) plus the 4 from `social-posts` renumbered to IDs 5-8
- [x] **AC-US3-02**: Given the renumbered social-posts evals (5-8), then the `skill_name` field is `social-media-posting` and any references to `nanobanana` skill are updated to `nano-banana-pro`
- [x] **AC-US3-03**: Given eval ID 5 (topic-to-all-platforms, originally social-posts eval 1), then its assertions include a check for strategic thinking phase and a check for saving copy files to `generated-assets/copy/`
- [x] **AC-US3-04**: Given the merged evals, then at least one eval assertion validates Veo 3.1 video generation or fallback behavior, and at least one assertion validates proof screenshot preference for X/Twitter or Threads

### US-004: Delete social-posts and Verify
**Project**: vskill
**As a** skill maintainer
**I want** the `social-posts/` directory deleted after the merge is complete
**So that** only one social media skill exists and there is no residual confusion

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the merge is complete, then the entire `social-posts/` directory (SKILL.md, evals/, evals/evals.json, evals/benchmark.json, evals/history/) is deleted
- [x] **AC-US4-02**: Given the deletion, then `social-media-posting/references/platform-posting.md` and `social-media-posting/references/engagement-playbook.md` remain unchanged
- [x] **AC-US4-03**: Given the merged skill, then the `description` field in the SKILL.md frontmatter includes trigger phrases from both original skills (covers "post about", "social media blast", "cross-post", "share on socials", "engage", "reply to threads", etc.)
- [x] **AC-US4-04**: Given the merged skill, then the "Related Skills" section no longer references `social-posts` and does not create a circular self-reference

## Out of Scope

- Rewriting the reference files (`platform-posting.md`, `engagement-playbook.md`) -- they are preserved as-is
- Adding new platforms beyond the existing 11
- Changing the posting automation mechanics (xurl, Puppeteer, Peekaboo workflows stay as-is)
- Implementing any code -- this is a content/documentation change to SKILL.md and evals.json files only

## Technical Notes

### File Locations
- Surviving skill: `repositories/anton-abyzov/vskill/plugins/marketing/skills/social-media-posting/`
- Deleted skill: `repositories/anton-abyzov/vskill/plugins/marketing/skills/social-posts/`

### Image Generation Approach
- Primary: `nano-banana-pro` skill reference with 3 options per image
- Fallback: Direct Gemini API call pattern (from social-posts) documented as alternative when skill is not installed

### Key Merge Decisions
- `social-media-posting` is the surviving skill; `social-posts` is fully absorbed then deleted
- Strategic thinking phase inserts before content writing in the workflow, after dedup
- Chrome-open fallback added as last column to all browser-based platform rows
- Proof screenshot requirement applies only to X/Twitter and Threads first images
- Product context file checked in `.claude/` first, project root second

## Success Metrics

- Single SKILL.md contains all capabilities from both original files with no content loss
- Merged evals.json passes all 8 test cases when run via `vskill eval`
- No references to `social-posts` skill remain in the codebase after deletion
- `social-media-posting` frontmatter description triggers on all activation phrases from both original skills
