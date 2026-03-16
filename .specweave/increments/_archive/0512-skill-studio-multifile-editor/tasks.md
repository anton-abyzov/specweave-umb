---
increment: 0512-skill-studio-multifile-editor
title: "Skill Studio Multi-File Editor"
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001, T-002, T-003, T-004, T-005, T-006]
coverage_target: 90
---

# Tasks: Skill Studio Multi-File Editor

## User Story: US-001 - Multi-File Browsing and Viewing in Skill Studio Editor

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09, AC-US1-10, AC-US1-11, AC-US1-12, AC-US1-13, AC-US1-14, AC-US1-15
**Tasks**: 6 total, 6 completed

---

### T-001: Backend file-list and file-read endpoints

**User Story**: US-001
**Satisfies ACs**: AC-US1-08, AC-US1-09, AC-US1-11, AC-US1-13, AC-US1-14, AC-US1-15
**Status**: [x] completed

**Test Plan**:
- **Given** `GET /api/skills/:plugin/:skill/files` is called with a valid plugin/skill
- **When** the handler resolves the skill directory and walks it recursively
- **Then** it returns `{ files: [...] }` sorted SKILL.md first, dirs before files, alphabetical

- **Given** `GET /api/skills/:plugin/:skill/file?path=` is called with a path containing `../`
- **When** the resolved path falls outside the skill directory
- **Then** the server returns 403 with "access denied"

- **Given** the file endpoint is called for a file whose size exceeds 1MB
- **When** statSync reports size > 1048576
- **Then** the server returns 413 with "file too large"

- **Given** the first 8KB of a file contain a null byte (0x00)
- **When** the binary detection check runs
- **Then** the response contains `{ binary: true, size }` with no content field

- **Given** the file is between 500KB and 1MB
- **When** the content is read
- **Then** the response includes `truncated: true` and content truncated to 500KB

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes-files.test.ts`
   - `listFiles_returnsSkillMdFirst()`: valid plugin/skill returns sorted file list with SKILL.md at top
   - `listFiles_excludesDotGitAndNodeModules()`: excluded dirs are absent from results
   - `listFiles_capsAt200Entries()`: directories with 201+ files return exactly 200 entries
   - `readFile_pathTraversal_returns403()`: path `../../etc/passwd` returns 403
   - `readFile_encodedTraversal_returns403()`: path `%2e%2e%2fpasswd` after decode returns 403
   - `readFile_oversizeFile_returns413()`: file > 1MB returns 413
   - `readFile_binaryFile_returnsBinaryFlag()`: file with null byte returns `binary: true`, no content
   - `readFile_truncatedFile_returnsTruncatedFlag()`: file 600KB returns `truncated: true`
   - `readFile_missingFile_returns404()`: path to non-existent file returns 404
   - `readFile_validJsonFile_returnsContent()`: returns `{ path, content, size }`
   - **Coverage Target**: 95%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
2. Add `statSync` to existing `fs` import; add `sep` to existing `path` import
3. After the existing `GET /api/skills/:plugin/:skill/dependencies` block, add the list-files handler:
   - Resolve skill dir via `resolveSkillDir(root, plugin, skill)`
   - Recursive `readdirSync` walk excluding `.git`, `node_modules`, `.DS_Store`
   - Cap at 200 entries; sort SKILL.md first, dirs before files, then alphabetical
   - Return `{ files: [...] }`
4. Add the read-file handler:
   - Extract `path` query param; return 400 if missing
   - Path traversal guard: `resolve(join(skillDir, reqPath))` must start with `resolve(skillDir) + sep` or equal it exactly; return 403 otherwise
   - `statSync` size check: >1MB returns 413
   - Binary detection: read first 8KB, check for null byte; return `{ binary: true, size }` if found
   - Read full content with `readFileSync('utf-8')`; if size > 500KB truncate and set `truncated: true`
   - Return `{ path, content, size, truncated? }`
   - 404 for ENOENT catch
5. Write unit tests in `__tests__/api-routes-files.test.ts` (mock `fs` calls)
6. Run `npx vitest run src/eval-server/__tests__/api-routes-files.test.ts`

---

### T-002: Frontend types and API client methods

**User Story**: US-001
**Satisfies ACs**: AC-US1-14, AC-US1-15
**Status**: [x] completed

**Test Plan**:
- **Given** `api.getSkillFiles(plugin, skill)` is called
- **When** the fetch succeeds
- **Then** it returns a typed `{ files: SkillFileEntry[] }` result

- **Given** `api.getSkillFile(plugin, skill, "evals/evals.json")` is called
- **When** building the URL
- **Then** the path is URL-encoded in the query string

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/api-skill-files.test.ts`
   - `getSkillFiles_callsCorrectUrl()`: verifies fetch URL is `/api/skills/p/s/files`
   - `getSkillFile_encodesPathParam()`: path `evals/history/2026.json` is URL-encoded in query string
   - `getSkillFile_returnsTypedContent()`: response shape matches `SkillFileContent`
   - **Coverage Target**: 90%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts`
2. Add `SkillFileEntry` interface: `{ path: string; size: number; type: "file" | "dir" }`
3. Add `SkillFileContent` interface: `{ path: string; content?: string; size: number; binary?: boolean; truncated?: boolean }`
4. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts`
5. Add `getSkillFiles(plugin, skill)`: GET `/api/skills/${plugin}/${skill}/files` returns `{ files: SkillFileEntry[] }`
6. Add `getSkillFile(plugin, skill, filePath)`: GET `/api/skills/${plugin}/${skill}/file?path=${encodeURIComponent(filePath)}` returns `SkillFileContent`
7. Write unit tests mocking `fetch`
8. Run `npx vitest run src/eval-ui/src/__tests__/api-skill-files.test.ts`

