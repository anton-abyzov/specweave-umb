# Cancellation verification - 2026-10-13

Source commits: c0a61b636 (origin-aware Morning briefing + theme Escape), c4cf3fdf9 (tooltip-owned Escape), 55272cd0a (chat-linked task editors), 1ec4388ae (expanded headless runner). The 0904 owner froze release1.0.8 at291f919c24b600e400b8c64e9f3dd383795f33a6 including only c0a61b636+c4cf3fdf9; chat-linked editor change55272cd0a is queued separately and is not claimed shipped in1.0.8.

The baseline headless run against the old1.0.7 client reproduced Cancel leaving Google and remaining on Scheduled tasks. It did not reproduce a direct Cancel-to-home navigation. Source audit additionally found a Theme variant Escape propagation defect and two chat-linked edit entry points needing explicit origins.

## Passed checks

- 34 original navigation/schedule logic tests +10 existing provider dialog tests +5 UsagePage nested Escape tests passed on the frozen navigation source (49 tests). The linked follow-up adds one logic regression (35 logic tests); independent review additionally ran the settings scope/navigation suite.
- Production web builds passed using separately scoped Node24.13.1; the final build disabled source maps. Production server builds passed and copied the exact already-built web client. Headless runtime used Node22.20.0 and explicit installed Chromium headless shell1243.
- Frozen c4 web receipt108-receipt.json: Cancel, X, Escape, backdrop all restore full originating URL including machine scope and persistent hash; nested Select Escape closes only the select; direct template cancellation removes its query and survives reload/history; local New/Edit Cancel stays on the task list and preserves data; successful disabled Create stays on the list; provider wizard Cancel/Escape stay in Settings; Theme hover-only and focused Escape both change radial opacity1 to0 and preserve the page.
- Linked552 web receiptlinked-receipt.json: repeats all above checks, plus routed edit dismissal returns to the supplied origin and direct edit dismissal consumes taskId before reload.
- Every successful browser receipt reports zero page errors, zero native provider turns, fake Google only, disabled fixture runCount0, and private home cleanup. Tests preserved live stores and used no personal browser or live Google account.
- Independent source review accepted c0/c4 after hover and tooltip Escape findings were repaired, and accepted552 after checking both direct chat editor callers. Full-origin normalizing checks reject external/protocol-relative/backslash/control/dot-segment authority escapes. Local list-launched edits retain local close semantics; successful save is distinct from dismissal.

The focused rebuilds used an own-client fake-Google fixture and report compiledGoogleClientAvailable=false. They prove navigation behavior, not a publishable bundled OAuth client or real Google API reads. The0904 owner independently confirmed the approved built-in client in its exact291 release artifacts. Real Aide Google proof remains T-06.

Evidence retained under /Users/antonabyzov/.local/share/specweave-studio/verification/0901/navigation, with hashes in manifest.json. Running verify-receipts.py checks saved evidence only, not a fresh browser/build. The canonical audit is ../cancel-navigation-audit.md; its initial inventory missed the two direct chat edit callers later fixed by552.
