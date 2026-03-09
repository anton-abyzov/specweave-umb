---
increment: 0466-skill-builder-preview-history
title: "Skill Builder: MD Preview & Per-Case History"
total_tasks: 12
completed_tasks: 12
by_user_story:
  US-001: [T-003, T-004]
  US-002: [T-005, T-006]
  US-003: [T-009, T-010, T-011, T-012]
  US-004: [T-001, T-002, T-007, T-008]
---

# Tasks: Skill Builder MD Preview & Per-Case History

> Implementation order: Phase 1 — US-004 (historyUtils extraction) → US-001 (renderMarkdown) | Phase 2 — US-002 (EditorPanel preview) → US-003 (CaseHistorySection)

---

## User Story: US-004 - Shared History Display Utilities

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 4 total, 0 completed

### T-001: Create historyUtils.tsx with extracted pure functions

**User Story**: US-004
**Satisfies ACs**: AC-US4-01
**Status**: [x] completed

**Test Plan**:
- **Given** pure utility functions (passRateColor, shortDate, fmtDuration) extracted from HistoryPerEval.tsx into a shared module
- **When** each function is called with representative inputs
- **Then** it returns the correct formatted value according to its documented thresholds and format strings

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/historyUtils.test.tsx`
   - `passRateColor_returnsGreenAbove80()`: rate=0.9 → green color string
   - `passRateColor_returnsYellowBetween50and80()`: rate=0.65 → yellow color string
   - `passRateColor_returnsRedBelow50()`: rate=0.3 → red color string
   - `shortDate_formatsISOStringToMonDDHHMM()`: valid ISO → "Mar 09, 14:30"
   - `fmtDuration_formatsMillisecondsToSeconds()`: 2500 → "2.5s"
   - `fmtDuration_formatsSubSecondToMs()`: 450 → "450ms"
   - `fmtDuration_returnsEmptyOnUndefined()`: undefined → "—"
   - **Coverage Target**: 95%

**Implementation**:
1. Read `src/eval-ui/src/components/HistoryPerEval.tsx` to locate existing `passRateColor`, `shortDate`, `fmtDuration` implementations
2. Write the test file `src/eval-ui/src/utils/__tests__/historyUtils.test.tsx` (TDD red phase)
3. Create `src/eval-ui/src/utils/historyUtils.tsx` with the three pure functions exported (no JSX yet)
4. Run tests: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/utils/__tests__/historyUtils.test.tsx`

---

### T-002: Add MiniTrend component to historyUtils.tsx

**User Story**: US-004
**Satisfies ACs**: AC-US4-01
**Status**: [x] completed

**Test Plan**:
- **Given** a `MiniTrend` React component accepting an array of `CaseHistoryEntry` entries
- **When** rendered with fewer than 2 entries
- **Then** it returns null; when rendered with 2 or more entries it renders an SVG element containing a polyline

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/historyUtils.test.tsx`
   - `MiniTrend_returnsNullForZeroEntries()`: entries=[] → renders nothing
   - `MiniTrend_returnsNullForOneEntry()`: entries=[one] → renders nothing
   - `MiniTrend_rendersSvgPolylineForTwoEntries()`: entries=[a,b] → SVG with polyline present
   - `MiniTrend_rendersSvgPolylineForManyEntries()`: entries=[a,b,c,d,e] → SVG with polyline
   - **Coverage Target**: 90%

**Implementation**:
1. Add `MiniTrend` JSX component to `historyUtils.tsx` (requires `.tsx` extension — already set)
2. Port the SVG sparkline implementation from `HistoryPerEval.tsx`
3. Import `CaseHistoryEntry` from `../../types`
4. Run tests: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/utils/__tests__/historyUtils.test.tsx`

---

### T-007: Update HistoryPerEval to import from historyUtils

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** `HistoryPerEval.tsx` currently defines passRateColor, shortDate, fmtDuration, MiniTrend locally
- **When** those definitions are removed and replaced with imports from `../utils/historyUtils`
- **Then** the component renders identically with no visual regression and existing tests still pass

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/historyUtils.test.tsx` (re-run after refactor)
   - All previously passing tests continue to pass
   - No new test failures introduced
   - **Coverage Target**: maintain >= 90%

**Implementation**:
1. In `HistoryPerEval.tsx`: remove local `passRateColor`, `shortDate`, `fmtDuration`, `MiniTrend` definitions
2. Add `import { passRateColor, shortDate, fmtDuration, MiniTrend } from '../utils/historyUtils'`
3. Run full test suite: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui`
4. Confirm no TypeScript errors: `npx tsc --noEmit`

