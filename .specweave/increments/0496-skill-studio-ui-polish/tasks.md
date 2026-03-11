---
increment: 0496-skill-studio-ui-polish
total_tasks: 9
completed_tasks: 9
---

# Tasks: Skill Studio UI Polish & Editor AI Builder

## User Story: US-001 - Rename "System Prompt" to "SKILL.md"

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 1 total, 0 completed

### T-001: Replace "System Prompt" heading with SKILL.md file icon badge in both create forms

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** CreateSkillInline is rendered
- **When** the user views the body textarea card header
- **Then** the heading reads "SKILL.md" with a file icon badge and "Skill Definition" subtitle (not "System Prompt")

- **Given** CreateSkillPage is rendered
- **When** the user views the body textarea card header
- **Then** the same "SKILL.md" file icon badge + "Skill Definition" subtitle pattern is present

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - rendersSkillMdHeading(): Query for text "SKILL.md", assert present; query for "System Prompt", assert absent
   - rendersFileIconBadge(): Assert SVG icon badge element exists in the SKILL.md header row
   - rendersSkillDefinitionSubtitle(): Assert "Skill Definition" subtitle text is present
   - **Coverage Target**: 90%

2. **Unit**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
   - rendersSkillMdHeadingOnPage(): Assert "SKILL.md" heading present; assert "System Prompt" absent
   - rendersSubtitleOnPage(): Assert "Skill Definition" subtitle present
   - **Coverage Target**: 90%

**Implementation**:
1. In `CreateSkillInline.tsx` (~line 584): Replace `<h3>System Prompt</h3>` with the file icon badge + "SKILL.md" + "Skill Definition" subtitle pattern reused from SkillContentViewer (lines 37-56)
2. In `CreateSkillPage.tsx` (~line 736): Apply the identical heading replacement
3. Run: `npx vitest run src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`

---

## User Story: US-002 - Write/Preview Toggle for SKILL.md Body

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 1 total, 0 completed

### T-002: Add segmented Write/Preview toggle to SKILL.md card in both create forms

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** CreateSkillInline with the SKILL.md card visible
- **When** the component renders
- **Then** a segmented toggle with "Write" and "Preview" options is present, defaulting to "Write"

- **Given** Preview mode is active
- **When** the card body renders
- **Then** the body is displayed as rendered markdown HTML using dangerouslySetInnerHTML

- **Given** the user switches between Write and Preview
- **When** switching back to Write
- **Then** the previously typed content is still present in the textarea (no data loss)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - rendersWritePreviewToggle(): Assert both "Write" and "Preview" buttons exist; assert "Write" is active by default
   - showsTextareaInWriteMode(): Assert textarea visible; assert markdown preview div absent in Write mode
   - showsMarkdownInPreviewMode(): Click "Preview", assert textarea absent; assert dangerouslySetInnerHTML div present
   - preservesContentOnToggle(): Type in textarea, switch to Preview, switch back to Write; assert textarea value unchanged
   - **Coverage Target**: 90%

2. **Unit**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
   - rendersToggleOnPage(): Assert Write/Preview toggle present on CreateSkillPage
   - previewRendersMarkdownOnPage(): Toggle to Preview, assert markdown div rendered
   - **Coverage Target**: 90%

**Implementation**:
1. Add `const [bodyPreviewMode, setBodyPreviewMode] = useState<"write" | "preview">("write")` to CreateSkillInline state
2. Add the two-option segmented toggle UI (Write/Preview) in the SKILL.md card header row, reusing EditorPanel's toggle pattern
3. In card body: conditionally render `<textarea>` (Write) or `<div dangerouslySetInnerHTML={{ __html: renderMarkdown(body) }}>` (Preview) with maxHeight 400px, overflowY auto
4. Repeat steps 1-3 for CreateSkillPage
5. Run: `npx vitest run src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`

---

## User Story: US-003 - Increase Description Textarea Height

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 1 total, 0 completed

### T-003: Update description textarea to rows=3, minHeight 72px, vertical resize in both create forms

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** CreateSkillInline is rendered
- **When** the description textarea renders
- **Then** it has rows=3, minHeight 72px in inline style, and CSS resize set to "vertical"

- **Given** CreateSkillPage is rendered
- **When** the description textarea renders
- **Then** the same rows=3, minHeight 72px, resize vertical are applied

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx`
   - descriptionTextareaHasRows3(): Query description textarea, assert rows attribute equals 3
   - descriptionTextareaHasMinHeight(): Assert inline style includes minHeight "72px"
   - descriptionTextareaResizesVertically(): Assert resize style is "vertical" not "none"
   - **Coverage Target**: 90%

2. **Unit**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`
   - descriptionTextareaHasRows3OnPage(): Assert description textarea rows=3
   - descriptionTextareaResizesVerticallyOnPage(): Assert resize vertical
   - **Coverage Target**: 90%

