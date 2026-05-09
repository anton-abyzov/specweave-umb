# Tasks: Skill Studio — in-panel install feedback + escape hotkey

## Task Notation
- `[T###]`: Task ID
- `[ ]` not started, `[x]` completed
- TDD: each task lands red→green→refactor

---

## Phase 1: TDD RED — failing tests for InstallPanel feedback banner

### T-001: Write failing tests for FeedbackBanner success/error state
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.feedback.test.tsx` (new)

**Test Plan**:
- **TC-001 success banner**: Given the InstallPanel is rendered with a safe skill name and `navigator.clipboard.writeText` is mocked to resolve, When the user clicks the primary "Install" button, Then the DOM contains an element with `data-testid="studio-install-feedback-success"` whose text matches `/Copied — paste in your terminal/i` and includes the copied command verbatim.
- **TC-002 error banner**: Given clipboard.writeText is mocked to reject AND `document.execCommand('copy')` is stubbed to return false, When the user clicks "Install", Then the DOM contains `[data-testid="studio-install-feedback-error"]` with text matching `/Copy failed/i`.
- **TC-003 a11y attributes**: Given the success banner is rendered, Then the banner element has `role="status"` and `aria-live="polite"`.
- **TC-004 legacy selector preserved**: Given the success banner is rendered, Then the legacy `[data-testid="studio-install-toast"]` selector still matches the same element (test compatibility).
- **TC-005 banner position**: Given both Install button and TerminalBlock are in the DOM, When success banner shows, Then the banner appears in document order between the Install button and the TerminalBlock.

### T-002: Write failing tests for shared variant-copy feedback
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**File**: same as T-001

**Test Plan**:
- **TC-006**: Given clipboard mock resolves, When the user clicks `[data-testid="studio-install-copy-bun"]`, Then `[data-testid="studio-install-feedback-success"]` shows the bun command.
- **TC-007**: Given clipboard mock resolves, When the user clicks `[data-testid="studio-install-copy-pnpm"]`, Then the banner shows the pnpm command.

### T-003: Write failing test for auto-dismiss + restart
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**File**: same as T-001

**Test Plan**:
- **TC-008**: Given the success banner is visible at t=0, When 6000ms elapses (fake timers), Then `[data-testid="studio-install-feedback-success"]` is removed from the DOM.
- **TC-009**: Given the banner has been dismissed, When the user clicks Install again, Then a fresh success banner re-appears.

---

## Phase 2: TDD RED — failing tests for DetailHeader Escape

### T-004: Write failing tests for DetailHeader Escape navigation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/__tests__/DetailHeader.test.tsx` (new)

**Test Plan**:
- **TC-010**: Given DetailHeader is rendered with `backHref="/studio/find?q=foo"` and the Next.js router is mocked, When `keydown` Escape fires on `window`, Then `router.push("/studio/find?q=foo")` is called once.
- **TC-011**: Given DetailHeader is rendered, Then a `<kbd>` with text `Esc` is visible next to the back link.
- **TC-012**: Given DetailHeader is rendered, Then the back link has accessible text `← Back to results`.

### T-005: Write failing tests for palette-deference + editable bail
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**File**: same as T-004

**Test Plan**:
- **TC-013**: Given the DOM contains `<div role="dialog" aria-modal="true" data-testid="search-palette-open"></div>` (simulated palette), When Escape fires, Then `router.push` is NOT called.
- **TC-014**: Given an `<input>` is focused, When Escape fires, Then `router.push` is NOT called.
- **TC-015**: Given a `<textarea>` is focused, When Escape fires, Then `router.push` is NOT called.
- **TC-016**: Given an element with `contenteditable="true"` is focused, When Escape fires, Then `router.push` is NOT called.

### T-006: Write failing test for listener lifecycle
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**File**: same as T-004

**Test Plan**:
- **TC-017**: Given DetailHeader is mounted then unmounted, When the unmount completes, Then `window.removeEventListener('keydown', handler)` was called with the same handler reference passed to `addEventListener`.

---

## Phase 3: TDD RED — failing test for next-step focus nudge

### T-007: Write failing test for back-link focus on success
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/__tests__/install-success-focus.test.tsx` (new — integration test wiring InstallPanel + DetailHeader)

**Test Plan**:
- **TC-018**: Given a test harness renders both `<DetailHeader backHref="/studio/find" />` and `<InstallPanel ... />`, When the user clicks Install successfully, Then the back link element receives keyboard focus (`document.activeElement === backLink`).
- **TC-019**: Given `prefers-reduced-motion: reduce` is set in the test environment, When focus is moved to the back link, Then `focus({ preventScroll: true })` was called (assert via spy).

---

## Phase 4: TDD GREEN — implementation

### T-008: Create DetailHeader.tsx client component
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01..05 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/DetailHeader.tsx` (new)

