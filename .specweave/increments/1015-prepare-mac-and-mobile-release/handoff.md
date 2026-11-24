# 1015 trigger handoff

## Start here

Owner: `thread:delegated-task:command%3Amcp%3Af9b6f93f-2383-4a68-8fb1-0a0bb9d73b36%3Adelegate-task%3Aprepare-five-hour-release-20261023`.

Spec: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/spec.md`.

Read `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/release-readiness.md` and new owner replies first. No publication before October23,2026 at6:26AM EDT. Sole coordinator timer already exists; create no duplicate.

## Trigger execution

1. Refresh CLI stable/version and owner/run/schedule state. Preserve active owners, cancelled historical1.0.75 and pending iOS submission. Check remote release runs, tags, drafts, release PRs and local processes before reserving version.
2. Reconcile all completed verified merges through6:00AM cutoff and late verified items through trigger. Freeze exact main SHA and record inclusion ancestry plus source/test/review receipts. No working-tree patch inclusion. Avoid shared-checkout switch/stash; use approved isolated release checkout only if needed.
3. Mac official workflow is `release-macos.yml` in `anton-abyzov/specwithcode-dev`, required input `version`, optional `previous`, `stop_after`, `resume`. Inspect latest remote workflow before use. Dispatch exactly once on frozen approved ref; record returned run ID and source. Follow its real gates; never skip server tests/signing/notarization/public mirror. If a release is already running, reconcile instead of dispatching another.
4. Verify both private/public releases, asset digest agreement, SHA256SUMS, update plan chain and source. Run the signature checker from the exact candidate on downloaded DMG/ZIP for Developer IDNMCB2JZ7QG, notarization, stapling and architecture. Save all receipts. No automatic service restart/force-drain from release authority alone. Ask updater owner to complete managed update acceptance under its existing authorization, measure hold/disconnect/disk, preserve backups/grants and notify1003/1007 owners only after actual installed evidence.
5. Mobile: refresh ASC version/submission/build state. Check local export8 receipt, exact archive and iOS tree; if newer iOS changes merged, rebuild/verify through current owner and named launch gate. Never claim development8 is TestFlight8. Verify archive/IPA build/source/signature, upload only after trigger, await VALID and run release stage dry-run plus validate. Preserve pending4 until replacement is ready. Use existing submission lane after exact cancel/status/attach/validate as needed; user authorized latest release replacement, but never cancel merely because Apple is slow.
6. The local asc wrapper requires exact-build real-iPhone launch proof and truthful ASC_LAUNCH_VERIFIED before review submission. Existing development8 launch receipt is source-bound; do not reuse it for a rebuilt or changed build. Resolve App Privacy published state using `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/privacy-evidence.md` and prior owner response. Cached web auth false is not proof that publication is missing; exact prior receipt is being traced. No new login/physical phone actions from this handoff. First0.1.0 may not expose WhatsNew; inspect rather than forcing unavailable fields. Dry-run before high-level mutation, explicit --confirm for submit. Submission receipt/status and independent public listing check must be reported distinctly.
7. Record T-03/T-04 only when real release/submission criteria met. T-05: `specweave verify 1015`, fresh-context subagent review, then `specweave complete 1015`. Do not mark complete for preparation alone.

## Commands and evidence

Use session-local `npx --yes --package specweave@3.1.6 specweave`, recheck registry on a new session. Task ledger positional syntax is `task claim T-01 1015` and `task done T-01 1015 --evidence ...` (not --increment).

ASC app6824245458/version08b06b7f-6e58-4982-8cbd-65681a10740b; pending submission9a5ec644-ead8-4159-9989-745db828915c. Existing supported read: `asc status --app 6824245458 --include builds,appstore,submission,review --output json`.

Preparation evidence folder: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/evidence`.

Prior Mac final receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/release-1073-20261022/final-acceptance.json`.

Build8 phone receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/iphone-latest-afdafde6c-b8/receipt.json`.

