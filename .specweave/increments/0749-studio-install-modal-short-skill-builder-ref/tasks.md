# Tasks: Studio install modal — use short skill-builder ref

## Task Notation

- `T-NNN`: Task ID
- `[ ]` not started · `[x]` completed
- Model hint: haiku (mechanical) · opus (judgment)
- TDD discipline: RED → GREEN → REFACTOR — test edits land BEFORE source edits

---

## Phase 1: RED — pin tests to the new short form (failing)

### T-001: Update InstallEngineModal display-string assertion to short ref
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed | **Model**: haiku

**Description**: Edit the existing test that asserts the displayed install command for the `vskill` engine to expect the new short ref. This must fail against the current (long-form) source — that's the RED gate.

**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/InstallEngineModal.test.tsx`
- Line 114: replace `"vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder"` with `"vskill install anton-abyzov/vskill/skill-builder"`.

**Test Plan** (Given/When/Then):
- **Given** the InstallEngineModal is rendered with `engine="vskill"` and the source still has the long-form constant
- **When** I run `npx vitest run src/eval-ui/src/components/__tests__/InstallEngineModal.test.tsx`
- **Then** the assertion at line 114 FAILS with a string-mismatch diff showing long-vs-short

**Verify**: `npx vitest run src/eval-ui/src/components/__tests__/InstallEngineModal.test.tsx` reports 1 failure on the updated assertion (RED achieved).

---

### T-002: Update install-engine-routes argv assertion to short ref
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed | **Model**: haiku

**Description**: Edit the existing route test that asserts the `vskill` engine's spawned argv to expect the new short ref. Must fail against current source.

**File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/install-engine-routes.test.ts`
- Line 251: replace `"anton-abyzov/vskill/plugins/skills/skills/skill-builder"` with `"anton-abyzov/vskill/skill-builder"`.

**Test Plan** (Given/When/Then):
- **Given** the install-engine route handler is invoked with `{ engine: "vskill" }` and the source still has the long-form argv
- **When** I run `npx vitest run src/eval-server/__tests__/install-engine-routes.test.ts`
- **Then** the assertion at line 251 FAILS with an array-element diff showing long-vs-short

**Verify**: `npx vitest run src/eval-server/__tests__/install-engine-routes.test.ts` reports 1 failure on the updated assertion (RED achieved).

---

## Phase 2: GREEN — apply source change (tests pass)

### T-003: Update InstallEngineModal source constant to short ref
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed | **Model**: haiku

**Description**: Replace the hardcoded long-form display string in `COMMAND_BY_ENGINE.vskill` with the short form. No other change to the file.

