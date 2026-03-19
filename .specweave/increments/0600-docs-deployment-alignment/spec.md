---
increment: 0600-docs-deployment-alignment
title: "Fix docs deployment alignment and domain references"
type: bug
priority: P1
status: active
created: 2026-03-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: Docs deployment alignment and domain references

## Overview

The documentation site is deployed at `spec-weave.com` but the umbrella CLAUDE.md and ~60+ living docs files reference `verified-skill.com/docs/...` (wrong domain). Additionally, the spec-weave.com homepage has a Docusaurus config error, and redirects are missing for legacy URL patterns.

## User Stories

### US-001: Correct domain references (P1)
**Project**: specweave

**As a** developer or user
**I want** all documentation links to point to the correct domain (spec-weave.com)
**So that** clicking docs links actually reaches the documentation site

**Acceptance Criteria**:
- [x] **AC-US1-01**: Umbrella CLAUDE.md references `spec-weave.com` instead of `verified-skill.com` for docs
- [x] **AC-US1-02**: All `verified-skill.com/docs/` URLs in `.specweave/docs/public/` are replaced with `spec-weave.com/docs/`
- [x] **AC-US1-03**: Platform references to `verified-skill.com` (without `/docs/` path) are preserved unchanged

---

### US-002: Fix homepage and add redirects (P1)
**Project**: specweave

**As a** visitor
**I want** the spec-weave.com homepage to load without errors and legacy URLs to redirect properly
**So that** all entry points to the docs work correctly

**Acceptance Criteria**:
- [x] **AC-US2-01**: `spec-weave.com/` homepage loads without Docusaurus config errors
- [x] **AC-US2-02**: `/docs/academy/videos/005-opencode-web-calculator` redirects to `/docs/academy/videos/opencode-web-calculator`
- [x] **AC-US2-03**: `/docs/guides/getting-started/quickstart` redirects to `/docs/getting-started`

---

### US-003: Audit and deploy (P2)
**Project**: specweave

**As a** maintainer
**I want** sidebar entries verified against actual files and the site deployed
**So that** no navigation links are broken on the live site

**Acceptance Criteria**:
- [x] **AC-US3-01**: `npm run build` in docs-site completes without errors
- [x] **AC-US3-02**: All sidebar entries in sidebars.ts resolve to actual files
- [ ] **AC-US3-03**: Changes are pushed and deployment triggered

## Out of Scope

- Syncing living docs structure to match deployed docs-site structure (separate systems by design)
- Cleaning up stale `.specweave/docs-site-public/` and `.specweave/docs-site-internal/` snapshots
