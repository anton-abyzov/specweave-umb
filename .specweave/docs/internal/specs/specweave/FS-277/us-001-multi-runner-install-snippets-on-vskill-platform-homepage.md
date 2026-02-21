---
id: US-001
feature: FS-277
title: Multi-Runner Install Snippets on vskill-platform Homepage
status: complete
priority: P1
created: 2026-02-21
project: vskill-platform
---
# US-001: Multi-Runner Install Snippets on vskill-platform Homepage

**Feature**: [FS-277](./FEATURE.md)

developer visiting the vskill homepage
**I want** to see install commands for my preferred package manager (npm, bun, pnpm, yarn)
**So that** I know vskill works with my toolchain without needing to mentally translate `npx` commands

---

## Acceptance Criteria

- [x] **AC-US1-01**: The homepage hero `$ npm install -g vskill` code snippet is replaced with a tabbed/multi-line snippet showing npx, bunx, pnpx, and yarn dlx alternatives
- [x] **AC-US1-02**: The AnimatedTerminal component cycles through different package runners (not just npx) in its demo scenarios
- [x] **AC-US1-03**: The skill detail page install command shows all four package runners, not just `$ npx vskill add`

---

## Implementation

**Increment**: [0277-multi-package-manager-docs](../../../../../increments/0277-multi-package-manager-docs/spec.md)

