---
increment: 0459-skill-eval-enhancements
title: "Skill Eval UI Enhancements"
updated: 2026-03-09
by_user_story:
  US-000: [T-000]
  US-001: [T-001, T-002, T-003]
  US-002: [T-004, T-005, T-006, T-007]
  US-003: [T-008, T-009, T-010]
  US-004: [T-011, T-012, T-013]
---

## Bonus: --root Bug Fixes (Already Implemented)

### T-000: Fix skill-scanner self-layout plugin name and serve root validation

**User Story**: Bonus (pre-increment fix)
**Satisfies ACs**: (bonus — no spec AC)
**Status**: [x] completed

**Summary**: Two bugs were found and fixed before increment work began:
1. `skill-scanner` used wrong plugin name for self-layout skills (was using directory name instead of SKILL.md `plugin` frontmatter field)
2. `vskill eval serve --root <path>` accepted invalid paths without early validation, causing confusing errors inside the server

**Test Plan**:
- **Given** a self-referential plugin layout
- **When** the skill scanner resolves the plugin name
- **Then** it uses the `plugin` frontmatter field from SKILL.md, not the directory name

**Test Cases**:
1. **Unit**: `src/eval/__tests__/skill-scanner.test.ts`
   - scannerUsesFrontmatterPluginName(): verifies plugin name comes from SKILL.md frontmatter
   - serveRootValidation(): verifies early exit with clear error when --root is not a directory
   - **Coverage Target**: 90%

**Implementation**: Already done. No further work required.

---

## User Story: US-001 - Skill Definition Viewer

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 3 total, 3 completed

### T-001: Extract resolveSkillDir to skill-resolver.ts and update imports

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Test Plan**:
- **Given** the `resolveSkillDir` function currently lives inside `api-routes.ts`
- **When** it is moved to `src/eval-server/skill-resolver.ts` and re-exported
- **Then** all existing callers in `api-routes.ts` still resolve paths identically

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/skill-resolver.test.ts` (new)
   - resolvesRelativeToRoot(): `resolveSkillDir("/root", "plug", "skill")` → `"/root/plug/skill"`
   - resolvesNestedPlugin(): handles plugin names without slashes correctly
   - **Coverage Target**: 95%
2. **Regression**: run `npx vitest run` after extraction — zero new failures

**Implementation**:
1. Create `src/eval-server/skill-resolver.ts` — export `resolveSkillDir(root, plugin, skill): string`
2. Remove the local function from `api-routes.ts`, add `import { resolveSkillDir } from "./skill-resolver.js"`
3. Run `npx vitest run` to confirm zero regressions

---

### T-002: Build SkillContentViewer component (parseFrontmatter + collapsible viewer)

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Test Plan**:
- **Given** a SKILL.md string with YAML frontmatter and a body
- **When** `<SkillContentViewer content={skillContent} />` renders
- **Then** metadata cards show frontmatter fields, allowed-tools render as pills, body renders in a monospace block, and the section is collapsible defaulting to expanded

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/parseFrontmatter.test.ts` (new)
   - parsesDescriptionAndModel(): extracts description and model fields correctly
   - parsesAllowedToolsAsArray(): comma-separated and YAML list values → string[]
   - noFrontmatterReturnsEmptyMeta(): no `---` block → `{ metadata: {}, body: fullContent }`
   - emptyAllowedTools(): allowed-tools absent → empty array, no error
   - **Coverage Target**: 95%
2. **Manual verification gate**: Load a skill with frontmatter → metadata cards visible, body visible, collapse/expand works; load a skill with no frontmatter → only body block shown, no cards

**Implementation**:
1. Create `src/eval-ui/src/utils/parseFrontmatter.ts` — pure `parseFrontmatter(content): { metadata: Record<string, string | string[]>; body: string }`
2. Create `src/eval-ui/src/components/SkillContentViewer.tsx` (~200 lines)
3. Render description/model/context as labeled cards; `allowed-tools` as pill chips
4. Collapsible wrapper with chevron toggle, `defaultExpanded={true}`
5. Body in `<pre style={{ maxHeight: "400px", overflowY: "auto" }}>`

