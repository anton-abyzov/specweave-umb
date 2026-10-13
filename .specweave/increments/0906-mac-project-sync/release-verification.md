# Coordinated release verification

Status: 1.0.9 published; M1, M3 and M4 services verified; M4 desktop verified in its native About panel.

The existing release owners retain source, packaging, publication and M4 installation control. This increment owns destination provisioning and M1/M3 runtime verification. The user explicitly authorized coordination between the existing release chats.

The destination baseline is SpecWithCode 1.0.7 at source `54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f`. The agreed target is the successor 1.0.9 release, including the audited 1.0.8 coordinator fixes and completed output/navigation changes. An intended version or frozen source is not publication or installation proof.

Acceptance requires authoritative public release readback, audited artifact hashes, compatible update plans, safe host state, and exact installed source/version readback on M4, M1 and M3. No active unrelated sessions may be interrupted and compatibility allowlists must not be widened to bypass a failed precondition.

## Published and installed evidence

The owner published [SpecWithCode 1.0.9](https://github.com/anton-abyzov/specwithcode/releases/tag/v1.0.9) on 2026-10-13. All 11 private/public release assets matched the frozen hashes. Runtime build source is `51c49ab4603c17c87362e9700cd242b24ed83e2e`; merged main is `34826e95eea37bf5979452773e6f5c75d6803556` (only the release-history document differs). The runtime archive SHA-256 is `552c4c7101b5d71e62e43d9e6d59b8ed95e7edc803368dbe6dbf0a2e8c053a7f`.

Both M1 and M3 updated from the exact approved 1.0.7 source using the published deployment plan. At 12:33 UTC, independent readbacks verified all 7,481 indexed runtime files, exact build source/archive hash, running owned launch services, root HTTP 200 and unauthenticated capacity HTTP 401. Update receipts report byte-identical database rows, complete database continuity, retained authentication/environment identity and preserved original services. Only each owned Studio service restarted. No native inference ran during installation.

The Mac desktop artifact is Apple Development signed; notarization is not verified. A remote service update is not a standalone desktop-app installation. The M4 release owner separately owns desktop installation and visible native verification.

M4's final readback at 13:14 UTC verified the same 7,481 files and source, HTTP asset equality, guarded database continuity, and service PID 16665. Desktop PID 49969 opened the exact audited ASAR, its code signature passed, and the native About panel independently displayed `1.0.9 (51c49ab4603c)`. The service verifier's missing desktop-bridge limitation is covered by this separate native About receipt. The installation reservation was released at 13:15 UTC.
