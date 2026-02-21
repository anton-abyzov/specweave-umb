# Tasks: Promotional Video & Homepage Redesign

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

---

## Phase 1: Remotion Video Setup

### US-001: Promotional Video Production with Remotion

#### T-001: Scaffold Remotion Project

**Description**: Install Remotion and create the video project structure in `src/remotion/`.

**References**: AC-US1-10

**Implementation Details**:
- Add `@remotion/cli`, `@remotion/renderer`, `remotion` to devDependencies
- Create `src/remotion/Root.tsx` with composition definition (1920x1080, 30fps, ~45s = 1350 frames)
- Create `src/remotion/index.ts` entry point
- Add `remotion.config.ts` at vskill-platform root
- Add `npm run video:preview` and `npm run video:render` scripts to package.json

**Test Plan**:
- **File**: Manual verification
- **Tests**:
  - **TC-001**: Remotion preview launches
    - Given Remotion is installed
    - When `npm run video:preview` is executed
    - Then browser opens with preview player

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Build Shared Video Primitives

**Description**: Create reusable components for the video scenes.

**References**: AC-US1-06, AC-US1-07, AC-US1-12

**Implementation Details**:
- `src/remotion/components/TerminalFrame.tsx` — macOS-style terminal with typing animation
- `src/remotion/components/BigText.tsx` — Large Geist Mono text with spring-in animation
- `src/remotion/components/AgentIcon.tsx` — Circular agent icon with brand color ring
- `src/remotion/components/TierBadgeVideo.tsx` — Animated tier badge (Scanned/Verified/Certified)
- `src/remotion/components/TransitionWipe.tsx` — Scene transition (fade, slide, scale)
- Import agent branding from `src/lib/agent-branding.ts`

**Test Plan**:
- **File**: Visual inspection in Remotion preview
- **Tests**:
  - **TC-002**: Each primitive renders correctly in isolation
    - Given a primitive component
    - When rendered in Remotion preview
    - Then it displays with correct typography, colors, and animations

**Dependencies**: T-001
**Status**: [x] Completed

---

#### T-003: Scene 1 — Increment Workflow

**Description**: Build the "Spec-First Development" scene showing `/sw:increment` terminal flow.

**References**: AC-US1-02, AC-US1-06

**Implementation Details**:
- ~8s scene
- Terminal typing: `> /sw:increment "user-authentication"`
- Output animation: "Created increment 0305-user-authentication" with checkmarks
- Files appearing: spec.md, plan.md, tasks.md
- Big text overlay: "Spec-First. Always."

**Dependencies**: T-002
**Status**: [x] Completed

---

#### T-004: Scene 2 — Team Lead Multi-Agent

**Description**: Build the team orchestration scene showing nested expert agents.

**References**: AC-US1-03, AC-US1-07

**Implementation Details**:
- ~10s scene
- Central "Team Lead" node with radiating connections
- Domain expert nodes animating in: Frontend, Backend, Security, Testing
- Agent icons (Claude Code, Codex, OpenClaw) appearing on nodes
- Parallel task execution visualization
- Big text: "Parallel Expert Teams"

**Dependencies**: T-002
**Status**: [x] Completed

---

#### T-005: Scene 3 — Verified Skills

**Description**: Build the security verification scene showing three-tier system.

**References**: AC-US1-04, AC-US1-06

**Implementation Details**:
- ~8s scene
- Three badges animating in sequence: Scanned -> Verified -> Certified
- Security pattern count: "52 patterns" with scanning animation
- Skills flowing through verification pipeline
- Big text: "Security-Verified Skills"

**Dependencies**: T-002
**Status**: [x] Completed

---

#### T-006: Scene 4 — Documentation & Code Generation

**Description**: Build scene showing living docs and code generation.

**References**: AC-US1-05, AC-US1-06

**Implementation Details**:
- ~8s scene
- Split screen: left = spec.md with ACs checking off, right = code writing animation
- Living docs sync visualization
- Big text: "Docs Write Themselves"