---

### T-003: Integrate SkillContentViewer into SkillDetailPage

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [x] completed

**Test Plan**:
- **Given** the SkillDetailPage loads via `api.getSkillDetail(plugin, skill)`
- **When** the page renders
- **Then** `<SkillContentViewer>` appears between the breadcrumb and action bar with the skill's SKILL.md content

**Test Cases**:
1. **Integration**: `src/eval-ui/src/__tests__/SkillDetailPage.integration.test.tsx` (new)
   - rendersSkillViewer(): mocks `api.getSkillDetail` → confirms SkillContentViewer is mounted
   - **Coverage Target**: 85%
2. **Manual verification gate**: Open SkillDetailPage for any skill → SKILL.md content appears above benchmark controls

**Implementation**:
1. Add `skillContent` state (`useState("")`) to `SkillDetailPage.tsx`
2. In existing `useEffect`, also call `api.getSkillDetail()` and set `skillContent`
3. Insert `<SkillContentViewer content={skillContent} />` between breadcrumb and action bar
4. Add `refreshSkillContent()` callback (re-fetches and sets state) for Feature 2 apply action

---

## User Story: US-002 - AI-Powered Skill Improvement

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 4 total, 4 completed

### T-004: Build diff.ts utility (line-by-line LCS diff, no external deps)

