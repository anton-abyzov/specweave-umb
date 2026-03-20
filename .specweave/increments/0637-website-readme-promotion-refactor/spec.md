---
increment: 0637-website-readme-promotion-refactor
title: "Website & README Promotion Refactor"
type: feature
priority: P1
status: planned
created: 2026-03-20
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Website & README Promotion Refactor

## Overview

Restructure spec-weave.com homepage with proof-first promotional messaging, rewrite GitHub README for professional positioning against vibe coding, and add mermaid diagrams to hierarchy mapping documentation.

## User Stories

### US-001: Homepage Hero Messaging (P1)
**Project**: specweave

**As a** developer visiting spec-weave.com
**I want** to immediately understand what SpecWeave does and why it's different
**So that** I can decide in 30 seconds whether it solves my problem

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Hero headline reads "Stop Prompting. Start Specifying."
- [ ] **AC-US1-02**: Subheadline communicates autonomous development with production proof
- [ ] **AC-US1-03**: Badge bar shows 4 key metrics (636+ Increments, 10+ Production Apps, 49 Agent Platforms, 100+ Skills)
- [ ] **AC-US1-04**: CTAs "Get Started" and "Watch Demo" remain functional

### US-002: Why Spec-First Section (P1)
**Project**: specweave

**As a** developer evaluating SpecWeave
**I want** to see a clear comparison against alternatives
**So that** I understand SpecWeave's unique value over instruction-layer tools

**Acceptance Criteria**:
- [ ] **AC-US2-01**: New WhySpecFirstSection component renders on homepage
- [ ] **AC-US2-02**: Comparison table covers 6 capabilities across 5 competitors
- [ ] **AC-US2-03**: Explainer text positions against vibe coding with concrete stats

### US-003: Production Showcase (P1)
**Project**: specweave

**As a** potential user
**I want** to see real production apps built with SpecWeave
**So that** I trust it works beyond demos

**Acceptance Criteria**:
- [ ] **AC-US3-01**: ShowcaseSection replaces StatsSection on homepage
- [ ] **AC-US3-02**: Shows SketchMate and Lulla with App Store identification
- [ ] **AC-US3-03**: Self-referential "SpecWeave builds SpecWeave" with GitHub link
- [ ] **AC-US3-04**: Stats row with real metrics (636+ Increments, 538+ Releases, 3200+ Commits)

### US-004: Top Skills Grid (P1)
**Project**: specweave

**As a** developer exploring capabilities
**I want** to see the best skills available
**So that** I understand the breadth of the platform

**Acceptance Criteria**:
- [ ] **AC-US4-01**: TopSkillsSection shows 8 skill cards
- [ ] **AC-US4-02**: Each card has icon, name, one-line description
- [ ] **AC-US4-03**: CTA links to verified-skill.com

### US-005: Homepage Section Restructure (P1)
**Project**: specweave

**As a** visitor to spec-weave.com
**I want** a streamlined homepage
**So that** I find key information without being overwhelmed

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Homepage renders 9 sections: Hero, TrustedBy, DemoVideo, HowItWorks, WhySpecFirst, Showcase, TopSkills, Integrations, CTA
- [ ] **AC-US5-02**: StatsSection, AcademyPromoSection, VerifiedSkillsSection, SkillStudioSection removed
- [ ] **AC-US5-03**: Docusaurus build passes without errors

### US-006: GitHub README Rewrite (P1)
**Project**: specweave

**As a** developer finding SpecWeave on GitHub
**I want** a proof-first README
**So that** I'm convinced to try it based on real results

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Badges show key metrics (636+ increments, 10+ apps, 49 platforms, 100+ skills)
- [ ] **AC-US6-02**: THE PROBLEM section (vibe coding failures)
- [ ] **AC-US6-03**: THE SOLUTION with ASCII workflow diagram
- [ ] **AC-US6-04**: BUILT WITH SPECWEAVE proof section
- [ ] **AC-US6-05**: HOW IT COMPARES comparison table
- [ ] **AC-US6-06**: QUICKSTART section (5 lines or fewer)

### US-007: Mermaid Diagrams in Docs (P2)
**Project**: specweave

**As a** developer reading hierarchy mapping docs
**I want** visual mermaid diagrams
**So that** I quickly understand the mapping without reading dense text

**Acceptance Criteria**:
- [ ] **AC-US7-01**: GitHub mapping diagram in hierarchy-mapping.md
- [ ] **AC-US7-02**: JIRA mapping diagram in hierarchy-mapping.md
- [ ] **AC-US7-03**: ADO mapping diagram in hierarchy-mapping.md
- [ ] **AC-US7-04**: Status lifecycle state machine diagram

### US-008: Metadata Reference Page (P2)
**Project**: specweave

**As a** developer configuring increments
**I want** complete metadata.json documentation
**So that** I understand all fields and the status lifecycle

**Acceptance Criteria**:
- [ ] **AC-US8-01**: New metadata-reference.md with all fields documented
- [ ] **AC-US8-02**: Status lifecycle with WIP counting rules
- [ ] **AC-US8-03**: Example metadata.json
- [ ] **AC-US8-04**: Page added to Reference section in sidebar

## Out of Scope

- Changes to verified-skill.com (vskill-platform)
- Changes to vskill README
- Config reference docs (already comprehensive)
- Enterprise docs (8 pages already exist)
- Academy/Learn section content
