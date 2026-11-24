# Background computer use without interrupting human pointer input

## Problem

SpecWithCode's macOS `computer_*` driver (`apps/desktop/src/computerUse/MacComputerUse.ts` and `computerUseSteps.ts`) currently executes every click, key, scroll, drag, and text entry through the global HID event tap (`CGEventPost(kCGHIDEventTap, ...)`) and `Electron.clipboard` + Cmd+V, and captures only the whole primary display (`screencapture -x -m -C`). As a result:

1. Every `computer_click` warps the user's physical cursor to the target coordinate and leaves it there, interfering with concurrent trackpad/pointer movement.
2. Every `computer_type` overwrites the user's clipboard and requires the target window to be frontmost, stealing focus from whatever the user is doing.
3. Full-display capture only sees unoccluded front windows, preventing an agent from reading an approved app window while the user works in another window in front of it.

Meanwhile, official macOS computer-use implementations across major providers (Claude Cowork/Desktop on macOS 15+ shipped Sept 2, 2026; OpenAI Codex `SkyComputerUseClient` shipped Apr 16, 2026; GitHub Copilot Computer Use public preview shipped Oct 1, 2026) all perform background window interaction on macOS via Accessibility (`AXUIElement`) + per-window capture rather than hijacking the global HID cursor. Because SpecWithCode owns the provider-neutral `computer_*` MCP toolkit used by Claude, OpenAI/Codex, GitHub Copilot, Gemini, and all other providers in SpecWithCode, upgrading `MacComputerUse` delivers background non-interfering computer use across every provider at once.

## Scope

In:
- Provider-neutral macOS background computer-use delivery in SpecWithCode's `computer_*` toolkit (`packages/contracts`, `apps/server`, `apps/desktop`):
  - Per-window background capture: optional `application` parameter on `computer_screenshot` (guarded by `SELF_CONTROL_REFUSAL` and `AccessGate` `requireAppAccess`) using public `screencapture -x -l <windowId>` and recording window screen origin so subsequent clicks map accurately to screen coordinates even when the window is occluded.
  - Background Accessibility (`AXUIElement`) click and text entry in `MacComputerUse`: for standard left-clicks (count 1, no modifiers, non-mirroring) with a resolved approved `targetPid`, attempt `AXUIElementCopyElementAtPosition` + `AXPress` (for pressable controls) or record an editable field (`AXTextField`/`AXTextArea`/`AXSearchField`/`AXComboBox`) for background `AXSelectedText` text entry on the subsequent `computer_type` without moving the physical cursor, stealing focus, or overwriting the clipboard.
  - Safe foreground HID fallback: when AX delivery is unsupported (canvas, Chromium/Electron web content without `AXPress`, right-click, double-click, modifiers, drag, keys, scroll), yield briefly if the human moved the pointer or pressed a key within 150ms (bounded wait <= 500ms via `CGEventSourceSecondsSinceLastEventType`), and restore the pre-action cursor position after `click`/`scroll` HID fallback so the pointer is not left hijacked.
  - Explicit `delivery` metadata (`"background_ax"` | `"foreground_hid"`) on action results so callers and tests can verify whether background delivery or HID fallback occurred.
  - Unit tests for step builders, coordinate mapping, window lookup, and server `AccessGate`/`SELF_CONTROL_REFUSAL` enforcement, plus an isolated self-owned macOS AppKit fixture verification proving 0px cursor displacement and 0 focus changes on an occluded background window.

Out:
- Private/undocumented Apple SPIs (`SkyLight.framework` `SLEventPostToPid` / `SLPSPostEventRecordTo`), which risk macOS version breakage and Developer ID / notarization fragility.
- Changing iPhone Mirroring (`runOnMirroring`), which requires foreground HID delivery and stays untouched.
- Weakening or bypassing `AccessGate` (`requireAppAccess`), `SELF_CONTROL_REFUSAL`, or macOS TCC permission checks.
- Windows/Linux desktop drivers (macOS host only in this increment).

## Acceptance Criteria

- [x] AC-01: `computer_screenshot` accepts an optional `application` string, enforces `SELF_CONTROL_REFUSAL` and `requireAppAccess(application)` before capture, captures that app's window via `screencapture -x -l <windowId>` without activating it, and maps subsequent click coordinates using the window's screen origin and scale.
- [x] AC-02: `computer_click` (single left-click, no modifiers, non-mirroring) with an approved `targetPid` attempts public `AXUIElement` delivery (`AXPress` when supported, or records editable text fields for background typing) with 0px physical cursor movement and 0 focus change, returning `delivery: "background_ax"`.
- [x] AC-03: `computer_type` (non-mirroring) targeting a previously selected background editable AX field inserts text via `AXSelectedText` (`AXUIElementSetAttributeValue`) when the target app is in the background and the selection is empty—without moving the cursor, stealing focus, overwriting the system clipboard, or replacing whole-field `AXValue`—returning `delivery: "background_ax"`.
- [x] AC-04: When AX delivery is unsupported (or for modifiers/double-click/right-click/scroll/key/drag), `MacComputerUse` falls back cleanly to foreground HID (`delivery: "foreground_hid"`), yielding briefly (<= 500ms) during active human pointer/key input (`CGEventSourceSecondsSinceLastEventType`) and restoring the pre-action cursor position after `click`/`scroll` HID fallback; `iPhone Mirroring` remains untouched.
- [x] AC-05: Existing security and ownership guards (`AccessGate`, `SELF_CONTROL_REFUSAL`, `pid !== process.pid`, `ComputerUseBroker` serialization) remain enforced and verified by unit tests and an isolated safe AppKit fixture test on macOS.

