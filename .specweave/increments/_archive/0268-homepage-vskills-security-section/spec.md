# 0268: Homepage V-Skills Security Section

## Overview

SpecWeave's homepage currently highlights enterprise capabilities but doesn't prominently feature the Verified Skills (V-Skills) security system. Given that 36.82% of public AI skills contain security flaws (Snyk ToxicSkills, Feb 2026), the trust and verification story is a key differentiator that must be front-and-center on the homepage.

This increment adds a dedicated V-Skills security section and updates the existing features section to highlight verified-only skill installation.

## User Stories

### US-001: V-Skills Security Section on Homepage
**As a** visitor evaluating SpecWeave,
**I want** to immediately see that SpecWeave only installs verified skills,
**so that** I understand the security advantage over other AI skill systems.

**Acceptance Criteria:**
- [x] AC-US1-01: New `VSkillsSection` component added to `index.tsx` between `ProblemSection` and `WhatsNewSection`
- [x] AC-US1-02: Section displays "36.82%" statistic prominently with source attribution (Snyk ToxicSkills)
- [x] AC-US1-03: Three-tier trust ladder visualized: Scanned -> Verified -> Certified
- [x] AC-US1-04: CTA links to `/docs/skills/verified-skills` (or `/docs/skills/` if 0267 not yet done)
- [x] AC-US1-05: Link to verifiedskill.com included
- [x] AC-US1-06: Section uses contrasting dark/shield visual treatment (red accent for danger, green for trust)

### US-002: Feature Card Update
**As a** visitor scanning the features grid,
**I want** the skills feature card to mention V-Skills verification,
**so that** the security story is reinforced throughout the page.

**Acceptance Criteria:**
- [x] AC-US2-01: "Extensible Skills (SOLID)" card updated to also mention verified installation
- [x] AC-US2-02: A new "Verified Skills" feature card added with shield icon and 3-tier description
- [x] AC-US2-03: Link to verifiedskill.com from the feature card

### US-003: Responsive & Dark Mode
**As a** mobile or dark-mode user,
**I want** the new section to render correctly,
**so that** the security message is clear on all devices and themes.

**Acceptance Criteria:**
- [x] AC-US3-01: Section is responsive on mobile (stacks vertically)
- [x] AC-US3-02: Dark mode compatible (uses existing CSS custom properties)

## Design Direction

- Shield/security visual metaphor
- Use existing purple theme with red accent for "danger" stats and green for "trust/verified"
- Three-tier badges: similar style to what's on the Verified Skills docs page
- Keep consistent with existing homepage section patterns (badge, title, subtitle, grid)

## Out of Scope

- Remotion video integration (see increment 0269)
- Changes to other pages
- New CSS file — extend existing `index.module.css`
