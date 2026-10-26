Closing or replacing a server live-preview pop-out during startup can let the old startup enter picture-in-picture later. Playback/metadata can also remain pending indefinitely, and access refresh errors leave no useful message.

Add cancellation-aware startup with a ten-second deadline, ordered native entry/exit, metadata errors, initial access failure propagation and retry/host-setup messages. Each startup cleans its own video, media tracks, listeners, timers, stream and painter. The native desktop capture/annotation paths are unchanged.

Validation: four baseline lifecycle regressions failed before the fix; 31 lifecycle/client/server stream checks now pass. Supported web typecheck, focused lint and production web build pass. Fresh-context review: SHIP after two findings were fixed. Product-native headless preview tools exercised real navigation, a 960px scroll, source-frame delivery through the production painter and real canvas/video, close/replacement, host failure and recovery.

OS picture-in-picture calls were substituted during headless runtime checks. This does not prove native macOS z-order, Spaces behavior or every website. An OS request that never resolves fences later native entries, while each caller still times out and releases media resources. No app/service restart or release dispatch.

Shipped T3 Code 0.1.2 REA findings and clean-room behavior specification: `docs/research/embedded-browser-1018.md`. Retained receipts: `/Users/antonabyzov/.specwithcode/m4/evidence/browser-live-1018`. Increment 1018. Snapshot increment 1016 remains disjoint; release 1015 owns inclusion and dispatch.


Independent credential-write repair (1024): CI exposed an existing race where sign-out deletes a renamed secret before a redundant chmod of the destination. The write then fails and its success-only completion signal never fires. Remove only the post-rename chmod; retain mode 0600 before atomic rename. A deterministic real-filesystem regression verifies private permissions and concurrent deletion. 105 settings/secret-store tests and 100 disposal stress cases pass; fresh review SHIP, independent 11-test rerun passes. Remote CI must pass on the combined head before merge. Native PiP/z-order/Spaces acceptance remains unverified.
