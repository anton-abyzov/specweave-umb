# Tasks: Studio Skill Version Display — Fallback & Consistency

## Task Notation

- `[T-NN]`: Task ID
- `[ ]`: Not started · `[x]`: Completed
- TDD discipline: RED → GREEN → REFACTOR
- All paths are relative to `repositories/anton-abyzov/vskill/` unless noted

---

### T-001: Write resolver unit tests (RED)
**User Story**: US-001, US-002, US-005 | **Satisfies ACs**: AC-US1-02, AC-US2-01, AC-US2-02, AC-US2-03, AC-US5-01 | **Status**: [x] Completed

**Description**: Write failing unit tests for `resolveSkillVersion` covering the full precedence chain and all edge cases. Tests must fail initially (function doesn't exist yet).

**Implementation Details**:
- Create `src/scanner/version-resolver.test.ts`
- Use Vitest (existing project framework)
- Test cases (one `describe` block per precedence branch + edge cases)

**Test Plan**:
- **File**: `src/scanner/version-resolver.test.ts`
- **Tests**:
  - **TC-001**: Given frontmatter `"1.4.0"` and registry `"1.0.0"` and plugin `"2.3.0"`, When resolver runs, Then returns `{ version: "1.4.0", versionSource: "frontmatter" }`
  - **TC-002**: Given no frontmatter and registry `"1.0.0"` and plugin `"2.3.0"`, When resolver runs, Then returns `{ version: "1.0.0", versionSource: "registry" }`
  - **TC-003**: Given no frontmatter, no registry, plugin `"2.3.0"`, When resolver runs, Then returns `{ version: "2.3.0", versionSource: "plugin" }`
  - **TC-004**: Given no frontmatter, no registry, no plugin, When resolver runs, Then returns `{ version: "0.0.0", versionSource: "default" }`
  - **TC-005**: Given frontmatter `"0.1.0"` and registry `"1.0.0"` (gws scenario), When resolver runs, Then returns `{ version: "0.1.0", versionSource: "frontmatter" }` — author choice wins
  - **TC-006**: Given frontmatter `"not-semver"` and registry `"1.0.0"`, When resolver runs, Then returns `{ version: "1.0.0", versionSource: "registry" }` — invalid frontmatter falls through
  - **TC-007**: Given frontmatter `""` (empty string) and registry `null`, When resolver runs, Then returns `{ version: "0.0.0", versionSource: "default" }` — empty treated as absent

**Dependencies**: None
**Acceptance**: All 7 tests written and failing (red).

---

### T-002: Implement resolver + plugin.json cache (GREEN)
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US4-01, AC-US4-02 | **Status**: [x] Completed

**Description**: Implement `resolveSkillVersion` and `plugin-version-cache` so all T-001 tests pass.

**Implementation Details**:
- Create `src/scanner/version-resolver.ts` exporting `resolveSkillVersion(input): { version, versionSource }`
- Use existing semver validator (project already has one — search `isValidSemver`); if not, use `semver` npm package check
- Create `src/scanner/plugin-version-cache.ts` exporting `createPluginVersionCache()` returning `{ get(pluginDir): string | null }` using `Map<string, string|null>`
- Reuse the read pattern from `src/commands/marketplace.ts:50-66` (path join + readFileSync + JSON.parse + try/catch)
- Wire resolver into local scanner emit sites and into eval-server `/api/skills` handler (find via `grep -rn "version: coerceStringOrNull(r.version)" src/`)

**Test Plan**:
- All T-001 tests pass
- Add integration test: `src/scanner/scanner.integration.test.ts` (or extend existing) — fixture skill in plugin dir produces `versionSource: "plugin"` with cached read

**Dependencies**: T-001
**Acceptance**: T-001 tests green; new integration test green; `npx vitest run src/scanner` clean.

---

### T-003: Update SkillInfo type + normalizers
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] Completed

**Description**: Make `SkillInfo.version` required `string` (was nullable) and add `versionSource` field. Update `normalizeSkillInfo` and any callers that destructure `version` assuming it could be null.

**Implementation Details**:
- Edit `src/types.ts` — change `version?: string | null` → `version: string`; add `versionSource: 'frontmatter' | 'registry' | 'plugin' | 'default'`
- Edit `src/api.ts:226` (`normalizeSkillInfo`) — coerce `version` to string with `?? "0.0.0"` safety net; pass `versionSource` through with `?? "default"` default
- Run `npx tsc --noEmit` — fix every type error surfaced by the type tightening
- Audit: `grep -rn "skill\.version" src/ | head -50` — remove any `if (!skill.version)` dead checks

**Test Plan**:
- **File**: existing `src/api.test.ts` (or create if missing)
- **Tests**:
  - **TC-008**: Given a SkillInfo from server response with `version: null`, When `normalizeSkillInfo` runs, Then output has `version: "0.0.0"` and `versionSource: "default"`
  - **TC-009**: Given a SkillInfo with `version: "1.4.0"` and `versionSource: "frontmatter"`, When normalized, Then both pass through unchanged

**Dependencies**: T-002
**Acceptance**: `npx tsc --noEmit` passes; new tests green.

---

### T-004: Component tests for VersionBadge + SkillRow (RED)
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] Completed

