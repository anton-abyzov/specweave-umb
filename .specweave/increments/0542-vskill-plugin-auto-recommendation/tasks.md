# Tasks: vskill Plugin Auto-Recommendation

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default)

---

## US-004: TypeScript Registry and detectVskillPlugins() Helper

> Dependency anchor — downstream tasks (US-005, US-006, US-007) import from this module.

### T-001: Add VSKILL_PLUGIN_REGISTRY and detectVskillPlugins() to llm-plugin-detector.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [ ] Not Started
**Test**: Given `llm-plugin-detector.ts` exports `VSKILL_PLUGIN_REGISTRY` and `detectVskillPlugins()`, when the module is imported in a Vitest test, then the registry contains exactly 5 entries (mobile, google-workspace, marketing, productivity, skills) and `detectVskillPlugins("deploy ios app")` returns `[{plugin: "mobile", matchedKeyword: "ios", installCommand: "vskill install anton-abyzov/vskill --plugin mobile"}]`

**File**: `src/core/lazy-loading/llm-plugin-detector.ts`

**Implementation Details**:
- Add `VskillPluginEntry` interface: `{ keywords: string[]; shortKeywords: string[]; description: string; installCommand: string; }`
- Add `VskillMatch` interface: `{ plugin: string; matchedKeyword: string; installCommand: string; }`
- Add exported `VSKILL_PLUGIN_REGISTRY: Record<string, VskillPluginEntry>` with all 5 plugins (mobile, google-workspace, marketing, productivity, skills) exactly as specified in plan.md
- Add exported `detectVskillPlugins(prompt: string): VskillMatch[]` — lowercase prompt, iterate registry, for shortKeywords use `\b<kw>\b` word-boundary regex, for keywords use case-insensitive substring; return first match per plugin; cap at 3 results sorted by matched keyword length descending
- Update `buildDetectionPrompt()` deny-list: remove `mobile, skills` from the "NOT available as plugins" line and add the vskill marketplace note as shown in plan.md

**Test File**: `src/core/lazy-loading/__tests__/llm-plugin-detector.vskill.test.ts`

**Test Cases**:
- **TC-001**: Given prompt `"deploy ios app to testflight"`, when `detectVskillPlugins()` is called, then returns array containing entry with `plugin: "mobile"` and `matchedKeyword: "ios"`
- **TC-002**: Given prompt `"I am curious about this feature"`, when `detectVskillPlugins()` is called, then returns `[]` (word-boundary prevents false positive on "ios" inside "curious")
- **TC-003**: Given prompt `"post on linkedin and update google sheets"`, when `detectVskillPlugins()` is called, then returns matches for both `marketing` and `google-workspace`
- **TC-004**: Given prompt `"update react component"`, when `detectVskillPlugins()` is called, then returns `[]`
- **TC-005**: Given a prompt matching 4 distinct plugins, when `detectVskillPlugins()` is called, then result length is exactly 3
- **TC-006**: Given `VSKILL_PLUGIN_REGISTRY`, when Object.keys() is inspected, then length is 5 and all 5 plugin names are present
- **TC-007**: Given updated deny-list text in `buildDetectionPrompt()`, when the prompt string is inspected, then it contains "vskill marketplace plugins" and no longer lists `mobile` or `skills` in the "NOT available" clause

**Dependencies**: None

---

## US-001: Hook-Level Keyword Detection for vskill Plugins

### T-002: Add detect_vskill_recommendations() to user-prompt-submit.sh
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [ ] Not Started
**Test**: Given the hook script includes `detect_vskill_recommendations()`, when it is called with `"deploy ios app to testflight"` and the mobile plugin is absent from `vskill.lock`, then stdout contains the suggestion block with plugin name `mobile`, description `App Store, TestFlight, mobile CI/CD`, and the exact install command `vskill install anton-abyzov/vskill --plugin mobile`

**File**: `plugins/specweave/hooks/user-prompt-submit.sh`

