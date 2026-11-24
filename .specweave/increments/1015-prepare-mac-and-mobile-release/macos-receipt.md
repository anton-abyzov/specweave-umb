# macOS 1.0.75 release receipt

Current status: macOS 1.0.75 published and service installation verified at `c52ee223ae58bf79e6aa313089f81aaf56286e9c`; desktop app last reported 1.0.74, so installed UI acceptance remains separate. Entries below retain chronological evidence. Later corrections supersede earlier claims: PR #633 merged for a future candidate, and stopped 9 refers to the last incident prepare result, not the first.

Status: published and release artifacts verified; installed app/service acceptance remains pending.

Run: https://github.com/anton-abyzov/specwithcode-dev/actions/runs/39939287862

Frozen source: `ddeaee06b130f8c582e6d4801d636fd66c6936e4`.

Dispatched October 23, 2026 at 6:27 AM EDT through official `release-macos.yml`, version `1.0.75`, previous `1.0.74`. No in-flight Mac release or local dispatcher existed. Workflow source read at the frozen SHA. Live run head matches frozen source. Required gates, server suite, Developer ID signing, notarization and public mirror remain enabled.

All 12 intended merges pass Git ancestry verification in `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/trigger-manifest.json`. This includes #625, #626, #627, #628, #629, combined #630/1024, repaired #631, conflict-repaired #632, #634 and #635. #622/#623 are also ancestors. No working-tree patch included. #633 still fails required typecheck and is excluded; 1008 has no merged readiness and is excluded. 1011 has no merge candidate; its before-capture receipt exists.

Installed acceptance remains separate. No local service restart, forced drain, live database access or recovery cleanup performed. Notify updater, usage, provider update, model recovery and folder-approval owners only after actual app/service identity readback.

## Terminal publication proof

Workflow `39939287862` completed SUCCESS at the exact frozen source. Version-bumped published source `c52ee223ae58bf79e6aa313089f81aaf56286e9c` contains frozen main and all 12 queued merges by ancestry. Private publication October 23 at 6:50 AM EDT, public publication 6:50 AM EDT. Four server shards passed 11,186 tests across 851 files, zero failures; stage timings record no retries/flakes. Complete workflow and downloaded stage/server logs are retained.

Both public/private releases are non-draft and their shared asset digests match. Public downloaded DMG, ZIP, runtime, deployment helpers, update plan and helper manifest match published digests and SHA256SUMS. The plan targets c52ee223ae58, supports the currently installed 1.0.74 source, and the helper archive contains the expected update entrypoint. User-facing notes were updated on both releases and read back.

Independent downloaded ZIP check: PASS, app and nested helpers Developer ID team NMCB2JZ7QG, hardened runtime, stable designated requirement, notarized Gatekeeper acceptance and stapled app ticket (the checker enforces these). Exact public DMG hash matches CI artifact; CI mounted-app checker passed Developer ID/notarization for DMG and ZIP. Local DMG filesystem CRC verifies VALID, but this Mac refused read-only mount with `hdiutil: attach failed - Permission denied`. Local container check reported `code object is not signed at all`, `source=no usable signature`, and no container ticket. The DMG container itself is not claimed signed/stapled; the application inside it is signed/notarized as verified by CI. This local mount limitation does not change exact-hash CI proof or independent ZIP app verification.

Artifact root `/Volumes/Work/specwithcode-release-1075-verify`. Signature checker outputs `/Volumes/Work/specwithcode-release-1075-verify/signature-zip.json` and `/Volumes/Work/specwithcode-release-1075-verify/signature-dmg.log`. CI signature evidence `/Volumes/Work/specwithcode-release-1075-verify/run-artifacts/release-1.0.75-logs/logs/sign.log`. Digest/plan receipts in the increment evidence folder.

Latest readback after publication: CLI/service installation metadata and `/Applications/SpecWithCode.app` remain 1.0.74. No install, force drain or service restart was performed by this release lane. Original updater owner has the published version/source and is coordinating managed update/measurements under existing authorization only; all recovery files must remain.

## M4 managed install refusal

0993 measurement owner reports target1.0.75downloaded but updater refused October23at10:52Zand11:02Z: "The SpecWithCode service lost its SQLite locks on its database. Restart SpecWithCode, then update." ServicePID47190,started04:30:36Z,stillholds database/WAL/SHM open, none deleted, per owner's supported diagnostic evidence. No direct database access by1015. Free4.1GiBpasses clone-sized approximately3.4GBpreflight; this is lock-loss refusal, not disk admission. Owner has already asked user for service restart approval;1015must not duplicate that question or force drain/restart. All recovery files intact. Published release evidence remainsPASS; installed app/service/timing/afterProof/newagent/readiness remain pending until approved install.


## M4 service installation and measurement incident

Owner receipt on October 23, 2026: service 1.0.75 at source `c52ee223ae58bf79e6aa313089f81aaf56286e9c`, verified with no rollback. Receipt phase independently read as `verified`: `/Users/antonabyzov/.specwithcode/m4/updates/receipts/update-1.0.75-20261023T143334594035Z.json`. Desktop application remains 1.0.74 pending Squirrel install on quit. No app/service alignment or installed UI acceptance is claimed.

Owner measured apply 116.8 seconds versus 153.5 seconds previously; beforeRead 66.5 seconds, gateSettle 12.2 seconds, disconnected about 10 seconds. Production afterProof pages mode: pageProof 6.9 seconds, readiness 5.6 seconds, 2 changed pages in auth_sessions and 55 reused tables. Backup clone 34 milliseconds. This upgrade still used the old agent full prestate read; the new held-snapshot path remains prospective. Peak disk samples were overwritten and other activity changed free space, so peak disk is unproven.

Incident reported by measurement owner: a launchctl submit job repeatedly relaunched after exit, causing 7 service restarts and 6 prepare-update --stop-work calls between 9:50 AM and 10:38 AM EDT, with 9 tasks stopped in the first run. Owner reports job removed and no hold left. Read-only accounting requested from original owner for job absence, exact events, all affected task/thread IDs, current states/owners and recovery gaps. No blanket resume, further restart, force drain or backup pruning is authorized by this report. 1015 remains open.


## Incident recovery accounting correction

Read-only owner recovery receipt reviewed: `/Users/antonabyzov/.specwithcode/m4/evidence/update-measure-1075/recovery/receipt.md`. Both measurement launchd jobs are reported absent, no measurement process or update hold remains. Affected 118 runs on 24 threads: 63 cancelled, 44 interrupted, 11 failed. Thirteen threads continued; eleven have no subsequent run. Two were substantive interrupted work threads (Usage and cost dashboard; EasyChamp Business, facilities and marketing prep). Nine were 1011 child-result notification relays interrupted during S3; leaf r9 completed, implementation had not started in that chain because of the earlier Claude credit gate.

Correction to earlier owner report: stopped 9 refers to the last prepare result, not the first run. Owner accounted every incident-period stop command inside S1-S6 and reports no user Stop overridden. Removal/hold absence and incident classification are owner evidence, not fresh live checks by release lane. No stopped thread has been resumed by release lane. Original coordinator receives recovery ownership routing; do not wake all nine relay threads or substitute providers. Peak disk and next-upgrade held snapshot remain unproven.
