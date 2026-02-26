---
status: completed
---
# 0331: Universal Skills Migration — SpecWeave to vskill

## Overview
Move ~75 fully-generic domain expertise skills from SpecWeave plugins to the vskill repo as universal plugins. Drop the `sw-` namespace prefix. Add `--repo` CLI flag for remote plugin installation.

## User Stories

### US-001: Universal Skill Installation
**As a** developer using any AI coding tool,
**I want to** install domain expertise skills from vskill without SpecWeave,
**So that** I get expert guidance (frontend, backend, infra, etc.) without framework lock-in.

**Acceptance Criteria:**
- [x] AC-US1-01: All generic skills (~75) exist in `vskill/plugins/` with correct directory structure
- [x] AC-US1-02: Each plugin has a valid `plugin.json` without `sw-` prefix (e.g., `frontend`, `backend`)
- [x] AC-US1-03: `marketplace.json` at vskill root lists all 15 plugins
- [x] AC-US1-04: Skills contain zero SpecWeave references (no `.specweave/`, no `specweave` CLI, no skill-memories boilerplate)
- [x] AC-US1-05: Cross-skill references updated (`/sw-frontend:figma` → `/frontend:figma`)

### US-002: Remote Plugin Installation via CLI
**As a** vskill user,
**I want to** run `vskill install --repo anton-abyzov/vskill --plugin frontend`,
**So that** skills install with namespace prefix (e.g., `/frontend:nextjs`).

**Acceptance Criteria:**
- [ ] AC-US2-01: `--repo` flag added to `vskill install` command
- [ ] AC-US2-02: Fetches marketplace.json from GitHub, resolves plugin, installs skills with namespace
- [ ] AC-US2-03: Lockfile records `source: "github:{owner}/{repo}#plugin:{name}"`
- [ ] AC-US2-04: Tests pass for --repo installation flow

### US-003: SpecWeave Cleanup
**As a** SpecWeave maintainer,
**I want to** remove migrated plugins from the SpecWeave repo,
**So that** SpecWeave focuses on workflow orchestration, not domain expertise.

**Acceptance Criteria:**
- [x] AC-US3-01: 13 plugin directories deleted from specweave
- [x] AC-US3-02: 3 core skills + 3 docs skills removed from specweave
- [x] AC-US3-03: SpecWeave marketplace.json updated (only framework-specific plugins remain)

### US-004: Platform Submission
**As a** platform operator,
**I want to** submit all vskill-hosted skills to verified-skill.com,
**So that** they appear in the registry for discovery.

**Acceptance Criteria:**
- [x] AC-US4-01: `submit-vskill.sh` script exists in vskill-platform
- [ ] AC-US4-02: Script lists all ~75 skills with correct repo URL and skill paths