**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/InstallEngineModal.tsx`
- Line 17: replace `"vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder"` with `"vskill install anton-abyzov/vskill/skill-builder"`.

**Test Plan** (Given/When/Then):
- **Given** T-001 has been applied (test now expects short form)
- **When** I run `npx vitest run src/eval-ui/src/components/__tests__/InstallEngineModal.test.tsx`
- **Then** the previously-failing assertion at line 114 PASSES; full file passes

**Verify**: vitest file passes 100%.

---

### T-004: Update install-engine-routes source argv to short ref
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed | **Model**: haiku

**Description**: Replace the long-form argv element in `INSTALL_COMMANDS.vskill.args` with the short form. No other change to the file.

**File**: `repositories/anton-abyzov/vskill/src/eval-server/install-engine-routes.ts`
- Line 55: replace `"anton-abyzov/vskill/plugins/skills/skills/skill-builder"` with `"anton-abyzov/vskill/skill-builder"`.

**Test Plan** (Given/When/Then):
- **Given** T-002 has been applied (test now expects short form)
- **When** I run `npx vitest run src/eval-server/__tests__/install-engine-routes.test.ts`
- **Then** the previously-failing assertion at line 251 PASSES; full file passes

**Verify**: vitest file passes 100%.

---

### T-005: Run the full vskill test suite
**User Story**: US-001, US-002 | **Satisfies ACs**: (regression guard) | **Status**: [x] completed (17/17 on changed files; pre-existing unrelated failures in submit/update/SSE-real-wire tests, tracked by 0690) | **Model**: haiku

**Description**: Confirm no other test in the vskill repo depended on the long-form string.

**Test Plan** (Given/When/Then):
- **Given** all four edits (T-001..T-004) are applied
- **When** I run `npx vitest run` from `repositories/anton-abyzov/vskill/`
- **Then** the suite passes with the same pass count as before the increment (modulo the two updated assertions)

**Verify**: full vitest suite green; no new failures.

---

## Phase 3: REFACTOR — verify no other long-form occurrences in shippable code

### T-006: Grep for long-form leftovers in source/test/e2e
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 (success-criteria check) | **Status**: [x] completed (0 matches in src/ + e2e/; test/ doesn't exist — tests are colocated as __tests__/) | **Model**: haiku

**Description**: Confirm the long form is gone from anywhere that ships or asserts. Coverage/dist/node_modules are fine to leave.

**Test Plan** (Given/When/Then):
- **Given** all source + test edits are applied
- **When** I run `grep -rn "anton-abyzov/vskill/plugins/skills/skills/skill-builder" repositories/anton-abyzov/vskill/src repositories/anton-abyzov/vskill/test repositories/anton-abyzov/vskill/e2e 2>/dev/null`
- **Then** the command returns 0 matches (CHANGELOG, README, .gitignore, marketplace.json comments are fine — those are not displayable command sources)

**Verify**: grep exits non-zero (no matches) for the listed paths.

---

## Phase 4: VERIFY — real install end-to-end

### T-007: Manual install verification via vskill studio
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed (real install via `vskill install anton-abyzov/vskill/skill-builder` succeeded: SKILL.md fetched, security scan 100/100 PASS, installed to /tmp/vskill-test-install/.claude/skills/skill-builder, SHA 13e597dae66c0c80836b0a6f2888e3dd0f33edb68340be161b885888854be2c3) | **Model**: opus

**Description**: Build vskill locally, run `vskill studio`, click Install on the VSkill skill-builder authoring engine, click Run install, verify the SSE stream completes successfully and skill-builder gets installed to disk.

**Implementation Details**:
1. From `repositories/anton-abyzov/vskill/`, run `npm run build`.
2. From a temp directory: `npx /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill studio` (or equivalent local-link invocation).
3. Open the Studio UI, navigate to the skill creation flow, click Install next to "VSkill skill-builder".
4. Confirm the modal displays `$ vskill install anton-abyzov/vskill/skill-builder` (no `plugins/skills/skills`).
5. Click "Run install" → wait for the SSE stream → observe the green "✓ VSkill skill-builder installed" success stage.
6. Confirm `~/.agents/skills/skill-builder/SKILL.md` (or the agent-detected install location) exists.

**Test Plan** (Given/When/Then):
- **Given** the locally-built vskill with this increment's changes is running and a fresh shell with no pre-installed skill-builder
- **When** I trigger Install → Run install from the Studio modal for the `vskill` engine
- **Then** the SSE stream completes with `success`, the modal shows the green checkmark, and skill-builder's `SKILL.md` is present in the installed-skills directory

**Verify**: Manual sign-off in this task's checkbox after a successful install run. Capture any stderr in the report folder if it fails.

**Fallback** (if Studio can't be launched in the test environment): run `vskill install anton-abyzov/vskill/skill-builder` directly in a shell and confirm a successful install with the same artifact check.

---

## Summary

- **Total tasks**: 7
- **Source files changed**: 2 (InstallEngineModal.tsx, install-engine-routes.ts)
- **Test files changed**: 2 (InstallEngineModal.test.tsx, install-engine-routes.test.ts)
- **New files**: 0
- **Lines of source delta**: ~2 (one string per file)
- **Lines of test delta**: ~2 (one assertion per file)
- **Risk**: low — string-only change, parity tests in place, real-install gate at the end
