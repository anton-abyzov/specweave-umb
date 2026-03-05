---
id: US-003
feature: FS-432
title: UI Primitive Components
status: complete
priority: P2
created: 2026-03-05
project: specweave
---
# US-003: UI Primitive Components

**Feature**: [FS-432](./FEATURE.md)

developer building landing page sections
**I want** a set of reusable UI primitive components (Button, Badge, Icon, Divider, CodeBlock)
**So that** I can compose sections with consistent styling and behavior

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given the Button component, when rendered with variant prop (primary, secondary, ghost, outline), then each variant displays correct colors, borders, hover/focus states, and disabled state using design tokens
- [x] **AC-US3-02**: Given the Badge component, when rendered with variant prop (default, success, warning, info, primary), then each displays the correct background, text color, and border-radius from tokens
- [x] **AC-US3-03**: Given the Icon component, when rendered with a Lucide icon name or a brand SVG slug, then it renders the correct SVG at the specified size with currentColor inheritance
- [x] **AC-US3-04**: Given the CodeBlock component, when rendered with code content and an optional copy button, then it displays syntax-highlighted code in a styled container with a one-click copy-to-clipboard action and visual feedback
- [x] **AC-US3-05**: Given any UI primitive, when rendered in dark mode, then all colors, borders, and shadows adapt correctly via token overrides

---

## Implementation

**Increment**: [0432-bold-website-redesign](../../../../../increments/0432-bold-website-redesign/spec.md)

