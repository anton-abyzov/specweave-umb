---
increment: 0538-mobile-detect-test-fix
title: Fix mobile project detection phantom plugin references and add tests
type: bugfix
priority: P1
status: completed
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Fix Mobile Project Detection Phantom Plugin References and Add Tests

## Problem Statement

The project-detector.ts module maps React Native, Expo, iOS, and Android project types to `plugins: ['mobile']`, but no "mobile" plugin exists in marketplace.json. This causes phantom plugin references that silently fail during auto-install. Additionally, `build.gradle` detection triggers false positives for Java/Spring projects that use Gradle but are not Android projects. Finally, auto-install.ts COMPONENT_MAPPING has zero mobile keyword entries, so mobile-related prompts never install any skills.

## Goals

- Eliminate phantom plugin references by removing non-existent plugin IDs from detection rules
- Prevent false positive Android detection for Java/Spring Gradle projects
- Register mobile keywords in auto-install so React Native/Expo prompts install relevant skills
- Achieve 95%+ unit test coverage for mobile detection paths and auto-install keyword mapping

## User Stories

### US-001: Remove Phantom Mobile Plugin References (P0)
**Project**: specweave

**As a** SpecWeave user with a mobile project
**I want** project detection to report only installable plugins
**So that** auto-install does not attempt to install non-existent plugins

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a React Native project (has `react-native` in package.json dependencies), when project-detector runs, then the result has `type: 'react-native'` and `plugins: []`
- [x] **AC-US1-02**: Given an Expo project (has `expo` in package.json dependencies), when project-detector runs, then the result has `type: 'expo'` and `plugins: []`
- [x] **AC-US1-03**: Given an iOS project (has `.xcodeproj` or `Podfile`), when project-detector runs, then the result has `type: 'ios'` and `plugins: []`
- [x] **AC-US1-04**: Given an Android project (has `build.gradle` containing `com.android`), when project-detector runs, then the result has `type: 'android'` and `plugins: []`
- [x] **AC-US1-05**: Given a Java/Spring project with `build.gradle` that does NOT contain `com.android`, when project-detector runs, then Android detection does not match

---

### US-002: Add Mobile Keywords to Auto-Install Component Mapping (P1)
**Project**: specweave

**As a** SpecWeave user describing a mobile project in a prompt
**I want** relevant keywords to be recognized by auto-install
**So that** React Native and Expo prompts install the frontend skill, and pure platform keywords are registered without installing phantom plugins

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a prompt containing "react native", when COMPONENT_MAPPING is checked, then it maps to `{ skills: ['frontend'], agents: [] }`
- [x] **AC-US2-02**: Given a prompt containing "expo", when COMPONENT_MAPPING is checked, then it maps to `{ skills: ['frontend'], agents: [] }`
- [x] **AC-US2-03**: Given a prompt containing any of "ios", "android", "mobile", "app store", "play store", when COMPONENT_MAPPING is checked, then it maps to `{ skills: [], agents: [] }`
- [x] **AC-US2-04**: Given a prompt containing "react native" and "ios", when auto-install runs, then it installs the frontend skill exactly once (no duplicates, no phantom plugins)

---

### US-003: Comprehensive Test Coverage for Mobile Detection Pipeline (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** unit and integration tests covering mobile detection rules, auto-install keywords, and pipeline graceful degradation
**So that** regressions in mobile project handling are caught before release

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given project-detector unit tests, then each mobile detection rule (React Native, Expo, iOS, Android) has at least one positive and one negative test case
- [x] **AC-US3-02**: Given project-detector unit tests, then the build.gradle false positive scenario (Java/Spring project with build.gradle lacking `com.android`) is covered
- [x] **AC-US3-03**: Given auto-install unit tests, then each new mobile keyword entry has a test verifying correct skill/agent mapping
- [x] **AC-US3-04**: Given an integration test, when a detected project type has no matching plugins in marketplace.json, then the pipeline completes without error and returns the correct project type with an empty plugins array
- [x] **AC-US3-05**: Given test coverage report, then mobile detection paths in project-detector.ts achieve 95%+ line coverage

## Out of Scope

- Creating an actual "mobile" plugin for marketplace.json
- Adding mobile-specific skills or agents (future increment)
- Changing the LLM detector mobile blocking logic (line 501 of llm-plugin-detector.ts) -- that block is correct
- Recursive build.gradle scanning in subdirectories

## Technical Notes

### Dependencies
- `src/core/lazy-loading/project-detector.ts` -- detection rules (lines 261-281)
- `src/utils/auto-install.ts` -- COMPONENT_MAPPING (lines 18-65)
- `src/core/lazy-loading/llm-plugin-detector.ts` -- LLM detector (no changes needed)
- `fileContains()` helper already exists in project-detector.ts

### Constraints
- Detection only checks root-level `build.gradle` via `fileExists()` -- no recursive scanning
- The `type` field already captures mobile project types; `plugins` field is strictly for installable marketplace plugins

### Architecture Decisions
- Mobile is a project TYPE, not a plugin -- `plugins: []` is correct for all mobile detections
- `fileContains(p, 'build.gradle', 'com.android')` replaces bare `fileExists(p, 'build.gradle')` for Android detection
- React Native and Expo keywords map to frontend skill since they use React; pure platform keywords map to empty arrays

## Non-Functional Requirements

- **Performance**: No impact -- detection still checks single root files, no new I/O operations added
- **Compatibility**: Must work on all platforms (Windows, macOS, Linux path formats)
- **Security**: N/A -- detection logic only, no user input reaches path resolution unsanitized

## Edge Cases

- **Java/Spring with build.gradle**: Must NOT trigger Android detection (fixed via `com.android` content check)
- **Kotlin multiplatform with build.gradle.kts**: Android detection should check both `build.gradle` and `build.gradle.kts` for `com.android` if both exist
- **Project with both React Native and Expo**: Detection should match the more specific type (Expo) since Expo check runs first
- **Empty or malformed build.gradle**: `fileContains` returns false on read error -- detection skips gracefully

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Existing tests rely on `plugins: ['mobile']` assertions | 0.3 | 3 | 0.9 | Search for existing test assertions before changing |
| build.gradle.kts not covered by `fileContains` check | 0.4 | 2 | 0.8 | Include `.kts` variant in detection rule |

## Success Metrics

- Zero phantom plugin references in project-detector mobile rules
- build.gradle false positive eliminated for Java/Spring projects
- 95%+ line coverage on mobile detection paths
- All new auto-install keywords have passing unit tests
