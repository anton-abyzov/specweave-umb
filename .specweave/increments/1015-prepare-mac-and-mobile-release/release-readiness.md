# Release readiness, October 23, 2026

Prepared at 1:31 AM EDT. This is preparation evidence, not a published release.

## Authority and timing

Anton authorized latest verified mobile and macOS release/submission. Sole coordinator trigger is October 23, 2026 at 6:26 AM EDT (`2026-10-23T10:26:00Z`), bound to coordinator and routes to this release owner. Schedule ID `scheduled-task:command:mcp:f9b6f93f-2383-4a68-8fb1-0a0bb9d73b36:schedule-task:release-mac-mobile-once-20261023-1026z`. Merge cutoff 6:00 AM EDT; reconcile completed verified work again at trigger. No early publication, duplicate timer or duplicate dispatch.

## Ownership

Prior release611 owner explicitly transferred next release dispatch to 1015 (project knowledge `release-ownership-transfer-1015.md`). Updater/#623 owner confirmed transfer in thread at 1:29 AM EDT; keeps updater code and runtime verification ownership. Its cancelled 1.0.75 attempt is run `39898480730`, source `ab96f4d1c25284282553a4099b503b307a0b26a5`. No active release run or local release/signing process found in fresh checks. Existing simulator runner is unrelated and preserved.

Release thread `thread:delegated-task:command%3Amcp%3Af9b6f93f-2383-4a68-8fb1-0a0bb9d73b36%3Adelegate-task%3Aprepare-five-hour-release-20261023` owns dispatch. Code owners remain in their checkouts. Cutoff notice delivered to usage1007, updater0993, recovery1003, activity1011, T3 Connect, showcase1008 and optional increment1001 owners. No active worker taken over.

## Candidate queue

| Item | Exact source or PR | Current disposition |
| --- | --- | --- |
| Published baseline | v1.0.74 | Latest published release; M4 installed acceptance in prior final receipt |
| Model recovery floors | #622 `ab96f4d1c25284282553a4099b503b307a0b26a5` | Merged; include by ancestry; installed automatic recovery remains owner gate |
| Clone-aware backup sizing | #623 `252be2eb414150ed57893c94f933bce7493cfd0d` | Merged; include by ancestry; runtime timing/disk gate retained |
| Fast update reads,0993 | #626 merged `ef227c979bb9522330c1c82b96b6774651f37f77` | Exact tested head `f8352ba12801a5706ae3e6b166267cec9025e38f`, Checks39905623031 SUCCESS;40 local fleet suites and fresh SHIP. Include by candidate ancestry; runtime gates retained. |
| Usage dashboard,1007 | #625 head `022b4b187ed132a847d808bc146c55237b79cd24` | Unmerged; owner collecting review/CI and acceptance |
| Optional notice,1001 | #624 head `ac2f8492293175b6b0db0ba82229fb404ce3baa7` | Unmerged follow-up; include only after owner green/merge |
| iOS thread lists | #614 `afdafde6cf87ddfd29df5e6a5d9e724681551764` | Merged; 378 Swift tests and nine simulator checks reported, development build8 launch independently proved |
| Project dedupe | #615 head `de9aba78cb391f956a59dd6dd2ed6ddcff240c4d` | Open; no assumed inclusion |
| Activity1011 | Existing owner | Pending exact merged SHA and evidence; no speculative inclusion |
| T3 Connect1014 | #628 head `e025a268fa25a7c3a4001108f5f504716439ad95`, branch `feat/t3-connect-onboarding` | Owner reports desktop phone preflight and address-bound expiring QR/renewal ready; 13 focused tests, 14 real-component headless checks, web typecheck/build, focused lint and fresh SHIP. Include only after exact-head CI and merge ancestry verification. No iOS edits. |
| Showcase1008 | Local scoped website patch | Review only; T-03/T-04 open, external-page typecheck failure, no installed acceptance claim |