**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- **Given** two strings (original and improved SKILL.md content)
- **When** `computeDiff(original, improved)` is called
- **Then** it returns `DiffLine[]` correctly classifying added, removed, and unchanged lines

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/diff.test.ts` (new — TDD RED first)
   - identicalInputs(): all lines return `type: "unchanged"`
   - pureAdditions(): new lines in improved only → `type: "added"`
   - pureDeletions(): lines only in original → `type: "removed"`
   - mixedEdits(): realistic SKILL.md edit → correct interleaving of add/remove/unchanged
   - emptyOriginal(): all improved lines are `type: "added"`
   - emptyImproved(): all original lines are `type: "removed"`
   - **Coverage Target**: 95%

**Implementation**:
1. Write failing tests first (RED phase)
2. Create `src/eval-ui/src/utils/diff.ts` with `DiffLine` interface and `computeDiff(original, improved): DiffLine[]`
3. Implement O(n*m) LCS on line arrays; walk both arrays to produce diff entries
4. Guard: inputs exceeding 1000 lines → return both sides as `"unchanged"` (fallback)
5. Run tests GREEN, then refactor

---

### T-005: Build improve-routes.ts backend (improve + apply-improvement endpoints)

**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04 | **Status**: [x] completed

**Test Plan**:
- **Given** `POST /api/skills/:plugin/:skill/improve` with `{ provider, model }`
- **When** processed
- **Then** reads SKILL.md, fetches up to 10 recent failed assertions from latest benchmark, calls LLM, returns `{ original, improved, reasoning }`

- **Given** `POST /api/skills/:plugin/:skill/apply-improvement` with `{ content }`
- **When** processed
- **Then** writes content to SKILL.md on disk, returns `{ ok: true }`

**Test Cases**:
1. **Integration**: `src/eval-server/__tests__/improve-routes.test.ts` (new — TDD RED first)
   - improveReturnsDiff(): mocks `createLlmClient`, verifies response shape `{ original, improved, reasoning }`
   - improveIncludesUpTo10Failures(): stub benchmark with 15 failures → only 10 included in prompt
   - improveHandlesMissingSkill(): missing SKILL.md → 404 JSON response
   - improveHandlesLlmError(): LLM throws → 500 with error message (no crash)
   - applyWritesToDisk(): spies on `writeFileSync`, verifies called with correct path and content
   - applyRejectsEmptyContent(): empty string body → 400 JSON response
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests first (RED phase)
2. Create `src/eval-server/improve-routes.ts` exporting `registerImproveRoutes(router, root)`
3. `POST improve`: `resolveSkillDir` → read SKILL.md, `readBenchmark` → extract ≤10 failed assertions → build prompt → `createLlmClient({ provider, model })` → return `{ original, improved, reasoning }`
4. `POST apply-improvement`: validate non-empty content → `writeFileSync(skillMdPath, content)` → `{ ok: true }`
5. Register in `eval-server.ts`: `registerImproveRoutes(router, root)` call
6. All imports use `.js` extensions (nodenext)

---

### T-006: Build SkillImprovePanel component (model picker + diff view + apply/discard)

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- **Given** `<SkillImprovePanel>` is mounted on SkillDetailPage
- **When** user clicks "Improve Skill"
- **Then** a panel appears with provider/model dropdowns and an "Improve" button

- **Given** an improvement response is received
- **When** displayed
- **Then** unified diff shows green/red/gray lines; "Apply" writes to disk; "Discard" closes without writing

**Test Cases**:
1. **Manual verification gate**:
   - Click "Improve Skill" → panel opens with model picker
   - Click "Improve" → loading state shown
   - Response received → diff renders with colored lines
   - Click "Apply" → success confirmation shown, viewer content refreshes
   - Click "Discard" → panel closes, no disk write occurs

**Implementation**:
1. Create `src/eval-ui/src/components/SkillImprovePanel.tsx` (~300 lines)
2. Props: `{ plugin, skill, skillContent, onApplied: (newContent: string) => void }`
3. State machine: `closed → open → loading → diff_shown`
4. Model picker: `api.getConfig()` → provider/model dropdowns (reuse ModelSelector pattern)
5. On response: `computeDiff(original, improved)` → render DiffLine[] with colored rows
6. Apply: `api.applyImprovement(plugin, skill, improved)` → `onApplied(improved)`
7. Add `improveSkill(plugin, skill, opts)` and `applyImprovement(plugin, skill, content)` to `src/eval-ui/src/api.ts`
8. Add `ImproveResult` interface to `src/eval-ui/src/types.ts`

---

### T-007: Wire SkillImprovePanel into SkillDetailPage

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- **Given** `<SkillImprovePanel>` is mounted in SkillDetailPage
- **When** the user applies an improvement
- **Then** `refreshSkillContent()` is called and `<SkillContentViewer>` updates with the new content

**Test Cases**:
1. **Manual verification gate**:
   - Apply improvement → SkillContentViewer immediately shows the updated content

**Implementation**:
1. Import `SkillImprovePanel` in `SkillDetailPage.tsx`
2. Mount below `<SkillContentViewer>`: `<SkillImprovePanel plugin={plugin} skill={skill} skillContent={skillContent} onApplied={refreshSkillContent} />`
3. Confirm `refreshSkillContent` re-fetches `api.getSkillDetail()` and updates `skillContent` state

---

## User Story: US-003 - Per-Test-Case Model A/B Comparison

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 3 total, 3 completed

### T-008: Build model-compare-routes.ts backend (SSE sequential model comparison)

**User Story**: US-003 | **Satisfies ACs**: AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Test Plan**:
- **Given** `POST /api/skills/:plugin/:skill/compare-models` with `{ eval_id, modelA, modelB }`
- **When** processed
- **Then** runs Model A first (SSE: model_a_start → model_a_result), then Model B (model_b_start → model_b_result), then done — no writes to benchmark history

**Test Cases**:
1. **Integration**: `src/eval-server/__tests__/model-compare-routes.test.ts` (new — TDD RED first)
   - runsModelsSequentially(): Model A client created before Model B; SSE event order enforced
   - doesNotWriteToHistory(): spy on any benchmark-write function → never called
   - unknownEvalId(): non-existent eval_id → SSE error event (not hard crash)
   - missingSkillMd(): SKILL.md absent → 404 SSE error event
   - sseHeadersSet(): response Content-Type is `text/event-stream`
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests first (RED phase)
2. Create `src/eval-server/model-compare-routes.ts` exporting `registerModelCompareRoutes(router, root)`
3. Parse body → load evals → find eval case by `eval_id` (error SSE event if not found)
4. Read SKILL.md → construct system prompt
5. `initSSE(res)` → run Model A: `createLlmClient(modelA)`, generate, judge, `sendSSE("model_a_result", ...)`
6. Run Model B: `createLlmClient(modelB)`, generate, judge, `sendSSE("model_b_result", ...)`
7. `sendSSEDone(res)` — no history writes
8. Register in `eval-server.ts`
9. Add `ModelCompareResult` to `src/eval-ui/src/types.ts`; all imports use `.js` extensions

---

### T-009: Build ModelCompareModal component (two model selectors + SSE + side-by-side results)

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05 | **Status**: [x] completed

**Test Plan**:
- **Given** user clicks "Compare Models" on an eval case
- **When** the modal opens
- **Then** two independent model selectors appear with a "Compare" button

- **Given** "Compare" is clicked
- **When** executing
- **Then** SSE progress shows "Model A running..." then "Model B running..." and side-by-side results on completion

**Test Cases**:
1. **Manual verification gate**:
   - Click "Compare Models" → modal opens with two independent model selectors (Model A, Model B)
   - Click "Compare" → progress shows which model is currently running
   - Both complete → side-by-side: model name, output, assertion pass/fail, duration, tokens
   - Dismiss → no data persisted to benchmark history

**Implementation**:
1. Create `src/eval-ui/src/components/ModelCompareModal.tsx` (~250 lines)
2. Props: `{ plugin, skill, evalCase: EvalCase, onClose: () => void }`
3. State: `idle → running_a → running_b → complete`
4. Two independent `<ModelSelector>` components (reuse existing from eval-ui)
5. SSE via `useSSE` hook; events map to state transitions
6. Side-by-side layout: model name, output text, assertion results, duration, token count per side
7. Dismiss = close with no side effects (results are ephemeral)
8. Add `compareModels(plugin, skill, payload)` to `src/eval-ui/src/api.ts`

---

### T-010: Wire ModelCompareModal into SkillDetailPage eval case rows

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05 | **Status**: [x] completed

**Test Plan**:
- **Given** each eval case row on SkillDetailPage
- **When** a "Compare Models" button is present and clicked
- **Then** `<ModelCompareModal>` opens scoped to that specific eval case

**Test Cases**:
1. **Manual verification gate**:
   - Each eval case row shows a "Compare Models" button
   - Clicking opens modal for that eval case
   - Closing modal returns page to normal state

**Implementation**:
1. Add `compareTarget: EvalCase | null` state to `SkillDetailPage.tsx`
2. Add "Compare Models" button to each eval case row (onClick sets `compareTarget`)
3. Mount `<ModelCompareModal>` conditionally when `compareTarget !== null`
4. `onClose` resets `compareTarget` to `null`

---

## User Story: US-004 - Skill Dependency Visibility (MCP + Skill-to-Skill)

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06
**Tasks**: 3 total, 3 completed

### T-011: Build mcp-detector.ts pure function with TDD (MCP + skill-to-skill detection)

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-04, AC-US4-05, AC-US4-06 | **Status**: [x] completed

**Test Plan**:
- **Given** SKILL.md content with tool patterns like `slack_send_message`
- **When** `detectMcpDependencies(content)` is called
- **Then** a `McpDependency` for Slack is returned with matched tools and a valid `.mcp.json` config snippet

- **Given** SKILL.md content referencing other skills (e.g., "use the scout skill")
- **When** `detectSkillDependencies(content)` is called
- **Then** referenced skill names are returned

**Test Cases**:
1. **Unit**: `src/eval/__tests__/mcp-detector.test.ts` (new — TDD RED first)
   - detectsSlackPattern(): `slack_send_message` in body → Slack dependency returned
   - detectsGitHubPattern(): `github_create_pr` in body → GitHub dependency
   - detectsGoogleWorkspace(): `drive_list_files` + `gmail_send` → single Google Workspace entry (deduped)
   - detectsLinearPattern(): `linear_create_issue` → Linear dependency
   - detectsFrontmatterAllowedTools(): `allowed-tools: [slack_post]` in frontmatter → Slack detected
   - noMatchReturnsEmpty(): body with no known patterns → empty array
   - configSnippetFormat(): `configSnippet` is valid JSON parseable as `.mcp.json`
   - detectsSkillToSkillInlineRef(): "use the scout skill" in body → scout skill reference returned
   - detectsExplicitDependenciesFrontmatter(): `dependencies: [scout, social-media-posting]` → both returned
   - noSkillReferencesReturnsEmpty(): no skill patterns → empty skill dependencies array
   - deduplicatesPatterns(): same tool in frontmatter and body → single matched tool entry
   - **Coverage Target**: 95%

**Implementation**:
1. Write all failing tests first (RED phase)
2. Create `src/eval/mcp-detector.ts` with:
   - `McpDependency` interface: `{ server, url, transport, matchedTools, configSnippet }`
   - `SkillDependency` interface: `{ name, link?: string }`
   - Hardcoded MCP registry: `slack_` → Slack, `github_` → GitHub, `linear_` → Linear, `gws_/drive_/gmail_/sheets_/calendar_/chat_` → Google Workspace
   - `detectMcpDependencies(content): McpDependency[]`
   - `detectSkillDependencies(content): SkillDependency[]` — scans for `/skill-name`, "use the X skill", "chains with X", `dependencies:` frontmatter key
3. Run tests GREEN, then refactor for clarity

---

### T-012: Add GET /api/skills/:plugin/:skill/dependencies endpoint

**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [x] completed

**Test Plan**:
- **Given** `GET /api/skills/:plugin/:skill/dependencies`
- **When** the skill has SKILL.md with known tool patterns
- **Then** returns `{ mcpDependencies: McpDependency[], skillDependencies: SkillDependency[] }`

**Test Cases**:
1. **Integration**: `src/eval-server/__tests__/api-routes-mcp.test.ts` (new)
   - returnsMcpDependencies(): stubs SKILL.md with slack pattern → Slack in response
   - returnsEmptyForNoPatterns(): SKILL.md with no patterns → both arrays empty
   - returns404ForMissingSkill(): SKILL.md not found → 404 JSON
   - **Coverage Target**: 90%

**Implementation**:
1. Add ~10 lines to `api-routes.ts`: import `{ detectMcpDependencies, detectSkillDependencies }` from `"../eval/mcp-detector.js"`
2. Register `GET /api/skills/:plugin/:skill/dependencies` — read SKILL.md, call both detectors, return combined JSON
3. Return 404 if SKILL.md not found
4. Add `getMcpDependencies(plugin, skill)` to `src/eval-ui/src/api.ts`
5. Add `McpDependency` and `SkillDependency` interfaces to `src/eval-ui/src/types.ts`

---

### T-013: Build McpDependencies component and wire into SkillDetailPage

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-05, AC-US4-06 | **Status**: [x] completed

**Test Plan**:
- **Given** a skill with Slack tool patterns in SKILL.md
- **When** `<McpDependencies>` mounts
- **Then** a Slack dependency card is shown with matched tools as pills and a "Copy Config" button

- **Given** a skill referencing the "scout" skill in its body
- **When** the section renders
- **Then** the referenced skill is listed with a link if it exists in the current plugin set

- **Given** a skill with no MCP patterns or skill references
- **When** the section renders
- **Then** "No dependencies detected" empty state is shown

**Test Cases**:
1. **Manual verification gate**:
   - Slack skill loaded → Slack MCP card visible with tool pills and "Copy Config" button
   - "Copy Config" clicked → clipboard contains valid `.mcp.json` JSON snippet
   - Skill with no patterns → "No dependencies detected" shown
   - Skill referencing another skill → skill-to-skill section visible with link (if skill exists)

**Implementation**:
1. Create `src/eval-ui/src/components/McpDependencies.tsx` (~150 lines)
2. Props: `{ plugin: string; skill: string }`
3. `useEffect` → `api.getMcpDependencies(plugin, skill)` on mount
4. MCP cards: server name, matched tools as pills, "Copy Config" button (`navigator.clipboard.writeText(dep.configSnippet)`)
5. Skill-to-skill section: list skill names with links to `/skill/:plugin/:name` if resolvable
6. Empty state: "No dependencies detected" when both `mcpDependencies` and `skillDependencies` are empty
7. Mount `<McpDependencies plugin={plugin} skill={skill} />` in `SkillDetailPage.tsx` below SkillContentViewer