**Description**: Write failing component tests asserting source-aware rendering and that the badge never returns null for a resolver output.

**Implementation Details**:
- Create or extend `src/eval-ui/src/components/VersionBadge.test.tsx`
- Use Vitest + @testing-library/react (existing project setup)

**Test Plan**:
- **File**: `src/eval-ui/src/components/VersionBadge.test.tsx`
- **Tests**:
  - **TC-010**: Given `version="1.4.0"` and `source="frontmatter"`, When rendered, Then text is `1.4.0`, no italic class, no `title` attribute
  - **TC-011**: Given `version="2.3.0"` and `source="plugin"`, When rendered, Then italic class present and `title` matches `/Inherited from .* plugin v2\.3\.0/`
  - **TC-012**: Given `version="1.0.0"` and `source="registry"`, When rendered, Then italic + `title` is `Inherited from registry`
  - **TC-013**: Given `version="0.0.0"` and `source="default"`, When rendered, Then italic + `title` is `No version declared`
  - **TC-014**: Given `version="0.0.0"` and `source="default"` (any falsy-looking version), When rendered, Then output is non-null DOM (no return null)
- **File**: `src/eval-ui/src/components/SkillRow.test.tsx`
- **Tests**:
  - **TC-015**: Given a skill with `version="0.0.0"` and `versionSource="default"`, When SkillRow renders, Then the badge element is present in the DOM (no conditional skip)

**Dependencies**: T-003
**Acceptance**: All 6 component tests written and failing.

---

### T-005: Update VersionBadge + SkillRow (GREEN)
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] Completed

**Description**: Make T-004 tests pass.

**Implementation Details**:
- Edit `src/eval-ui/src/components/VersionBadge.tsx`:
  - Remove the `if (!version || ...) return null` early-return at line 27-29
  - Add `source?: 'frontmatter' | 'registry' | 'plugin' | 'default'` prop (default `'default'`)
  - When `source !== 'frontmatter'`, apply italic style (Tailwind `italic` class or equivalent in current styling system) and set a `title` attribute with provenance text:
    - `'plugin'` → `Inherited from {pluginName ?? 'plugin'} v{version}` (if plugin name available, else generic)
    - `'registry'` → `Inherited from registry`
    - `'default'` → `No version declared`
- Edit `src/eval-ui/src/components/SkillRow.tsx:139-141`:
  - Drop the `{skill.version && (...)}` wrapper
  - Always render `<VersionBadge version={skill.version} source={skill.versionSource} size="sm" showPrefix={false} data-testid="skill-row-version" />`
- Re-run T-004 tests until green

**Test Plan**: All T-004 tests pass + no regressions in existing VersionBadge/SkillRow tests.

**Dependencies**: T-004
**Acceptance**: `npx vitest run src/eval-ui` green; build passes.

---

### T-006: Manual studio verification
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US5-03 | **Status**: [x] Completed

**Description**: End-to-end smoke test of the studio sidebar to confirm the visual outcome matches the spec.

**Implementation Details**:
- From repo root: `cd repositories/anton-abyzov/vskill && npm install && npm run build`
- `npx vskill studio` — opens `localhost:3162`
- Visit AVAILABLE list in sidebar

**Test Plan** (visual checklist):
- **TC-016**: Every skill row in AVAILABLE shows a version badge — no blanks. (AC-US1-01)
- **TC-017**: `gws` badge shows `0.1.0`, normal weight, no tooltip on hover. (AC-US2-01, AC-US3-01)
- **TC-018**: `obsidian-brain` badge shows `1.4.0`, normal weight, no tooltip. (AC-US3-01)
- **TC-019**: `architect`, `brainstorm`, `do`, `done` badges render in italic with hover tooltip text matching `/Inherited from .* plugin v\d+\.\d+\.\d+/` (likely SpecWeave plugin version). (AC-US3-02, AC-US4-01)
- **TC-020**: A skill outside any plugin and not in registry (synthetic — drop a stub SKILL.md without `version:` in `~/.claude/skills/test-skill-no-plugin/`) shows `0.0.0` italic with tooltip "No version declared". (AC-US1-03)
- **TC-021**: Reverting all code changes restores prior behavior — sidebar shows blanks for sw:* skills, no leftover state. (AC-US5-03 — verified mentally; do not actually revert)

**Dependencies**: T-005
**Acceptance**: All visual checks pass; screenshot/note captured in increment `reports/` for closure.

---

## Out-of-Scope (do NOT do in this increment)

- Modifying any existing SKILL.md files to add `version:` frontmatter
- Database backfill of `Skill.currentVersion` rows
- Changing `vskill-platform/src/lib/submission/publish.ts` 1.0.0 default
- Refactoring `marketplace.ts:50-66` plugin.json read pattern
- Adding new icons / design tokens for the version badge

## Test Stack

- Unit: Vitest (`*.test.ts`)
- Component: Vitest + @testing-library/react (`*.test.tsx`)
- E2E: Manual visual verification (T-006)

## Coverage Target

- Resolver: 100% branch coverage (small pure function)
- VersionBadge: 100% of branches (4 sources × normal/italic/tooltip)
- SkillRow conditional change: covered via TC-015
