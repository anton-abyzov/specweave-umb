---
increment: 0428-plugin-install-reliability
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001, T-003]
  US-002: [T-004]
  US-003: [T-002, T-005]
  ALL: [T-006]
total_tasks: 6
completed_tasks: 0
---

# Tasks: Fix vskill plugin install: stale temp dirs, missing prompts, confusing errors

## User Story: US-001 - Fix plugin install reliability

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 2 total, 0 completed

### T-001: Fix registerMarketplace() return type and add deregisterMarketplace

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/utils/claude-cli.ts`

**Test Plan**:
- **Given** registerMarketplace is called and succeeds **When** checking result **Then** returns `{ success: true }`
- **Given** registerMarketplace is called and fails **When** checking result **Then** returns `{ success: false, stderr: "error message" }`
- **Given** deregisterMarketplace is called **When** marketplace exists **Then** calls `claude plugin marketplace remove` and returns true
- **Given** listMarketplaces is called **When** output is `"url1\nurl2"` **Then** returns `["url1", "url2"]`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/utils/claude-cli.test.ts`
   - `testRegisterMarketplaceSuccess()`: Returns `{ success: true }` on zero exit
   - `testRegisterMarketplaceFailure()`: Returns `{ success: false, stderr }` on non-zero exit
   - `testDeregisterMarketplace()`: Calls remove subcommand and returns true
   - `testListMarketplaces()`: Splits newline-delimited stdout into array
   - **Coverage Target**: 95%

**Implementation**:
1. Change `registerMarketplace()` return type to `{ success: boolean; stderr?: string }`
2. Capture stderr in the failure branch and include in result
3. Add `deregisterMarketplace(url: string): Promise<boolean>` running `claude plugin marketplace remove <url>`
4. Add `listMarketplaces(): Promise<string[]>` running `claude plugin marketplace list` and splitting stdout
5. Export new functions from the module
6. Run `npx vitest run src/utils/claude-cli.test.ts`

---

### T-003: Fix temp directory fallback in tryNativeClaudeInstall()

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Test Plan**:
- **Given** marketplacePath is in `os.tmpdir()` and no gitUrl **When** tryNativeClaudeInstall called **Then** returns false with warning
- **Given** registerMarketplace fails first time **When** retrying after deregister **Then** succeeds on second attempt
- **Given** registerMarketplace fails both times **When** all retries exhausted **Then** returns false with stderr shown

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/commands/add.test.ts`
   - `testTmpDirFallbackReturnsEarly()`: Detects temp path and returns false
   - `testRetryAfterDeregisterSucceeds()`: Deregisters then registers again successfully
   - `testAllRetriesExhausted()`: Returns false after two failures
   - **Coverage Target**: 90%

**Implementation**:
1. Detect if `marketplacePath` starts with `os.tmpdir()` in `tryNativeClaudeInstall()`
2. If temp dir and no `gitUrl`, log warning and return false immediately
3. On `registerMarketplace()` failure, call `deregisterMarketplace()` then retry once
4. Display `result.stderr` in dim text when both attempts fail
5. Run `npx vitest run src/commands/add.test.ts`

---

## User Story: US-002 - Add single-plugin confirmation

**Linked ACs**: AC-US2-01, AC-US2-02
**Tasks**: 1 total, 0 completed

### T-004: Add single-plugin confirmation in installMarketplaceRepo()

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Test Plan**:
- **Given** single-plugin marketplace in TTY **When** user confirms **Then** plugin is installed
- **Given** single-plugin marketplace with `--yes` **When** auto-confirmed **Then** plugin is installed without prompt
- **Given** single-plugin marketplace in TTY **When** user declines **Then** installation is aborted

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/commands/add.test.ts`
   - `testSinglePluginConfirmYes()`: Mocks TTY confirm true, asserts install called
   - `testSinglePluginAutoYes()`: Passes `--yes` flag, no prompt, install called
   - `testSinglePluginConfirmNo()`: Mocks TTY confirm false, asserts install not called
   - **Coverage Target**: 90%

**Implementation**:
1. After resolving a marketplace with exactly one plugin, check `process.stdout.isTTY`
2. If TTY and not `--yes`, prompt: `Install plugin "<name>" from <source>? (y/N)`
3. Parse user input; abort with message if declined
4. If `--yes` or non-TTY, skip prompt and proceed
5. Run `npx vitest run src/commands/add.test.ts`