**Implementation**:
- `"use client"` directive
- Props: `{ backHref: string }`
- Renders `<Link href={backHref}>← Back to results</Link>` + `<kbd>Esc</kbd>` chip styled like SearchPalette's
- `useEffect` registers `window` keydown for Escape
- Predicate: skip if `document.querySelector('[role="dialog"][aria-modal="true"]')` truthy
- Predicate: skip if `document.activeElement` matches `INPUT | TEXTAREA | SELECT | [contenteditable="true"]`
- Otherwise `router.push(backHref)`
- Listens for custom event `studio-focus-back-link` and calls `linkRef.current?.focus({ preventScroll: true })`
- Unregister both listeners on unmount

**Test ref**: T-004, T-005, T-006

### T-009: Wire DetailHeader into page.tsx
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/page.tsx`

**Implementation**:
- Replace inline `<Link href={backHref}>← Back to results</Link>` with `<DetailHeader backHref={backHref} />`
- Remove `backLinkStyle` if no longer used (or keep if still referenced elsewhere)

**Test ref**: existing `studio-detail-back-link` selector still matches (regression check)

### T-010: Refactor InstallPanel feedback state machine
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01..06 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx`

**Implementation**:
- Replace `const [toast, setToast] = useState<string | null>(null)` with `const [feedback, setFeedback] = useState<{ state: 'idle' | 'success' | 'error'; command: string | null }>({ state: 'idle', command: null })`
- New constant `FEEDBACK_DURATION_MS = 6000`
- `runInstallAction` and per-variant copy handlers set `feedback` based on `copyViaClipboard` outcome (true → success, false → error)
- On success: dispatch `new CustomEvent('studio-focus-back-link')` so DetailHeader focuses the back link
- Replace the `toast && (<div ...>)` block with a `<FeedbackBanner state={feedback.state} command={feedback.command} />` component (inline in same file or local helper)
- Banner uses `--status-success-*` for success, `--status-danger-*` for error, fontSize `0.9375rem`, padding `0.6rem 0.75rem`, prominent leading `✓` or `✕` glyph
- Banner sits between the primary Install button and the TerminalBlock (move JSX order accordingly)
- Banner element exposes both `data-testid="studio-install-toast"` (legacy) AND `data-testid="studio-install-feedback-success"` / `studio-install-feedback-error`

**Test ref**: T-001, T-002, T-003, T-007

### T-011: Verify focus-event wiring end-to-end
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01..03 | **Status**: [x] completed

**Implementation**:
- Run integration tests T-007 against the wired DetailHeader + InstallPanel
- Confirm `document.activeElement` lands on the back link after a successful copy
- Confirm `preventScroll: true` is honored (spy on `Element.prototype.focus`)

---

## Phase 5: TDD REFACTOR + polish

### T-012: Extract `<FeedbackBanner>` if it grows beyond 30 lines
**Status**: [x] completed
- Only extract if the inline JSX in `InstallPanel.tsx` becomes hard to read.
- Otherwise leave inline and add a one-line comment marking the role.

### T-013: Update e2e Playwright spec
**User Story**: US-001 + US-002 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill-platform/e2e/studio-install-feedback.spec.ts` (new)

**Test Plan** (Playwright):
- Navigate to a seeded skill detail page
- Click `[data-testid="studio-install-primary-button"]`
- Expect `[data-testid="studio-install-feedback-success"]` visible with command text
- Press `Escape`
- Expect URL to match `/studio/find?q=...`

### T-014: Manual preview verification
**Status**: [x] completed
- `preview_start` the platform dev server
- Navigate to `/studio/find/anthropics/skills/webapp-testing`
- `preview_click` the Install button
- `preview_screenshot` to confirm banner is prominent and readable
- `preview_eval` to dispatch `Escape` and confirm router round-trip

---

## Phase 6: Closure
- [x] [T-015] Run `npx vitest run` in vskill-platform — all green
- [x] [T-016] Run `npx playwright test studio-install-feedback.spec.ts` — green
- [x] [T-017] `/sw:done 0835` — code-review + simplify + grill + judge-llm + PM gates
