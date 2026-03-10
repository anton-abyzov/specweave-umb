---
id: US-001
feature: FS-477
title: "Shared VideoPlayer Component"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** developer."
project: vskill-platform
---

# US-001: Shared VideoPlayer Component

**Feature**: [FS-477](./FEATURE.md)

**As a** developer
**I want** a shared VideoPlayer component that encapsulates video playback with lazy loading
**So that** video logic is not duplicated across HomepageDemoHero and SkillStudioSection

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given the VideoPlayer component, when rendered with a `src` prop (mp4 + webm), then it displays a video element with play/pause overlay button, autoPlay, muted, loop, and playsInline attributes
- [ ] **AC-US1-02**: Given the VideoPlayer component with default props, when the video enters the viewport, then it starts loading via IntersectionObserver (lazy-load by default)
- [ ] **AC-US1-03**: Given the VideoPlayer component with `eager={true}`, when the page loads, then the video loads immediately without waiting for intersection
- [ ] **AC-US1-04**: Given the VideoPlayer component, when rendered, then it accepts `ariaLabel`, `accentColor`, and `className` props for customization, and the play/pause button border uses the accent color

---

## Implementation

**Increment**: [0477-homepage-studio-nav-redesign](../../../../../increments/0477-homepage-studio-nav-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
