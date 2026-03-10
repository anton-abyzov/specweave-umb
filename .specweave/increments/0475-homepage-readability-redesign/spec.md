---
increment: 0475-homepage-readability-redesign
title: "Homepage Readability Redesign"
type: feature
priority: P1
status: planned
created: 2026-03-10
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Homepage Readability Redesign

## Overview

Five targeted CSS/layout fixes to verified-skill.com homepage readability. Agent badges are unreadable at 10px, the value proposition is buried below the video, the "36.82% have flaws" stat is invisible at 40% opacity inline, the bottom "Works with" badges are too small, and the hero is too dense with a standalone CLI copy row. All changes are CSS/layout -- no data flow, no new components, no server/client boundary changes.

**Files affected**: `HomepageDemoHero.tsx`, `page.tsx`, `globals.css`

## User Stories

### US-001: Readable Hero Agent Badges (P1)
**Project**: vskill-platform

**As a** homepage visitor
**I want** agent badges in the hero section to be clearly legible
**So that** I can quickly see which AI agents are supported without squinting

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Hero badge font size is `0.75rem` (was `0.625rem`)
- [ ] **AC-US1-02**: Hero badge height is `26px` (was `20px`)
- [ ] **AC-US1-03**: Hero badge padding is `0.25rem 0.5rem` (was `0.125rem 0.3125rem`)
- [ ] **AC-US1-04**: Hero badge icon size is `14x14` (was `11x11`)
- [ ] **AC-US1-05**: Badge text color remains `rgba(230,237,243,0.7)` and border contrast is preserved

---

### US-002: Value Proposition Above Video (P1)
**Project**: vskill-platform

**As a** homepage visitor
**I want** the heading "Install AI skills you can trust" to appear above the demo video
**So that** I understand what the product does before seeing the demo

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `children` slot renders above the video container in `HomepageDemoHero.tsx`
- [ ] **AC-US2-02**: Visual order is: heading/stats, then video, then any below-video content
- [ ] **AC-US2-03**: No change to the server/client component boundary -- children remain server-rendered React nodes passed into the client component

---

### US-003: Standalone Flaws Stat Callout (P1)
**Project**: vskill-platform

**As a** homepage visitor
**I want** the "36.82% have flaws" statistic displayed as a distinct callout
**So that** the security scanning value proposition is immediately visible

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Stat is extracted from the inline `<span>` into its own block element between the description paragraph and the "Works with" badges
- [ ] **AC-US3-02**: Callout has `border-left: 2px solid rgba(245,158,11,0.4)` accent
- [ ] **AC-US3-03**: Callout font size is `0.8125rem` with color `rgba(230,237,243,0.6)`
- [ ] **AC-US3-04**: "Scan results" link remains accessible and navigates to `/audits`

---

### US-004: Enlarged Bottom Works-With Badges (P1)
**Project**: vskill-platform

**As a** homepage visitor
**I want** the bottom "Works with" agent badges to be larger and more readable
**So that** I can identify supported agents without effort in the lower section

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Featured badge font size is `0.8125rem` with height `28px` (was `0.6875rem`/`22px`)
- [ ] **AC-US4-02**: Non-featured badge font size is `0.75rem` with height `24px` (was `0.625rem`/`20px`)
- [ ] **AC-US4-03**: Featured icon size is `16x16` (was `13x13`), non-featured is `14x14` (was `11x11`)
- [ ] **AC-US4-04**: Featured dot indicator is `6px` (was `5px`), non-featured is `5px` (was `4px`)
- [ ] **AC-US4-05**: Badge padding scales proportionally with the size increase

---

### US-005: CLI Copy Button in Video Overlay (P1)
**Project**: vskill-platform

**As a** homepage visitor
**I want** the CLI copy command integrated into the video overlay
**So that** the hero section is less dense and the copy action is contextually tied to the demo

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Copy button is pill-shaped, positioned bottom-left of the video overlay (mirroring the play/pause button at bottom-right)
- [ ] **AC-US5-02**: Button uses glass morphism: `rgba(0,0,0,0.6)` background, `backdrop-filter: blur(4px)`, `1px solid rgba(255,255,255,0.2)` border
- [ ] **AC-US5-03**: Button shows full text `$ npx vskill find code-review` with copy/copied state
- [ ] **AC-US5-04**: The standalone CLI row below the video and the "as shown in video" label are removed
- [ ] **AC-US5-05**: At 480px viewport, copy button font shrinks to `0.5625rem` with reduced padding
- [ ] **AC-US5-06**: `globals.css` includes `video-copy-btn` hover and responsive rules matching the play button style

## Functional Requirements

### FR-001: No New Components
All changes are CSS/layout edits to existing files. No new React components are created.

### FR-002: No Data Flow Changes
No props, state, API calls, or server/client boundaries change. The `children` slot pattern remains identical.

### FR-003: Responsive Preservation
All existing responsive breakpoints (768px, 480px) continue to work. New video-copy-btn responsive rule added at 480px.

## Success Criteria

- All 5 readability issues resolved with specified values
- No visual regressions in existing sections (role cards, trending, dashboard)
- WCAG text contrast ratios maintained or improved

## Out of Scope

- Color theme changes (dark/light mode variables unchanged)
- New components or pages
- Server-side data changes or API modifications
- Badge interaction behavior (hover states remain as-is, no click-through)
- Agent branding data (`AGENT_COLORS`, `AGENT_ICONS`) unchanged

## Dependencies

- None -- purely CSS/layout, self-contained within existing homepage files