**Implementation Details**:
- Add registry metadata variables near top of non-slash-command section: `VSKILL_PLUGINS`, `VSKILL_DESC_*`, and `VSKILL_INSTALL_CMD` as shown in plan.md
- Add per-plugin keyword match functions `vskill_keywords_match_mobile()`, `vskill_keywords_match_google_workspace()`, `vskill_keywords_match_marketing()`, `vskill_keywords_match_productivity()`, `vskill_keywords_match_skills()` — short keywords (<5 chars) via `grep -qwi`, multi-word/long keywords via `case/esac` (bash 3.2 compatible, no associative arrays)
- Add `detect_vskill_recommendations(prompt)` function: lowercase prompt, loop `VSKILL_PLUGINS`, for each: (a) call `check_plugin_in_vskill_lock()` — skip if installed; (b) check `${TMPDIR:-/tmp}/specweave-vskill-suggested-<plugin>` marker — skip if exists; (c) call keyword match function; (d) on match: `touch` marker, accumulate suggestion line, increment counter; stop after 3 matches
- Function outputs formatted block (header + bullet lines) or empty string
- Integration point: call `detect_vskill_recommendations "$normalized_prompt"` after plugin auto-load check, before LLM detect-intent call; prepend result to `additionalContext`

**Test Approach**: Shell-level — source the relevant functions into a bash test or use a Vitest test that shells out and inspects stdout

**Test Cases**:
- **TC-001**: `detect_vskill_recommendations "deploy ios app to testflight"` (no lock) — output contains `mobile` suggestion with install command
- **TC-002**: `detect_vskill_recommendations "update google sheets report"` with `google-workspace` in vskill.lock — output does NOT contain `google-workspace`
- **TC-003**: `detect_vskill_recommendations "post on linkedin and instagram"` — output contains `marketing` bullet with `slack-messaging, social-media-posting` skills text
- **TC-004**: `detect_vskill_recommendations "I am curious about this"` — returns empty (no false positive from "ios" in "curious")
- **TC-005**: `detect_vskill_recommendations "search google drive for the google docs file"` — output contains `google-workspace` (multi-word keyword "google drive" matches)
- **TC-006**: Prompt matching 4 plugins — output contains exactly 3 suggestion bullets

**Dependencies**: T-001 (registry design reference; hook is independent bash but mirrors same keyword logic)

---

## US-002: Session-Level Suggestion Deduplication

### T-003: Implement TMPDIR session marker deduplication in detect_vskill_recommendations()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] Not Started
**Test**: Given `detect_vskill_recommendations()` is called twice with a prompt matching `mobile` and no lock entry, when the second call runs in the same shell session (TMPDIR marker still present), then the second call returns empty output for `mobile`

**File**: `plugins/specweave/hooks/user-prompt-submit.sh`

**Implementation Details**:
- Inside `detect_vskill_recommendations()`, before appending a suggestion, check: `[ -f "${TMPDIR:-/tmp}/specweave-vskill-suggested-${plugin}" ]` — skip if file exists
- After deciding to suggest, `touch "${TMPDIR:-/tmp}/specweave-vskill-suggested-${plugin}"` before accumulating output
- If TMPDIR is not writable, the touch will fail silently (no `set -e` on touch call) — suggestion may repeat, which is acceptable per spec
- Use flat path without PID suffix (session-scoped, not process-scoped) so any Claude Code instance within the same session sees the dedup

**Test Cases**:
- **TC-001**: Given marker file pre-exists at `$TMPDIR/specweave-vskill-suggested-mobile`, when `detect_vskill_recommendations "deploy ios app"` is called, then output is empty for mobile
- **TC-002**: Given no marker file, when `detect_vskill_recommendations "deploy ios app"` runs, then marker file is created at `$TMPDIR/specweave-vskill-suggested-mobile`
- **TC-003**: Given marker files are in TMPDIR (session-scoped), when a new shell session starts with a fresh TMPDIR, then `detect_vskill_recommendations "deploy ios app"` produces a suggestion again

**Dependencies**: T-002 (deduplication logic is part of the same function)

---

## US-003: Multi-Plugin Match Capping

### T-004: Enforce cap of 3 suggestions per prompt in detect_vskill_recommendations()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [ ] Not Started
**Test**: Given a prompt that contains keywords triggering mobile, google-workspace, marketing, and productivity plugins simultaneously, when `detect_vskill_recommendations()` processes it, then the output contains exactly 3 suggestion bullets and no 4th plugin entry appears

**File**: `plugins/specweave/hooks/user-prompt-submit.sh`

**Implementation Details**:
- In the loop inside `detect_vskill_recommendations()`, maintain a `match_count=0` counter; when `match_count` reaches 3, `break` the loop
- The iteration order of `VSKILL_PLUGINS` string determines priority when >3 match (this is acceptable per spec — no dynamic sort needed in bash)
- In TypeScript `detectVskillPlugins()` (T-001), sort by matched keyword length descending before capping at 3

