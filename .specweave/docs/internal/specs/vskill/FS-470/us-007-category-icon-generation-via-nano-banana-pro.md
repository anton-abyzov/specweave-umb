---
id: US-007
feature: FS-470
title: "Category Icon Generation via Nano Banana Pro"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author browsing the skill list."
project: vskill
external:
  github:
    issue: 65
    url: https://github.com/anton-abyzov/vskill/issues/65
---

# US-007: Category Icon Generation via Nano Banana Pro

**Feature**: [FS-470](./FEATURE.md)

**As a** skill author browsing the skill list
**I want** each plugin group to have a distinctive generated icon
**So that** I can visually distinguish plugin groups at a glance

---

## Acceptance Criteria

- [x] **AC-US7-01**: A one-time generation script uses the Nano Banana Pro model (`gemini-3-pro-image-preview`) to create plugin group icons in a consistent minimalist line-art style on transparent background
- [x] **AC-US7-02**: Generated icons are stored as static assets (WebP, 32x32px) in `src/eval-ui/public/images/icons/` and served by the eval server's static file handler
- [x] **AC-US7-03**: Each plugin group header renders its icon at 16x16 display size to the left of the plugin name
- [x] **AC-US7-04**: A fallback SVG icon (the existing box/package icon from `IconSkills`) is shown when a plugin-specific icon is not available
- [x] **AC-US7-05**: One empty-state illustration is generated and stored at `src/eval-ui/public/images/empty-studio.webp` (128x128, theme-neutral) for use in empty states

---

## Implementation

**Increment**: [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-020**: Create `scripts/generate-studio-icons.ts` generation script
- [x] **T-021**: Wire plugin icons in `SkillGroupHeader` with fallback
