# Architecture Plan: Skill Studio Multi-File Editor

## Overview

Add a file browser and read-only file viewer to the Skill Studio editor panel. Users can browse all files in a skill directory and view them inline without leaving the editor. SKILL.md editing remains unchanged.

## Architecture Decisions

### AD-1: Secondary file state is local to EditorPanel, not in WorkspaceContext

**Decision**: The `useSkillFiles` hook manages file list, active file path, and secondary file content as local state within EditorPanel. WorkspaceContext is not modified.

**Rationale**: No other panel (EvalPanel, HistoryPanel, ActivationPanel) needs access to the file browser state. Adding it to WorkspaceContext would unnecessarily increase the reducer surface area and cause re-renders in unrelated panels. The file browser is purely an EditorPanel concern. When the user switches skills, WorkspaceProvider remounts (keyed by plugin/skill), which naturally resets the hook state.

### AD-2: File read endpoint uses query parameter, not wildcard path segment

**Decision**: `GET /api/skills/:plugin/:skill/file?path=evals/evals.json` rather than `GET /api/skills/:plugin/:skill/files/*`.

**Rationale**: The custom Router class in `router.ts` converts `:param` segments to `([^/]+)` regex groups. It has no wildcard/splat support -- a path like `files/evals/history/2026-01-01.json` would not match a single capture group. Adding wildcard support to the router would be scope creep. A query parameter handles arbitrary depth paths cleanly and is already used by other endpoints (history filters).

**Note**: The spec mentions `GET /api/skills/:plugin/:skill/files/*` as a desired endpoint. The query-parameter approach satisfies the same AC (AC-US1-15) with identical functionality. The list endpoint remains at `GET /api/skills/:plugin/:skill/files` (AC-US1-14).

### AD-3: Flat file list from backend, tree built on client

**Decision**: The `/files` endpoint returns a flat array of `{ path, size, type }` entries. The SkillFileBrowser component builds the hierarchical tree structure on the client side from the flat list.

**Rationale**: A flat list is simpler to produce server-side (single `readdirSync` walk), simpler to cache, and smaller over the wire. Building a tree from sorted path strings is a ~15-line client function. Typical skill directories have 5-50 files, so client-side tree construction is instantaneous.

### AD-4: Binary detection via null byte scan

**Decision**: The file-read endpoint reads the first 8KB of the file and checks for null bytes (`0x00`). If found, the response returns `{ binary: true, size }` with no content.

**Rationale**: This matches the spec requirement (AC-US1-11). The approach is the same heuristic used by `git diff` and most editors. False positive risk is negligible for the file types found in skill directories (markdown, JSON, text).

### AD-5: Path traversal protection via resolve + startsWith

**Decision**: The file-read endpoint uses `path.resolve(path.join(skillDir, requestedPath))` and checks that the resolved path starts with `path.resolve(skillDir)`. This is identical to the existing pattern on line 249 of api-routes.ts (the delete endpoint).

**Rationale**: Reuses a proven pattern already in the codebase. Handles encoded sequences, `..`, symlinks (after resolution), and edge cases. Returns 403 on violation per AC-US1-13.

## Component Architecture

```
EditorPanel.tsx
  |
  +-- useSkillFiles(plugin, skill)          # NEW hook: file list + active file + content
  |     - files: SkillFileEntry[]
  |     - activeFile: string                # default "SKILL.md"
  |     - secondaryContent: SkillFileContent | null
  |     - loading, error
  |     - selectFile(path), refresh()
  |     - isSkillMd: boolean
  |
  +-- <SkillFileBrowser />                  # NEW: collapsible strip between toolbar and editor body
  |     - collapsed by default
  |     - shows active file path when collapsed
  |     - expands to show tree with folders/files
  |     - onClick -> selectFile(path)
  |     - refresh button
  |
  +-- (existing editor)                     # when isSkillMd === true, zero changes
  |
  +-- <SecondaryFileViewer />               # NEW: when isSkillMd === false
        - .json -> raw text + formatted JSON
        - .md -> raw text + rendered markdown
        - other -> raw text only
        - binary -> error message
        - truncated -> warning banner
```

## Data Flow

```
1. Skill selected in sidebar
   -> WorkspaceProvider remounts (plugin, skill change)
   -> useSkillFiles() mounts, fetches GET /api/skills/:plugin/:skill/files
   -> stores file list in local state, activeFile = "SKILL.md"

2. User expands file browser, clicks "evals/evals.json"
   -> useSkillFiles.selectFile("evals/evals.json")
   -> fetches GET /api/skills/:plugin/:skill/file?path=evals/evals.json
   -> stores response in secondaryContent, sets activeFile
   -> isSkillMd becomes false
   -> EditorPanel renders <SecondaryFileViewer /> instead of textarea

3. User clicks "SKILL.md" in file browser
   -> useSkillFiles.selectFile("SKILL.md")
   -> isSkillMd becomes true, secondaryContent cleared
   -> EditorPanel renders existing editor (unchanged)

4. User clicks refresh in file browser
   -> useSkillFiles.refresh()
   -> re-fetches file list from backend
```