**Dependencies**: T-002
**Status**: [x] Completed

---

#### T-007: Scene 5 — CLI Command Showcase

**Description**: Build the vskill CLI commands scene.

**References**: AC-US1-08

**Implementation Details**:
- ~8s scene
- Terminal with sequential commands: `npx vskill init`, `vskill scan`, `vskill install`
- Each command shows output with colored results
- Agent compatibility badges scrolling across bottom
- Big text: "One CLI. Every Agent."

**Dependencies**: T-002
**Status**: [x] Completed

---

#### T-008: Compose Full Video with Transitions

**Description**: Sequence all scenes with transitions and timing.

**References**: AC-US1-01, AC-US1-12

**Implementation Details**:
- Wire scenes in Root.tsx with `<Series>` or `<Sequence>` from Remotion
- Add transitions between scenes (fade, slide)
- Add intro/outro frames with SpecWeave logo
- Total: ~45s (1350 frames at 30fps)
- Ensure seamless loop (outro fades into intro)
- Add easing curves (spring, ease-in-out)

**Dependencies**: T-003, T-004, T-005, T-006, T-007
**Status**: [x] Completed

---

#### T-009: Render Video to MP4 and WebM

**Description**: Render final video files and optimize file size.

**References**: AC-US1-11

**Implementation Details**:
- `npx remotion render Root Promo --codec=h264 --crf=23` for MP4
- `npx remotion render Root Promo --codec=vp8 --crf=30` for WebM
- Place files in `public/video/specweave-promo.mp4` and `.webm`
- Target file size: <5MB for MP4
- Verify loop playback in browser

**Dependencies**: T-008
**Status**: [x] Completed

---

## Phase 2: Homepage Redesign

### US-002: Homepage Hero Section with Video Player

#### T-010: Create VideoHero Component

**Description**: Build the cinematic hero section with HTML5 video player.

**References**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06

**Implementation Details**:
- `src/app/components/homepage/VideoHero.tsx` (client component)
- HTML5 `<video>` element: autoplay, muted, loop, playsInline
- `<source>` for MP4 and WebM with type attributes
- Dark gradient background with subtle CSS grain texture
- Tagline: "Spec-Driven Development for AI Agents" in 2.5rem Geist Mono
- Two CTAs: "Browse Skills >>" (link) and "npx vskill init" (copy button)
- Play/pause overlay button (absolute positioned, bottom-right)
- Responsive: video max-width 1080px, container full-width
- Mobile: reduce video height, stack CTAs vertically

**Test Plan**:
- **File**: `src/app/components/homepage/__tests__/VideoHero.test.tsx`
- **Tests**:
  - **TC-010**: VideoHero renders video element with correct attributes
    - Given VideoHero component
    - When rendered
    - Then video element has autoplay, muted, loop, playsInline attributes
  - **TC-011**: CTAs render correctly
    - Given VideoHero component
    - When rendered
    - Then "Browse Skills" link and "npx vskill init" copy button are present

**Dependencies**: T-009 (needs video files)
**Status**: [x] Completed

---

### US-003: Feature Sections Redesign

#### T-011: Create ScrollFadeIn Animation Wrapper

**Description**: Build IntersectionObserver-based scroll animation component.

**References**: AC-US3-06

**Implementation Details**:
- `src/app/components/homepage/ScrollFadeIn.tsx` (client component)
- Uses IntersectionObserver with threshold 0.15
- Applies CSS transition: opacity 0->1, translateY 20px->0
- Respects prefers-reduced-motion
- Props: direction ('up' | 'left' | 'right'), delay (ms)

**Test Plan**:
- **File**: `src/app/components/homepage/__tests__/ScrollFadeIn.test.tsx`
- **Tests**:
  - **TC-012**: Renders children
    - Given children content
    - When ScrollFadeIn mounts
    - Then children are in DOM
  - **TC-013**: Starts with opacity 0
    - Given ScrollFadeIn component
    - When initially rendered
    - Then container has opacity 0 style

