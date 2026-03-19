---
increment: 0591-docs-config-reference
title: "Configuration Reference Documentation Page"
type: feature
priority: P1
status: planned
created: 2026-03-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Configuration Reference Documentation Page

## Overview

Create a comprehensive Configuration Reference page in the SpecWeave docs-site that documents all three configuration surfaces: `config.json` (project-level), `metadata.json` (per-increment), and environment variables. The page provides a single source of truth for every configurable property, its type, default value, and purpose. A prominent "Disableable Features" quick-reference table addresses the most common user need: knowing how to turn off specific SpecWeave behaviors.

**Target file**: `repositories/anton-abyzov/specweave/docs-site/docs/reference/configuration.md`
**Sidebar**: Reference section in `sidebars.ts`

## User Stories

### US-001: Find and Understand Configuration Properties (P1)
**Project**: specweave

**As a** SpecWeave user setting up or customizing my project
**I want** a single reference page documenting every config.json property, metadata.json field, and environment variable
**So that** I can quickly look up any setting's purpose, type, default value, and usage without reading source code

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Page exists at `docs/reference/configuration.md` and renders correctly in the docs-site
- [ ] **AC-US1-02**: Page is linked in the Reference section of `sidebars.ts`
- [ ] **AC-US1-03**: All `config.json` top-level sections are documented with property name, type, default value, and description:
  - Core: `version`, `language`, `project`, `adapters`
  - Plugins: `plugins` (enabled list, settings)
  - Living Documentation: `livingDocs` (copyBasedSync, threeLayerSync)
  - Testing & Quality: `testing` (defaultTestMode, coverageTargets, tddEnforcement, playwright), `grill`
  - Planning: `planning` (deepInterview), `incrementAssist`
  - Limits: `limits` (maxActiveIncrements, hardCap, allowEmergencyInterrupt, typeBehaviors, staleness)
  - Sync & Integrations: `sync` (enabled, direction, autoSync, profiles, github, jira, ado, orchestration), `hooks`, `issueTracker`
  - CI/CD & Repository: `cicd` (pushStrategy, git, release, autoFix, monitoring), `repository`
  - Documentation: `documentation` (directories, preview), `apiDocs` (OpenAPI, Postman)
  - AI & Automation: `auto` (maxIterations, maxTurns, requireTests, etc.), `reflect` (enabled, model, maxLearningsPerSession), `contextBudget`, `skillGen`
  - Advanced: `umbrella` (enabled, childRepos, storyRouting, sync), `archiving`, `deduplication`, `statusLine`, `pluginAutoLoad`, `translation`, `multiProject`, `projectMappings`
- [ ] **AC-US1-04**: All `metadata.json` properties are documented:
  - Core: `id`, `type`, `status`, `priority`, `created`, `lastActivity`, `testMode`, `coverageTarget`
  - Lifecycle: `backlogReason`, `backlogAt`, `pausedReason`, `pausedAt`, `abandonedReason`, `abandonedAt`, `readyForReviewAt`, `approvedAt`
  - External: `externalLinks`, `externalRefs`, `syncTarget`, `feature_id`, `epic_id`
  - Multi-project: `projectId`, `multiProject`, `externalContainer`
  - CI/CD: `prRefs`, `skipLivingDocsSync`
- [ ] **AC-US1-05**: All environment variables are documented with name, purpose, and example values:
  - SpecWeave internals: `SPECWEAVE_DISABLE_HOOKS`, `SPECWEAVE_DEBUG`, `SPECWEAVE_DISABLE_AUTO_LOAD`, `SPECWEAVE_SHELL`, `SPECWEAVE_DISABLE_LOCKS`, `SPECWEAVE_FORCE_LOCKS`, `SPECWEAVE_AUTO_INSTALL`, `SPECWEAVE_SKIP_IMAGE_GEN`, `SPECWEAVE_UPDATE_NO_SELF`, `SPECWEAVE_NO_INCREMENT`, `SPECWEAVE_BACKGROUND_PROCESS`, `SPECWEAVE_BACKGROUND_JOB`
  - Import config: `SPECWEAVE_IMPORT_ENABLED`, `SPECWEAVE_IMPORT_TIME_RANGE_MONTHS`, `SPECWEAVE_IMPORT_PAGE_SIZE`
  - External tool credentials: `GITHUB_TOKEN`, `JIRA_API_TOKEN`, `JIRA_DOMAIN`, `AZURE_DEVOPS_PAT`, `AZURE_DEVOPS_ORG`
