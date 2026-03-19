---
increment: 0542-vskill-plugin-auto-recommendation
title: vskill Plugin Auto-Recommendation
status: completed
priority: P1
type: feature
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# vskill Plugin Auto-Recommendation

## Problem Statement

When users write prompts that reference domains covered by vskill marketplace plugins (mobile deployment, Google Workspace, marketing, productivity, skill discovery), SpecWeave has no mechanism to suggest installing the relevant plugin. Users must already know the plugin exists and manually run `vskill install`. This creates a discoverability gap -- users miss capabilities that would directly help their current task.

## Goals

- Surface relevant vskill plugin suggestions inline when user prompts mention covered domains
- Maintain consent-first UX -- suggest only, never auto-install by default
- Avoid adding latency to the prompt submission path (regex-only, no LLM calls)
- Provide session-level deduplication so suggestions appear at most once per plugin per session

## User Stories

### US-001: Hook-Level Keyword Detection for vskill Plugins
**Project**: specweave
**As a** SpecWeave user
**I want** the user-prompt-submit hook to detect when my prompt mentions domains covered by available vskill plugins
**So that** I am informed about relevant plugins I have not yet installed

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a prompt containing "deploy ios app to testflight", when the hook processes the prompt and vskill `mobile` plugin is not in `vskill.lock`, then additionalContext includes a suggestion to install the `mobile` plugin with the exact command `vskill install anton-abyzov/vskill --plugin mobile`
- [x] **AC-US1-02**: Given a prompt containing "update google sheets report", when the hook processes the prompt and vskill `google-workspace` plugin is already in `vskill.lock`, then no suggestion for `google-workspace` appears in additionalContext
- [x] **AC-US1-03**: Given a prompt containing "post on linkedin and instagram", when the hook processes the prompt and vskill `marketing` plugin is not in `vskill.lock`, then the suggestion appears as a bullet with plugin name, skills provided (slack-messaging, social-media-posting), and install command
- [x] **AC-US1-04**: Given the keyword "ios" appearing inside a longer word (e.g., "curious"), when the hook processes the prompt, then no false-positive match occurs because short keywords (<5 chars) use word-boundary regex (`\bios\b`)
- [x] **AC-US1-05**: Given multi-word keywords like "google drive" or "social media", when the hook processes the prompt, then substring matching correctly detects them without requiring word boundaries

---

### US-002: Session-Level Suggestion Deduplication
**Project**: specweave
**As a** SpecWeave user
**I want** each vskill plugin suggestion to appear at most once per session
**So that** I am not repeatedly nagged about the same plugin across multiple prompts

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the `mobile` plugin was already suggested in the current session, when a subsequent prompt mentions "app-store-connect", then no duplicate suggestion for `mobile` appears in additionalContext
- [x] **AC-US2-02**: Given session dedup uses TMPDIR marker files (pattern `${TMPDIR:-/tmp}/specweave-vskill-suggested-{plugin}`), when the shell session ends, then marker files are naturally cleaned up and suggestions reset for the next session
- [x] **AC-US2-03**: Given a new shell session starts, when a prompt mentions "ios", then the `mobile` plugin suggestion appears again (markers from previous session are gone)

---

### US-003: Multi-Plugin Match Capping
**Project**: specweave
**As a** SpecWeave user
**I want** at most 3 vskill plugin suggestions per prompt
**So that** the additionalContext stays within the 3000-char budget and remains readable

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a prompt that triggers 4+ vskill plugins, when the hook processes it, then only the top 3 plugins by keyword match specificity are suggested
- [x] **AC-US3-02**: Given 2 plugins are matched, when the hook formats the suggestion block, then both are shown (cap only applies at 4+)
- [x] **AC-US3-03**: Given the suggestion block for 3 plugins, when measured, then total suggestion text is under 300 chars per plugin (900 chars total, well within 3000-char limit)

---

### US-004: LLM Detector Deny-List Update
**Project**: specweave
**As a** developer maintaining the LLM plugin detector
**I want** the Haiku prompt deny-list updated to reflect that vskill marketplace plugins exist but are handled separately
**So that** the LLM does not incorrectly tell users these plugins are unavailable

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the current deny-list says "DO NOT suggest: mobile, skills...", when updated, then the wording changes to indicate these are vskill marketplace plugins detected via keyword matching, not available as `sw-*` plugins
- [x] **AC-US4-02**: Given a VSKILL_PLUGIN_REGISTRY constant is added to `llm-plugin-detector.ts`, then it contains entries for all 5 plugins (mobile, google-workspace, marketing, productivity, skills) with their trigger keywords
- [x] **AC-US4-03**: Given a `detectVskillPlugins(prompt)` helper is exported, when called with "deploy ios app", then it returns `[{plugin: "mobile", matchedKeyword: "ios"}]`

---

### US-005: Project-Detector vskill Plugin Recommendations
**Project**: specweave
**As a** SpecWeave user working on a mobile project
**I want** the project-detector to recommend vskill plugins at session start based on project file signatures
**So that** I get plugin suggestions proactively, not just when I mention keywords

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a project with `Podfile` or `ios/` directory, when `detectProjectType()` runs, then the result includes `vskillPlugins: ["mobile"]`
- [x] **AC-US5-02**: Given a project with `react-native` in package.json, when `detectProjectType()` runs, then `vskillPlugins: ["mobile"]` is included
- [x] **AC-US5-03**: Given the `ProjectTypeResult` interface, when the `vskillPlugins` field is added, then it is typed as `string[]` and defaults to `[]`
- [x] **AC-US5-04**: Given vskill plugin `mobile` is already in `vskill.lock`, when the session-start hook checks project-detector results, then the `mobile` suggestion is suppressed