**Dependencies**: None
**Status**: [x] Completed

---

#### T-012: Create FeatureSection Layout Component

**Description**: Build reusable alternating-layout feature block.

**References**: AC-US3-05

**Implementation Details**:
- `src/app/components/homepage/FeatureSection.tsx`
- Props: title, description, visual (ReactNode), reversed (boolean), id
- Flexbox layout: text on one side, visual on other
- `reversed` prop flips the order
- Max-width 960px centered (matching existing layout)
- Border-bottom separator between sections

**Test Plan**:
- **File**: `src/app/components/homepage/__tests__/FeatureSection.test.tsx`
- **Tests**:
  - **TC-014**: Renders title and description
    - Given title "Test" and description "Desc"
    - When rendered
    - Then both appear in the DOM
  - **TC-015**: Reversed prop changes order
    - Given reversed=true
    - When rendered
    - Then flex-direction changes (visual comes first in DOM)

**Dependencies**: T-011
**Status**: [x] Completed

---

#### T-013: Create ImagePlaceholder Component

**Description**: Build nanobanana placeholder component with prompt metadata.

**References**: AC-US4-01, AC-US4-02, AC-US4-03

**Implementation Details**:
- `src/app/components/homepage/ImagePlaceholder.tsx`
- Props: prompt (string), width, height, filename
- Renders: SVG gradient placeholder with dimensions text overlay
- `data-nanobanana-prompt` attribute on the img element
- Falls back to placeholder if image file doesn't exist
- CSS: rounded corners, subtle border

**Test Plan**:
- **File**: `src/app/components/homepage/__tests__/ImagePlaceholder.test.tsx`
- **Tests**:
  - **TC-016**: Renders with nanobanana prompt attribute
    - Given prompt "futuristic workflow"
    - When rendered
    - Then img has data-nanobanana-prompt="futuristic workflow"

**Dependencies**: None
**Status**: [x] Completed

---

#### T-014: Build Feature Content — Spec-First Development [P]

**Description**: Content component for the spec-first development feature.

**References**: AC-US3-01

**Implementation Details**:
- `src/app/components/homepage/FeatureSpecFirst.tsx`
- Animated terminal showing `/sw:increment` flow (reuse AnimatedTerminal pattern)
- Bullet points: "spec.md defines truth", "plan.md before code", "tasks.md tracks progress"
- Image placeholder: spec workflow diagram

**Dependencies**: T-012, T-013
**Status**: [x] Completed

---

#### T-015: Build Feature Content — Multi-Agent Teams [P]

**Description**: Content component for multi-agent team orchestration.

**References**: AC-US3-02

**Implementation Details**:
- `src/app/components/homepage/FeatureMultiAgent.tsx`
- Visual: CSS-based diagram showing team-lead node connected to domain experts
- Agent icons from agent-branding.ts
- Bullet points: "Team lead orchestrates", "Domain experts in parallel", "Staff-engineer quality"
- Image placeholder: multi-agent orchestration visual

**Dependencies**: T-012, T-013
**Status**: [x] Completed

---

#### T-016: Build Feature Content — Security-Verified Skills [P]

**Description**: Content component for three-tier verification.

**References**: AC-US3-03

**Implementation Details**:
- `src/app/components/homepage/FeatureSecurityVerified.tsx`
- Visual: Three tier badges (Scanned/Verified/Certified) in vertical stack with descriptions
- Reuse TierBadge component from existing code
- Stats: "52 patterns", "36.82% flagged"
- Image placeholder: security shield

**Dependencies**: T-012, T-013
**Status**: [x] Completed

---

#### T-017: Build Feature Content — Agent Ecosystem [P]

**Description**: Content component for agent compatibility.

**References**: AC-US3-04

