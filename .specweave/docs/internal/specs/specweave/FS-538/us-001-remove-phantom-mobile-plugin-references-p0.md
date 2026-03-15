---
id: US-001
feature: FS-538
title: Remove Phantom Mobile Plugin References (P0)
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
tldr: "**As a** SpecWeave user with a mobile project."
project: specweave
external_tools:
  ado:
    id: 194
  jira:
    key: SWE2E-278
---

# US-001: Remove Phantom Mobile Plugin References (P0)

**Feature**: [FS-538](./FEATURE.md)

**As a** SpecWeave user with a mobile project
**I want** project detection to report only installable plugins
**So that** auto-install does not attempt to install non-existent plugins

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a React Native project (has `react-native` in package.json dependencies), when project-detector runs, then the result has `type: 'react-native'` and `plugins: []`
- [x] **AC-US1-02**: Given an Expo project (has `expo` in package.json dependencies), when project-detector runs, then the result has `type: 'expo'` and `plugins: []`
- [x] **AC-US1-03**: Given an iOS project (has `.xcodeproj` or `Podfile`), when project-detector runs, then the result has `type: 'ios'` and `plugins: []`
- [x] **AC-US1-04**: Given an Android project (has `build.gradle` containing `com.android`), when project-detector runs, then the result has `type: 'android'` and `plugins: []`
- [x] **AC-US1-05**: Given a Java/Spring project with `build.gradle` that does NOT contain `com.android`, when project-detector runs, then Android detection does not match

---

## Implementation

**Increment**: [0538-mobile-detect-test-fix](../../../../../increments/0538-mobile-detect-test-fix/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