Updater tests: `/Users/antonabyzov/Projects/github/studio-research-notes/update-path-20261023/fleet-final-result.json`.

Updater review: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0993-one-press-updates-app-applies-install-proofs-in-seconds/reports/review-updater-20261023.md`.

Never directly access userdata/statev2.sqlite files. Every browser automation headless:true with file-backed evidence. Preserve all active sessions and code owners.

## Updater0993 runtime continuation

Include #626 merge `ef227c979bb9522330c1c82b96b6774651f37f77` by exact candidate ancestry. Read `/Users/antonabyzov/Projects/github/studio-research-notes/update-path-20261023/release-1015-handoff.json`. After an authorized controlled install, wake `thread:delegated-task:command%3Amcp%3A9bc507ed-4650-4e13-83b6-9529929a4092%3Adelegate-task%3A123ba876-eadc-4e59-a9ab-0a7ab21a3c78` for0993T03/T04 measurements/closure. Required: hold/disconnect duration, peak free-space delta, app/service version/source and afterProof mode/fallback/readiness. Old installed agent lacks held-snapshot support, so first upgrade can retain its prestate scan; do not claim this cost gone before confirming the new agent. Preserve recovery files and existing restart authorization boundary.

## 1007 superseding merge hold

Do not merge #625 head `ccf2ae998848317c3f76f91333b81be2cd6b0307` even on green CI. Owner is verifying expanded dashboard scope and must send a new exact reviewed head and receipts. Preserve the same worker/worktree. Exclude stale1007 candidate until explicit new final handoff.

## 1017 installed acceptance and closure ownership

Source `26904bba4ad6b06462cda4f78eee1ccb19d59eb5` is clean. Owner recordedT-01 throughT-03 done. Verification reran100 focused tests successfully; overallFAIL is solely AC-06/T-04 installed UI manual acceptance (5/6ACs,3/4tasks), not a test failure. No completion override. After release and authorized installed UI acceptance, return concrete receipt to the original1017 implementation thread; that owner retains final verification/closure. Reports `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/report.md` and `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/report.html`; verify log `/Users/antonabyzov/.specwithcode/m4/evidence/provider-cli-fleet-update-1017/specweave-verify.log`.

## 1017 post-rollout acceptance procedure

Keep1017 open; #631 expected head `26904bba4ad6b06462cda4f78eee1ccb19d59eb5`, source clean. Existing parent watch only. Record actual installed app/service versions and SHAs. Open Settings > Providers selected Codex action; verify selected instance/local default, explicit connected-peer opt-in, skip reasons, authoritative destination permission and per-machine outcomes. Do not restart. Local Codex already0.164.0: never downgrade or reinstall just for a demonstration. Use an honestly outdated safe instance only with existing authority, otherwise report current/unsupported plan inspection separately from real update execution. Before any remote execution verify fresh existing `providers:manage` grant plus executable ownership and busy-state evidence; worker `needs_grant` is not UI-scope proof. Return screenshot/receipt and remaining limitations to original1017 owner forT-04 verification/closure.

## #625 final expanded head supersedes hold

Final candidate `4d477571d62a9142317a601d315eb39abc9c3772` supersedes prior held head; only the new exact-head green CI/merged SHA can qualify. Owner will send merge after Checks39910856904 passes. Retain installed `/usage` acceptance/1007closure and iOS no-native-dashboard boundary.

## 1011 no-hold exclusion

No1011 merge candidate. At trigger check `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1011-activity-diffs-and-compact-output/reports/installed-before/receipt.json`; due5:45AM EDT. If absent report missing before set and proceed without delay. Capture owner uses private scratch/own serverPID, no live service/DB. Do not wait or infer code acceptance.

## 1013 and1003 post-release runtime proof

Include #627 merge `8ddb581237755e91154beaf5aece8271eb6ddadc` by ancestry. After authorized install, coordinate original recovery owner for actual recovered child delivering newer result to parent (1013), plus complex/routine routing and exhausted-provider skip for #622 (1003). Source/test success is not installed runtime proof; retain exact result/session evidence and avoid unapproved paid turns. Evidence source `/Users/antonabyzov/.specwithcode/m4/evidence/limit-child-result-20261023`.

## #627 known Stop gap, repair635

1013 closure review found High: Stop during child fallback can re-arm parent wake. Repair635 head `e5fe764a0f93450b78ede307b4b795ca5ad3f96c`, Checks39912222288 and fresh review pending; original1013 owner handles merge and sends SHA. At cutoff include merged635by ancestry if green. Explicit direction allows627shipping if635misses cutoff, with this gap disclosed. Do not claim Stop gap fixed without635merge inclusion.

## #625 latest expected head

Final candidate now `499b54fdfe1175c33fcd6a57bd06fcb448a4201f`, superseding4d477571dafter4reviewfindings fixed. Checks39916297454queued; owner handles merge/sendSHA. If not merged green by6:00AM EDT, explicitly ship without625.

## #635 supersedes known Stop-gap warning

Include #635merge `f8999fcfefbcdf7e6e83e1053a2435012893d3b7` with #627merge `8ddb581237755e91154beaf5aece8271eb6ddadc`.1013sourceverify/completePASS; known sourceStopgap is repaired when635ancestry is verified. Installed childdelivery/1003routing receipts still required; do not infer runtime acceptance from closure.

## #634 inclusion and installed acceptance

Include #634merge `4b7962d9fe678406c2e8df5f99e8341005ed4ece` by final candidate ancestry. Release notes: "Project settings can add a folder while threads are running, and agents can ask you to approve a folder from a card." After authorized install notify original1009/1023owner to add the app folder tospecweaveproject while threads run; installed acceptance stays distinct from892tests/greenCI/freshSHIP.

## #625 now merged before cutoff

Include #625merge `ddeaee06b130f8c582e6d4801d636fd66c6936e4`, superseding priorconditionalexclude warning. Exact499b54fdhead passed39916297454attempt2, evidence retained. Release note: "Usage separates API-equivalent estimates, billed spend and plan allowance, never shows unknown cost as $0, and adds provider/model filters, day pinning and a 7-day outlook." After installation notifyoriginal1007owner with exactapp/serviceversions/SHAs for installed/usagecapture/closure. No nativeiOSscreen.

## Installed M4 restart approval pending with0993owner

1.0.75downloaded, not installed. Lock-loss refusal at10:52Z/11:02Z: "The SpecWithCode service lost its SQLite locks on its database. Restart SpecWithCode, then update."0993owner already asked user to approve service restart; do not duplicate or infer approval from release authority. CurrentPID47190and1.0.74remain. Free4.1GiBpasses clonepreflight. Preserve backups and sessions; after approved update owner measures hold/disconnect/peakdisk/afterProof/readiness/newagent/version.


## Release increment completed October 23, 2026

1015 completed after all six unchanged umbrella verification commands passed under Node 22 with inherited CODEX_SESSION_ID and CODEX_THREAD_ID removed. Earlier failed Node 26 and inherited-session receipts retained. ACs 5/5, tasks 5/5, fresh independent review PASS. Canonical review `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1015-prepare-mac-and-mobile-release/reports/review.md`.

macOS 1.0.75 published and service installed; desktop application last reported 1.0.74. iOS 0.1.0 build 8 submitted, WAITING_FOR_REVIEW, submission `3cf1d21d-dc72-418d-a88e-f8ec77586a4f`. Published Data Not Collected privacy independently verified using the user-requested Chrome extension. Public iOS availability, desktop/feature installed acceptance and incident work recovery remain with original owners. No new release or restart authorized by closure.

Completion emitted non-blocking JIRA/ADO mapping errors because no issue key/work item ID exists; zero external items were closed. Do not retry tracker sync without a real target.