---

### T-003: useSkillFiles hook

**User Story**: US-001
**Satisfies ACs**: AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-12
**Status**: [x] completed

**Test Plan**:
- **Given** the hook mounts with plugin/skill
- **When** the component renders
- **Then** `api.getSkillFiles` is called; `activeFile` is `"SKILL.md"`; `isSkillMd` is `true`

- **Given** `selectFile("evals/evals.json")` is called
- **When** the API resolves
- **Then** `activeFile` is `"evals/evals.json"`, `secondaryContent` holds the response, `isSkillMd` is `false`

- **Given** `selectFile("SKILL.md")` is called while a secondary file is active
- **When** it executes
- **Then** `activeFile` resets to `"SKILL.md"`, `secondaryContent` is `null`, `isSkillMd` is `true`

- **Given** `refresh()` is called
- **When** it executes
- **Then** `api.getSkillFiles` is called again and `activeFile` resets to `"SKILL.md"`

- **Given** `api.getSkillFile` throws an error
- **When** `selectFile` is called
- **Then** `error` state contains a message and `secondaryContent` remains null

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/useSkillFiles.test.ts`
   - `onMount_fetchesFileList()`: getSkillFiles called on mount
   - `onMount_defaultsToSkillMd()`: activeFile is "SKILL.md", isSkillMd is true
   - `selectFile_nonSkillMd_fetchesContent()`: getSkillFile called, secondaryContent populated
   - `selectFile_skillMd_clearsSecondary()`: secondaryContent null, isSkillMd true
   - `refresh_refetchesAndResetsActiveFile()`: getSkillFiles called again after refresh
   - `selectFile_apiError_setsErrorState()`: error state populated on fetch failure
   - **Coverage Target**: 95%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/useSkillFiles.ts`
2. State: `files: SkillFileEntry[]`, `activeFile: string` (default `"SKILL.md"`), `secondaryContent: SkillFileContent | null`, `loading: boolean`, `error: string | null`
3. `useEffect([plugin, skill])`: call `api.getSkillFiles(plugin, skill)`, set `files`, handle error
4. `selectFile(path)`: if `"SKILL.md"` set activeFile and clear secondaryContent; else fetch `api.getSkillFile(plugin, skill, path)` and set `activeFile` + `secondaryContent`; catch sets `error`
5. `refresh()`: re-run file list fetch, reset `activeFile` to `"SKILL.md"`, clear `secondaryContent`
6. Return: `{ files, activeFile, secondaryContent, loading, error, selectFile, refresh, isSkillMd: activeFile === "SKILL.md" }`
7. Write unit tests using `vi.mock` for `../../api`
8. Run `npx vitest run src/eval-ui/src/__tests__/useSkillFiles.test.ts`