At preparation main is `252be2eb414150ed57893c94f933bce7493cfd0d`. Compare to v1.0.74 is ahead3/behind0 (release merge plus #622/#623). Candidate version remains unreserved until trigger; next available may be1.0.75, but re-read tags/drafts/runs first. All public notes must describe verified behavior and preserve #608 upgrade caveat when relevant.

## Mobile state

App `6824245458`, bundle `com.specwithcode.ios`, version0.1.0, version ID `08b06b7f-6e58-4982-8cbd-65681a10740b`.

Live ASC reads confirm build4 `ff92b650-1fbc-495c-a899-47237c4ea689` attached to pending submission `9a5ec644-ead8-4159-9989-745db828915c`, WAITING_FOR_REVIEW. Latest uploaded build6 `765cbfd2-f74e-4a98-88b3-d41193df49e2` is VALID. Build6 does not include #614. No submission cancelled, build attached, upload or distribution performed by this preparation.

Latest main iOS tree `0953d367dcd64f402668836939582928e682fec7` exactly equals the build8 source tree from `afdafde6cf87ddfd29df5e6a5d9e724681551764`. Build8 development archive is `/Users/antonabyzov/.specwithcode/m4/evidence/iphone-latest-afdafde6c-b8/SpecWithCode.xcarchive`. Independent receipt confirms installation and live process19990 on iPhoneA, iPhone16Pro/iOS27.0.1, October23 at12:43AM EDT. This is direct development-app launch, not TestFlight launch or store availability. Installer owner holds no active build lane; no TestFlight6 launch confirmation exists.

Local App Store export8 SUCCEEDED from that same archive, destination export, automatic signing/teamNMCB2JZ7QG, build number management disabled. IPA signature verified, App Store distribution profile (no provisioned devices, get-task-allow false). SHA256 `cef31915b41b3268207e4efe276cf9da71fb5291c97a35414b0644758e4757ac`. Export and IPA verification receipts are in the evidence folder. No upload or new phone action performed.

Validator reports one expected state error: `version is in non-editable state "WAITING_FOR_REVIEW"`. Also warns `what's new is empty` (first-version history says unavailable) and raises App Privacy publish-state advisory. Cached Apple web auth is unauthenticated. Confirm published privacy via retained exact evidence or user before submission; do not invent a privacy confirmation or start new login flow. Preserve pending build4 until replacement artifact, exact-build launch evidence and readiness are established. Submission is not public availability.

## Safety and verification

SpecWeave installed3.1.4 versus live npm3.1.6; use session-local `npx --yes --package specweave@3.1.6 specweave`. Created and filled increment before any artifact changes. Product checkout `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio` was clean but behind remote; never switch its branch. Root CLI checkout has unrelated website changes and untracked apps; preserved.

Do not restart/force-drain service, directly access live SQLite, prune recovery files, use stash or kill foreign processes. Official Mac CI release produces signed/notarized artifacts without local fleet/app activation. Separately prove updater/service source, finalization, preservation and app version. Updater owner needs before/after hold, disconnect and peak disk acceptance. Browser work stays headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never, HTML open:never.

Verify and close 1015 after trigger execution, final evidence and fresh-context review.

## 1014 owner receipt

Owner checkout `/Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014`, branch `feat/t3-connect-onboarding`. Report `/Users/antonabyzov/.specwithcode/m4/worktrees/t3-connect-1014/docs/research/t3-connect-1014.md`. Exact PR/head and merged SHA awaited. Reported validation remains owner evidence until release reconciliation. Hosted relay is excluded: workflow `disabled_manually`, no runs, `relay.spec-weave.com` DNS failure reported. Native searchable model sheet with staged Save/Cancel and route diagnosis is evaluation only, not this release scope. No service restart or release dispatch by this lane.

## 1014 PR handoff

Release owner1015 now owns CI/merge inclusion for https://github.com/anton-abyzov/specwithcode-dev/pull/628 at head `e025a268fa25a7c3a4001108f5f504716439ad95`, open and unmerged at handoff. Owner reports increment1014 completed after verifyPASS (5/5ACs,3/3tasks), fresh-context final-commit reviewSHIP,13 focused tests,14 headless real-component checks, supported web typecheck, focused lint and production web buildPASS. Receipts `/Users/antonabyzov/.specwithcode/m4/evidence/t3-connect-1014`. Physical iPhone route and installed acceptance remain unverified. Existing Connect PRs444/445/469 are merged; no hosted relay deployment is inferred. No competing watcher started by code owner.

CI hookup for #628: exact head readback matches; OPEN/MERGEABLE, PR Gate/typecheck/Google pending. Native watch failed twice with `Could not change whether the pull request is watched.` Requested parent watch/terminal-event relay only, clientRequestId `1015-pr628-parent-watch-fallback`; no extra schedule or polling process created.

## 1018 browser lifecycle candidate

Owner reports fixes in progress in `/Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018`, branch `fix/browser-live-lifecycle`. Scope agreed with1016 is limited to `/Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/apps/web/src/browser/serverPictureInPicture.ts`, focused tests, isolated fixture and docs. Native capture/Manager untouched. Reported baseline regressions cover cancelled/older startup entering PiP, pending playback not settling on close, and missing metadata timeout. Await exact reviewed PR/head, verification and merged SHA before inclusion. No release, restart or deployment performed by this lane.

## 1016 snapshot quality candidate

Release1015 owns CI/merge/inclusion for https://github.com/anton-abyzov/specwithcode-dev/pull/629, reported commit `c1003ccea`, branch `fix/snapshot-retina-quality`. Fixes reported Retina downsample3024x1964 to1512x982 and blank picked-element capture at nondefault guest zoom (CSS versus Electron DIP). Owner reports347 focused tests, desktop vp pack, actual headless picker/comment/Attach at75/100/150percent and fresh reviewPASS with no findings. Evidence `/Users/antonabyzov/.specwithcode/m4/evidence/snapshot-quality-1016/report.html` and `/Users/antonabyzov/.specwithcode/m4/evidence/snapshot-quality-1016/verified/receipt.json`. Optional Claude adapter suite could not load pre-existing missing `pptxgenjs`; no installed or live-provider acceptance claimed. Await exact-head CI and merge ancestry. No independent release.

## 1020 harness support, not ready

Owner checkout `/Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020`, branch `feat/harness-support-1020`, base `252be2eb4`. Pi RPC discovery false-ready fix and picker harness/protocol explanation underway;111 focused tests reportedPASS. Actual OpenCode1.14.33 native local synthetic-model contract check running. Installed Pi0.66.1 is below minimum0.80.5. No release inclusion until exact verified SHA, review/CI and merge ancestry are supplied. No dispatch. Preserve6:00AM EDT cutoff and6:26AM EDT trigger.

## 0993 merged updater handoff

#626 squash merge `ef227c979bb9522330c1c82b96b6774651f37f77` verified remotely. Handoff `/Users/antonabyzov/Projects/github/studio-research-notes/update-path-20261023/release-1015-handoff.json`. CI receipt `/Users/antonabyzov/Projects/github/studio-research-notes/update-path-20261023/pr626-checks-f8352ba12.json`; complete log `/Users/antonabyzov/Projects/github/studio-research-notes/update-path-20261023/pr626-checks-f8352ba12-full.log`. No iOS changes, release dispatch or restart.

Runtime acceptance must independently show signed/notarized release ancestry containing this merge, installed app/service readbacks, actual held/disconnected duration, peak filesystem free-space delta and afterProof mode/fallback/readiness. Baseline1.0.74 hold261seconds/disconnect approximately6seconds; beforeRead61067ms/readiness70998ms/clone34ms. Current installed `/Users/antonabyzov/.specwithcode/install/updater/update_agent.py` lacks held-snapshot support per updater owner. First upgrade may still incur old-agent prestate read; do not attribute its removal to source alone. Wake updater owner after controlled authorized install to measure0993T03/T04 and close that increment. Preserve all recovery files.

## 1007 explicit merge hold

User-expanded scope includes grounded next-seven-day forecast, responsive ranked models/category bars, exact sampled lines and touch/keyboard cursor. Existing owner/worktree retain implementation. Do not merge or accept #625 head `ccf2ae998848317c3f76f91333b81be2cd6b0307` as final even if its CI passes. Follow-up code is being verified;108 focused web/branding tests and source typecheck reportedPASS. Await new exact reviewed head plus merged SHA/receipts before6:00AM EDT cutoff. No release dispatch or service restart. This hold supersedes any earlier1007 candidate readiness.

## 1017 provider CLI update PR

Release1015 inspected clean owner checkout `/Users/antonabyzov/.specwithcode/m4/worktrees/provider-cli-fleet-update`, branch `feat/provider-cli-fleet-update`, exact commit `26904bba4ad6b06462cda4f78eee1ccb19d59eb5`. Pushed exact commit without force and opened https://github.com/anton-abyzov/specwithcode-dev/pull/631. Owner reports100 focused tests, production web/server builds, server tsc, headless routing/outcomes and fresh reviewPASS. Local update receipt `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/live-local-update.json` confirms Codex0.162.1 to0.164.0, old entrypoint/auth hash retained, no restart and zero remote updates. Web tsc TS2883 in untouched newThreadWorkspaceDefault.ts remains disclosed. Five peers need_grant is not proof of UI providers:manage. Installed UI acceptance and1017 closure stay with owner. No0957 updater files changed. Await CI/merge ancestry.

## 1018 browser lifecycle PR

Release1015 owns CI/merge inclusion of https://github.com/anton-abyzov/specwithcode-dev/pull/630, exact head `fadc5da6712a7fb018bb46cc24b33be40c0a0da7`, open/unmerged at handoff. Owner reports1018 complete after verifyPASS4/4ACs,3/3tasks,31 lifecycle/client/server stream tests, web typecheck/lint/build and fresh SHIP after two findings fixed. Headless native preview tool evidence covers real navigation,960px scroll, source frame through production painter to real canvas/video, replaced/cancelled startup, host failure/recovery. OS PiP API substituted; native z-order/Spaces not proven. Report `/Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/docs/research/embedded-browser-1018.md`; evidence `/Users/antonabyzov/.specwithcode/m4/evidence/browser-live-1018`. Scope does not touch1016 capture/annotation/Manager. No restart/release or competing watcher. Retain interactive embedded-browser and view-only always-on-top live-frame paths; no redesign inferred.

## #631 exact-head typecheck failure

Checks run39908894634 at `26904bba4ad6b06462cda4f78eee1ccb19d59eb5`, job120267111191 failed. Complete log `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr631-typecheck-26904bba4-full.log`; complete47-file artifact `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr631-typecheck-artifact-26904bba4`. Gate reports15packages,7new diagnostics: changed providerMaintenanceRunner.test.ts TS377023+1; changed providerMaintenanceRunner.ts TS377021+2,TS377030+4. These are introduced Effect-aware typecheck failures, not the webTS2883 baseline. Original1017 code owner asked to repair typed errors, run matching gate and focused checks/review, push new head to631; no baseline/suppression/waiver. Parent watch remains.

## 1020 local ready source

Owner supplies local SHA `37e17345d` on `feat/harness-support-1020`, checkout `/Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020`, base252be2eb4. Pi failed-RPC startup warning, OpenCode2 truthful MCP capability, picker harness/protocol/model-billing facts and docs. Reports208focused tests, production web/server builds, fresh SHIP and actual OpenCode1.14.33 adapter tools/stream/native-session resume on synthetic local model without spend. Report `/Users/antonabyzov/.specwithcode/m4/evidence/harness-support-1020/report.md`. Installed UI/compatible Pi live acceptance unclaimed; no settings/installs altered. Await release-owner integration and exact CI/merge.

1020 exact clean commit `37e17345dee81f92defed832664faa003c31f73c` pushed without force; opened https://github.com/anton-abyzov/specwithcode-dev/pull/632 and requested parent CI-event relay. No product code changed during integration.

## #631 repaired candidate supersedes original head

New expected head `4c25c1effd1f5dd57d6125b9072b0c17d33f37bf`, fast-forward pushed without force. Owner replaced unknown promise/idle-check error channels with existing ProviderMaintenanceCommandError, preserving messages/causes. Matching Effect-aware gate15packages,0new diagnostics,checkers2, baseline unchanged (existing79server,web0);74focused tests and fresh reviewPASS/no findings. Earlier plain tsc receipt is superseded. Full47-file artifact `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/effect-repair/typecheck`; gate log `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/effect-repair/typecheck-gate.log`; report `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/effect-repair/report.md`. T-05 done, T-04 installed acceptance open. Await exact new-head required CI; no baseline waiver. Parent watch remains.

## #632 typecheck failure

Exact head `37e17345dee81f92defed832664faa003c31f73c`, run39909794515/job120269924872:15packages,4new diagnostics,FAILED. New TS2379 optional existingProviderThread explicitly undefined at OpenCodeAdapterV2.live.test.ts82; TS377033 multiple Effect.provide at202; TS2322 plain strings missing ProviderDriverKind brand at HarnessDescription.test.tsx47/55. Introduced diagnostics; local tests/builds do not waive. Full job log `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr632-typecheck-37e17345d-full.log`; complete artifact `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr632-typecheck-artifact-37e17345d`. Original1020 owner asked to repair/run matching gate and fresh review/push fast-forward. Existing parent watch retained; no duplicate schedule or release.

## #628 merged for release inclusion

Re-read exact head `e025a268fa25a7c3a4001108f5f504716439ad95`: all checks SUCCESS/SKIPPED, aggregate PR Gate/typecheck/public mirror/Google SUCCESS, OPEN/MERGEABLE/CLEAN, no review findings on GitHub. Retained fresh reviewSHIP. Authorized squash/admin merge with match-head guard succeeded as `470f9076579c137a6aaba650bb6f953fe09c0f11`. Merge receipt `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr628-merge.json`. Candidate inclusion still checked by final release ancestry; no release dispatched. Hosted relay and physical iPhone acceptance remain unverified.

## #625 new final candidate replaces earlier hold

Owner supplies final expanded head `4d477571d62a9142317a601d315eb39abc9c3772`: grounded7day forecast, exact shared provider cursor, keyboard/direct-tap pinning, five stacked cost types and responsive ranked models. Earlier `ccf2ae998848317c3f76f91333b81be2cd6b0307` remains excluded; hold is lifted only for this new reviewed candidate.113focused web plus30shared tests, source tsc, production build and fresh reviewPASS reported. Exact Checks run39910856904 pending; superseded39906876093 cancelled by owner. Owner will send merged SHA after green. Fixture receipt `/Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023/forecast-fixture-receipt.json`; screenshots `/Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023/v2-desktop-dark.png` and `/Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023/v2-mobile-breakdown.png`. Installed `/usage` acceptance and1007closure open. iOS receives additive shared merge fields only, no native dashboard. No dispatch/restart.

## #632 repaired head, required Checks still pending

Resolved new full head `67ee8f8d529f7139858be3792a40458e1e1c8d4e`. Inspected two-test-file repair: omit undefined optional field, combine Effect providers, construct branded driver IDs. Matching15package gate0new diagnostics/baseline unchanged,208focused tests and actual adapter passed per `/Users/antonabyzov/.specwithcode/m4/evidence/harness-support-1020/pr632-repair/receipt.json`; fresh approve/no findings in `/Users/antonabyzov/.specwithcode/m4/evidence/harness-support-1020/pr632-repair/review.md`. Six green watcher-event checks were ancillary Security/Labels only. Checks run39910966487 PENDING; mergeStateStatusBLOCKED; not merge-ready, no merge performed. Parent relay updated to new full head, same watch. Original37e17345d failure historical, not waived.

## 1011 excluded, optional before-capture receipt

1011 owner explicitly reports NO merge candidate for this release; app code gated on app-folder approval, nothing merged or merging. Exclude1011 from release claims. Owner plans headless BEFORE capture of installed1.0.74 using private scratch state and own serverPID, without live service/DB contact; due5:45AM EDT. Receipt `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1011-activity-diffs-and-compact-output/reports/installed-before/receipt.json`. At6:26AM trigger check receipt existence; if missing report before set missing and proceed. No release hold, restart or dispatch requested.

## 1013 recovered child delivery merged

#627 https://github.com/anton-abyzov/specwithcode-dev/pull/627 squash merge `8ddb581237755e91154beaf5aece8271eb6ddadc`, tested head `38919d3cc5cae714f9a034c1abc50c1df499d218`, exact-head Checks39906202894 SUCCESS. PR Gate/typecheck/Google/public mirror/native fingerprint/security/attribution pass; fleet/release/mobile native path-filter skipped.143tests across six delivery/recovery/MCP/fallback suites reportedPASS; fresh reviewPASS. Evidence `/Users/antonabyzov/.specwithcode/m4/evidence/limit-child-result-20261023`. Include by final candidate ancestry. Installed recovered-child-newer-result delivery remains unverified; source proof alone does not close runtime gate.1003 still needs installed complex/routine routing and exhausted-provider skip receipts for #622 `ab96f4d1c25284282553a4099b503b307a0b26a5`. No dispatch/restart from owner.

## 1022 source candidate, PR633

Inspected clean checkout `/Users/antonabyzov/.specwithcode/m4/worktrees/coordinator-readiness-1022`; pushed exact `dd7851aa9f9305a6a1c08bef2dd529b23c1c4a92` without force and opened https://github.com/anton-abyzov/specwithcode-dev/pull/633. Reviewed code head84f488335, later docs only. Native helper/assets preflight before capture, actionable provider/platform/ElevenLabs setup gates, automatic default excludes known paid/no-tools models.174focused tests,5headless scenarios,web/server/desktop builds,Swift compile/free synthesis reportedPASS; fresh independent review0findings/103tests. Evidence `/Users/antonabyzov/.specwithcode/m4/evidence/coordinator-readiness-1022/fresh-review.md` and `/Users/antonabyzov/.specwithcode/m4/evidence/coordinator-readiness-1022/browser-receipt.json`; report `/Users/antonabyzov/.specwithcode/m4/worktrees/coordinator-readiness-1022/docs/research/coordinator-readiness-1022.md`. Server typecheck errors outside changed code retained, requiredCI remains enforced. Installed native microphone/spoken request/reply/mute/hang-up still1022T04; synthetic fixture/nativeWAV is not call acceptance. Paid ElevenLabs check requires separate authority. Parent CI relay requested; no dispatch/restart/provider turn.

## #629 merged

Re-read exact tested head `c1003ccea07c1a9b7e156a977ea67a2dc830b5e5`: aggregate PR Gate/typecheck/public mirror SUCCESS, all remaining checksSUCCESS/SKIPPED, OPEN/MERGEABLE/CLEAN, no GitHub review findings. Retained source/fixture receipt and owner fresh reviewPASS. Squash/admin merge with exact match-head guard succeeded as `5b0e564eb28c65be94338f38daa82fdf134cb96e`. Receipt `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr629-merge.json`. Include by final candidate ancestry; installed/live-provider acceptance remains unclaimed. No release dispatched.

## #633 required gate failure

Exact `dd7851aa9f9305a6a1c08bef2dd529b23c1c4a92`, run39911603382/job120275702125 reports15packages,2NEW TS377033 in changed ProjectCoordinatorService.test.ts. Introduced chained Effect.provide lifecycle diagnostics, not disclosed outside-code baseline. Full log `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr633-typecheck-dd7851aa9-full.log`; complete artifact `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr633-typecheck-artifact-dd7851aa9`. Original1022 owner requested repair, matching Effect-aware15package gate, focused tests/fresh review and fast-forward push to633; no suppression/baseline waiver. Installed call gate remains open. Parent watch retained.

## 1013 closure review High and repair635

Closure review found High in merged #627: user Stop during child's fallback run can re-arm parent wake. Repair https://github.com/anton-abyzov/specwithcode-dev/pull/635 exact head `e5fe764a0f93450b78ede307b4b795ca5ad3f96c`, one Orchestrator.ts guard plus regression red without guard.144tests across six suites/server build/typecheck reportedPASS. Checks39912222288 running and fresh review in progress. Original1013 owner retains merge after green before6:00AM EDT and will send merged SHA. Explicit release direction: if635misses cutoff, ship627with known Stop gap disclosed; no silent full Stop acceptance claim. Prefer635inclusion once exact reviewed merge ancestry verified.

## #630 PR Gate timeout investigation

Current head still `fadc5da6712a7fb018bb46cc24b33be40c0a0da7`. Run39908820281 failed, Stage1pass; server shard1 5643tests1failure, shard2 5510tests0failures. Exact error: `src/serverSettings.test.ts > server settings clears a sign-in the registry's driver writes while it is disposed: TimeoutError: Operation timed out after '10s'`. Changed paths are web lifecycle/tests/docs only; failed serverSettings.test.ts unchanged since716827f73/#451. This establishes unrelated source path, not flakiness or merge readiness. Original1018 owner requested focused watcher-race/infrastructure investigation before rerun, no weakened timeout/waiver. Full job `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr630-gate-fadc5da67-full.log`; complete artifact `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr630-gate-artifact-fadc5da67`. Parent watch retained, no merge.

## #634 pending owner merge

1023 Add approved folders while project work runs: https://github.com/anton-abyzov/specwithcode-dev/pull/634, head `df2ad5fb7f7738938ba81d6cea7061deb01ca204`. Original1009/1023owner retains merge after requiredCI and fresh exact-headSHIP. Reports typecheck gatePASS/883focused tests; PR Gate/Google pending. Await exact mergedSHA by cutoff. No release/restart from owner.

## #631 repaired source merged

Fresh readback exact `4c25c1effd1f5dd57d6125b9072b0c17d33f37bf`, OPEN/MERGEABLE/CLEAN, all checksSUCCESS/SKIPPED including aggregatePRGate/typecheck/publicmirror/Google; no GitHub review findings. Retained fresh repair reviewPASS and15package0new diagnostic receipt. Authorized squash/admin merge guarded by exact head succeeded as `05fa77b27d7b8d3652dcf6da36745ba359affbc2`. Receipt `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr631-merge.json`. Final candidate ancestry still required. Remote fleet and installed manual acceptance remain unverified; no release/restart/update executed by merge.

1018 owner confirmed focused settings-watcher/disposal-handshake investigation on clean original browser-live-1018 checkout; no rerun/watch/release/restart, native/capture scopes untouched. Await reproduction before any independent fix.

## #632 green head conflicts with main

Parent reports actual required gates now green on `67ee8f8d529f7139858be3792a40458e1e1c8d4e` and new main conflict. Original1020owner requested safe merge-main conflict repair in its existing checkout, preserve1017/1003behavior and ownership, no force push/rebase/shared branch changes. Resolution creates new head requiring matching renewedCI, focused affected checks and fresh review. Old green is not proof for repair. Parent watch retained; no merge/dispatch from conflict notice.

## #630 local timeout reproduction

Original1018owner reproduced exact original test sequence timeout5/100cases. Trace receives wanted=true then wanted=false, enters late credential write that never completes, while removal returns. This is evidence of local secret-store write/delete interleaving, not filesystem-watch loss or CI-only infrastructure. Diagnostic `/Users/antonabyzov/.specwithcode/m4/evidence/pr630-settings-race/diagnostic.log`. Owner narrowing cause; no product edits/gate rerun. Keep630blocked, no blind retry.

## #630 deterministic secret-store root cause

Owner controlled interleaving reproduces timeout: late refresh renames mode0600 temp secret into place, concurrent removal deletes final before redundant chmod(finalPath), chmod returnsNotFound, cleanup of renamed-away temp also fails, watcher never signalslateWrite. ControlledIO receipt `/Users/antonabyzov/.specwithcode/m4/evidence/pr630-settings-race/controlled-interleaving.log`. Proposed smallest independent repair removes post-rename chmod while retaining pre-rename0600chmod. Owner preparing focused regression and fresh review separately; no remote push/CI rerun/merge. Await verified repair before630gate rerun; preserve secret permissions and no broader lifecycle/native scope.

## #625 superseding reviewed head499b54fd

1007owner reports fresh review of4d477571dfound4issues, fixed/re-reviewedSHIP in `499b54fdfe1175c33fcd6a57bd06fcb448a4201f`. Follow-up web-only underapps/web/src/components/usage. Checks39916297454queued for new exact head. Owner retains squash merge only after exact-headgreen and sends mergeSHA before6:00AM EDT. Explicit direction: if625misses cutoff, ship without625. Earlier4d477571dnot final. No dispatch/restart; no reply requested.

## 1024 independent repair validation, clarification

Independent1024repair local:105settings/secret-store testsPASS, original disposal diagnostic100/100PASS,lintPASS,server Effect-aware baseline79existing/0newPASS,specweave3.1.6verifyPASS. Fresh review in progress; exact commit awaited. Patch `/Users/antonabyzov/.specwithcode/m4/evidence/pr630-settings-race/repair.patch`. Correct interpretation: credential setFAILS at redundant post-renamechmod; success-onlylateWriteDeferred is never reached. This is NOT stalledIO. Supersedes prior informal wording that late write never completes. #630remote unchangedfadc5da67; no push/rerun/watch/release/restart. Await reviewed commit before integrating repair intoCI.

## #630 combined head237d07f68

Inspected clean owner checkout, exact source/test repair and1024freshSHIP review; fast-forward pushed `237d07f6899fd333c4ce70a22c724ca14cf1ed9b` atopfadc5da67 to existing630branch, no force. PR body updated to reflect independent credential-write repair. Temp0600protected before atomic rename; redundant postrenamechmod removed.105settings/secret-store tests,100disposal cases,lint,79existing/0new server diagnostic gate,reviewer11tests and1024verify/completePASS reported. New combined head requires renewed remoteCI; no prior failure rerun or bypass. Parent relay bound to237d07f68; nativePiP/z-order/Spaces exclusions unchanged. No release/restart.

## #635 Stop repair merged,1013closed

Owner reports #635merge `f8999fcfefbcdf7e6e83e1053a2435012893d3b7`, exact tested head `fcbfa5060b20fc579ed496f1bea7b348182f32ec`, Checks39913798767SUCCESS. Supersedes queuede5fehead. Include alongside #627merge `8ddb581237755e91154beaf5aece8271eb6ddadc` by final release ancestry. UserStop before/during child recovery preserves earlier result and prevents re-waking stopped parent; agentinterrupt/serviceupdate/watchdog/start-timeout still deliver.202tests/ninesuites,serverbuild/typecheck,freshreviewrounds1-5PASS.1013verify3/3ACs4/4tasksPASS andcomplete reported. Evidence `/Users/antonabyzov/.specwithcode/m4/evidence/limit-child-result-20261023`. Known sourceStopgap resolved by635inclusion; installed recovered-child delivery and1003complex/routine/exhausted-provider-skip receipts remain. No dispatch/restart.

## #634 approved-folder repair merged

Owner reports3:59AM EDTmerge `4b7962d9fe678406c2e8df5f99e8341005ed4ece`, reviewed/tested head `3f1be725eaf6b175bd9202dce81706f6106702bf`, supersedingdf2ad5fb. RequiredCIincludingPRGate/Google/typecheck/publicmirror/security/attributionPASS;892focused tests/fourfreshreviewsfinalSHIP. Include by final release ancestry. Release-note line: "Project settings can add a folder while threads are running, and agents can ask you to approve a folder from a card." Original1023owner will run installed acceptance after install: add app folder tospecweaveproject while threads run. No release/restart from owner.

## #630 combined1018/1024merged

Fresh read exact `237d07f6899fd333c4ce70a22c724ca14cf1ed9b`, OPEN/MERGEABLE/CLEAN, all checksSUCCESS/SKIPPED including aggregatePRGate/typecheck/publicmirror/Google; no GitHub review findings. Retained fresh lifecycle/independent1024SHIP. Squash/admin merge guarded by match-head succeeded as `55f392a9715dfad2b69c4916890d3f6c8783e0c3`. Receipt `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr630-merge.json`. Priorfadcgatefailure resolved through tested independent secret-store repair, not waived. Include final merge by release ancestry. NativeOSPiP/z-order/Spaces stillunverified. No release/restart dispatched.

## #632 repaired main-merge head merged

Resolved full head `e6e2c06a48f068d651efad5cf3987b52d8a7fe28`, parents67ee8f8and05fa77b27. Only conflictCHANGELOG, both notes retained;22provider/installer/fleet/routing blobs match mergedmain unchanged per receipt. Fresh exact-head review nofindings,15package0newdiagnostics/352focused/realOpenCodeadapterPASS. RequiredremotePRGate/typecheck/publicmirror/GoogleSUCCESS, allotherSUCCESS/SKIPPED,OPEN/MERGEABLE/CLEAN,noGitHubreviewfindings. Squash/admin match-head merge succeeded as `1d63fd291f5ca8199008b7947fe43f7018386d32`. Merge receipt `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr632-merge.json`; conflict review `/Users/antonabyzov/.specwithcode/m4/evidence/harness-support-1020/pr632-main-merge/review.md`. Include finalmerge by ancestry; installedapp/compatiblePilive/OpenCode2live acceptance unclaimed,OpenCode1no-toolsMCPretention followup retained. No release/restart.

## #625 final expanded dashboard merged

#625squashmerge `ddeaee06b130f8c582e6d4801d636fd66c6936e4`, exact finalhead `499b54fdfe1175c33fcd6a57bd06fcb448a4201f`,4:49AM EDTbeforecutoff. Owner reports allgreenChecks39916297454attempt2; attempt1time-sensitiveServiceUpdateHold.test.tsfailure untouchedbyweb-onlyPR retained. Freshre-reviewSHIP. Evidence `/Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023/ci-39916297454-terminal.json`, `/Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023/ci-39916297454-complete.log`, `/Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023/ci-39916297454-attempt1.log` and `/Users/antonabyzov/.specwithcode/m4/evidence/usage-cost-dashboard-20261023/pr625-merge.json`. Include finalmerge by ancestry; earlierheads superseded. ScopewebUsagepage/additivesharedmergefields; mobile newfields only, no screen. Release note: "Usage separates API-equivalent estimates, billed spend and plan allowance, never shows unknown cost as $0, and adds provider/model filters, day pinning and a 7-day outlook." After authorizedrollout return actualapp/serviceversion/source to1007owner for installed/usagecapturesandclosure. No ownerdispatch/restart.

## #633 repaired after1.0.75publication, next candidate only

New exact head `8f0b1ca111ff7362f83367138e69005f749962e0` fast-forward fromdd7851aa9. BothnewTS377033sites use one Coordinator.layerwithLayer.provideMerge(dependencies). Owner matching15packageEffect-aware gate0newdiagnostics/baselineunchanged(server79accepted),174focusedtests/freshnarrowreviewPASS. Logs `/Users/antonabyzov/.specwithcode/m4/evidence/coordinator-readiness-1022/pr633-typecheck-final.log`; completepackagefiles `/Users/antonabyzov/.specwithcode/m4/evidence/coordinator-readiness-1022/pr633-typecheck-final`; tests `/Users/antonabyzov/.specwithcode/m4/evidence/coordinator-readiness-1022/pr633-repair-tests.log`; review `/Users/antonabyzov/.specwithcode/m4/evidence/coordinator-readiness-1022/pr633-typecheck-fresh-review.md`. Earlieroutside-codeclaimcorrected,nowaiver. This head is NOT included in already-published1.0.75frozenatddeaee06/candidatec52ee223. Retain existingparentwatchnewhead; nextreleasecandidateonly, no newdispatch from this notice.1022owner retainsinstalledT04.


## PR #633 merged for the next candidate

On October 23, 2026 at 10:08 AM EDT, PR #633 squash-merged at `4726037365435c03db827ded75787eace5ae2fa6`, guarded by exact head `8f0b1ca111ff7362f83367138e69005f749962e0`. Independent live readback confirmed CLEAN/MERGEABLE, no submitted GitHub reviews, and SUCCESS for all three actual required checks: Changed paths, PR Gate, and PR Gate (typecheck). Public mirror also passed. Existing source and narrow repair review receipts were retained.

This merge is a next-candidate change; published 1.0.75 excludes it. No release dispatch or restart occurred. Installed native call acceptance T-04 remains with the 1022 owner. Merge receipt: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence/pr633-merge.json`.
