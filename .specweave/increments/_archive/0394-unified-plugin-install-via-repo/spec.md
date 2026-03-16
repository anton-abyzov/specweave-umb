# Unified Plugin Installation via --repo

## Problem Statement

SpecWeave's `user-prompt-submit.sh` hook has two separate plugin installation paths:

1. **sw-* plugins** (sw-github, sw-jira, sw-ado, sw-release, sw-diagrams, sw-media, docs): Uses `install_plugin_via_vskill()` which depends on `~/.claude/plugins/marketplaces/specweave` local directory containing a copy of the specweave repo with `marketplace.json`. This directory no longer exists after the plugin cleanup on 2026-02-25.

2. **Domain plugins** (frontend, backend, testing, mobile, infra, etc.): Uses `install_vskill_repo_plugin()` which correctly uses `npx vskill install --repo anton-abyzov/vskill --plugin <name>` -- fetching from GitHub directly.

The sw-* path is broken because `~/.claude/plugins/marketplaces/specweave` was removed and is not recreated. The fix is to unify both paths to use `--repo`, making sw-* plugins install via `npx vskill install --repo anton-abyzov/specweave --plugin <name>` (from GitHub), identical to how domain plugins already work.

Additionally, the `VSKILL_REPO_PLUGINS` list references plugins (`k8s`, `cost`, `docs`) that do not exist in the vskill marketplace.json, causing silent install failures.

## User Stories

### US-001: Unified sw-* Plugin Installation via --repo
**Project**: specweave

**As a** SpecWeave user
**I want** sw-* plugins (sw-github, sw-jira, etc.) to install from GitHub via `--repo anton-abyzov/specweave`
**So that** plugin installation works without requiring a local marketplace directory at `~/.claude/plugins/marketplaces/specweave`

**Acceptance Criteria**:
- [x] **AC-US1-01**: `install_plugin_via_vskill()` function in `user-prompt-submit.sh` uses `npx vskill install --repo anton-abyzov/specweave --plugin <name>` instead of `--plugin-dir ~/.claude/plugins/marketplaces/specweave`
- [x] **AC-US1-02**: The function no longer checks for or depends on `~/.claude/plugins/marketplaces/specweave` directory existence
- [x] **AC-US1-03**: The scope guard migration code (lines ~297-304) also uses the --repo path for sw-* reinstallation
- [x] **AC-US1-04**: sw-* plugins install successfully when triggered by lazy-loading keyword detection or LLM detection

### US-002: Clean Up Stale Plugin References
**Project**: specweave

**As a** SpecWeave developer
**I want** the `VSKILL_REPO_PLUGINS` list to match the actual plugins available in the vskill marketplace
**So that** install attempts for non-existent plugins don't fail silently

**Acceptance Criteria**:
- [x] **AC-US2-01**: `k8s` is removed from `VSKILL_REPO_PLUGINS` (infra plugin covers Kubernetes)
- [x] **AC-US2-02**: `cost` is removed from `VSKILL_REPO_PLUGINS` (not in vskill marketplace)
- [x] **AC-US2-03**: `docs` is removed from `VSKILL_REPO_PLUGINS` (docs is a specweave sw-* plugin at `anton-abyzov/specweave`, not a vskill domain plugin)
- [x] **AC-US2-04**: The suggest-only mode message (line ~1266) uses the `--repo` flag syntax instead of `--plugin-dir`

### US-003: Startup Health Check Cleanup
**Project**: specweave

**As a** SpecWeave developer
**I want** the startup health check to not reference the removed marketplace directory
**So that** startup scripts don't log false warnings about missing directories

**Acceptance Criteria**:
- [x] **AC-US3-01**: `startup-health-check.sh` does not reference `~/.claude/plugins/marketplaces/specweave` as a dependency
- [x] **AC-US3-02**: The `SPECWEAVE_DIR` variable in startup-health-check.sh is updated or removed if it only pointed to the marketplace directory

## Out of Scope

- Changing how the core `sw` plugin is installed (it uses the inline copier via `plugin-copier.ts`, which works correctly from the specweave npm package)
- Changes to `plugin-installer.ts` or `refresh-plugins.ts` (these handle first-party bundled plugin installation from the npm package, not on-demand lazy loading)
- Changes to vskill CLI itself (the `--repo` flag already works correctly)
- LSP plugin installation (uses `claude plugin install` from the boostvolt marketplace, unrelated)

## Technical Notes

- The specweave repo is at `anton-abyzov/specweave` on GitHub and has `.claude-plugin/marketplace.json` with plugins: sw, sw-github, sw-jira, sw-ado, sw-release, sw-diagrams, docs, sw-media
- The vskill repo is at `anton-abyzov/vskill` on GitHub and has `.claude-plugin/marketplace.json` with plugins: frontend, backend, testing, mobile, infra, ml, kafka, confluent, payments, security, skills, blockchain
- Both repos' marketplace.json files are accessible via raw.githubusercontent.com, which is what `--repo` uses
- The `docs` plugin is in the specweave marketplace (not vskill), so when LLM detection identifies "docs" as needed, it should route to specweave repo, not vskill repo
