---
id: US-002
feature: FS-277
title: Multi-Runner Examples on spec-weave.com Docs Site
status: complete
priority: P1
created: 2026-02-21
project: specweave
---
# US-002: Multi-Runner Examples on spec-weave.com Docs Site

**Feature**: [FS-277](./FEATURE.md)

developer reading the SpecWeave docs
**I want** installation guides and code examples to include bun, pnpm, and yarn alternatives alongside npm
**So that** I can follow the docs using my preferred package manager

---

## Acceptance Criteria

- [x] **AC-US2-01**: The docs-site homepage CTA (`npm install -g specweave && specweave init .`) shows alternatives for bun, pnpm, and yarn
- [x] **AC-US2-02**: The Quick Start guide installation section shows all four package managers
- [x] **AC-US2-03**: The Installation guide's "Method 1: Global Install" and "Method 2: npx" sections include bun/pnpm/yarn equivalents
- [x] **AC-US2-04**: The verified-skills.md doc's `npx vskill` CLI section shows all four runners
- [x] **AC-US2-05**: The skills/index.md reference to `npx vskill` CLI mentions all runners

---

## Implementation

**Increment**: [0277-multi-package-manager-docs](../../../../../increments/0277-multi-package-manager-docs/spec.md)

