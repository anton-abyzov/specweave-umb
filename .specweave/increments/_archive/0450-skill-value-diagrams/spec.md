---
increment: 0450-skill-value-diagrams
title: Skill Value Diagrams & Content Assets
type: feature
priority: P1
status: completed
created: 2026-03-07T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Value Diagrams & Content Assets

## Problem Statement

SpecWeave's public docs and YouTube channel lack visual content that communicates the core value proposition of skills. Developers encounter skills as a concept but have no quick, visual way to understand why skills matter. The existing fundamentals page explains _what_ skills are, but not _why_ they produce dramatically better results. A hand-drawn "before/after" diagram style has been validated as effective for communicating this gap -- same prompt, radically different output quality.

## Goals

- Create 4 Excalidraw before/after comparison diagrams illustrating the skill value proposition
- Publish a new "Why Skills Matter" docs page as the motivational entry point to the skills section
- Draft a YouTube script outline for a ~8-10 minute video aimed at developers unfamiliar with skills
- Establish a reusable visual style (red=without, green=with, hand-drawn annotations) for future content

## User Stories

### US-SW-001: "What is a Skill?" Diagram
**Project**: specweave
**As a** developer visiting the docs
**I want** a before/after diagram showing that the same prompt produces generic output without a skill vs production-grade output with a skill
**So that** I immediately understand the core value proposition of skills

**Acceptance Criteria**:
- [x] **AC-US1-01**: Excalidraw source file exists at `docs-site/static/img/skills/diagrams/what-is-a-skill.excalidraw` and is valid Excalidraw JSON
- [x] **AC-US1-02**: SVG export exists at `docs-site/static/img/skills/what-is-a-skill.svg` and renders correctly in a browser
- [x] **AC-US1-03**: Diagram uses abstract labels (not code snippets) with red for without/bad and green for with/good color coding, matching the hand-drawn reference style
- [x] **AC-US1-04**: Diagram includes annotation arrows and concise text labels that are readable at both full-size and 50% scale

---

### US-SW-002: "How Skills Work" Diagram
**Project**: specweave
**As a** developer visiting the docs
**I want** a diagram comparing raw LLM output vs LLM + skill (domain knowledge injection)
**So that** I understand the mechanism behind skill-enhanced output

**Acceptance Criteria**:
- [x] **AC-US2-01**: Excalidraw source file exists at `docs-site/static/img/skills/diagrams/how-skills-work.excalidraw`
- [x] **AC-US2-02**: SVG export exists at `docs-site/static/img/skills/how-skills-work.svg`
- [x] **AC-US2-03**: Diagram visually shows a prompt entering a raw LLM (red path) vs entering an LLM augmented with skill knowledge (green path), with distinct output quality labels
- [x] **AC-US2-04**: Hand-drawn style with annotation arrows consistent with US-SW-001 diagram

---

### US-SW-003: "Creating Skills" Diagram
**Project**: specweave
**As a** developer visiting the docs
**I want** a diagram contrasting vague ad-hoc instructions vs a structured SKILL.md file
**So that** I understand how skills formalize domain knowledge

**Acceptance Criteria**:
- [x] **AC-US3-01**: Excalidraw source file exists at `docs-site/static/img/skills/diagrams/creating-skills.excalidraw`
- [x] **AC-US3-02**: SVG export exists at `docs-site/static/img/skills/creating-skills.svg`
- [x] **AC-US3-03**: Diagram shows "before" (red) as scattered/vague prompt instructions and "after" (green) as a structured SKILL.md anatomy with labeled sections
- [x] **AC-US3-04**: SKILL.md anatomy labels include at minimum: frontmatter, instructions body, and supporting files -- without showing actual code

---

### US-SW-004: "Skill Eval/Testing" Diagram
**Project**: specweave
**As a** developer visiting the docs
**I want** a diagram comparing no feedback loop vs an eval framework with metrics for skills
**So that** I understand that skills should be tested and measured, not blindly trusted