**Implementation**:
1. In `CreateSkillInline.tsx` (~line 555): Change `rows={2}` to `rows={3}`, add `minHeight: "72px"` to inline style, replace `resize-none` with `resize-y` (or set `style={{ resize: "vertical" }}`)
2. In `CreateSkillPage.tsx` (~line 688): Apply the same three changes to the description textarea
3. Run: `npx vitest run src/eval-ui/src/components/__tests__/CreateSkillInline.test.tsx src/eval-ui/src/pages/__tests__/CreateSkillPage.test.tsx`

---

## User Story: US-004 - Render SKILL.md Body as Markdown in SkillContentViewer

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 1 total, 0 completed

### T-004: Replace raw pre block with renderMarkdown() in SkillContentViewer

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** SkillContentViewer receives a skill with a markdown body
- **When** the component renders
- **Then** the body is displayed as rendered markdown HTML, not a raw pre element, with maxHeight 400px and overflowY auto scroll

- **Given** the body contains headings, bold, code blocks, lists, and tables
- **When** rendered
- **Then** all markdown elements display as styled HTML matching the EditorPanel preview pane

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/SkillContentViewer.test.tsx`
   - rendersMarkdownNotPreTag(): Assert no pre element in body output; assert a div with dangerouslySetInnerHTML is rendered
   - rendersMarkdownHeadings(): Pass body with "# Heading", assert rendered HTML contains h1 or h2 tag
   - rendersMarkdownCodeBlocks(): Pass body with fenced code block, assert rendered HTML contains code element
   - maintainsMaxHeightConstraint(): Assert container div has inline style maxHeight "400px" and overflowY "auto"
   - **Coverage Target**: 90%

**Implementation**:
1. In `SkillContentViewer.tsx`: Add import for `renderMarkdown` from `../utils/renderMarkdown`
2. Replace the `<pre>` block (~lines 117-133) with a `<div dangerouslySetInnerHTML={{ __html: renderMarkdown(body) }}>` with maxHeight 400px, overflowY auto, padding 16px, borderRadius 8px, var(--surface-0) background, var(--border-subtle) border
3. Run: `npx vitest run src/eval-ui/src/components/__tests__/SkillContentViewer.test.tsx`

---

## User Story: US-005 - AI Regenerate on Editor Page

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06, AC-US5-07
**Tasks**: 3 total, 0 completed

### T-005: Add "Regenerate" button with sparkle icon to EditorPanel toolbar

**User Story**: US-005
**Satisfies ACs**: AC-US5-01
**Status**: [x] completed

**Test Plan**:
- **Given** the EditorPanel is rendered with a skill loaded
- **When** the toolbar renders
- **Then** a "Regenerate" button with a sparkle icon appears next to the existing "AI Edit" button

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`
   - rendersRegenerateButton(): Assert button with text "Regenerate" exists in the toolbar
   - rendersSparkleIcon(): Assert sparkle SVG icon is present inside the Regenerate button
   - **Coverage Target**: 90%

**Implementation**:
1. In `EditorPanel.tsx` (~line 153-170 toolbar area): Add a "Regenerate" button with SparkleIcon using the same styling as "AI Edit" button
2. Wire onClick to toggle `regenOpen` state (state additions done in T-006)
3. Run: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`

---

### T-006: Add Regenerate prompt panel and SSE streaming with diff display

**User Story**: US-005
**Satisfies ACs**: AC-US5-02, AC-US5-03, AC-US5-06, AC-US5-07
**Status**: [x] completed

**Test Plan**:
- **Given** the user clicks "Regenerate"
- **When** the panel opens
- **Then** a prompt textarea is displayed below the toolbar

- **Given** the user submits a prompt
- **When** the SSE stream to /api/skills/generate?sse completes
- **Then** a diff view is shown with line-by-line green/red highlighting using computeDiff

- **Given** a regeneration is already in progress
- **When** the user clicks "Regenerate" again
- **Then** the SSE stream is aborted via AbortController and a new generation starts

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`
   - showsPromptPanelOnRegenClick(): Click Regenerate, assert prompt textarea appears below toolbar
   - hidesPromptPanelByDefault(): Assert prompt textarea absent before Regenerate is clicked
   - callsSseEndpointOnSubmit(): Mock fetch, submit prompt, assert fetch called with /api/skills/generate?sse and correct body
   - showsDiffAfterSseComplete(): Mock SSE response, assert diff view renders with colored lines
   - abortsExistingStreamOnReclick(): Start generation, click Regenerate again, assert AbortController.abort() was called
   - usesWorkspaceProviderModel(): Assert SSE request body includes provider/model from workspace config
   - **Coverage Target**: 85%

