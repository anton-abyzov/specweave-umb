# Tasks: Fix install tracking callback

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex)

## Phase 1: Platform Endpoint Fix

### T-001: Add decodeURIComponent to installs route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] Completed

**Description**: Apply `decodeURIComponent()` to the `name` URL parameter in the POST handler before using it for DB lookup.

**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[name]/installs/route.ts`

**Implementation**:
- Change `const { name: skillName } = await params;` to `const { name: rawName } = await params; const skillName = decodeURIComponent(rawName);`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[name]/installs/__tests__/route.test.ts`
- **Tests**:
  - **TC-001**: URL-encoded skill name is decoded before DB lookup
    - Given a POST request with URL-encoded skill name `my%40skill`
    - When the handler processes the request
    - Then `findUnique` is called with decoded name `my@skill`

**Dependencies**: None

---

### T-002: Add test for URL-encoded skill name
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] Completed

**Description**: Add unit test verifying URL-encoded names are decoded on the platform endpoint.

**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[name]/installs/__tests__/route.test.ts`

**Test Plan**:
- **Tests**:
  - **TC-002**: Encoded name `my%40skill` decoded to `my@skill` for DB lookup
    - Given mock DB returns skill for name `my@skill`
    - When POST is called with params `{ name: "my%40skill" }`
    - Then `findUnique` receives `{ where: { name: "my@skill" } }`
    - And response is 200 `{ ok: true }`

**Dependencies**: T-001

## Phase 2: CLI Fixes

### T-003: Add reportInstall to installPluginDir
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] Completed

**Description**: Add `reportInstall(pluginName).catch(() => {})` call at the end of `installPluginDir()` after the lockfile write.

**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Implementation**:
- Add `reportInstall(pluginName).catch(() => {});` after line ~677 (after lockfile write, before summary print)

**Dependencies**: None

---

### T-004: Add reportInstall to installRepoPlugin
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] Completed

**Description**: Add `reportInstall(pluginName).catch(() => {})` call at the end of `installRepoPlugin()` after the lockfile write.

**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Implementation**:
- Add `reportInstall(pluginName).catch(() => {});` after line ~1088 (after lockfile write, before summary print)

**Dependencies**: None

---

### T-005: Remove reportInstall from tryNativeClaudeInstall
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] Completed

**Description**: Remove `reportInstall(pluginName).catch(() => {})` from `tryNativeClaudeInstall()` to prevent double-reporting (the parent `installPluginDir` now handles it via T-003).

**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Implementation**:
- Remove line 189: `reportInstall(pluginName).catch(() => {});`

**Dependencies**: T-003 (must add to parent before removing from child)

---

### T-006: Fix installFromRegistry to use canonical name
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] Completed

**Description**: Change `reportInstall(skillName)` to `reportInstall(detail.name)` in `installFromRegistry()` so the canonical registry name is sent instead of user input.

**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Implementation**:
- Change line 1479: `reportInstall(skillName).catch(() => {});` to `reportInstall(detail.name).catch(() => {});`

**Dependencies**: None

## Phase 3: Verification

### T-007: Run platform tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] Completed

**Description**: Run vskill-platform test suite to verify all tests pass including the new URL-decoding test.

**Test Plan**:
- Run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/api/v1/skills/\\[name\\]/installs`
- All existing tests pass
- New URL-encoding test passes

**Dependencies**: T-001, T-002

---

### T-008: Verify CLI changes compile
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02 | **Status**: [x] Completed

**Description**: Run TypeScript compilation on vskill CLI to verify no type errors from the changes.

**Test Plan**:
- Run: `cd repositories/anton-abyzov/vskill && npx tsc --noEmit`
- No type errors

**Dependencies**: T-003, T-004, T-005, T-006