---

### US-006: Auto-Install Component Mapping for vskill Plugins
**Project**: specweave
**As a** developer extending the auto-install system
**I want** the COMPONENT_MAPPING in `auto-install.ts` to include a `vskillPlugin` field
**So that** intent analysis can distinguish between specweave skill installs and vskill plugin recommendations

**Acceptance Criteria**:
- [~] **AC-US6-01** [DROPPED - auto-install.ts is dead code]: Given COMPONENT_MAPPING entries for "ios", "android", "mobile", "app store", "react native", when updated, then each includes a `vskillPlugin: "mobile"` field
- [~] **AC-US6-02** [DROPPED - auto-install.ts is dead code]: Given the `analyzeUserIntent()` return type, when updated, then it includes `vskillPlugins: string[]`
- [~] **AC-US6-03** [DROPPED - auto-install.ts is dead code]: Given a prompt "deploy my ios app", when `analyzeUserIntent()` is called, then result includes `vskillPlugins: ["mobile"]`

---

### US-007: Detect-Intent CLI vskill Recommendations
**Project**: specweave
**As a** developer using the detect-intent CLI command
**I want** vskill plugin recommendations included in the detection result
**So that** tooling and scripts can programmatically access vskill suggestions

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given the `DetectIntentResult` interface, when updated, then it includes `vskillRecommendations?: {plugin: string, matchedKeyword: string, installCommand: string}[]`
- [x] **AC-US7-02**: Given `specweave detect-intent "deploy ios app to testflight"` is run and mobile plugin is not in vskill.lock, then JSON output includes `vskillRecommendations` with the mobile plugin entry
- [x] **AC-US7-03**: Given `specweave detect-intent "update react component"` is run and no vskill keywords match, then `vskillRecommendations` is absent or empty array

## Out of Scope

- Auto-installation of vskill plugins (suggest-only; auto-install when `suggestOnly: false` is a follow-up)
- Adding new vskill plugins to the registry (hardcoded for 5 known plugins)
- VSCode extension integration for vskill suggestions (CLI/hook only)
- Telemetry for vskill suggestion impressions
- Config toggles specific to vskill suggestions (uses existing `pluginAutoLoad.enabled` gate)

## Technical Notes

### Dependencies
- `vskill.lock` file format (checked via existing `check_plugin_in_vskill_lock()`)
- `vskill install anton-abyzov/vskill --plugin <name>` CLI command
- Existing `output_approve_with_context()` helper for additionalContext injection

### Constraints
- Consent-first: default is suggest-only
- No LLM latency: keyword regex in hook, not Haiku call
- Context budget: each plugin suggestion under 300 chars; max 3 per prompt
- Graceful degradation: if vskill CLI unavailable, still show command text
- Word-boundary regex for short keywords (<5 chars)

### Architecture Decisions
- TMPDIR session markers: `${TMPDIR:-/tmp}/specweave-vskill-suggested-{plugin}`, matching existing on-demand pattern
- Detection ordering: vskill regex runs BEFORE async LLM detect-intent
- Dual detection paths: hook keyword detection (per-prompt) AND project-detector (session-start), both check vskill.lock
- Registry as constant: hardcoded in hook (bash) and TypeScript (VSKILL_PLUGIN_REGISTRY), no config file

## Non-Functional Requirements

- **Performance**: Keyword detection adds < 5ms to hook execution (no LLM, no disk I/O beyond vskill.lock stat)
- **Compatibility**: macOS and Linux (bash 4+ for associative arrays)
- **Security**: No user input reaches command execution; suggestions are static text
- **Maintainability**: New plugin requires updating registry in 2 places (hook + TypeScript)

## Edge Cases

- **No vskill.lock file**: All plugins treated as not-installed; show suggestions for any match
- **vskill CLI not installed**: Still show install command text
- **Empty/malformed prompt**: No keywords match, no suggestions
- **Keyword inside code block or URL**: May false-positive (accepted; suggestion is informational only)
- **TMPDIR not writable**: Skip dedup silently; suggestion may repeat
- **additionalContext near limit**: Existing truncation guard handles overflow

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| False-positive matches on short keywords | 0.3 | 2 | 0.6 | Word-boundary regex for <5 char keywords |
| Bash 4+ associative arrays unavailable | 0.1 | 5 | 0.5 | Fallback to case/esac if needed |
| Registry goes stale as new plugins publish | 0.5 | 3 | 1.5 | Document update process; future auto-sync |
| Suggestions push additionalContext over limit | 0.2 | 4 | 0.8 | Cap at 3 suggestions; existing truncation |

## Success Metrics

- 80%+ of prompts mentioning covered domains produce a correct plugin suggestion
- Zero false-positives from short keywords inside longer words
- Suggestion text under 900 chars total (3 plugins x 300 chars)
- No measurable increase in hook latency (< 5ms overhead)
