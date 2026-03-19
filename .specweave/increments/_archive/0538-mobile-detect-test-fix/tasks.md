# Tasks: Fix Mobile Project Detection Phantom Plugin References and Add Tests

**Increment**: 0538-mobile-detect-test-fix
**Tracks**: US-001, US-002, US-003
**Execution**: Parallelizable — Track A (T-001 to T-003: source fixes) and Track B (T-006 to T-008: new test files) can run concurrently. T-004/T-005 must precede T-007.

---

## US-001: Remove Phantom Mobile Plugin References

### T-001: Remove phantom `mobile` plugin from React Native and Expo detection rules
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
**Test**: Given `project-detector.ts` mobile detection rules → When `plugins: ['mobile']` is replaced with `plugins: []` for react-native and expo → Then `grep -r "plugins.*mobile" src/` returns no results for those rules

Before editing, run `grep -r "plugins.*\['mobile'\]" tests/` to confirm no existing test assertions will break. Then edit `src/core/lazy-loading/project-detector.ts` lines 262-271 to set `plugins: []` for both `react-native` and `expo` rules.

---

### T-002: Remove phantom `mobile` plugin from iOS detection rule
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] Completed
**Test**: Given a project with a `Podfile` at root → When project-detector runs → Then result has `type: 'ios'` and `plugins: []` (no `mobile` reference)

Edit `src/core/lazy-loading/project-detector.ts` lines 272-276: set `plugins: []` for the `ios` rule.

---

### T-003: Fix Android detection — replace bare `fileExists` with `fileContains` and clear phantom plugin
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [x] Completed
**Test**: Given `build.gradle` containing `com.android.application` → When project-detector runs → Then `type: 'android'`, `plugins: []`. Given `build.gradle` without `com.android` (Spring/Java project) → When project-detector runs → Then the android rule does NOT match.

Edit `src/core/lazy-loading/project-detector.ts` lines 277-281 to:
```typescript
{
  type: 'android',
  plugins: [],
  detect: (p) =>
    dirExists(p, 'android') ||
    fileContains(p, 'build.gradle', 'com.android') ||
    fileContains(p, 'build.gradle.kts', 'com.android'),
},
```

---

## US-002: Add Mobile Keywords to Auto-Install Component Mapping

### T-004: Add React Native and Expo keyword entries to COMPONENT_MAPPING
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given `COMPONENT_MAPPING` is imported → When `'react native'`, `'react-native'`, and `'expo'` keys are looked up → Then each returns `{ skills: ['frontend'], agents: [] }`

Edit `src/utils/auto-install.ts` to append after the existing Integration detection block (before closing `}`):
```typescript
// Mobile detection
'react native':  { skills: ['frontend'], agents: [] },
'react-native':  { skills: ['frontend'], agents: [] },
'expo':          { skills: ['frontend'], agents: [] },
'ios':           { skills: [], agents: [] },
'android':       { skills: [], agents: [] },
'mobile':        { skills: [], agents: [] },
'app store':     { skills: [], agents: [] },
'play store':    { skills: [], agents: [] },
```

---

### T-005: Verify `analyzeUserIntent` deduplication handles overlapping mobile keywords
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04
**Status**: [x] Completed
**Test**: Given a prompt "build a react native ios app" → When `analyzeUserIntent` runs → Then `frontend` skill appears exactly once and no `mobile` phantom plugin appears in the result

Read `analyzeUserIntent` in `src/utils/auto-install.ts`. If skill deduplication is already `Set`-based, confirm and document. If not, add `Set`-based dedup before returning. No change needed if already correct — mark task complete after verifying.

---

## US-003: Comprehensive Test Coverage for Mobile Detection Pipeline

### T-006: Write unit tests for all mobile detection rules in project-detector
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05
**Status**: [x] Completed
**Test**: Given `tests/unit/core/lazy-loading/project-detector-mobile.test.ts` exists → When `npx vitest run tests/unit/core/lazy-loading/project-detector-mobile.test.ts` executes → Then all 12 test cases pass

Create `tests/unit/core/lazy-loading/project-detector-mobile.test.ts`. Mirror the `vi.hoisted()` + `vi.mock()` ESM pattern used in `lazy-loading-vskill.test.ts`. Mock `fs` functions (`existsSync`, `readFileSync`, `readdirSync`). Import and call the detection array or exported `detectProjectType` function directly.

Test cases (one `it()` per row):

| # | Scenario | Expected type | Expected plugins |
|---|----------|---------------|-----------------|
| 1 | package.json has `react-native` dep | `react-native` | `[]` |
| 2 | `metro.config.js` exists | `react-native` | `[]` |
| 3 | No React Native markers | not detected | — |
| 4 | package.json has `expo` dep | `expo` | `[]` |
| 5 | `app.json` exists | `expo` | `[]` |
| 6 | `ios/` directory exists | `ios` | `[]` |
| 7 | `Podfile` exists | `ios` | `[]` |
| 8 | `build.gradle` contains `com.android` | `android` | `[]` |
| 9 | `build.gradle.kts` contains `com.android` | `android` | `[]` |
| 10 | `build.gradle` exists but lacks `com.android` | NOT android | — |
| 11 | `build.gradle` is empty / fileContains returns false | graceful skip | — |
| 12 | Both `expo` and `react-native` in package.json — Expo rule wins (runs first) | `expo` | `[]` |

