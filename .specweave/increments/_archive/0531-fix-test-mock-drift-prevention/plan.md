# Plan: Fix Test Mock Drift with Shared npm Constants

## Overview

Extract hardcoded npm registry URLs into a shared constants module at `src/utils/npm-constants.ts`, following the established `pricing-constants.ts` pattern. Both production code and test mocks import from this single source of truth, eliminating the class of bugs where mock strings silently drift from production.

## Architecture

### Module Design: `src/utils/npm-constants.ts`

```
Exports:
  NPM_REGISTRY_URL  = "https://registry.npmjs.org"     (const string)
  npmRegistryFlag()  -> "--registry https://registry.npmjs.org"  (helper fn)
```

**Why `src/utils/` not `src/constants/`**: No `src/constants/` directory exists. The precedent (`pricing-constants.ts`) lives in `src/utils/`. Creating a new top-level directory for one file adds unnecessary structure.

**Why a helper function**: Three of four production call sites use `--registry ${url}` (space-separated). The fourth (`package-installer.ts`) uses `--registry=${url}` (equals form) and will use the raw constant directly. One helper covers the common case without over-abstracting.

### Components

- **`src/utils/npm-constants.ts`**: Single source of truth for registry URL and CLI flag formatting
- **4 production files**: Consume constants instead of hardcoding
- **3 test files**: Consume same constants for mock construction

No new directories, no barrel exports, no config indirection.

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Testing**: Vitest
- **Constraint**: All imports must use `.js` extension

**Architecture Decision**: Place constants in `src/utils/` alongside `pricing-constants.ts` rather than creating a new `src/constants/` directory. This follows the existing codebase convention and avoids structural changes for a single file.

## Migration Map

### Production files (4 files)

| File | Current pattern | After |
|------|----------------|-------|
| `src/core/doctor/checkers/installation-health-checker.ts:527` | `` `${command} --registry https://registry.npmjs.org` `` | `` `${command} ${npmRegistryFlag()}` `` |
| `src/cli/commands/update.ts:843` | `` `${command} --registry https://registry.npmjs.org` `` | `` `${command} ${npmRegistryFlag()}` `` |
| `src/utils/docs-preview/package-installer.ts:66` | `'--registry=https://registry.npmjs.org'` | `` `--registry=${NPM_REGISTRY_URL}` `` |
| `src/core/fabric/discovery/npm-provider.ts:11` | `'https://registry.npmjs.org/-/v1/search'` | `` `${NPM_REGISTRY_URL}/-/v1/search` `` |

### Test files (3 files)

| File | Change |
|------|--------|
| `tests/unit/core/doctor/checkers/installation-health-checker.test.ts` | Import `npmRegistryFlag`, use in mock command match |
| `tests/unit/cli/commands/update.test.ts` | Import `npmRegistryFlag`, use in mock command match and expect |
| `tests/unit/cli/commands/update-robustness.test.ts` | Import `npmRegistryFlag`, use in assertion |

### Import path convention

All imports use `.js` extension per ESM/nodenext:
```typescript
import { NPM_REGISTRY_URL, npmRegistryFlag } from '../../utils/npm-constants.js';
```

Relative depth varies by importing file's position in the tree.

## Implementation Phases

### Phase 1: Create Constants Module (US-002)
- Create `src/utils/npm-constants.ts` with `NPM_REGISTRY_URL` constant and `npmRegistryFlag()` helper
- Write unit tests for the module (TDD: red then green)

### Phase 2: Fix TC-UH-02 and Migrate Production (US-001, US-003)
- Fix the immediate bug: correct mock in `installation-health-checker.test.ts`
- Replace hardcoded strings in all 4 production files with imported constants

### Phase 3: Migrate Test Mocks (US-004)
- Update mock command strings in all 3 test files to use shared constants
- Run full test suite to verify zero regressions

## Testing Strategy

- **TDD for constants module**: Write tests first for `NPM_REGISTRY_URL` value and `npmRegistryFlag()` return value
- **Regression**: Run full Vitest suite after each migration phase
- **Completeness check**: `grep -r "registry.npmjs.org" src/ tests/` must return zero hits in migrated files

## Technical Challenges

### Challenge 1: Varying flag formats across call sites
**Solution**: `npmRegistryFlag()` returns the space-separated `--registry URL` form (3 of 4 sites). The one `=` form site uses `NPM_REGISTRY_URL` directly with template literal.
**Risk**: Low. Both forms are covered by the two exports.

### Challenge 2: npm-provider.ts uses URL as API base, not CLI flag
**Solution**: Use `NPM_REGISTRY_URL` directly to construct the search endpoint URL. The constant is the base URL, not the flag -- it works for both CLI and HTTP contexts.

## No Domain Skill Delegation Needed

Single-file constants extraction in TypeScript/Node.js ESM. No frontend, backend service, or infrastructure changes. Standard refactoring -- no domain skills required.