## Backend Changes

### File: `src/eval-server/api-routes.ts`

Two new route registrations inside `registerRoutes()`, added after the existing `GET /api/skills/:plugin/:skill/dependencies` block.

**Endpoint 1: List files**

```
GET /api/skills/:plugin/:skill/files
```

- Resolves skill directory via `resolveSkillDir(root, params.plugin, params.skill)`
- Path containment guard: resolved dir must be under root (same as delete endpoint)
- Recursive directory walk using `readdirSync({ withFileTypes: true, recursive: true })`
- Exclusions: `.git`, `node_modules`, `.DS_Store`
- Response: `{ files: [{ path: string, size: number, type: "file" | "dir" }] }`
- Sorting: SKILL.md first, directories before files, then alphabetical
- Cap: 200 entries max to prevent abuse on huge directories

**Endpoint 2: Read file**

```
GET /api/skills/:plugin/:skill/file?path=<relative-path>
```

- Extracts `path` from URL query string
- Path traversal guard: `resolve(join(skillDir, path)).startsWith(resolve(skillDir) + sep)` or exact match -- returns 403 on violation
- `statSync` for size check: >1MB returns 413
- Binary detection: reads first 8KB, checks for null bytes
- Content read: `readFileSync` with utf-8 encoding
- Truncation: if size > 500KB, truncates to 500KB and sets `truncated: true`
- Response: `{ path, content, size, binary?, truncated? }`
- 404 for missing files, 403 for path traversal, 413 for oversize

**New imports needed**: `statSync` (add to existing `fs` import), `sep` from `node:path` (add to existing `path` import).

### File: `src/eval-server/router.ts`

No changes. The router already supports `:param` patterns which is sufficient for both endpoints.

## Frontend Changes

### File: `src/eval-ui/src/types.ts`

Add two new interfaces:

```typescript
export interface SkillFileEntry {
  path: string;
  size: number;
  type: "file" | "dir";
}

export interface SkillFileContent {
  path: string;
  content?: string;
  size: number;
  binary?: boolean;
  truncated?: boolean;
}
```

### File: `src/eval-ui/src/api.ts`

Add two new methods to the `api` object:

```typescript
getSkillFiles(plugin: string, skill: string): Promise<{ files: SkillFileEntry[] }>
getSkillFile(plugin: string, skill: string, filePath: string): Promise<SkillFileContent>
```

The `getSkillFile` method URL-encodes the path parameter in the query string.

### File: `src/eval-ui/src/pages/workspace/useSkillFiles.ts` (NEW)

Custom hook managing all file browser state.

**State**:
- `files: SkillFileEntry[]` -- flat list from backend
- `activeFile: string` -- currently selected file path, default `"SKILL.md"`
- `secondaryContent: SkillFileContent | null` -- loaded content for non-SKILL.md files
- `loading: boolean` -- true during file list or content fetch
- `error: string | null`

**Effects**:
- On mount (plugin/skill change): fetch file list via `api.getSkillFiles()`
- `selectFile(path)`: if path is `"SKILL.md"`, sets activeFile and clears secondaryContent. Otherwise, fetches content via `api.getSkillFile()` and stores it.
- `refresh()`: re-fetches file list, resets to SKILL.md

**Return value**:
```typescript
{
  files, activeFile, secondaryContent,
  loading, error,
  selectFile, refresh,
  isSkillMd: activeFile === "SKILL.md"
}
```

### File: `src/eval-ui/src/components/SkillFileBrowser.tsx` (NEW)

Collapsible horizontal strip that sits between the toolbar and editor body.

**Props**:
```typescript
{
  files: SkillFileEntry[];
  activeFile: string;
  onSelectFile: (path: string) => void;
  onRefresh: () => void;
  loading: boolean;
}
```

**Behavior**:
- Collapsed by default: single row showing the active file path with a chevron expand button and a refresh button
- Expanded: indented tree built from flat file paths. Folders shown with folder icon (reuse SVG from SkillFileTree.tsx). Files shown with file icon (same source). Active file highlighted with accent color background.
- Tree construction: split each `path` by `/`, build nested nodes, sort directories first then alphabetical. Place SKILL.md at top of root level.
- Compact styling: 24px row height, monospace font, `surface-0` background
- Accessibility: `role="tree"`, `role="treeitem"`, `aria-expanded` on folders, `tabIndex={0}` with Enter to select, ArrowUp/Down navigation

### File: `src/eval-ui/src/components/SecondaryFileViewer.tsx` (NEW)

Read-only viewer for non-SKILL.md files.

