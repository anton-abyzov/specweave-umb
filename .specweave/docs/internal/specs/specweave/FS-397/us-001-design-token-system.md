---
id: US-001
feature: FS-397
title: Design Token System
status: complete
priority: P1
created: 2026-03-02
project: specweave
external:
  github:
    issue: 1463
    url: https://github.com/anton-abyzov/specweave/issues/1463
---
# US-001: Design Token System

**Feature**: [FS-397](./FEATURE.md)

docs site visitor
**I want** a consistent, professional visual design
**So that** the site feels polished and trustworthy

---

## Acceptance Criteria

- [x] **AC-US1-01**: CSS token file defines refined indigo-purple palette (primary ~#6b58b8), semantic colors, neutrals, typography (Inter + JetBrains Mono), spacing (4px grid), radius, shadows
- [x] **AC-US1-02**: Dark mode has intentional dark palette, not just inverted values
- [x] **AC-US1-03**: Infima variables (`--ifm-*`) are mapped from design tokens
- [x] **AC-US1-04**: custom.css uses only `var(--sw-*)` tokens — no hard-coded colors
- [x] **AC-US1-05**: Inter font loaded via Google Fonts CDN with preconnect

---

## Implementation

**Increment**: [0397-development-loom-docs-rework](../../../../../increments/0397-development-loom-docs-rework/spec.md)