---

### T-007: Extend auto-install unit tests with mobile keyword coverage
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [x] Completed
**Test**: Given `tests/unit/utils/auto-install.test.ts` extended with a `describe('COMPONENT_MAPPING - mobile keywords')` block → When `npx vitest run tests/unit/utils/auto-install.test.ts` executes → Then all 10 new assertions pass

Append to `tests/unit/utils/auto-install.test.ts` (existing mock scaffolding already handles imports):

```typescript
describe('COMPONENT_MAPPING - mobile keywords', () => {
  it('maps "react native" to frontend skill', () => {
    expect(COMPONENT_MAPPING['react native']).toEqual({ skills: ['frontend'], agents: [] });
  });
  it('maps "react-native" to frontend skill', () => {
    expect(COMPONENT_MAPPING['react-native']).toEqual({ skills: ['frontend'], agents: [] });
  });
  it('maps "expo" to frontend skill', () => {
    expect(COMPONENT_MAPPING['expo']).toEqual({ skills: ['frontend'], agents: [] });
  });
  it('maps "ios" to empty arrays', () => {
    expect(COMPONENT_MAPPING['ios']).toEqual({ skills: [], agents: [] });
  });
  it('maps "android" to empty arrays', () => {
    expect(COMPONENT_MAPPING['android']).toEqual({ skills: [], agents: [] });
  });
  it('maps "mobile" to empty arrays', () => {
    expect(COMPONENT_MAPPING['mobile']).toEqual({ skills: [], agents: [] });
  });
  it('maps "app store" to empty arrays', () => {
    expect(COMPONENT_MAPPING['app store']).toEqual({ skills: [], agents: [] });
  });
  it('maps "play store" to empty arrays', () => {
    expect(COMPONENT_MAPPING['play store']).toEqual({ skills: [], agents: [] });
  });
  it('installs frontend skill exactly once for combined "react native ios" prompt', () => {
    const result = analyzeUserIntent('build a react native ios app');
    const frontendCount = result.skills.filter((s) => s === 'frontend').length;
    expect(frontendCount).toBe(1);
    expect(result.skills).not.toContain('mobile');
  });
  it('no phantom mobile plugin in any mobile COMPONENT_MAPPING entry', () => {
    const mobileKeys = ['react native', 'react-native', 'expo', 'ios', 'android', 'mobile', 'app store', 'play store'];
    for (const key of mobileKeys) {
      expect(COMPONENT_MAPPING[key]).toBeDefined();
      expect(COMPONENT_MAPPING[key].skills).not.toContain('mobile');
    }
  });
});
```

---

### T-008: Write integration test for mobile detection pipeline with empty plugin resolution
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] Completed
**Test**: Given a temp directory with `package.json` containing `react-native` dependency → When the full lazy-loading detection pipeline runs against it → Then result has `type: 'react-native'`, `plugins: []`, no exception thrown, and `plugins` does not contain `'mobile'`

Create `tests/integration/lazy-loading/mobile-detection-pipeline.test.ts`.

Use `os.tmpdir()` + unique subfolder. Clean up in `afterEach`. Write real files to disk (no mocking) to exercise `fileExists`, `fileContains`, `dirExists` helpers end-to-end.

Scenarios:
1. `package.json` with `{"dependencies":{"react-native":"*"}}` → `type: 'react-native'`, `plugins: []`
2. `build.gradle` with `apply plugin: 'com.android.application'` → `type: 'android'`, `plugins: []`
3. `build.gradle` with `apply plugin: 'java'` (no `com.android`) → Android NOT in results; pipeline completes without error
4. No mobile markers at all → no mobile type in results, pipeline completes cleanly

All scenarios assert `plugins` does not contain `'mobile'`.

---

### T-009: Run full test suite and confirm no regressions and 95%+ mobile path coverage
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05
**Status**: [x] Completed
**Test**: Given all source changes and new test files are complete → When vitest runs across all three new/extended test files → Then zero failures and mobile detection paths in `project-detector.ts` hit >= 95% line coverage

Run in order:
```bash
cd repositories/anton-abyzov/specweave
npx vitest run tests/unit/core/lazy-loading/project-detector-mobile.test.ts
npx vitest run tests/unit/utils/auto-install.test.ts
npx vitest run tests/integration/lazy-loading/mobile-detection-pipeline.test.ts
npx vitest run --coverage --reporter=verbose 2>&1 | grep -A 8 "project-detector"
```

Fix any failures before marking this task complete. Do not mark `[x]` until all four commands exit 0.
