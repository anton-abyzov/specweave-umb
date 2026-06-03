---
increment: 0871-plugin-version-sync
title: Sync plugin.json version on every publish path (stop plugin-cache drift)
type: bug
priority: P1
status: completed
created: 2026-06-03T07:30:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug: plugin.json version freezes → users' plugin cache never refreshes

## Overview

`plugins/specweave/.claude-plugin/plugin.json` `version` is the key `claude plugin install`
/ `specweave refresh-plugins` use to decide whether to re-copy plugin content. It froze at
**1.0.586** while `package.json` reached **1.0.589**, so the installer version-dedups and
**silently skips refreshing** users' `~/.claude/plugins/cache/specweave/...` — shipping stale
hooks.json (e.g. missing the new `stop` Stop hook) and missing skills (handoff + 3 others,
47 vs 51) even after a successful npm publish. (Observed live in this session; hotfixed one
machine by rsync — not a real fix.)

## Root cause

The version-sync into `plugin.json` + `.claude-plugin/marketplace.json` exists **only** in
`scripts/build/bump-version.sh` (added by 0794). But the actual release paths bypass it:
- **CI `release.yml`** uses `npm version … --no-git-tag-version` + `npm publish` (not bump-version.sh).
- **Manual** releases use `npm version` + `npm publish` (e.g. 0868's `npm version patch`).
- The `npm version` lifecycle script only runs `auto-changelog.js` (CHANGELOG) — no plugin.json sync.
- `prepublishOnly` only runs `rebuild` — no stamp, no validation gate.

`validate-versions.cjs` exists but only runs as a path-filtered PR check (`version-alignment.yml`),
so it never blocks a drifted publish.

## Goal

`plugin.json` (and `.claude-plugin/marketplace.json`) version is **always** equal to
`package.json` version in any published tarball, regardless of how the release is cut, and a
drift can neither be published nor pass tests.

## User Stories

### US-001: Version stamp runs on every publish path (P1)
**Project**: specweave

**As a** SpecWeave maintainer cutting a release by any path
**I want** plugin.json + marketplace.json version stamped to package.json automatically
**So that** Claude Code's plugin update detection never freezes and users always get fresh content.

**Acceptance Criteria**:
- [x] **AC-US1-01**: A reusable `scripts/build/stamp-plugin-version.cjs` writes `package.json.version` into `plugins/specweave/.claude-plugin/plugin.json` (`version`) and `.claude-plugin/marketplace.json` (`version` + `plugins[0].version`); idempotent, skips missing files, prints what it changed.
- [x] **AC-US1-02**: The stamp is wired into the `build` script so it runs on `prepublishOnly → rebuild → build` — i.e. on **every** `npm publish` (CI and manual), and into the `version` npm lifecycle so local `npm version` bumps reflect + commit it.
- [x] **AC-US1-03**: `prepublishOnly` runs `validate:versions` (new npm script wrapping `validate-versions.cjs`) AFTER the rebuild, so a drift hard-fails the publish.
- [x] **AC-US1-04**: `bump-version.sh` calls the new script instead of its inline `node -e` block (DRY — single source of truth); behavior preserved.

### US-002: Drift can't pass tests + current drift fixed (P1)
**Acceptance Criteria**:
- [x] **AC-US2-01**: A unit test asserts three-way alignment (package.json == `.claude-plugin/marketplace.json` root + plugins[0] == plugin.json); it FAILS on drift (proven RED against the current 1.0.586/1.0.589 mismatch) and passes once aligned.
- [x] **AC-US2-02**: The current drift is fixed: plugin.json + marketplace.json stamped to the current package.json version (1.0.589); `validate:versions` exits 0; the guard test is green.
- [x] **AC-US2-03**: `npm run build` succeeds and leaves plugin.json/marketplace.json stamped to package.json version.

## Out of Scope

- `plugins/specweave/marketplace.json` (skill-catalog schema version 1.1.0) — independently versioned, intentionally not synced.
- The end-to-end republish that proves `refresh-plugins` creates a fresh cache dir — OTP-gated; offered to Anton separately. (Requires a new version, since published 1.0.589 already shipped with plugin.json 1.0.586.)
- Reconciling the historical cache dir name `sw/1.0.0` (a claude-plugin internal) — noted, not changed here.

## Success Criteria

- Stamp + validate wired into build/prepublishOnly/version + bump-version.sh; guard test green; `npm run build` stamps; `node scripts/validation/validate-versions.cjs` exits 0.

## Dependencies

- `package.json` scripts, `scripts/build/bump-version.sh`, `scripts/validation/validate-versions.cjs`, the three version files.
