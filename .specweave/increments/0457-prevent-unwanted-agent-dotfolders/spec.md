---
increment: 0457-prevent-unwanted-agent-dotfolders
title: "Consent-First Plugin Auto-Loading"
type: feature
priority: P0
status: active
created: 2026-03-09
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Consent-First Plugin Auto-Loading

## Problem Statement

SpecWeave's plugin auto-loading mechanism silently installs plugins without user consent. The `UserPromptSubmit` hook uses an LLM (Haiku) to detect relevant plugins and installs them with `--force --yes` flags, bypassing any approval step. This leads to irrelevant plugins being installed (e.g., Java/Rust backend skills for a Node.js project). Additionally, LSP plugins bypass the existing `suggestOnly` config flag entirely. The `suggestOnly` mechanism exists but defaults to `false`, making the unsafe behavior the default.

## Goals

- Make consent-first (`suggestOnly: true`) the default for all plugin auto-loading
- Ensure LSP plugin auto-install respects the `suggestOnly` flag
- Remove phantom marketplace entries that declare non-existent plugins
- Update TypeScript types and config schema to include `suggestOnly`
- Update tests to reflect new defaults and consent flow

## User Stories

### US-SW-001: Default to Suggest-Only Mode
**Project**: specweave
**As a** SpecWeave user
**I want** plugin auto-loading to suggest plugins instead of installing them silently
**So that** I maintain control over what gets installed in my project

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a fresh SpecWeave project with no explicit `suggestOnly` in config, when the hook detects a relevant plugin, then it displays a recommendation message instead of installing
- [ ] **AC-US1-02**: Given an existing project with `autoLoad.enabled: true` but no `suggestOnly` field, when the hook runs, then `suggestOnly` defaults to `true` (consent-first)
- [ ] **AC-US1-03**: Given a project with explicit `suggestOnly: false`, when the hook detects a plugin, then it auto-installs as before (opt-in to old behavior)
- [ ] **AC-US1-04**: Given a project with `suggestOnly: true` (explicit or default), when the hook detects a plugin, then the recommendation includes: plugin name, why it was detected, and the exact install command

---

### US-SW-002: Suggest-Only Recommendation Display
**Project**: specweave
**As a** SpecWeave user
**I want** clear, actionable plugin recommendations shown once per session
**So that** I can decide whether to install without being nagged repeatedly

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given a plugin recommendation is triggered, when the suggestion is displayed, then it includes the plugin name, detection reason, and a copy-pasteable install command (e.g., `npx vskill install --repo anton-abyzov/vskill --plugin mobile --agent claude-code`)
- [ ] **AC-US2-02**: Given a plugin was already suggested in the current session, when the same plugin is detected again, then no duplicate suggestion is shown
- [ ] **AC-US2-03**: Given a plugin suggestion was shown, when the user ignores it and starts a new session, then the suggestion may appear again

---

### US-SW-003: LSP Plugin Consent Guard
**Project**: specweave
**As a** SpecWeave user
**I want** LSP plugin auto-installation to respect the `suggestOnly` flag
**So that** LSP analyzers are not installed without my consent

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given `suggestOnly: true` (default), when an LSP plugin (TypeScript, Python, Rust analyzer) is detected, then it is suggested with an install command instead of auto-installed
- [ ] **AC-US3-02**: Given `suggestOnly: false` (explicit opt-in), when an LSP plugin is detected, then it auto-installs as before
- [ ] **AC-US3-03**: Given an LSP plugin suggestion is shown but not installed, when the user runs `specweave lsp` commands, then the existing CLI fallback works without the plugin

---

### US-SW-004: TypeScript Types and Config Schema Update
**Project**: specweave
**As a** SpecWeave contributor
**I want** the `PluginAutoLoadConfig` interface and config schema to include the `suggestOnly` field
**So that** the type system and validation accurately reflect the available configuration

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given the `PluginAutoLoadConfig` TypeScript interface, when inspected, then it includes a `suggestOnly?: boolean` field with JSDoc describing its purpose and default value
- [ ] **AC-US4-02**: Given the `specweave-config.schema.json`, when validated, then it includes `suggestOnly` as a boolean property under `autoLoad` with `default: true`
- [ ] **AC-US4-03**: Given a config file with `suggestOnly` set to a non-boolean value, when validated against the schema, then validation fails with a clear error message

---

