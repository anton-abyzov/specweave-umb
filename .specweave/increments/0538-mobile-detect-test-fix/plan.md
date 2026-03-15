# Plan: Fix Mobile Project Detection Phantom Plugin References

## Overview

Targeted bugfix in two files (`project-detector.ts`, `auto-install.ts`) plus test additions. No new components, no architectural changes. All work stays within existing detection and auto-install patterns.

## Changes

### 1. project-detector.ts -- Remove phantom plugins and tighten Android rule

**File**: `src/core/lazy-loading/project-detector.ts` (lines 261-281)

Four detection rules change `plugins: ['mobile']` to `plugins: []`. Android detection replaces bare `fileExists(p, 'build.gradle')` with `fileContains(p, 'build.gradle', 'com.android')` (and adds `build.gradle.kts` variant per edge case in spec).

Before:
```typescript
{ type: 'react-native', plugins: ['mobile'], detect: ... }
{ type: 'expo',         plugins: ['mobile'], detect: ... }
{ type: 'ios',          plugins: ['mobile'], detect: ... }
{ type: 'android',      plugins: ['mobile'], detect: ... }
```

After:
```typescript
{ type: 'react-native', plugins: [], detect: (p) => packageJsonHas(p, 'react-native') || fileExists(p, 'metro.config.js') }
{ type: 'expo',         plugins: [], detect: (p) => packageJsonHas(p, 'expo') || fileExists(p, 'app.json') }
{ type: 'ios',          plugins: [], detect: (p) => dirExists(p, 'ios') || fileExists(p, 'Podfile') }
{ type: 'android',      plugins: [], detect: (p) => dirExists(p, 'android') || fileContains(p, 'build.gradle', 'com.android') || fileContains(p, 'build.gradle.kts', 'com.android') }
```

**Rationale**: No "mobile" plugin exists in marketplace.json. Mobile is a project TYPE, not a plugin. The `fileContains` check prevents Java/Spring Gradle projects from false-matching as Android.

### 2. auto-install.ts -- Add mobile keyword entries

**File**: `src/utils/auto-install.ts` (lines 18-65, COMPONENT_MAPPING)

Add 8 entries after the existing framework detection block:

```typescript
// Mobile detection
'react native': { skills: ['frontend'], agents: [] },
'react-native': { skills: ['frontend'], agents: [] },
'expo':         { skills: ['frontend'], agents: [] },
'ios':          { skills: [], agents: [] },
'android':      { skills: [], agents: [] },
'mobile':       { skills: [], agents: [] },
'app store':    { skills: [], agents: [] },
'play store':   { skills: [], agents: [] },
```

**Note**: `expo` key already absent from COMPONENT_MAPPING (no collision). React Native/Expo map to `frontend` skill since they use React. Pure platform keywords map to empty arrays -- no phantom plugins.

### 3. Tests

#### 3a. New unit test: `tests/unit/core/lazy-loading/project-detector-mobile.test.ts`

Tests for each mobile detection rule using existing test patterns (mock `fs` via `vi.hoisted()` + `vi.mock()`, call detection functions).

Test cases:
- React Native positive: package.json with `react-native` dep -> `type: 'react-native'`, `plugins: []`
- React Native positive: `metro.config.js` exists -> same result
- React Native negative: no matching files -> not detected
- Expo positive: package.json with `expo` dep -> `type: 'expo'`, `plugins: []`
- Expo positive: `app.json` exists -> same result
- iOS positive: `ios/` directory exists -> `type: 'ios'`, `plugins: []`
- iOS positive: `Podfile` exists -> same result
- Android positive: `build.gradle` containing `com.android` -> `type: 'android'`, `plugins: []`
- Android positive: `build.gradle.kts` containing `com.android` -> same result
- Android negative (false positive guard): `build.gradle` WITHOUT `com.android` -> not detected as android
- Empty/malformed `build.gradle` -> graceful skip
- Expo + React Native co-existing: Expo matches first (order-dependent)

#### 3b. Extend: `tests/unit/utils/auto-install.test.ts`

Add test block for each new mobile keyword entry:
- Each keyword maps to expected `{ skills, agents }` values
- "react native" + "ios" prompt -> frontend installed once, no duplicates, no phantom plugins

#### 3c. New integration test: `tests/integration/lazy-loading/mobile-detection-pipeline.test.ts`

End-to-end test: create temp directory with mobile project markers, run full detection pipeline, verify:
- Correct `type` returned
- `plugins: []` (empty, not `['mobile']`)
- Pipeline completes without error when marketplace.json has no matching plugin for detected type

## Decision Log

| Decision | Rationale |
|----------|-----------|
| `plugins: []` not `plugins: ['frontend']` for mobile rules | Mobile detection identifies project TYPE for context; plugin installation handled separately by auto-install keywords and LLM detector |
| `fileContains` for both `.gradle` and `.gradle.kts` | Kotlin multiplatform projects use `.kts` variant; spec edge case |
| React Native/Expo -> `frontend` skill in auto-install | These frameworks use React; the frontend skill covers them |
| Pure platform keywords -> empty arrays | No phantom plugins; future mobile-specific skills can be added later |
| No ADR needed | No architectural changes; fix operates entirely within existing patterns |

## Risks

- Existing tests may assert `plugins: ['mobile']` -- search before changing (low risk, mitigated by grep before edit)
- `build.gradle.kts` variant adds one extra `fileContains` call per detection run -- negligible I/O impact since `existsSync` short-circuits when file absent

## Domain Delegation

No domain skills needed. This is a pure TypeScript bugfix + test increment in the specweave CLI. Standard Vitest patterns apply.
