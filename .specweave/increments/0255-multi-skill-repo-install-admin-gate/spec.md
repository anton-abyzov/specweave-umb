---
increment: 0255-multi-skill-repo-install-admin-gate
title: "Multi-Skill Repo Install & Queue Admin Gating"
type: feature
priority: P1
status: planned
created: 2026-02-20
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Multi-Skill Repo Install & Queue Admin Gating

## Overview

Two targeted improvements across the vskill ecosystem:

1. **vskill CLI**: `vskill add owner/repo` currently installs only a single SKILL.md (root or `--skill <name>`). Repos that contain multiple skills (root SKILL.md + `skills/*/SKILL.md`) require separate `add` invocations for each. The CLI should discover and install ALL skills from a repo in a single command.

2. **vskill-platform**: The queue page (`/queue`) exposes a batch submission form to any authenticated user. This form should be restricted to admin users only, since batch submission is an operational tool, not a public user feature.

## User Stories

### US-001: Multi-Skill Repo Discovery & Install (P1)
**Project**: vskill

**As a** developer installing skills via the CLI
**I want** `vskill add owner/repo` to discover and install all skills from a GitHub repo
**So that** I don't have to run separate `add` commands for each skill in a multi-skill repository

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `vskill add owner/repo` (without `--skill`) fetches the GitHub Trees API to discover all `SKILL.md` files (root + `skills/*/SKILL.md`)
- [ ] **AC-US1-02**: Each discovered SKILL.md is fetched, scanned (blocklist + platform security + tier1), and installed independently
- [ ] **AC-US1-03**: If any single skill fails the scan, only that skill is skipped; remaining skills are still installed
- [ ] **AC-US1-04**: Each installed skill gets its own entry in the lockfile with the correct skill name derived from its path (root -> repo name, `skills/foo/SKILL.md` -> `foo`)
- [ ] **AC-US1-05**: The summary output lists all installed skills with their individual scan verdicts
- [ ] **AC-US1-06**: `--skill <name>` flag continues to work as before, installing only the specified skill (backward compatible)
- [ ] **AC-US1-07**: If the repo contains only a root SKILL.md (no `skills/` directory), behavior is identical to current single-skill install

---

### US-002: Queue Batch Submit Admin Gate (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the batch submission form on the queue page restricted to admin users only
**So that** regular users cannot flood the queue with bulk submissions and the form is only available to trusted operators

**Acceptance Criteria**:
- [ ] **AC-US2-01**: The "Submit Skills" button and batch submission form on `/queue` are only visible when `isAdmin` is true
- [ ] **AC-US2-02**: Non-admin authenticated users see the queue list but no batch submission controls
- [ ] **AC-US2-03**: Unauthenticated users see the queue list but no batch submission controls
- [ ] **AC-US2-04**: The existing `/submit` page remains available to all authenticated users for individual skill submission (unaffected)
- [ ] **AC-US2-05**: Admin status is determined by the existing `useAdminStatus` hook (no new auth mechanism needed)

## Non-Functional Requirements

- **NFR-01**: Multi-skill discovery must use the GitHub Trees API (single request) rather than N individual raw.githubusercontent.com fetches for discovery
- **NFR-02**: The CLI must handle repos with up to 200 skills without timeout
- **NFR-03**: All existing `vskill add` tests must continue to pass (backward compatibility)
- **NFR-04**: The queue page admin gate is a UI-only change; the submission API endpoints remain unchanged

## Success Criteria

- `vskill add owner/multi-skill-repo` installs N skills in a single invocation where N > 1
- Existing single-skill repos install identically to before (zero regression)
- Queue page batch form is invisible to non-admin users

## Out of Scope

- Deduplication of submissions (covered by increment 0253)
- Plugin/marketplace structure discovery in the CLI (existing `--plugin` path is separate)
- Rate limiting changes on the submission API
- Admin authentication mechanism changes
- Recursive nested skill directories beyond `skills/*/SKILL.md`

## Dependencies

- Existing GitHub raw content API for fetching individual SKILL.md files
- GitHub Trees API (`GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1`) for skill discovery
- Existing `useAdminStatus` hook and `/api/v1/auth/me` endpoint on vskill-platform