**Acceptance Criteria**:
- [x] **AC-US4-01**: Excalidraw source file exists at `docs-site/static/img/skills/diagrams/skill-eval-testing.excalidraw`
- [x] **AC-US4-02**: SVG export exists at `docs-site/static/img/skills/skill-eval-testing.svg`
- [x] **AC-US4-03**: Diagram is tool-agnostic -- shows generic eval concepts (run, measure, improve loop) without referencing specific tooling
- [x] **AC-US4-04**: "Before" side (red) shows a blind "deploy and hope" flow; "after" side (green) shows a measure-iterate cycle with quality metrics

---

### US-SW-005: "Why Skills Matter" Documentation Page
**Project**: specweave
**As a** developer browsing the skills docs section
**I want** a motivational intro page that uses the 4 diagrams to explain why skills matter
**So that** I have a compelling reason to learn more about skills before diving into technical details

**Acceptance Criteria**:
- [x] **AC-US5-01**: Doc page exists at `docs-site/docs/skills/why-skills-matter.md` with valid Docusaurus frontmatter
- [x] **AC-US5-02**: Page embeds all 4 SVG diagrams with descriptive alt text for accessibility
- [x] **AC-US5-03**: Page is placed BEFORE `fundamentals.md` in the sidebar via `sidebar_position` frontmatter (lower number than fundamentals)
- [x] **AC-US5-04**: Page links forward to `fundamentals.md` for readers who want technical details on skills, plugins, and marketplaces
- [x] **AC-US5-05**: Each diagram is accompanied by 2-4 sentences of explanatory text that reinforces the visual message

---

### US-SW-006: YouTube Script Outline for "Why Skills Matter"
**Project**: specweave
**As a** content creator preparing a YouTube video
**I want** a script outline for an ~8-10 minute video explaining skills to developers who have never heard of them
**So that** I have a structured narrative to record from

**Acceptance Criteria**:
- [x] **AC-US6-01**: Script file exists at `.specweave/docs/public/academy/videos/004-why-skills-matter.md` following the existing video template structure
- [x] **AC-US6-02**: Script targets developers unfamiliar with skills -- minimal Claude Code prerequisites, focus on "you've been getting generic AI output, here's how to fix that"
- [x] **AC-US6-03**: Script references all 4 diagrams as visual aids at appropriate points in the narrative
- [x] **AC-US6-04**: Script is structured with timed sections totaling ~8-10 minutes (intro, 4 diagram sections, call to action)
- [x] **AC-US6-05**: Script includes a "Related Videos" section linking to existing academy videos (001, 002, 003)

## Out of Scope

- Animated or interactive diagram versions (static SVG only for this increment)
- Recording or editing the actual YouTube video (script outline only)
- Updating the existing `fundamentals.md` content (this increment adds a new page, not modifies existing)
- Diagrams for plugin or marketplace concepts (skills only)
- Translations or localization of content
- Blog post or social media content derived from the diagrams

## Technical Notes

### File Locations
- Excalidraw sources: `repositories/anton-abyzov/specweave/docs-site/static/img/skills/diagrams/`
- SVG exports: `repositories/anton-abyzov/specweave/docs-site/static/img/skills/`
- Doc page: `repositories/anton-abyzov/specweave/docs-site/docs/skills/why-skills-matter.md`
- Video script: `.specweave/docs/public/academy/videos/004-why-skills-matter.md`

### Visual Style Guide
- Hand-drawn aesthetic (Excalidraw default hand-drawn font)
- Red (#FF6B6B or similar) for "without skill" / bad path
- Green (#51CF66 or similar) for "with skill" / good path
- Annotation arrows with concise labels
- Abstract labels, not code snippets -- instantly understandable
- Both `.excalidraw` source and `.svg` export committed for editability

### Docusaurus Integration
- Use `sidebar_position` in frontmatter to order before fundamentals
- Reference SVGs via relative paths from the docs page
- Include alt text on all image embeds

## Success Metrics

- All 4 diagrams render correctly in Docusaurus local dev and production build
- "Why Skills Matter" page is the first page in the Skills sidebar section
- YouTube script covers the full narrative arc in ~8-10 minute target
- Diagrams are reusable in other contexts (blog posts, presentations) via SVG exports