### US-VK-005: Clean Up Phantom Marketplace Entries
**Project**: vskill
**As a** vskill maintainer
**I want** the marketplace.json to only list plugins that actually exist on disk
**So that** users and tooling do not reference unavailable plugins

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given the vskill `marketplace.json`, when inspected, then it contains only plugins with corresponding directories on disk (mobile, skills, google-workspace, marketing)
- [ ] **AC-US5-02**: Given the 8 phantom plugins (frontend, backend, testing, infra, payments, ml, kafka, confluent, security, blockchain), when removed from marketplace.json, then they are also removed from the `VSKILL_REPO_PLUGINS` list in the shell hook and the `VSKILL_PLUGINS` constant in the LLM detector
- [ ] **AC-US5-03**: Given the LLM detection prompt catalog, when a phantom plugin name is encountered, then it is marked as "not yet available" rather than completely removed, so the LLM knows not to suggest it
- [ ] **AC-US5-04**: Given existing tests that reference phantom plugins, when the test suite runs, then all tests pass with updated references

---

### US-SW-006: Update Hook Plugin Detection Logic
**Project**: specweave
**As a** SpecWeave developer
**I want** the `user-prompt-submit.sh` hook and `llm-plugin-detector.ts` to use suggest-only as the default path
**So that** the detection-to-installation flow respects consent by default

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Given the `user-prompt-submit.sh` hook, when `suggestOnly` is not set in config, then the hook follows the suggest-only code path (no `--force --yes` flags)
- [ ] **AC-US6-02**: Given the `llm-plugin-detector.ts`, when it returns detected plugins, then the caller checks `suggestOnly` before deciding to install or suggest
- [ ] **AC-US6-03**: Given the shell hook's `VSKILL_REPO_PLUGINS` list, when compared to actual available plugins, then only existing plugins are listed

---

### US-SW-007: Test Suite Updates
**Project**: specweave
**As a** SpecWeave contributor
**I want** the test suite to reflect the new `suggestOnly: true` default
**So that** tests validate consent-first behavior and catch regressions

**Acceptance Criteria**:
- [ ] **AC-US7-01**: Given existing unit tests for `llm-plugin-detector.ts`, when the default behavior assertions are checked, then approximately 14 assertions are flipped from expecting auto-install to expecting suggest-only
- [ ] **AC-US7-02**: Given the test suite, when new consent-flow tests are added, then they cover: suggestion display format, once-per-session dedup, explicit opt-out (`suggestOnly: false`) still auto-installs, and LSP guard behavior
- [ ] **AC-US7-03**: Given all test updates, when `npx vitest run` is executed, then all tests pass with no regressions

## Out of Scope

- Changing the `--force --yes` CLI flags themselves (they remain for explicit opt-in via `suggestOnly: false`)
- Adding a "don't suggest this again" persistent preference
- Degraded/fallback LSP mode when plugins are not installed (existing `specweave lsp` CLI is sufficient)
- Creating the 8 phantom plugins that are being removed from marketplace
- UI/dashboard changes (this is CLI-only)

## Technical Notes

### Key Files
- **Shell hook**: `repositories/anton-abyzov/specweave/plugins/specweave/hooks/user-prompt-submit.sh` (2000+ lines)
- **LLM detector**: `repositories/anton-abyzov/specweave/src/core/lazy-loading/llm-plugin-detector.ts`
- **Types**: `repositories/anton-abyzov/specweave/src/core/config/types.ts`
- **Config schema**: `repositories/anton-abyzov/specweave/src/core/schemas/specweave-config.schema.json`
- **Marketplace**: `repositories/anton-abyzov/vskill/.claude-plugin/marketplace.json`
- **Tests**: `repositories/anton-abyzov/specweave/tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`

### Cross-Repo Coordination
This increment spans two repos in the umbrella:
1. **specweave** — hook logic, LLM detector, types, schema, tests (US-SW-001 through US-SW-004, US-SW-006, US-SW-007)
2. **vskill** — marketplace.json cleanup (US-VK-005)

### Backward Compatibility
- All existing projects get the new `suggestOnly: true` default immediately
- Users who want auto-install can explicitly set `suggestOnly: false`
- No migration needed; the default flip is the entire mechanism

## Success Metrics

- Zero plugins auto-installed without consent on fresh projects
- LSP plugins blocked by `suggestOnly` guard when flag is true
- Marketplace.json entries match actual plugin directories (4 plugins, not 12)
- All existing and new tests pass (`npx vitest run`)