- [ ] **AC-US1-06**: Each config section includes a JSON code example showing realistic usage
- [ ] **AC-US1-07**: Valid enum values are listed for enum-type properties (e.g., `status`, `type`, `testMode`, `pushStrategy`, `language`)

---

### US-002: Disable Specific SpecWeave Features (P1)
**Project**: specweave

**As a** SpecWeave user who wants faster iteration or simpler workflow
**I want** a quick-reference table showing which features can be disabled and the exact config to do so
**So that** I can turn off features like living docs, TDD enforcement, or deep interview without hunting through documentation

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A "Quick Reference: Disableable Features" section is prominently placed near the top of the page (after the introduction, before detailed sections)
- [ ] **AC-US2-02**: The table includes all disableable features with columns: Feature, Config Path, Value to Disable, Default
- [ ] **AC-US2-03**: The following features are documented as disableable:
  - Living docs (copy-based sync) -- `livingDocs.copyBasedSync.enabled: false`
  - Living docs (three-layer sync) -- `livingDocs.threeLayerSync.enabled: false`
  - TDD enforcement -- `testing.tddEnforcement: "off"`
  - Deep interview mode -- `planning.deepInterview.enabled: false`
  - Plugin auto-loading -- `pluginAutoLoad.enabled: false`
  - Reflection/learning -- `reflect.enabled: false`
  - Grill quality gate -- `grill.required: false`
  - External sync -- `sync.enabled: false`
  - Auto-sync on completion -- `sync.settings.autoSyncOnCompletion: false`
  - Auto-create external issues -- `sync.autoCreateOnIncrement: false`
  - Increment assist -- `incrementAssist.enabled: false`
  - Hooks -- `SPECWEAVE_DISABLE_HOOKS=1` (env var)
  - Auto-archiving -- `archiving.autoArchive: false`
  - Status line -- `statusLine.enabled: false`
  - API docs generation -- `apiDocs.enabled: false`
  - Context budget (hook output) -- `contextBudget.level: "off"`
  - Skill generation -- `skillGen.detection: "off"`
  - Translation -- `translation.enabled: false`
  - Command deduplication -- `deduplication.enabled: false`
  - Auto-install -- `SPECWEAVE_AUTO_INSTALL=false` (env var)
- [ ] **AC-US2-04**: An introductory note explains that disabling living docs reduces LLM context richness but increases speed

## Functional Requirements

### FR-001: Page Structure
The page must follow this structure:
1. Title and introduction
2. Quick Reference: Disableable Features (table)
3. config.json Reference (organized by category with nested property tables)
4. metadata.json Reference (organized by category)
5. Environment Variables Reference (organized by purpose)

### FR-002: Property Documentation Format
Each property must include: property path (dot-notation), type, default value, description, and since-version where available.

### FR-003: Docusaurus Compatibility
The page must use standard Docusaurus Markdown (frontmatter, admonitions, code blocks). No custom React components required.

### FR-004: Security Note for Credentials
Environment variable credentials (GITHUB_TOKEN, JIRA_API_TOKEN, AZURE_DEVOPS_PAT) must include a note that these should be set via environment variables or secret managers, never hardcoded in config files.

## Success Criteria

- Page renders correctly in the docs-site
- All properties from `SpecWeaveConfig` interface (30+ top-level sections) are documented
- All properties from `IncrementMetadataV2` interface are documented
- All `SPECWEAVE_*` environment variables found in source are documented
- Disableable features table covers 20+ features
- Page is accessible from the sidebar under Reference

## Out of Scope

- Auto-generating docs from TypeScript types (manual documentation for now)
- Interactive config builder/validator
- Per-plugin configuration reference (plugins have their own docs)
- Documenting internal/undocumented config properties not in the public TypeScript types

## Dependencies

- Source of truth: `src/core/config/types.ts` (SpecWeaveConfig interface)
- Source of truth: `src/core/types/increment-metadata.ts` (IncrementMetadataV2 interface)
- Source of truth: `src/core/auto/types.ts` (AutoConfig interface)
- Source of truth: `src/core/reflection/reflect-handler.ts` (ReflectConfig interface)
- Existing sidebar structure in `docs-site/sidebars.ts`