---

### T-008: Verify visual consistency between HistoryPerEval and CaseDetail

**User Story**: US-004
**Satisfies ACs**: AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** both HistoryPerEval and the upcoming CaseHistorySection import from the same historyUtils module
- **When** both views display a run entry with the same pass rate, duration, and timestamp
- **Then** the formatted values (color, string format) are identical because they share the same function implementations

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/historyUtils.test.tsx`
   - `sharedFormatting_passRateColorConsistentAcrossViews()`: same rate value → same color string from single source
   - `sharedFormatting_shortDateConsistentAcrossViews()`: same ISO → same display string
   - **Coverage Target**: 85%

**Implementation**:
1. Confirm `HistoryPerEval.tsx` and `TestsPanel.tsx` (after T-010) both import exclusively from `historyUtils`
2. Run tests to confirm shared module is the single source
3. Note: full visual consistency confirmed during manual QA gate

---

## User Story: US-001 - Custom Markdown Renderer Utility

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06
**Tasks**: 2 total, 0 completed

### T-003: Create renderMarkdown utility with core element support

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-06
**Status**: [x] completed

**Test Plan**:
- **Given** a pure `renderMarkdown(text: string): string` function
- **When** called with markdown text containing headers, bold, italic, inline code, fenced code blocks, and lists
- **Then** it returns an HTML string with the appropriate tags and inline styles for each element; given empty or undefined input it returns an empty string

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/renderMarkdown.test.ts`
   - `headers_h1producesH1Tag()`: "# Title" → `<h1 style="...">Title</h1>`
   - `headers_h2producesH2Tag()`: "## Sub" → `<h2 ...>`
   - `headers_h3producesH3Tag()`: "### Sub" → `<h3 ...>`
   - `bold_producesStrongTag()`: "**word**" → `<strong>word</strong>`
   - `italic_producesEmTag()`: "*word*" → `<em>word</em>`
   - `inlineCode_producesCodeTag()`: backtick code backtick → `<code style="...">code</code>`
   - `fencedCodeBlock_producesPreCodeBlock()`: triple-backtick block → `<pre><code>...</code></pre>`
   - `fencedCodeBlock_preservesWhitespace()`: indented code lines preserved inside pre
   - `unorderedList_producesIndentedItems()`: "- item" lines → div with bullet style
   - `orderedList_producesNumberedItems()`: "1. item" lines → div with number style
   - `emptyString_returnsEmptyString()`: "" → ""
   - `undefinedInput_returnsEmptyString()`: undefined cast → ""
   - **Coverage Target**: 95%

**Implementation**:
1. Write test file `src/eval-ui/src/utils/__tests__/renderMarkdown.test.ts` (TDD red phase — all tests fail)
2. Read `repositories/anton-abyzov/vskill-platform/src/app/components/eval/EvalCaseCard.tsx` lines 34-56 to port the base implementation
3. Create `src/eval-ui/src/utils/renderMarkdown.ts` with the `renderMarkdown` function adapting style tokens to `var(--text-primary)` / `var(--surface-2)` / `var(--surface-3)`
4. Run tests until green: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/utils/__tests__/renderMarkdown.test.ts`

---

### T-004: Extend renderMarkdown with link and table support

**User Story**: US-001
**Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the `renderMarkdown` function
- **When** called with markdown containing `[text](url)` links or pipe-separated tables with a separator row
- **Then** links produce `<a href="url" target="_blank" rel="noopener noreferrer">text</a>` and tables produce a `<table>` with `<thead>` containing the header row and `<tbody>` containing data rows

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/renderMarkdown.test.ts`
   - `links_producesAnchorWithBlankTarget()`: "[Go](https://x.com)" → anchor with target="_blank"
   - `links_handlesMultipleLinksInOneLine()`: two links on one line → two anchors
   - `tables_producesTableWithThead()`: 3-row markdown table → `<table>` with `<thead>` and `<tbody>`
   - `tables_handlesMinimalTwoColumnTable()`: 2 columns → correct column count in output
   - `tables_ignoresMalformedTableWithNoSeparator()`: no separator row → not treated as table
   - `mixedContent_rendersAllElementsCorrectly()`: paragraph with headers, lists, code, links → all rendered
   - **Coverage Target**: 95%