**Implementation Details**:
- `src/app/components/homepage/FeatureAgentEcosystem.tsx`
- Visual: Grid of agent badges with icons and brand colors (reuse existing pattern)
- Highlight top 10, show "+29 more" with expandable grid
- Image placeholder: agent ecosystem visual

**Dependencies**: T-012, T-013
**Status**: [x] Completed

---

### US-004: Nanobanana Image Placeholders

#### T-018: Create Placeholder Images Directory and Assets

**Description**: Set up the image directory structure with SVG placeholders.

**References**: AC-US4-04

**Implementation Details**:
- Create `public/images/homepage/` directory
- Create 4 SVG placeholder files:
  - `spec-workflow.svg` (400x300)
  - `multi-agent.svg` (400x300)
  - `security-shield.svg` (400x300)
  - `agent-ecosystem.svg` (400x300)
- Each SVG has gradient background, centered text with dimensions, and prompt description

**Dependencies**: None
**Status**: [x] Completed

---

## Phase 3: Integration

### US-005: Existing Dashboard & Trending Integration

#### T-019: Refactor page.tsx to Include New Sections

**Description**: Update the homepage to include video hero and feature sections above the existing dashboard.

**References**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05

**Implementation Details**:
- Modify `src/app/page.tsx`
- Insert VideoHero at the top (before existing Hero section)
- Insert feature sections after VideoHero, before Market Dashboard
- Wrap feature sections in ScrollFadeIn components
- Preserve ALL existing sections: Hero stats, Market Dashboard, Trending, Categories, Verification, Agents
- Existing server-side data fetching (getSkills, getSkillCategories) remains untouched
- Move existing hero content into a condensed "Quick Stats" bar below features

**Test Plan**:
- **File**: Visual regression + existing test suite
- **Tests**:
  - **TC-019**: Homepage renders without errors
    - Given the updated page.tsx
    - When the homepage loads
    - Then no console errors and all sections visible
  - **TC-020**: Data fetching unchanged
    - Given getSkills and getSkillCategories
    - When page renders
    - Then skill data populates dashboard and trending sections

**Dependencies**: T-010, T-014, T-015, T-016, T-017, T-018
**Status**: [x] Completed

---

#### T-020: Add Homepage CSS for New Sections

**Description**: Add CSS styles for the new homepage sections to globals.css.

**References**: AC-US2-05, AC-US3-06

**Implementation Details**:
- Video hero gradient and grain texture styles
- Feature section alternating layout responsive breakpoints
- ScrollFadeIn animation keyframes
- Play/pause button styling
- Dark theme compatibility for all new sections
- Mobile breakpoints (768px, 480px)

**Dependencies**: T-019
**Status**: [x] Completed

---

## Phase 4: Polish & Verification

#### T-021: Accessibility Audit

**Description**: Ensure all new content meets accessibility standards.

**References**: AC-US2-06

**Implementation Details**:
- Video: aria-label, role, captions track (even if empty)
- Play/pause button: proper aria-label, keyboard accessible
- ScrollFadeIn: prefers-reduced-motion disables animations
- Image placeholders: meaningful alt text
- Color contrast check on new text elements

**Dependencies**: T-019, T-020
**Status**: [x] Completed

---

#### T-022: Responsive Testing & Mobile Optimization

**Description**: Test and optimize for mobile viewports.

**References**: AC-US2-06, AC-US3-05

**Implementation Details**:
- Test at 320px, 480px, 768px, 1024px, 1440px
- Video hero: reduce height on mobile, hide play/pause on very small screens
- Feature sections: stack vertically on mobile
- Agent grid: scroll horizontally on narrow screens
- Verify no horizontal overflow

**Dependencies**: T-021
**Status**: [x] Completed

---

#### T-023: Final Build & Deployment Verification

**Description**: Ensure everything builds and deploys correctly.

**Implementation Details**:
- `npm run build` succeeds without errors
- Video files included in build output
- Cloudflare Workers deployment handles video static assets
- Lighthouse performance score check (target: >80 performance)

**Dependencies**: T-022
**Status**: [x] Completed
