# 0269: Remotion Hero Animation for SpecWeave Homepage

## Overview

Create a cinematic 45-second Remotion video composition that tells SpecWeave's security story — from the threat landscape to the V-Skills protection system. This video will be rendered to MP4 and embedded on the SpecWeave homepage as an autoplay background/hero video.

The `remotion-best-practices` skill is already installed in the project, providing patterns for text animations, spring physics, sequencing, and transitions.

## Creative Script: "From Chaos to Trust"

### Scene 1: THE PROBLEM (0-9s)
- **Visual**: Dark purple background. Dangerous skill code snippets (`curl | bash`, `eval(atob(...))`, credential theft patterns) float upward at 15% opacity with subtle blur — creating an ominous atmosphere
- **Animation**: "36.82%" slams into center with spring physics (damping: 200). Red gradient text, weight 900, 108px
- **Subtitle**: "of public AI skills contain security flaws" fades up below
- **Source**: "Snyk ToxicSkills Study - Feb 2026 - 3,984 skills" appears with 1s delay
- **Tags**: Threat types (credential theft, crypto miners, prompt injection, memory poisoning) fade in as red pill-shaped badges
- **Exit**: Full scene fades to 0 over final 1s

### Scene 2: THE SCANNER (8-18s, overlaps Scene 1)
- **Visual**: Split layout — skill file card on left, scan results on right
- **Left**: A mock `SKILL.md` file in a dark code window. Lines appear one by one. Last two lines are red (dangerous patterns)
- **Animation**: Green scan line sweeps top-to-bottom across the file card (1.5s, eased). After scan completes, red "BLOCKED" overlay slams over the card
- **Right**: "41-Pattern Security Scan" header. Results appear row by row (8px delay each). `FOUND` in red, `CLEAN` in green, monospace
- **Bottom**: "5 critical findings - Rejected" in red bold after all rows visible

### Scene 3: THREE TIERS OF TRUST (17-27s, overlaps Scene 2)
- **Visual**: Centered layout. Purple "VERIFIED SKILLS STANDARD" subtitle, white "Three Tiers of Trust" title
- **Animation**: Three circular badges pop in sequentially with bouncy spring (damping: 12, stiffness: 180):
  1. "Scanned" (green) — lightning icon — "41 patterns - <500ms - Free"
  2. Arrow fades in
  3. "Verified" (purple) — magnifier icon — "LLM intent analysis - 5-15s - $0.03"
  4. Arrow fades in
  5. "Certified" (amber) — shield icon — "Human review + sandbox - 1-5 days"
- **Footer**: "verifiedskill.com" fades in at bottom

### Scene 4: THE INSTALL FLOW (26-37s, overlaps Scene 3)
- **Visual**: macOS-style terminal window (traffic light dots, dark background)
- **Animation**: Typewriter effect types `$ npx vskill add @specweave/react-frontend` at 2 frames/char with blinking cursor
- **Output lines** appear one by one:
  1. "Fetching SKILL.md..."
  2. "Running 41-pattern scan..."
  3. "Pattern check: PASS (0 findings)" (green)
  4. "LLM intent analysis: PASS (96/100)" (green)
  5. "Verified - Installing..." (green bold)
- **Badge**: Green "Verified by vSkill" badge bounces in below terminal (damping: 8, springy)

### Scene 5: SHIP SAFELY (36-45s, overlaps Scene 4)
- **Visual**: Purple radial glow intensifies from center. Dark background
- **Animation**:
  1. "SpecWeave" wordmark slides up with spring (80px, weight 900, white-to-purple gradient)
  2. "Ship features while you sleep. **Safely.**" — "Safely." in green, weight 700
  3. Install command fades in: `npm install -g specweave && specweave init .`
  4. Trust badges fade in: "Verified Skills Only" (green), "41-Pattern Scan" (purple), "verifiedskill.com" (amber)

## Technical Specs

- **Resolution**: 1280x720 (HD)
- **FPS**: 30
- **Duration**: 1350 frames (45 seconds)
- **Fonts**: Inter (sans), JetBrains Mono (mono)
- **Color palette**: Purple dark (#0f0a1e), Purple (#7c3aed), Green (#22c55e), Red (#ef4444), Amber (#f59e0b)
- **Output**: MP4 (H.264), WebM fallback

## User Stories

### US-001: Remotion Project Setup
**As a** developer,
**I want** a Remotion project scaffolded within the docs-site,
**so that** I can preview and render the hero video.

**Acceptance Criteria:**
- [ ] AC-US1-01: Remotion dependencies installed (`remotion`, `@remotion/cli`, `@remotion/bundler`)
- [ ] AC-US1-02: `remotion/` directory created with `Root.tsx` and composition registration
- [ ] AC-US1-03: `npx remotion preview` shows the composition in the Remotion Studio
- [ ] AC-US1-04: `npm run remotion:preview` script added to `package.json`

### US-002: 5-Scene Composition
**As a** viewer,
**I want** the video to tell a clear story from problem to solution,
**so that** I understand why V-Skills matter.

**Acceptance Criteria:**
- [ ] AC-US2-01: Scene 1 displays 36.82% statistic with floating threat snippets
- [ ] AC-US2-02: Scene 2 shows scanning animation with green scan line and BLOCKED result
- [ ] AC-US2-03: Scene 3 presents three tiers with bouncy badge animations
- [ ] AC-US2-04: Scene 4 shows terminal typewriter with `npx vskill add` flow
- [ ] AC-US2-05: Scene 5 shows SpecWeave wordmark with "Ship safely" tagline
- [ ] AC-US2-06: Scene transitions use opacity crossfades (30 frame overlap)
- [ ] AC-US2-07: Spring physics used for badge/card entrances, typewriter for terminal text

### US-003: Video Render & Homepage Integration
**As a** homepage visitor,
**I want** the video to autoplay silently on the homepage,
**so that** the security story plays as I browse.

**Acceptance Criteria:**
- [ ] AC-US3-01: Video rendered to MP4 (H.264) and WebM
- [ ] AC-US3-02: `npm run remotion:render` script produces output
- [ ] AC-US3-03: Video embedded in homepage with `autoPlay muted loop playsInline`
- [ ] AC-US3-04: Fallback poster image for browsers without autoplay
- [ ] AC-US3-05: Video file committed to `static/video/` (or CDN if too large)

## Out of Scope

- Voiceover / audio (silent video with autoplay)
- AI-generated images — all visuals are code-rendered
- Mobile-specific video variant