---

### T-004: SkillFileBrowser component

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-12
**Status**: [x] completed

**Test Plan**:
- **Given** the component renders with files
- **When** it first mounts
- **Then** it is collapsed, showing only the active file path and a chevron expand button

- **Given** the component is collapsed
- **When** the user clicks the expand chevron
- **Then** the strip expands and shows a hierarchical file tree

- **Given** the tree is expanded and a file is clicked
- **When** the click fires
- **Then** `onSelectFile` is called with that file path

- **Given** a tree item has keyboard focus and Enter is pressed
- **When** the key event fires
- **Then** `onSelectFile` is called with that path

- **Given** the refresh button is clicked
- **When** it fires
- **Then** `onRefresh` callback is called

- **Given** the tree is expanded with a folder node
- **When** it renders
- **Then** the folder has `aria-expanded` attribute set appropriately

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SkillFileBrowser.test.tsx`
   - `renders_collapsedByDefault()`: only active file path visible, tree items not in DOM
   - `expandsOnChevronClick()`: tree items appear after clicking expand button
   - `collapsesOnChevronClickAgain()`: tree items hidden after second click
   - `clickFile_callsOnSelectFile()`: clicking a file item calls handler with correct path
   - `keyboardEnter_callsOnSelectFile()`: Enter key on focused item calls handler
   - `refreshButton_callsOnRefresh()`: refresh button triggers callback
   - `activeFile_isHighlighted()`: active file item has accent highlight class
   - `tree_buildsFolderHierarchy()`: nested paths render as nested folder/file nodes
   - `folderNodes_haveAriaExpanded()`: folder nodes carry aria-expanded attribute
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillFileBrowser.tsx`
2. Props: `{ files: SkillFileEntry[], activeFile: string, onSelectFile: (path: string) => void, onRefresh: () => void, loading: boolean }`
3. Local state: `expanded: boolean` (default `false`)
4. Collapsed view: single row with active file path, chevron button (toggles `expanded`), refresh button
5. `buildTree(files)` helper: split each path on `/`, construct nested nodes, sort dirs first then alphabetical, SKILL.md at root top
6. Expanded view: render tree with 24px row height, monospace font, `surface-0` background
7. Accessibility: `role="tree"` on container, `role="treeitem"` on each item, `aria-expanded` on folder nodes, `tabIndex={0}`, `onKeyDown` for Enter/ArrowUp/ArrowDown
8. Write tests using `@testing-library/react`
9. Run `npx vitest run src/eval-ui/src/__tests__/SkillFileBrowser.test.tsx`

---

### T-005: SecondaryFileViewer component

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-08, AC-US1-10, AC-US1-11
**Status**: [x] completed

**Test Plan**:
- **Given** content with `.json` extension
- **When** SecondaryFileViewer renders
- **Then** left pane shows raw text in a read-only textarea; right pane shows `JSON.stringify(parsed, null, 2)` in a `<pre>` block

- **Given** content with `.md` extension
- **When** SecondaryFileViewer renders
- **Then** left pane shows raw text; right pane shows rendered HTML via `renderMarkdown()`

- **Given** content with an unknown extension (e.g., `.sh`)
- **When** SecondaryFileViewer renders
- **Then** only a single raw-text pane spanning full width is shown

- **Given** `content.binary === true`
- **When** SecondaryFileViewer renders
- **Then** a centered message "Binary file ({size} bytes) -- cannot be displayed" is shown; no text panes

- **Given** `content.truncated === true`
- **When** SecondaryFileViewer renders
- **Then** an amber warning banner states "File content truncated for display. Original size: {size} bytes."

