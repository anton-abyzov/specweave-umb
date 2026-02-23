# Spec — 0335: Auto-Loading Update, Discovery Skill & --all Flag

## Problem

Increment 0331 migrated ~75 generic domain skills from specweave to vskill repo (`sw-frontend` → `frontend`, etc.). The auto-loading mechanism still references old `sw-*` names that no longer exist in specweave's marketplace.json — auto-loading fails for all 13 migrated plugin categories. Additionally, there's no way to install all plugins from a repo at once, and no skill-level discovery backed by verified-skill.com.

## Solution

1. Update specweave auto-loading to use new plugin names and install migrated plugins via `vskill add --repo`
2. Add `--all` flag to `vskill add --repo` for bulk plugin installation
3. Create a "scout" discovery skill that searches verified-skill.com and installs matching skills

## User Stories

### US-001: Auto-loading handles migrated plugins
As a SpecWeave user, I want auto-loading to install domain plugins from the vskill repo so that skills like `/frontend:nextjs` work after lazy-loading.

**Acceptance Criteria**:
- [x] AC-US1-01: `SPECWEAVE_PLUGINS` split into specweave-only and vskill lists
- [x] AC-US1-02: Haiku prompt uses new names (`frontend` not `sw-frontend`) for migrated plugins
- [x] AC-US1-03: `installPluginViaCli()` routes vskill plugins to `--repo` install path
- [x] AC-US1-04: `user-prompt-submit.sh` has third branch for vskill repo plugins
- [x] AC-US1-05: Unit tests verify plugin classification helpers

### US-002: Bulk plugin install via --all flag
As a developer, I want to install all plugins from a repo marketplace at once so I don't have to install each one individually.

**Acceptance Criteria**:
- [x] AC-US2-01: `vskill add --repo owner/repo --all` installs all plugins from marketplace.json
- [x] AC-US2-02: `--all` implies `--yes` (non-interactive)
- [x] AC-US2-03: Progress shown during bulk install
- [x] AC-US2-04: `source` argument optional when `--repo` is present
- [x] AC-US2-05: Tests cover --all flag

### US-003: Discovery skill for verified-skill.com
As a developer, I want a skill that discovers and installs relevant skills from verified-skill.com so I can quickly find domain expertise.

**Acceptance Criteria**:
- [x] AC-US3-01: Scout plugin created in vskill/plugins/scout/
- [x] AC-US3-02: SKILL.md instructs Claude to search via `vskill find` and present trust-scored results
- [x] AC-US3-03: Supports both individual skill install and plugin bundle install
- [x] AC-US3-04: Added to vskill marketplace.json
- [x] AC-US3-05: Added to submit-vskill.sh
