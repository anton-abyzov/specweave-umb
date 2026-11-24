---
title: "Wispr Flow and SpecWithCode computer use on M5"
thread: "thread:delegated-task:command%3Amcp%3Afa43f133-3057-4a60-a8c7-bcc96542ad30%3Adelegate-task%3Ad87435a4-6279-43a1-a0ed-19edc88765aa"
threadTitle: "Wispr Flow and computer use"
savedAt: "2026-11-19T22:52:22.526Z"
---

# Wispr Flow and SpecWithCode computer use on M5

Date: November 19, 2026. Machine: Anton M5MAX PROLED, macOS 27.2.1, Wispr Flow 1.6.1537 (running, untouched). Read-only: no desktop input, no Flow settings, history or clipboard read.

## Finding

**Evidence.** Flow keeps one on-screen window while it runs. `CGWindowListCopyWindowInfo` (window metadata only) on M5 returned `Wispr Flow | layer 1000 | alpha 1 | x 500, y 379, 512 x 614` on the 1512 x 993 main display: a transparent box over the lower middle of the screen. A read-only Accessibility hit test (`AXUIElementCopyElementAtPosition`, pid only, no click) at four points inside and outside that box returned **OBS Studio**, the app underneath, every time. So Flow's box is click-through, matching Wispr's docs ([Move and Dock the Flow Bar](https://docs.wisprflow.ai/articles/1790396454-move-and-dock-the-flow-bar-on-desktop)).

**Evidence.** SpecWithCode's click gate does not use that answer. `applicationAtPoint` in `repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/computerUseSteps.ts` takes the first window in the list with `alpha > 0` under the point, and `targetApps` in `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/computer/handlers.ts` gates every click, scroll and drag on it. On M5 right now that first window at all four points is a full-screen macOS `MenuBarAgent` window (layer 26, 1512 x 993, listed ahead of Flow), and Flow's box is next. The gate can name the wrong app for transparent overlays, Flow's included.

**Not shown.** No "Use Wispr Flow" (or MenuBarAgent) card was found in the app logs, and the exact failure Anton saw is not recorded. The gate mismatch is the leading hypothesis for a Flow-related refusal or extra card, not a confirmed cause. It also cannot explain dictation, focus or paste trouble.

## Other overlaps checked

| Area | SpecWithCode | Flow | Verdict |
|---|---|---|---|
| Hit test for clicks | topmost window owner | 512 x 614 click-through window, layer 1000 | Gate can name the wrong app (above); leading hypothesis |
| Key events | `CGEventPost` at the HID tap, null source (`JXA_INPUT_SCRIPT`) | global shortcuts: Fn hold, Fn double-tap, Fn+Space, Ctrl+Cmd+V, Ctrl+Cmd+C (docs) | Evidence: Flow sees agent keys like real ones. Only `fn`, `fn+space`, `ctrl+cmd+v/c` would trigger it; agents rarely send those |
| Typing | `computer_type` saves clipboard, writes text, Cmd+V, restores after 300 ms | Flow also pastes via the clipboard and restores it (docs) | Guess: only collides if Anton dictates while the agent types; could restore the wrong item. Not the reported symptom |
| Focus | `computer_open` uses `open -a`; no focus stealing | Flow Bar follows the cursor's display (docs) | No conflict found |
| Screenshots | `screencapture -x` | Flow Bar shows in captures (docs) | Cosmetic only |

## Recommendation

Keep Flow running. Fix the gate, not Flow:

1. **Code fix (small, needs its own test):** in the click target lookup, ask Accessibility what is actually under the point (`AXUIElementCopyElementAtPosition` on the system-wide element, then its pid's app name), and fall back to the window list only when that fails. That respects click-through overlays like Flow, Raycast or screen recorders. Keep the refusal when neither method can tell. Do not just skip Flow or high-layer windows: real Flow controls must still count as Flow.
2. **Until then, no Flow change needed:** if a "Use Wispr Flow" card appears, deny it and have the agent click a point outside the box, or move the target window. Allowing it works but lets clicks in that box skip the gate for the real app below.
3. **Optional Flow-side mitigation (unverified):** Flow's own "Hide for 1 hour" or "Show Flow Bar at all times" off. Unknown whether the 512 x 614 window leaves the window list when hidden, so this may not help.

## Quick optional test (after the stream)

1. Note what actually went wrong: a "Use Wispr Flow" card, a refusal naming an app, Flow starting to record, or a lost clipboard. Each points to a different row above.
2. To test the card theory, open TextEdit, allow it for one thread, and ask an agent to `computer_click` near the bottom middle of the main screen (about x 756, y 900 in display points), then near the top. A card naming Wispr Flow or MenuBarAgent on either click confirms the gate mismatch.
3. If dictation starts by itself during agent work, check whether the agent sent `fn`, `fn+space` or `ctrl+cmd+v`; those are Flow's default shortcuts.

The read-only comparison (window list vs Accessibility hit test, no clicks) can be rerun any time and needs nothing from Anton.