**Implementation**:
1. Add link regex replacement to `renderMarkdown.ts` (before paragraph processing to avoid double-escaping)
2. Add table detection: collect consecutive lines starting with `|`, check for separator row containing `---`, emit `<table><thead>...</thead><tbody>...</tbody></table>`
3. Run tests: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/utils/__tests__/renderMarkdown.test.ts`
4. Run full suite to confirm no regressions: `npx vitest run src/eval-ui`

---

## User Story: US-002 - Real Markdown Preview in EditorPanel

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 0 completed

### T-005: Replace raw pre block with renderMarkdown in EditorPanel preview

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** `EditorPanel.tsx` currently renders the SKILL.md body inside a `<pre>` block
- **When** replaced with a `<div dangerouslySetInnerHTML={{ __html: renderMarkdown(body) }}>`
- **Then** the preview pane shows formatted HTML for markdown content, updates reactively as content changes, and shows nothing for an empty body without errors

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/renderMarkdown.test.ts` (already covers the utility)
   - Verify `renderMarkdown("")` returns "" (AC-US2-04 empty body case)
   - Verify `renderMarkdown("# Heading\n**bold**")` returns non-empty HTML string
   - **Coverage Target**: 95% (utility covered; UI wiring via manual QA gate)
2. **Integration**: Manual QA gate
   - Open Skill Builder at localhost:3162
   - Edit SKILL.md body with `# Heading` and `**bold**`
   - Confirm preview pane shows rendered heading and bold text (not raw monospace)

**Implementation**:
1. Read `src/eval-ui/src/pages/workspace/EditorPanel.tsx` to locate the `<pre>{body}</pre>` pattern
2. Add import: `import { renderMarkdown } from '../../utils/renderMarkdown'`
3. Replace the body pre block with:
   `<div style={{ fontSize: '13px', lineHeight: '1.7', color: 'var(--text-secondary)' }} dangerouslySetInnerHTML={{ __html: renderMarkdown(body) }} />`
4. Run unit tests: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui`
5. Confirm no TypeScript errors: `npx tsc --noEmit`

---

### T-006: Verify frontmatter cards and allowed-tools pills unaffected

**User Story**: US-002
**Satisfies ACs**: AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** the EditorPanel preview pane renders both parsed frontmatter metadata (cards) and the markdown body
- **When** only the `body` string (after `parseFrontmatter` split) is passed to `renderMarkdown`
- **Then** the frontmatter cards and allowed-tools pills above the body are unchanged in markup and visual appearance

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/renderMarkdown.test.ts`
   - `renderMarkdown_doesNotProcessFrontmatterDelimiters()`: input containing "---" frontmatter block → passes through unmodified (since parseFrontmatter strips it before renderMarkdown receives it)
   - **Coverage Target**: 85%

**Implementation**:
1. Read `EditorPanel.tsx` to confirm `parseFrontmatter(skillContent)` destructures into `{ metadata, body, allowedTools }` or equivalent — only `body` is passed to `renderMarkdown(body)`
2. Confirm frontmatter and allowedTools remain on their existing render path (no changes to those sections)
3. Run full test suite: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui`
4. Manual QA gate: confirm frontmatter cards visible and correct above rendered body

---

## User Story: US-003 - Per-Case Execution History in TestsPanel

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 4 total, 0 completed

### T-009: Add CaseHistorySection skeleton with collapsed default state

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** `CaseDetail` in `TestsPanel.tsx` renders below `OutputSection`
- **When** a test case is selected and CaseDetail renders
- **Then** a collapsible "Execution History" section header appears below the LLM Output section, collapsed by default, and clicking it toggles open/closed

**Test Cases**:
1. **Unit**: collapse/toggle is React state — covered by TypeScript check and manual QA gate
   - `historyUtils.test.tsx` pure functions remain unaffected (run as regression check)
   - **Coverage Target**: utility 90%; UI state via manual gate
2. **Integration**: Manual QA gate
   - Select a test case in TestsPanel
   - Confirm "Execution History" section header appears below LLM Output
   - Confirm it is collapsed by default (no content visible)
   - Confirm clicking the header toggles open/closed

**Implementation**:
1. Read `src/eval-ui/src/pages/workspace/TestsPanel.tsx` to understand `CaseDetail` layout and `OutputSection` chevron/collapse pattern
2. Add `CaseHistorySection` local function component inside `TestsPanel.tsx`:
   - Props: `{ evalId: number }`
   - State: `const [open, setOpen] = useState(false)`
   - Header row with chevron icon matching `OutputSection` visual style
   - Empty body when `open` is true (placeholder for T-010)
3. Render `<CaseHistorySection evalId={evalCase.id} />` below `<OutputSection>` in `CaseDetail`
4. TypeScript check: `cd repositories/anton-abyzov/vskill && npx tsc --noEmit`

---

### T-010: Wire API call and render history entries in CaseHistorySection

**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** `CaseHistorySection` is expanded for the first time for a given evalId
- **When** the section opens
- **Then** it calls `api.getCaseHistory(plugin, skill, evalId)`, shows a loading spinner during fetch, and on success renders up to 10 entries each showing timestamp, model, run type badge, pass rate, duration, tokens, and per-assertion pass/fail with reasoning; on empty response shows "No history for this case"

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/historyUtils.test.tsx`
   - `passRateColor`, `shortDate`, `fmtDuration` formatting correctness already verified (T-001)
   - Run as regression check after wiring
   - **Coverage Target**: utility formatting 95%; API wiring via manual gate