**Props**:
```typescript
{
  content: SkillFileContent;
  viewMode: "split" | "raw" | "preview";
}
```

**Rendering logic by file extension**:
- `.json`: raw text on left (read-only textarea), formatted JSON on right (JSON.stringify with 2-space indent, rendered in a `<pre>` block)
- `.md`: raw text on left, rendered HTML on right (reuse `renderMarkdown()` from `utils/renderMarkdown.ts`)
- Other extensions: raw text only in a read-only textarea, spanning full width regardless of viewMode
- Binary files (`content.binary === true`): centered message "Binary file ({size} bytes) -- cannot be displayed"
- Truncated files (`content.truncated === true`): amber warning banner at top: "File content truncated for display. Original size: {size} bytes."
- Error state (no content, not binary): "Unable to open file" with error details

**Styling**: Mirrors the existing editor pane (same font family, font size, padding, background colors) for visual consistency.

### File: `src/eval-ui/src/pages/workspace/EditorPanel.tsx` (MODIFIED)

Minimal changes to integrate the file browser and secondary viewer.

**Additions**:
1. Import `useSkillFiles` hook, `SkillFileBrowser`, `SecondaryFileViewer`
2. Call `useSkillFiles(plugin, skill)` in the component body
3. Insert `<SkillFileBrowser />` between the toolbar div and the editor body div
4. Wrap the editor body in a conditional:
   - `isSkillMd === true`: render existing textarea + preview (zero changes to this path)
   - `isSkillMd === false`: render `<SecondaryFileViewer content={secondaryContent} viewMode={viewMode} />`
5. When viewing a secondary file, hide: AI Edit button, Regenerate button, Save/Discard buttons. Show: file path as a breadcrumb label.
6. When viewing a secondary file, do not render `<AiEditBar />`, regenerate panel, or `<SkillImprovePanel />` (these are already conditionally rendered, but guard them with `isSkillMd` as well).

**Key constraint**: The `isSkillMd === true` path must remain byte-identical in behavior. No WorkspaceContext changes, no reducer changes, no state shape changes.

## File Inventory

| File | Action | Lines (est.) |
|------|--------|-------------|
| `src/eval-server/api-routes.ts` | Modify -- add 2 endpoints | +80 |
| `src/eval-ui/src/types.ts` | Modify -- add 2 interfaces | +12 |
| `src/eval-ui/src/api.ts` | Modify -- add 2 methods | +12 |
| `src/eval-ui/src/pages/workspace/useSkillFiles.ts` | New | ~80 |
| `src/eval-ui/src/components/SkillFileBrowser.tsx` | New | ~150 |
| `src/eval-ui/src/components/SecondaryFileViewer.tsx` | New | ~120 |
| `src/eval-ui/src/pages/workspace/EditorPanel.tsx` | Modify -- integrate | +30, ~10 moved |

All paths relative to `repositories/anton-abyzov/vskill/`.

## Implementation Order

1. **Backend endpoints** (api-routes.ts) -- no frontend dependencies, can be tested with curl
2. **Frontend types + API client** (types.ts, api.ts) -- type foundation for frontend work
3. **useSkillFiles hook** -- core state management, unit-testable
4. **SkillFileBrowser component** -- interactive tree UI
5. **SecondaryFileViewer component** -- read-only viewer with file-type detection
6. **EditorPanel integration** -- wire everything together

Steps 4 and 5 can be done in parallel since they are independent components.

## Security Considerations

- Path traversal protection (AD-5) is the primary security concern. The `resolve + startsWith` check on the file-read endpoint is critical.
- The file-list endpoint only returns paths relative to the skill directory -- no absolute paths are leaked.
- File size limits (1MB hard cap, 500KB display truncation) prevent memory exhaustion on the server and browser.
- Symlinks are followed by `readFileSync` by default. The `startsWith` check operates on the resolved real path, so a symlink pointing outside the skill directory will be blocked.
- No user input is interpolated into HTML. The SecondaryFileViewer uses `dangerouslySetInnerHTML` only for markdown rendering (same pattern as existing EditorPanel preview pane, using the same `renderMarkdown()` function).

## Testing Strategy

- **Backend unit tests**: Test both endpoints with valid paths, path traversal attempts, binary files, oversize files, missing files, empty directories
- **useSkillFiles hook tests**: Mock `api.getSkillFiles` and `api.getSkillFile`, verify state transitions for selectFile, refresh, error handling
- **SkillFileBrowser tests**: Render with various file lists, verify tree structure, click handlers, collapsed/expanded states, keyboard navigation
- **SecondaryFileViewer tests**: Render with JSON content (verify formatting), markdown content (verify renderMarkdown called), binary flag, truncated flag, error state
- **EditorPanel integration tests**: Verify SKILL.md editing path is unchanged, verify secondary file display, verify toolbar changes when viewing secondary files