---

## User Story: US-003 - Improve error messages and validation

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 2 total, 0 completed

### T-002: Add validateMarketplace() function

**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/marketplace/marketplace.ts`, `repositories/anton-abyzov/vskill/src/marketplace/index.ts`

**Test Plan**:
- **Given** valid marketplace.json **When** validateMarketplace called **Then** returns `{ valid: true, pluginCount: N, name: "X" }`
- **Given** missing name field **When** validated **Then** returns `{ valid: false, error: "Missing 'name' field" }`
- **Given** empty plugins array **When** validated **Then** returns `{ valid: false, error: "No plugins defined" }`
- **Given** invalid JSON **When** validated **Then** returns `{ valid: false, error: "Invalid JSON: ..." }`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/marketplace/marketplace.test.ts`
   - `testValidMarketplace()`: Returns valid result with count and name
   - `testMissingName()`: Returns error for missing name
   - `testEmptyPlugins()`: Returns error for empty plugins array
   - `testInvalidJson()`: Returns error with parse message
   - **Coverage Target**: 95%

**Implementation**:
1. Define `ValidateResult` type: `{ valid: boolean; error?: string; pluginCount?: number; name?: string }`
2. Implement `validateMarketplace(raw: string): ValidateResult` in `marketplace.ts`
3. Parse JSON in try/catch; return error on parse failure
4. Check for required `name` string field; return error if missing
5. Check `plugins` is a non-empty array; return error if empty
6. On success return `{ valid: true, pluginCount: plugins.length, name }`
7. Export from `src/marketplace/index.ts`
8. Run `npx vitest run src/marketplace/marketplace.test.ts`

---

### T-005: Improve error messages

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Test Plan**:
- **Given** plugin not found in marketplace **When** error shown **Then** available plugins are listed
- **Given** registration fails with stderr **When** error shown **Then** stderr is displayed in dim text
- **Given** installPluginDir called **When** pre-install **Then** overview shows plugin name and source path

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/commands/add.test.ts`
   - `testPluginNotFoundListsAvailable()`: Error message includes available plugin names
   - `testRegistrationErrorShowsStderr()`: Dim-formatted stderr shown to user
   - `testInstallOverviewShown()`: Pre-install log includes name and path
   - **Coverage Target**: 85%

**Implementation**:
1. On plugin-not-found error, collect available plugin names from marketplace and append to error
2. When displaying registration failure, format `result.stderr` using chalk dim or equivalent
3. In `installPluginDir()`, log an overview line before install: `Installing "<name>" from <path>`
4. Run `npx vitest run src/commands/add.test.ts`

---

## Cross-Cutting: Update Tests

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 1 total, 0 completed

### T-006: Update tests for all changed modules

**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Files**:
- `repositories/anton-abyzov/vskill/src/utils/claude-cli.test.ts`
- `repositories/anton-abyzov/vskill/src/marketplace/marketplace.test.ts`
- `repositories/anton-abyzov/vskill/src/commands/add.test.ts`

**Test Plan**:
- **Given** updated registerMarketplace **When** tests run **Then** RegisterResult assertions pass
- **Given** new deregisterMarketplace **When** tests run **Then** new test cases pass
- **Given** new validateMarketplace **When** tests run **Then** validation test cases pass
- **Given** updated add.test.ts mocks **When** tests run **Then** all existing tests still pass with new mock shape

**Test Cases**:
1. **Integration**: All three test files
   - Update mock shapes for `registerMarketplace` to return `RegisterResult`
   - Add test cases for `deregisterMarketplace` and `listMarketplaces`
   - Add `validateMarketplace` test suite in `marketplace.test.ts`
   - Verify no regressions in `add.test.ts` after mock updates
   - **Coverage Target**: 90%

**Implementation**:
1. Update `claude-cli.test.ts` mocks to expect `{ success, stderr? }` shape
2. Add `deregisterMarketplace` and `listMarketplaces` test cases
3. Add full `validateMarketplace` test suite in `marketplace.test.ts`
4. Update `add.test.ts` mock for `registerMarketplace` to new return type
5. Run full suite: `npx vitest run` from vskill root
6. Confirm all tests pass with zero failures