2. **Integration**: Manual QA gate
   - Expand Execution History for a case with existing runs — spinner briefly appears then entries load
   - Confirm each entry shows all 7 data fields (timestamp, model, run type badge, pass rate, duration, tokens, per-assertion results)
   - Expand Execution History for a case with no runs — "No history for this case" message appears

**Implementation**:
1. In `CaseHistorySection`:
   - Add `useState<Record<number, CaseHistoryEntry[]>>({})` for per-evalId cache
   - Add `useState(false)` for loading state
   - Destructure `{ state: { plugin, skill }, dispatch }` from `useWorkspace()`
   - On expand (open toggles true): if evalId not in cache, call `api.getCaseHistory(plugin, skill, evalId)`, set loading=true, await, cache result, set loading=false
   - Render: `loading` → spinner div with `className="spinner"`, empty entries → "No history for this case", entries present → list sliced to 10
2. Import `CaseHistoryEntry` from `../../types`
3. Import `passRateColor`, `shortDate`, `fmtDuration` from `../../utils/historyUtils`
4. TypeScript check: `npx tsc --noEmit`

---

### T-011: Add MiniTrend sparkline and "View full history" link

**User Story**: US-003
**Satisfies ACs**: AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** the Execution History section is expanded with history entries loaded
- **When** 2 or more entries exist
- **Then** a `MiniTrend` sparkline from `historyUtils` appears showing the pass rate trend; a "View full history" link appears at the bottom that dispatches `{ type: "SET_PANEL", panel: "history" }` to switch to HistoryPanel

**Test Cases**:
1. **Unit**: `src/eval-ui/src/utils/__tests__/historyUtils.test.tsx`
   - `MiniTrend_rendersSvgPolylineForTwoEntries()`: already covered in T-002
   - `MiniTrend_returnsNullForOneEntry()`: already covered in T-002
   - **Coverage Target**: MiniTrend 90%
2. **Integration**: Manual QA gate
   - Expand Execution History with >= 2 runs → sparkline SVG visible above entry list
   - Expand Execution History with 1 run → no sparkline rendered
   - Click "View full history" → active panel switches to HistoryPanel (Ctrl+4 equivalent)

**Implementation**:
1. In `CaseHistorySection`, after entries render:
   - Import `MiniTrend` from `../../utils/historyUtils`
   - Render `<MiniTrend entries={entries} />` above the entry list (MiniTrend handles the <2 entries null case internally)
2. Add "View full history" button/link at the bottom of the open section:
   - `onClick={() => dispatch({ type: 'SET_PANEL', panel: 'history' })}`
   - Style consistently with existing link patterns in TestsPanel
3. TypeScript check: `npx tsc --noEmit`

---

### T-012: Run full test suite and confirm zero regressions

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** all phases of implementation are complete (T-001 through T-011)
- **When** the full eval-ui Vitest suite runs
- **Then** all pre-existing tests pass, all new historyUtils and renderMarkdown tests pass, and TypeScript compilation exits with no errors

**Test Cases**:
1. **Unit + Regression**: full suite
   - All `renderMarkdown.test.ts` cases pass (coverage >= 95%)
   - All `historyUtils.test.tsx` cases pass (coverage >= 90%)
   - All pre-existing tests (`parseFrontmatter.test.ts`, `diff.test.ts`, others) still pass
   - `npx tsc --noEmit` exits 0
   - **Coverage Target**: new files >= 90%; no overall regression

**Implementation**:
1. Run full suite: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui`
2. Run TypeScript check: `npx tsc --noEmit`
3. Fix any failures discovered before marking complete
4. Mark all tasks `[x]` only after this task passes cleanly
