# Live diagnosis, 2026-10-13

The native SpecWithCode app reproduces repository labels in the sidebar and EasyChamp in its workspace header. Read-only installed Info.plist/package metadata and release-owner readback identify candidate 1.0.10, source a26cf (R2), PID 82926 at inspection. Public/private published latest releases were both 1.0.9. Packaged frontend includes the 0908 custom-name grouping fix.

Read-only M4 project data contains saved EasyChamp, SpecWeave umbrella and JobWeave names alongside differently named same-repository handoff-proof projects. Evaluating the actual buildProjectGroups implementation over those records reproduces the three repository labels. No stored title was renamed. The old fallback predates the Studio fork; additional grouped checkouts expose it. Choosing the first/oldest custom title is insufficient because JobWeave's proof registration predates its ordinary project registration.

The sidebar's manual Check for updates action was clicked once before the release owner's live-UI freeze. The desktop trace records a successful web-ui check at 2026-10-13T19:24:59.127Z, completed after 431.6ms, then handleUpdateNotAvailable at 19:24:59.559Z. No visible result appeared. SidebarUpdatePill returned immediately for checked=true; that flag can also accompany handled check errors.

The installed candidate version is already 1.0.10. githubReleaseFeed excludes equal versions, so publication of a different final 1.0.10 binary cannot offer this Mac a normal update. The coordinated next version above 1.0.10 is the normal-updater acceptance target. The 0907 owner owns its frozen R3 candidate and six real handoff gates; this task does not restart, replace or navigate the live app during those gates.

No credentials, project/chat payloads or private runtime databases are copied into this evidence. The observations above were obtained through native accessibility, scoped read-only metadata and source inspection.
