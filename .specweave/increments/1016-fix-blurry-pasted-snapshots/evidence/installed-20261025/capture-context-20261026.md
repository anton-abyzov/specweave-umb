# Snapshot conversation and context follow-up

PR: https://github.com/anton-abyzov/specwithcode-dev/pull/867

Candidate: `5b44c7a190b000c5d38a748dfa93509350d39784`.

Worktree: `/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016`.

## Behavior

Project-pane conversation identity is read from its scoped search parameters and pinned when a capture begins. Opening Settings retains that target. The resulting image is attached to the original thread or viewed coordinator, preserving all existing prompt text. Returning from Settings is conditional on the user not having navigated elsewhere. An unresolved project never silently becomes a Scratch chat.

Self-capture skips activation and native feedback overlays. This removes the app-driven activation path; the reported macOS Space change has not been independently reproduced on the patched installation.

Coordinator capture waits for durable image and source metadata before acknowledgment. App/window identity, accessibility text/tree and pixel coordinates survive local journal restoration, host schema transport, disk saves and host restoration. Metadata-only changes trigger a save without resending stored image bytes. Old source-less drafts remain supported.

## Verification

199 focused tests pass across capture routing, desktop activation, durable save/restart, server draft files and provider attachment serialization. Five tests fail against pre-repair production files and pass after the repair. The earlier mounted routing regression fails twice with the original routing implementation.

Web, desktop and contracts typechecks pass. The full server typecheck reports 43 errors at both the unchanged base and candidate, with identical diagnostics. No new server diagnostic is present. This does not make the server gate green.

Evidence logs are retained under `/Users/antonabyzov/.specwithcode/m4/evidence/snapshot-installed-20261025`. Fresh exact-head review is SHIP at `5b44c7a190b000c5d38a748dfa93509350d39784`. PR checks were still queued or running at the readback; the candidate is mergeable. Merge ownership remains with the existing integration thread. Native 150% annotation and patched installed routing remain pending.
