# Implementation Plan: Skill Studio UI Polish & Editor AI Builder

## Overview

Frontend-only changes to six components in the vskill Skill Studio (React 19 + Vite + Tailwind CSS 4). No backend changes, no new dependencies. All work reuses existing patterns: `renderMarkdown()` for markdown preview, `computeDiff` + line-by-line diff rendering from SkillImprovePanel, segmented toggle from EditorPanel, file icon badge from SkillContentViewer, and SSE streaming with AbortController from CreateSkillInline.

## Architecture

### Component Map

```
Changed files (6 components):
  src/components/CreateSkillInline.tsx   -- US-001, US-002, US-003
  src/pages/CreateSkillPage.tsx          -- US-001, US-002, US-003
  src/components/SkillContentViewer.tsx  -- US-004
  src/pages/workspace/EditorPanel.tsx    -- US-005
  src/components/LeftPanel.tsx           -- US-006

Unchanged dependencies (reused as-is):
  src/utils/renderMarkdown.ts            -- markdown-to-HTML (already used in EditorPanel)
  src/utils/diff.ts                      -- computeDiff + DiffLine type
  src/api.ts                             -- api.getSkillCreatorStatus()
  src/types.ts                           -- SkillCreatorStatus interface
```

No new files. No new components. All changes are inline modifications to existing files.

### Data Flow

```
US-001/US-002/US-003: Local state only (label text, toggle state, textarea props)
US-004: SkillContentViewer receives `content` prop -> parseFrontmatter -> renderMarkdown(body)
US-005: EditorPanel local state -> SSE fetch -> computeDiff -> inline diff rendering
US-006: LeftPanel -> useEffect -> api.getSkillCreatorStatus() -> local state -> conditional render
```

## Technology Stack

- **Framework**: React 19 + Vite (existing)
- **Styling**: Tailwind CSS 4 + inline styles with CSS custom properties (existing pattern)
- **Libraries**: None new -- everything uses existing utilities
- **Testing**: Vitest (unit tests for component behavior)

## Implementation Phases

### Phase 1: Label & Ergonomics (US-001, US-003)

Simple text and prop changes across both create forms.

**CreateSkillInline.tsx**:
- Line 584-585: Change `<h3>System Prompt</h3>` to file icon badge + "SKILL.md" label + "Skill Definition" subtitle, reusing SkillContentViewer's icon/badge pattern (lines 37-56 of SkillContentViewer)
- Line 555: Change description textarea `rows={2}` to `rows={3}`, add `minHeight: "72px"`, change `resize-none` to `resize-y`

**CreateSkillPage.tsx**:
- Line 736-738: Change `<h3>System Prompt</h3>` to the same SKILL.md file icon badge + subtitle
- Line 688-695: Change description textarea `rows={2}` to `rows={3}`, add `minHeight: "72px"`, change `resize-none` to `resize-y`

**Pattern to reuse** (from SkillContentViewer lines 37-56):
```tsx
<div className="flex items-center gap-2.5">
  <div className="w-7 h-7 rounded-lg flex items-center justify-center"
       style={{ background: "var(--accent-muted)" }}>
    <svg ...file icon... />
  </div>
  <div>
    <span className="text-[13px] font-semibold">SKILL.md</span>
    <span className="text-[11px] ml-2" style={{ color: "var(--text-tertiary)" }}>
      Skill Definition
    </span>
  </div>
</div>
```

### Phase 2: Write/Preview Toggle (US-002)

Add a segmented Write/Preview toggle to the SKILL.md body card in both create forms.

**State**: New `bodyPreviewMode` local state (`"write" | "preview"`, default `"write"`)

**Toggle UI**: Reuse EditorPanel's segmented toggle pattern (lines 121-150). Simplified to just two options (Write/Preview) instead of three (Editor/Split/Preview). Placed in the card header row next to "SKILL.md".

**Preview rendering**: When `bodyPreviewMode === "preview"`, replace the `<textarea>` with a `<div>` that uses `dangerouslySetInnerHTML={{ __html: renderMarkdown(body) }}`. Container has `maxHeight: "400px"`, `overflowY: "auto"`, and matching EditorPanel preview styling.

**Content preservation**: The `body` state variable persists regardless of toggle position -- the toggle only switches which element renders (textarea vs rendered div). No data loss.

**Both forms get identical toggle logic** -- the same state + toggle + conditional render pattern is applied to CreateSkillInline and CreateSkillPage.

### Phase 3: Markdown in SkillContentViewer (US-004)

**SkillContentViewer.tsx** lines 117-133: Replace the `<pre>` block with a rendered markdown `<div>`.

Before (current):
```tsx
<pre className="..." style={{ maxHeight: "400px", overflowY: "auto", ... }}>
  {body}
</pre>
```

After:
```tsx
<div
  className="text-[12px] leading-relaxed overflow-x-auto"
  style={{
    maxHeight: "400px",
    overflowY: "auto",
    color: "var(--text-secondary)",
    background: "var(--surface-0)",
    border: "1px solid var(--border-subtle)",
    padding: "16px",
    borderRadius: "8px",
    wordBreak: "break-word",
  }}
  dangerouslySetInnerHTML={{ __html: renderMarkdown(body) }}
/>
```

Import `renderMarkdown` from `../utils/renderMarkdown`. Retains `maxHeight: 400px` and `overflowY: auto` per AC-US4-03.

### Phase 4: AI Regenerate in EditorPanel (US-005)

