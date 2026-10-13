# 1.0.7 installed on M4

Verified 2026-10-13 at 05:14:44 UTC. Server and running desktop are both 1.0.7. The server runs source `54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f`, archive SHA-256 `600a4c54e381cbaed29c7e530e19ae424e70ac80ba5da7d41104566b97951830`, PID 8552; desktop PID 5765. Production HTML and its JavaScript asset both returned HTTP 200.

The unchanged published helper completed a fresh guarded install in 210.04 seconds. Its receipt records `phase: verified`, `completeDatabaseContinuity: verified`, `rowPreservation: byte-identical`, and preserved authentication, settings, identity and other services. No comparator, timeout or quiescence guard was relaxed. The private raw receipt is `/Users/antonabyzov/.local/share/specweave-studio/verification/0901/install-live/update-20261013T051050Z.json`, SHA-256 `f7a17bc5440f971d684bdb94d74ed511dffdcb1f83c0a3ecde09a6216fcfe3f4`.

`verify-live-installed.py` independently checked that positive receipt against the current installation, live service PID, production HTTP response and running desktop version. Its sanitized output is `.../verification/0901/install-live/live-installed.json`. See `desktop-live.md` for app bundle and running-process evidence.

## Earlier failures and coordination

The automatic attempt exceeded its preparation budget without changing the installation. The same snapshot took 8 seconds in a foreground measurement versus over five minutes in the background updater, whose launchd definition enables low-priority I/O. The original scheduler was reserved only after its process exited and its lock was acquired. Exact original plist, configuration and updater state were captured locally.

The first foreground install switched successfully but correctly refused continuity acceptance because another authorized chat's headless recovery audit created temporary pairing links and browser sessions during restart. Its failure receipt remains untouched at `.../install-live/update-20261013T045742Z.json`. `install-continuity-audit.md` separately verifies every original auth cell (except bounded reconnect timestamps), historical log prefix and project table; concurrent audit additions and event-backed metadata are documented.

The recovery audit confirmed a pause via its `paused-report.json`. A subsequent snapshot refused transient provider/CLI descendants and made no changes. Once those processes finished naturally, the final fresh snapshot and unchanged same-version helper passed. No active process was killed to obtain quiescence. The maintenance, recovery-audit and coordinator-QA chats were told the reservation ended after verification.

At 05:15:08 UTC, the updater's normal `Agent.complete_install` path recorded `installed` and the positive receipt. Its original unchanged launchd plist and configuration were restored. `.../install-live/scheduler-restored.json` proves restoration, preserved config and retained failure receipts. Future automatic checks remain enabled.

## Google live state

At 05:15:43 UTC, an official, temporary, read-scoped bearer session queried the running 1.0.7 server. The bundled Google OAuth client is configured (`clientSource: studio`). Google is not signed in: `connected: false`, no granted services, no Aide project access, no pending sign-in, no connection error. This fixes the earlier absent-client packaging problem but does not prove access to a Google account.

The temporary session was revoked exactly; existing active sessions were preserved and no pairing link was created. The sanitized receipt is `/Users/antonabyzov/.local/share/specweave-studio/verification/0901/google-status-20261013T0515.json`.

Anton was asked to complete Google's sign-in/consent under Settings > Google account and enable Gmail, Calendar and Drive for Aide. T-06 stays open until the native Aide coordinator returns actual API health and all three read outcomes. `aide-google-live.mjs` is prepared to collect only states/counts and clean up its own scoped session. No Google access or content retrieval is claimed yet.