**Test Cases**:
- **TC-001**: Prompt matching 4 plugins — bash output has exactly 3 `- ` bullet lines
- **TC-002**: Prompt matching 2 plugins — bash output has exactly 2 `- ` bullet lines (cap does not truncate when under limit)
- **TC-003**: Measure length of a 3-plugin suggestion block — total chars under 900 (each plugin line under 300 chars)
- **TC-004** (TypeScript): `detectVskillPlugins()` with 4-plugin prompt returns array of length 3, sorted by keyword match length descending

**Dependencies**: T-002, T-003

---

## US-005: Project-Detector vskill Plugin Recommendations

### T-005: Add vskillPlugins field to ProjectTypeResult and mobile DetectionRules in project-detector.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [ ] Not Started
**Test**: Given a project directory containing a `Podfile`, when `detectProjectType()` is called, then the returned `ProjectTypeResult` has `vskillPlugins: ["mobile"]`; given a `package.json` with `"react-native"` in dependencies, then `vskillPlugins: ["mobile"]` is also present

**File**: `src/core/lazy-loading/project-detector.ts`

**Implementation Details**:
- Add `vskillPlugins?: string[]` field to `ProjectTypeResult` interface (defaults to `[]` when absent)
- Add `vskillPlugins?: string[]` field to `DetectionRule` interface
- Update the four existing mobile detection rules (react-native line ~263, expo line ~268, ios/Podfile line ~273, android line ~279) to include `vskillPlugins: ['mobile']`
- In `detectProjectType()`, collect all matched rule `vskillPlugins` entries into a `Set<string>` and return as `vskillPlugins: [...set]` on the result
- In the session-start hook or wherever project-detector results are consumed: if a plugin in `vskillPlugins` is already in `vskill.lock`, suppress that suggestion (this check is handled in the consuming code path, not in project-detector itself)

**Test File**: `src/core/lazy-loading/__tests__/project-detector.vskill.test.ts`

**Test Cases**:
- **TC-001**: Project with `Podfile` — `detectProjectType()` returns `vskillPlugins: ["mobile"]`
- **TC-002**: Project with `ios/` directory — `detectProjectType()` returns `vskillPlugins: ["mobile"]`
- **TC-003**: `package.json` containing `"react-native"` in dependencies — returns `vskillPlugins: ["mobile"]`
- **TC-004**: `package.json` containing `"expo"` — returns `vskillPlugins: ["mobile"]`
- **TC-005**: Plain Node.js project (no mobile signals) — returns `vskillPlugins: []` or field absent
- **TC-006**: `ProjectTypeResult` type check — `vskillPlugins` field accepts `string[]` and TS compiler accepts `[]` as default
- **TC-007**: When `mobile` is in `vskill.lock` and consuming code checks `vskillPlugins`, the suggestion for `mobile` is suppressed (integration-level test in the session-start consumer, documented here for coverage traceability)

**Dependencies**: T-001 (interfaces as design reference; module is independent)

---

## US-006: Auto-Install Component Mapping for vskill Plugins

### T-006: Add vskillPlugin field to COMPONENT_MAPPING and extend analyzeUserIntent() return type
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [ ] Not Started
**Test**: Given `analyzeUserIntent("deploy my ios app")` is called, when the function processes the prompt against COMPONENT_MAPPING, then the return value includes `vskillPlugins: ["mobile"]`

**File**: `src/utils/auto-install.ts`

**Implementation Details**:
- Extend the COMPONENT_MAPPING entry type: `{ skills: string[]; agents: string[]; vskillPlugin?: string }`
- Add `vskillPlugin: "mobile"` to entries for: `"react native"`, `"react-native"`, `"expo"`, `"ios"`, `"android"`, `"mobile"`, `"app store"`, `"play store"` (8 entries total)
- Extend `analyzeUserIntent()` return type: add `vskillPlugins: string[]` field
- In the function body, after collecting `skills` and `agents`, also collect any `vskillPlugin` values from matched entries into a `Set<string>` and return as `vskillPlugins`

**Test File**: `src/utils/__tests__/auto-install.vskill.test.ts`

**Test Cases**:
- **TC-001**: `analyzeUserIntent("deploy my ios app")` — `vskillPlugins` contains `"mobile"`
- **TC-002**: `analyzeUserIntent("build react native app")` — `vskillPlugins` contains `"mobile"`
- **TC-003**: `analyzeUserIntent("update react component styling")` — `vskillPlugins` is `[]`
- **TC-004**: `analyzeUserIntent("submit to app store")` — `vskillPlugins` contains `"mobile"`
- **TC-005**: COMPONENT_MAPPING type check — entries with `vskillPlugin` set are valid TS; entries without it still compile
- **TC-006**: `analyzeUserIntent` return type includes `vskillPlugins: string[]` — TypeScript compiler accepts usage `result.vskillPlugins.forEach(...)`