The most complex change. Adds a "Regenerate" button to the EditorPanel toolbar, an inline prompt panel, SSE streaming, and diff display with Apply/Discard actions.

**State additions** (local to EditorPanel):
```ts
const [regenOpen, setRegenOpen] = useState(false);
const [regenPrompt, setRegenPrompt] = useState("");
const [regenLoading, setRegenLoading] = useState(false);
const [regenResult, setRegenResult] = useState<string | null>(null);
const [regenDiff, setRegenDiff] = useState<DiffLine[]>([]);
const [regenError, setRegenError] = useState<string | null>(null);
const regenAbortRef = useRef<AbortController | null>(null);
```

**Toolbar button**: Add a "Regenerate" button with SparkleIcon next to the existing "AI Edit" button (line 153-170 area). Uses the same styling pattern as the AI Edit button but with a sparkle icon instead of wand icon.

**Prompt panel**: When `regenOpen && !regenResult`, render a prompt textarea below the toolbar (between toolbar and editor body), similar to AiEditBar's input area. Includes a Submit button and Cancel button.

**SSE call**: Reuse the exact SSE streaming pattern from CreateSkillInline's `handleGenerate` (lines 169-241). Calls `/api/skills/generate?sse` with `POST { prompt, provider, model }`. Provider/model resolved from workspace config (matching AC-US5-07 -- no separate model picker).

**Diff rendering**: When SSE completes, compute diff via `computeDiff(skillContent, generatedBody)` and display using the identical diff line rendering pattern from SkillImprovePanel (lines 288-316) and AiEditBar (lines 250-278). Both use the same `DiffLine` iteration with green/red background and left border.

**Apply**: Replace `skillContent` via `dispatch({ type: "SET_CONTENT", content: regenResult })`. Close the diff panel.

**Discard**: Clear `regenResult`, `regenDiff`, close panel.

**Abort on re-click** (AC-US5-06): If `regenLoading` and user clicks Regenerate again, call `regenAbortRef.current?.abort()` and start new generation. Same AbortController pattern used in SkillImprovePanel.

**Cleanup on unmount**: `useEffect(() => () => { regenAbortRef.current?.abort(); }, [])` -- same pattern as SkillImprovePanel line 47-49.

**Layout**: The prompt panel and diff view render between the toolbar and the editor body area, pushing the editor content down. This avoids blocking the toolbar actions.

### Phase 5: Skill-Creator Status (US-006)

**LeftPanel.tsx**: Add a `useEffect` that calls `api.getSkillCreatorStatus()` and stores result in local state. On error, set state to `null` (graceful degradation per AC-US6-05).

**Render location**: Below the "New Skill" button (after line 76, before the skill list).

**Installed state**: Green dot (`background: #22c55e`) + "Skill Creator installed" text in `text-[11px]`.

**Not installed state**: Amber dot (`background: #f59e0b`) + "Skill Creator not installed" text + copyable code block showing `status.installCommand`. Copy button uses `navigator.clipboard.writeText()`.

**Container styling**: `px-3 py-2` with subtle background, matching sidebar density.

## Testing Strategy

Unit tests with Vitest for each user story:

- **US-001**: Verify "SKILL.md" label renders (not "System Prompt") in both forms; verify file icon badge presence; verify "Skill Definition" subtitle
- **US-002**: Verify Write/Preview toggle renders; verify textarea visible in Write mode; verify renderMarkdown output in Preview mode; verify content preserved on toggle
- **US-003**: Verify description textarea has `rows={3}`, `minHeight: 72px`, `resize: vertical`
- **US-004**: Verify SkillContentViewer renders markdown HTML (not raw pre); verify maxHeight constraint
- **US-005**: Verify Regenerate button renders in toolbar; verify prompt panel opens on click; verify diff rendering after SSE completion; verify Apply replaces content; verify Discard clears state; verify AbortController abort on re-click
- **US-006**: Verify status indicator renders for installed/not-installed states; verify hidden on error; verify copy-to-clipboard on install command click

## Technical Challenges

### Challenge 1: SSE Streaming in EditorPanel Without Duplicating Code

The SSE parsing loop (event/data parsing, AbortController management) is duplicated across SkillImprovePanel, CreateSkillInline, CreateSkillPage, and AiEditBar. Adding it to EditorPanel would be a fifth copy.

**Solution**: Inline the pattern as-is (matching existing codebase style). The SSE loop is ~30 lines and tightly coupled to component-specific state setters, making extraction into a shared hook a refactor beyond this increment's scope. All five instances follow the identical pattern, so future refactoring is straightforward.

**Risk**: Low. The pattern is battle-tested across four existing implementations.

### Challenge 2: Write/Preview Toggle Content Preservation

Switching from textarea to rendered div must not lose the user's typed content.

**Solution**: The `body` state variable is the single source of truth. The toggle only controls which DOM element renders (textarea vs div). React preserves state across re-renders. No additional preservation logic needed.

**Risk**: None. This is standard React state management.

### Challenge 3: Regenerate vs AI Edit Conflict

Both "AI Edit" and "Regenerate" produce diffs. If both are open simultaneously, the UI becomes confusing.

**Solution**: When opening the Regenerate panel, close AI Edit first (`dispatch({ type: "CLOSE_AI_EDIT" })`). When opening AI Edit, close Regenerate (`setRegenOpen(false)`). Mutual exclusion via the click handlers.

**Risk**: None. Simple state coordination.