## Approach

1. `packages/contracts/src/computerUse.ts`: Add optional `application` on `ComputerScreenshotInput` / `ComputerScreenshotAction`, optional `windowId` and `bounds` on `ComputerScreenshotResult`, optional `targetPid` / `targetApp` on click/type/scroll desktop actions, and optional `delivery` (`"background_ax" | "foreground_hid"`) on `ComputerUseActionResult`.
2. `apps/server/src/mcp/toolkits/computer/tools.ts` & `handlers.ts`: Expose optional `application` on `computer_screenshot`, enforce `SELF_CONTROL_REFUSAL` + `requireAppAccess(application)`, track the last captured/resolved `targetPid`/`targetApp`, forward `targetPid`/`targetApp` to desktop actions, and surface `delivery` in tool results.
3. `apps/desktop/src/computerUse/computerUseSteps.ts`: Add `JXA_AX_ACTION_SCRIPT` (pure public `ApplicationServices.framework` bindings using `void *`), add `findWindowForApplication` and origin-aware `toPoint`, and add optional `yieldForHumanInput` + `restoreCursor` to `JXA_INPUT_SCRIPT`.
4. `apps/desktop/src/computerUse/MacComputerUse.ts`: Wire per-window capture (`screencapture -x -l`), `ax_click` / `ax_type` background-first dispatch with `pid !== process.pid` guard, and yielding/cursor-restoring HID fallback while keeping `runOnMirroring` untouched.
5. Tests: Extend `computerUseSteps.test.ts` and `handlers.test.ts`, plus run an isolated self-owned Swift AppKit background-window fixture test on macOS to verify real `screencapture -l`, `AXPress`, `AXSelectedText`, 0px cursor movement, and 0 focus steal.

Rejected alternatives:
- Private `SkyLight.framework` SPIs (`SLEventPostToPid` / `SLPSPostEventRecordTo`): fragile across macOS versions (host is macOS 27.2) and risky for signed/notarized desktop builds; public `AXUIElement` + `screencapture -l` + yielding/restoring HID fallback is fully supported by Apple's SDK with zero new binaries or signing changes.
- Separate native Swift helper binary: requires bundling and code-signing a new executable; running public CoreGraphics/ApplicationServices bindings via `/usr/bin/osascript -l JavaScript` inherits `SpecWithCode.app`'s existing TCC grant cleanly.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: Use public Apple APIs (`AXUIElement`, `screencapture -l`, `CGEventSourceSecondsSinceLastEventType`) via JXA rather than private `SkyLight.framework` SPIs → default (reversible; avoids macOS version breakage and code-signing changes).
- D-02: Preserve full-display default for `computer_screenshot()` and make `application` optional → default (reversible; 100% backward-compatible with existing agents and tests).
- D-03: Automatically attempt background AX delivery on standard single left-clicks and subsequent text entry for approved non-mirroring apps, falling back transparently to yielding/cursor-restoring HID when AX is unsupported → default (reversible; works out-of-the-box for Claude, OpenAI/Codex, GitHub Copilot, and all providers).
- D-04: Accepted macOS Accessibility IPC boundary for background `AXSelectedText` typing — Apple's public `AXUIElement` API provides no atomic check-and-insert Mach IPC primitive across process boundaries. Pre-write checks (`frontmostPid !== targetPid`, `verifyElementWindow`, `expectedFieldKey`, readable `AXValue`, empty `AXSelectedText`, second frontmost-PID re-check immediately before `AXUIElementSetAttributeValue`) plus post-write `AXValue` readback (`ax-selection-replaced` / `ax-set-uncertain`) minimize the microsecond IPC window without violating AC-03 or relying on private SPIs.

### Open
- none

## Tasks

### T-01 Add background capture, targetPid, and delivery fields to computer-use contracts and MCP toolkit
- AC: AC-01, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/computerUse.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/computer/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/computer/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/computer/handlers.test.ts | Test: pnpm --filter @specwithcode/server test -- src/mcp/toolkits/computer/handlers.test.ts

### T-02 Implement JXA AXUIElement background actions, per-window origin mapping, and HID yield/cursor-restore in desktop driver
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/computerUseSteps.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/computerUseSteps.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/MacComputerUse.ts | Test: pnpm --filter @specwithcode/desktop test -- src/computerUse/computerUseSteps.test.ts

### T-03 Verify end-to-end on isolated macOS background-window fixture, run full checks, adversarial review, merge, release, and verify
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/MacComputerUse.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/computerUseSteps.ts | Test: pnpm --filter @specwithcode/desktop test -- src/computerUse/computerUseSteps.test.ts && pnpm --filter @specwithcode/server test -- src/mcp/toolkits/computer/handlers.test.ts