**Dependencies**: T-001 (VSKILL_PLUGIN_REGISTRY as design reference; module is independent)

---

## US-007: Detect-Intent CLI vskill Recommendations

### T-007: Add vskillRecommendations to DetectIntentResult and wire detectVskillPlugins() in detect-intent.ts
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03
**Status**: [ ] Not Started
**Test**: Given `specweave detect-intent "deploy ios app to testflight"` is run and the mobile plugin is absent from `vskill.lock`, when the command outputs JSON, then the output contains `"vskillRecommendations"` with at least one entry where `plugin === "mobile"` and `installCommand === "vskill install anton-abyzov/vskill --plugin mobile"`

**File**: `src/cli/commands/detect-intent.ts`

**Implementation Details**:
- Add `vskillRecommendations?: { plugin: string; matchedKeyword: string; installCommand: string; }[]` to `DetectIntentResult` interface
- Import `detectVskillPlugins` from `../../core/lazy-loading/llm-plugin-detector.js`
- In `detectIntentCommand()`, after LLM detection completes (or in parallel since it is pure sync), call `detectVskillPlugins(prompt)`
- Filter results: for each match, check if plugin is in `vskill.lock` (reuse existing lockfile check util); exclude installed plugins
- Assign filtered array to `result.vskillRecommendations` (omit field or set to `[]` when no matches)

**Test File**: `src/cli/commands/__tests__/detect-intent.vskill.test.ts`

**Test Cases**:
- **TC-001**: `detectIntentCommand("deploy ios app to testflight")` with no vskill.lock — result has `vskillRecommendations` containing entry with `plugin: "mobile"`
- **TC-002**: `detectIntentCommand("deploy ios app to testflight")` with `mobile` already in vskill.lock — `vskillRecommendations` is absent or empty
- **TC-003**: `detectIntentCommand("update react component")` — `vskillRecommendations` is absent or `[]`
- **TC-004**: `DetectIntentResult` type accepts `vskillRecommendations` field — TypeScript compiler accepts the field without errors
- **TC-005**: CLI JSON output when run with a matching prompt — stdout is valid JSON containing `vskillRecommendations` key (integration-level, shells out to binary or uses programmatic CLI runner)

**Dependencies**: T-001 (imports `detectVskillPlugins` from llm-plugin-detector)

---

## Coverage Matrix

| AC-ID | Task | Status |
|-------|------|--------|
| AC-US1-01 | T-002 | [ ] |
| AC-US1-02 | T-002 | [ ] |
| AC-US1-03 | T-002 | [ ] |
| AC-US1-04 | T-002 | [ ] |
| AC-US1-05 | T-002 | [ ] |
| AC-US2-01 | T-003 | [ ] |
| AC-US2-02 | T-003 | [ ] |
| AC-US2-03 | T-003 | [ ] |
| AC-US3-01 | T-004 | [ ] |
| AC-US3-02 | T-004 | [ ] |
| AC-US3-03 | T-004 | [ ] |
| AC-US4-01 | T-001 | [ ] |
| AC-US4-02 | T-001 | [ ] |
| AC-US4-03 | T-001 | [ ] |
| AC-US5-01 | T-005 | [ ] |
| AC-US5-02 | T-005 | [ ] |
| AC-US5-03 | T-005 | [ ] |
| AC-US5-04 | T-005 | [ ] |
| AC-US6-01 | T-006 | [ ] |
| AC-US6-02 | T-006 | [ ] |
| AC-US6-03 | T-006 | [ ] |
| AC-US7-01 | T-007 | [ ] |
| AC-US7-02 | T-007 | [ ] |
| AC-US7-03 | T-007 | [ ] |

## Execution Order

```
T-001  (llm-plugin-detector.ts — no deps)
  |
  +---> T-002  (hook bash — mirrors keyword logic, no TS import)
  |       |
  |       +---> T-003  (dedup — extends T-002 function body)
  |               |
  |               +---> T-004  (cap — extends T-002/T-003 function body)
  |
  +---> T-005  (project-detector.ts — independent of hook)
  |
  +---> T-006  (auto-install.ts — independent of hook)
  |
  +---> T-007  (detect-intent.ts — imports from T-001)
```
