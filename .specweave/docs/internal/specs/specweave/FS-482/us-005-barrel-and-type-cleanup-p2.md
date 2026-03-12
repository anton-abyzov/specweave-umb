---
id: US-005
feature: FS-482
title: "Barrel and Type Cleanup (P2)"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** maintainer."
project: specweave
external:
  github:
    issue: 1532
    url: "https://github.com/anton-abyzov/specweave/issues/1532"
---

# US-005: Barrel and Type Cleanup (P2)

**Feature**: [FS-482](./FEATURE.md)

**As a** maintainer
**I want** unused init types and barrel exports cleaned up
**So that** the codebase is not cluttered with dead code from removed init flows

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given `types.ts`, when inspected, then `ProjectMaturity` and `RepositoryHosting` types (and REPO_FETCH_LIMITS constant) are removed
- [x] **AC-US5-02**: Given `index.ts` barrel, when inspected, then exports for `setupRepositoryHosting`, `promptTestingConfig`, `promptTranslationConfig`, `promptBrownfieldAnalysis`, `promptDeepInterviewConfig`, `promptQualityGatesConfig`, `promptAndRunExternalImport`, and their associated types are removed
- [x] **AC-US5-03**: Given `index.ts` barrel, when inspected, then `detectProvider` is exported from `./provider-detection.js`
- [x] **AC-US5-04**: Given the full test suite (`npx vitest run`), when run after all removals, then no tests fail due to missing imports or broken references
- [x] **AC-US5-05**: Given `npm run build`, when run after all changes, then TypeScript compiles cleanly with zero errors

---

## Implementation

**Increment**: [0482-simplify-init](../../../../../increments/0482-simplify-init/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-013**: Clean index.ts barrel exports
- [x] **T-014**: Simplify config.json.template
- [x] **T-015**: Add deprecation warning to resolve-structure.ts
- [x] **T-016**: Rewrite init.test.ts and run full test suite
