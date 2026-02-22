---
increment: 0277-multi-package-manager-docs
title: "Multi-Package-Manager Documentation Update"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Multi-Package-Manager Documentation Update

## Overview

Update homepage and docs across vskill-platform, vskill CLI, and specweave docs-site to showcase multi-package-manager support (npx, bunx, pnpx, yarn dlx) instead of npm-only examples. Users should see that vskill and specweave work with any JavaScript package runner.

## User Stories

### US-001: Multi-Runner Install Snippets on vskill-platform Homepage (P1)
**Project**: vskill-platform

**As a** developer visiting the vskill homepage
**I want** to see install commands for my preferred package manager (npm, bun, pnpm, yarn)
**So that** I know vskill works with my toolchain without needing to mentally translate `npx` commands

**Acceptance Criteria**:
- [x] **AC-US1-01**: The homepage hero `$ npm install -g vskill` code snippet is replaced with a tabbed/multi-line snippet showing npx, bunx, pnpx, and yarn dlx alternatives
- [x] **AC-US1-02**: The AnimatedTerminal component cycles through different package runners (not just npx) in its demo scenarios
- [x] **AC-US1-03**: The skill detail page install command shows all four package runners, not just `$ npx vskill add`

---

### US-002: Multi-Runner Examples on spec-weave.com Docs Site (P1)
**Project**: specweave

**As a** developer reading the SpecWeave docs
**I want** installation guides and code examples to include bun, pnpm, and yarn alternatives alongside npm
**So that** I can follow the docs using my preferred package manager

**Acceptance Criteria**:
- [x] **AC-US2-01**: The docs-site homepage CTA (`npm install -g specweave && specweave init .`) shows alternatives for bun, pnpm, and yarn
- [x] **AC-US2-02**: The Quick Start guide installation section shows all four package managers
- [x] **AC-US2-03**: The Installation guide's "Method 1: Global Install" and "Method 2: npx" sections include bun/pnpm/yarn equivalents
- [x] **AC-US2-04**: The verified-skills.md doc's `npx vskill` CLI section shows all four runners
- [x] **AC-US2-05**: The skills/index.md reference to `npx vskill` CLI mentions all runners

---

### US-003: Multi-Runner Examples in vskill CLI README (P1)
**Project**: vskill

**As a** developer discovering vskill via its GitHub README
**I want** to see that I can use bunx, pnpx, or yarn dlx as alternatives to npx
**So that** I can use vskill with my preferred toolchain immediately

**Acceptance Criteria**:
- [x] **AC-US3-01**: The vskill README.md top code block shows npx, bunx, pnpx, and yarn dlx alternatives for the main commands
- [x] **AC-US3-02**: The Commands section examples include alternative runners

## Functional Requirements

### FR-001: Consistent Multi-Runner Format
All multi-runner snippets use a consistent format across all three repos. The preferred format is a comment-annotated code block:

```bash
# npm
npx vskill add anthropics/frontend-design

# bun
bunx vskill add anthropics/frontend-design

# pnpm
pnpx vskill add anthropics/frontend-design

# yarn
yarn dlx vskill add anthropics/frontend-design
```

### FR-002: Tabbed UI for Platform Pages
On the vskill-platform (React/Next.js), use a tabbed component for switching between runners. On the docs-site (Docusaurus), use Docusaurus `<Tabs>` component where available, or comment-annotated code blocks otherwise.

### FR-003: AnimatedTerminal Variety
The AnimatedTerminal component should randomly or sequentially cycle through different package runners across its scenarios, not use `npx` for all three.

## Success Criteria

- Every install/run command across all three repos shows at least npx and one alternative (bunx preferred as second)
- No npm-only code examples remain in user-facing pages (homepage, install guide, quick-start, skill detail pages)

## Out of Scope

- Adding actual bun/pnpm/yarn package publishing (already works via npx-compatible runners)
- Changing CLI code or logic -- this is docs/UI only
- Updating non-user-facing files (test fixtures, internal docs, build scripts)

## Dependencies

- None -- purely content/UI changes