- **Given** content object has no content string and is not binary
- **When** SecondaryFileViewer renders
- **Then** "Unable to open file" message is shown

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/SecondaryFileViewer.test.tsx`
   - `jsonFile_rendersSplitView()`: two panes visible; right pane contains formatted JSON
   - `mdFile_rendersSplitView()`: two panes; right pane has rendered HTML
   - `unknownFile_rendersSinglePane()`: only one textarea spanning full width
   - `binaryContent_showsBinaryMessage()`: binary message rendered, no textareas
   - `truncatedContent_showsWarningBanner()`: amber banner with original size visible
   - `missingContent_showsErrorMessage()`: "Unable to open file" visible
   - `renderMarkdown_calledForMdFiles()`: renderMarkdown spy called with file content
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SecondaryFileViewer.tsx`
2. Props: `{ content: SkillFileContent | null; viewMode?: "split" | "raw" | "preview" }`
3. Guard: if `!content` render "Unable to open file" error state
4. Guard: if `content.binary` render centered "Binary file ({content.size} bytes) -- cannot be displayed"
5. Truncation banner: if `content.truncated` render amber banner "File content truncated for display. Original size: {content.size} bytes."
6. Extension detection: `ext = content.path.split('.').pop()?.toLowerCase()`
7. `.json` branch: left `<textarea readOnly>` with raw content; right `<pre>` with `JSON.stringify(JSON.parse(content.content!), null, 2)` (catch parse errors, fall back to raw)
8. `.md` branch: left `<textarea readOnly>` with raw content; right `<div dangerouslySetInnerHTML={{ __html: renderMarkdown(content.content!) }}`
9. Other: single full-width `<textarea readOnly>`
10. Mirror existing editor styles: same font-family, font-size, padding, background colors
11. Write tests using `@testing-library/react`; mock `renderMarkdown`
12. Run `npx vitest run src/eval-ui/src/__tests__/SecondaryFileViewer.test.tsx`

---

### T-006: EditorPanel integration

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Status**: [x] completed

**Test Plan**:
- **Given** EditorPanel renders with a skill selected
- **When** the component mounts
- **Then** SkillFileBrowser is rendered between the toolbar and editor body; SKILL.md editor is visible; AI Edit / Save / Regenerate buttons are visible

- **Given** the user selects a secondary file via SkillFileBrowser
- **When** isSkillMd becomes false
- **Then** SecondaryFileViewer replaces the editor textarea; AI Edit / Save / Regenerate / AiEditBar / SkillImprovePanel are hidden; breadcrumb label shows the active file path

- **Given** the user clicks SKILL.md in SkillFileBrowser while viewing a secondary file
- **When** isSkillMd becomes true
- **Then** the existing textarea editor reappears with all editing controls intact

- **Given** the user navigates to a different skill
- **When** plugin/skill props change and the component re-renders
- **Then** useSkillFiles resets; SkillFileBrowser shows SKILL.md; editor shows SKILL.md content

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/EditorPanel.integration.test.tsx`
   - `renders_skillFileBrowserAboveEditor()`: SkillFileBrowser present in DOM
   - `skillMdActive_showsEditingControls()`: Save, AI Edit buttons visible when isSkillMd true
   - `secondaryFileActive_hidesEditingControls()`: Save, AI Edit buttons absent when isSkillMd false
   - `secondaryFileActive_showsBreadcrumb()`: active file path label visible
   - `secondaryFileActive_showsSecondaryViewer()`: SecondaryFileViewer rendered
   - `skillNavigation_resetsFileState()`: re-render with different skill prop resets to SKILL.md
   - `skillMdPath_behaviorUnchanged()`: textarea still present and editable when isSkillMd true
   - **Coverage Target**: 85%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/EditorPanel.tsx`
2. Add imports: `useSkillFiles`, `SkillFileBrowser`, `SecondaryFileViewer`
3. Call `const { files, activeFile, secondaryContent, loading, selectFile, refresh, isSkillMd } = useSkillFiles(plugin, skill)` in the component body
4. Insert `<SkillFileBrowser files={files} activeFile={activeFile} onSelectFile={selectFile} onRefresh={refresh} loading={loading} />` between toolbar div and editor body div
5. Wrap editor body: if `isSkillMd` render existing textarea+preview unchanged; else render `<SecondaryFileViewer content={secondaryContent} />`
6. When `!isSkillMd`: hide AI Edit button, Regenerate button, Save/Discard buttons; show breadcrumb with `activeFile`; guard `<AiEditBar />`, regenerate panel, `<SkillImprovePanel />` with `{isSkillMd && ...}`
7. Write integration tests mocking `useSkillFiles` return values and child components
8. Run full frontend suite: `npx vitest run` from `repositories/anton-abyzov/vskill/src/eval-ui/`
9. Run full backend suite: `npx vitest run` from `repositories/anton-abyzov/vskill/src/eval-server/`