**Implementation**:
1. Add state vars to EditorPanel: `regenOpen`, `regenPrompt`, `regenLoading`, `regenResult`, `regenDiff`, `regenError`, and `regenAbortRef = useRef<AbortController | null>(null)`
2. Add `useEffect` cleanup: `() => { regenAbortRef.current?.abort(); }`
3. Implement `handleRegenSubmit()` reusing SSE streaming pattern from CreateSkillInline's `handleGenerate` — calls POST `/api/skills/generate?sse` with `{ prompt, provider, model }` from workspace config
4. On SSE completion: compute `computeDiff(skillContent, generatedBody)`, store in `regenDiff` and `regenResult`
5. Render prompt panel (textarea + Submit + Cancel buttons) when `regenOpen && !regenResult`
6. Render line-by-line diff view when `regenResult` is set, using the identical rendering pattern from SkillImprovePanel (green/red line backgrounds + left border)
7. Run: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`

---

### T-007: Implement Apply and Discard actions for Regenerate diff

**User Story**: US-005
**Satisfies ACs**: AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** the diff is displayed after SSE completes
- **When** the user clicks "Apply"
- **Then** the editor content is replaced with the generated content and the diff panel closes

- **Given** the diff is displayed
- **When** the user clicks "Discard"
- **Then** the generated content is discarded, the diff panel closes, and editor content is unchanged

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`
   - applyReplacesEditorContent(): After SSE completes, click Apply, assert dispatch called with SET_CONTENT and generated content
   - applyClosesDiffPanel(): After Apply, assert diff panel no longer rendered
   - discardPreservesEditorContent(): After SSE completes, click Discard, assert dispatch NOT called with SET_CONTENT
   - discardClosesDiffPanel(): After Discard, assert diff panel no longer rendered
   - **Coverage Target**: 90%

**Implementation**:
1. Implement `handleRegenApply()`: call `dispatch({ type: "SET_CONTENT", content: regenResult })`, then reset regen state (clear regenResult, regenDiff, set regenOpen false)
2. Implement `handleRegenDiscard()`: reset regen state without dispatching SET_CONTENT
3. Wire "Apply" and "Discard" buttons in the diff panel UI
4. Add mutual exclusion: opening Regenerate closes AI Edit (`dispatch({ type: "CLOSE_AI_EDIT" })`); opening AI Edit closes Regenerate (`setRegenOpen(false)`)
5. Run: `npx vitest run src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx`

---

## User Story: US-006 - Skill-Creator Installation Check

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Tasks**: 2 total, 0 completed

### T-008: Fetch and display Skill-Creator installation status in LeftPanel sidebar

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-05
**Status**: [x] completed

**Test Plan**:
- **Given** the LeftPanel sidebar renders
- **When** the component mounts
- **Then** it calls api.getSkillCreatorStatus() and displays a status indicator below the "New Skill" button area

- **Given** Skill-Creator is installed (status.installed === true)
- **When** the indicator renders
- **Then** a green dot with "Skill Creator installed" text is shown

- **Given** Skill-Creator is NOT installed (status.installed === false)
- **When** the indicator renders
- **Then** an amber dot with "Skill Creator not installed" text and install command code block are shown

- **Given** the status check fails (network error)
- **When** the indicator renders
- **Then** no indicator is shown (graceful degradation, no error message)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/LeftPanel.test.tsx`
   - callsGetSkillCreatorStatusOnMount(): Assert api.getSkillCreatorStatus called once after mount
   - showsGreenDotWhenInstalled(): Mock api returning `{ installed: true }`, assert green dot and "Skill Creator installed" text present
   - showsAmberDotWhenNotInstalled(): Mock api returning `{ installed: false, installCommand: "vskill install ..." }`, assert amber dot and "Skill Creator not installed" text present; assert install command code block visible
   - hidesIndicatorOnError(): Mock api rejecting, assert no status indicator rendered
   - **Coverage Target**: 90%

**Implementation**:
1. In `LeftPanel.tsx`: Add `const [creatorStatus, setCreatorStatus] = useState<{ installed: boolean; installCommand?: string } | null>(null)` state
2. Add `useEffect` that calls `api.getSkillCreatorStatus()` on mount, sets state on success, leaves state null on error (catch silently)
3. Render status indicator below the "New Skill" button: green dot + "Skill Creator installed" when `creatorStatus.installed`, amber dot + "Skill Creator not installed" + code block when `!creatorStatus.installed`
4. Render nothing when `creatorStatus === null`
5. Run: `npx vitest run src/eval-ui/src/components/__tests__/LeftPanel.test.tsx`

---

### T-009: Copy install command to clipboard on code block click

**User Story**: US-006
**Satisfies ACs**: AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** Skill-Creator is NOT installed and the install command code block is visible
- **When** the user clicks the code block or copy button
- **Then** the install command text is copied to the clipboard via navigator.clipboard.writeText()

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/LeftPanel.test.tsx`
   - copiesInstallCommandOnCodeBlockClick(): Mock navigator.clipboard.writeText, click the code block, assert writeText called with the install command string
   - showsVisualFeedbackAfterCopy(): After click, assert button or label briefly shows "Copied!" (if implemented)
   - **Coverage Target**: 85%

**Implementation**:
1. In the "not installed" render branch: add an onClick handler to the code block (or a copy icon button) that calls `navigator.clipboard.writeText(creatorStatus.installCommand)`
2. Optionally add brief "Copied!" state feedback with a `useState` boolean that resets after 2 seconds
3. Run: `npx vitest run src/eval-ui/src/components/__tests__/LeftPanel.test.tsx`
