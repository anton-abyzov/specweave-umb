# Studio 1.0.178 release follow-up

SpecWithCode Connect is the primary worker transport. Tailscale is a fallback when Connect is unavailable. A Connect authorization or policy denial must remain visible and must not trigger a retry over SSH. Select the route using a read-only operation before submitting a mutation, and keep it pinned for the operation.

The fresh Connect readback matched the expected M3 and M1 identities and reported `transport=connect`, `serverVersion=1.0.178`, `installedVersion=1.0.178`, and `status=up-to-date` on both. The older 1.0.175 installed state cannot be verified on these upgraded workers. See studio-1.0.178-connect-readback.json.

The current rollout has the opposite preference in `scripts/studio-fleet/fleet_rollout.py` (FallbackHost). The umbrella verifier checks M1/M3 service through fixed local ports and checks their desktop bundles with pinned SSH. Connect fleet status supplies no local bundle signature or Gatekeeper evidence. The release owner should move remote service checks to authenticated Connect and retain a separate desktop gate. A native receipt must bind the intended machine and version to the installed bundle, strict codesign, the required Developer ID, and Gatekeeper. Existing pinned SSH can supply that evidence as a fallback. M3 desktop and full release acceptance remain open.

Ubuntu 22.04 Retry proof run 41750197586, job 126316994314, passed the clean update from 1.0.176 to 1.0.178. The Retry relaunch failed before installing the rejected payload or exercising Retry. Runner journal lines 2583–2584 show port 9333 already in use and DevTools unable to start. Lines 2645–2656 show the relaunched app attached to the running 1.0.178 service. Later pairing-token messages are separate observations. The port owner is unknown. The change proposal for PR #1256 adds a bounded port-release wait before the proof relaunch. Its loopback fixture passed. Hosted Ubuntu reproof and cross-platform artifact attachment remain open with the release/proof owners.

The umbrella post-ship verifier printed failed rows to the invoking terminal and removed its temporary JSON on exit. The original rows were unavailable. The release/status owner proposal appends the table to the existing ship log and preserves the verifier exit status. Test logs and both proposal patches are retained beside this report. Active owners' branches and publisher runs were left intact.

The verifier regression was the sole baseline failure (115 passed, 1 failed). With the proposal applied, all 116 tests passed.

## Integration

Verifier logging merged in umbrella [PR #141](https://github.com/anton-abyzov/specweave-umb/pull/141), `b69a95e458dda7a2fa0db37aacbd6660eec9d1c1`. The earlier umbrella release/status increment 1196 and its PR #138 were already closed and merged, so this follow-up used an isolated small fix based on current main. Independent review approved exact head `b2d6adecf90239b2d55446f60be62508c5aa4c45`. The merge patch ID matches that head. No hosted workflow path filter or branch ruleset applies to these files. The 116 passing tests are the shipped patch's verification evidence. The clean worktree was removed after checking all three local ownership databases and process working directories.

Ubuntu proof increment 1189 remains with [PR #1256](https://github.com/anton-abyzov/specwithcode-dev/pull/1256), branch `fix/linux-update-no-password` at `03845c60f427438eb122b464a19ac18122520971`. The isolated [stacked draft #1347](https://github.com/anton-abyzov/specwithcode-dev/pull/1347) uses branch `codex/ubuntu-update-proof-cdp-port` at `ecfe24f5a8db1d46f25eb76c61b7d5e81200532e`. The owner branch was left intact. The [isolated, nonpublishing dry run](https://github.com/anton-abyzov/specwithcode-dev/actions/runs/41755689449) uses this exact workflow ref and rebuilds its own candidate for Ubuntu 22.04 and 24.04. Its concurrency group is scoped to the dry-run ID. It cannot attach assets and does not test the exact failed release artifact bytes.

Connect-first release rollout is a follow-up to completed increment 1119. No open owner PR modified the rollout script at branch selection. The isolated [draft #1348](https://github.com/anton-abyzov/specwithcode-dev/pull/1348), branch `codex/connect-first-worker-rollout`, adds a Connect-only CLI route for the rollout. Structured unreachability on the initial status read permits pinned SSH fallback. Authorization, policy, missing credentials, identity mismatch and incompatible CLI errors fail closed. After selection, the rollout keeps the route for mutations and readback. For an inventory Mac, the independent desktop operation can use pinned SSH because Connect does not expose that capability. A pre-connect network failure yields an explicit desktop skip, while SSH authorization, transfer, installation, or verification failures remain errors. Relay unreachability does not allow SSH service fallback when matching Team Rules cannot be established. The release script upgrades M4 before using its installed CLI for worker rollout. New auth acceptance remains required. Gmail #1339 and Team Rules Retry #1336 remain held separately.

Independent review approved the Ubuntu draft's exact head and confirmed the Retry assertions are intact. Independent re-review approved the Connect draft at `eee098aa96b99a522984b159e07fe2043d0e5d16`, after the first review found the desktop and peer-policy gaps. Focused results are 84 Python rollout tests, 46 Python desktop tests, and 62 TypeScript tests. Draft-preserving [full Checks run 41756422205](https://github.com/anton-abyzov/specwithcode-dev/actions/runs/41756422205) targets that exact head. A hosted pass will leave the manual auth gate in place.

The hosted dry run passed the signed update from 1.0.176 to 1.0.178, Retry and replacement on both Ubuntu 22.04 (job 126334199449) and 24.04 (job 126334199383). Both job logs are retained. The owner of #1256 controls integration of #1347 and any subsequent release attachment.

Dry run 41755689449 finished successfully with all eight jobs green. Its release upload step was skipped and the run retained its artifacts. This closes the hosted proof on the stack. Integration and attachment remain with the existing owner.

Connect draft full hosted Checks completed at the exact approved head with 19 passed, one expected skip and zero failures. Its macOS Scripts check also passed. See connect-first-rollout-acceptance.md for the manual auth gate. No new auth acceptance was applied.

## November 3 owner reconciliation

| PR | Exact head | Disposition |
|---|---|---|
| #1237 | `450a6346bd4c2301b1753b1f6dbed94e54aa40f1` | Open, `feat/team-rules-phase-3` owner retains integration |
| #1256 | `03845c60f427438eb122b464a19ac18122520971` | Open, `fix/linux-update-no-password` owner retains integration |
| #1341 | `b339513efe7bff1bc80403b2ebb0d88eb63d5a90` | Open draft stacked on #1237 |
| #1347 | `ecfe24f5a8db1d46f25eb76c61b7d5e81200532e` | Open draft stacked on #1256 |
| #1336 | `4e0d5c79c622c46fe55b71743a0093c5fbed4287` | Open draft, auth held |
| #1339 | `1962cad03285859037bbc66feb0c5e91043438a3` | Open draft, auth held |
| #1348 | `eee098aa96b99a522984b159e07fe2043d0e5d16` | Open draft, auth held |

No owner or draft head changed and no checkout newly qualified for removal. The private and public 1.0.178 listings still lack Windows/Linux desktop assets. The publisher subsequently published 1.0.179 on both repositories (21:56:12 and 21:56:45 ET on November 3). Both 1.0.179 listings lacked Windows/Linux desktop assets at readback. Publisher attachment run 41763972938 was in progress at head `d9417cfdeb8f2f5bfa0fa8b2d3a3dbba523791a5`. Both Linux builds had passed and both Ubuntu proofs and Windows builds were still running. This separate release does not establish integration of either stacked fix or any held auth draft.

Publisher 1.0.179 attachment [run 41763972938](https://github.com/anton-abyzov/specwithcode-dev/actions/runs/41763972938) completed successfully at `d9417cfdeb8f2f5bfa0fa8b2d3a3dbba523791a5`. All eight jobs passed, including the Ubuntu 22.04 and 24.04 update proofs (126361426436 and 126361426410) and attachment to both releases (126362412292). The public and private release APIs returned matching SHA-256 digests for all 14 new Windows/Linux assets. See `studio-1.0.179-publisher-attachment.json` for job and asset detail. This closes the current publisher Windows/Linux availability gate with 1.0.179. The 1.0.178 listings still lack these assets. The separate stacked drafts and auth holds remain outside this result, as does installed M3 desktop attestation.

### Existing 1.0.179 fleet and desktop receipt

The publisher's retained `.specweave/state/release-logs/studio-20261104T023932Z.log` records the following. M4 installed service 1.0.179 and its installed app passed strict codesign and the notarized Developer ID check (NMCB2JZ7QG). M1 installed service 1.0.179 over SSH and swapped in the 1.0.179 app after checking the archive SHA-256, signature, designated requirement, and Gatekeeper. M3 and Ministorm installed the 1.0.179 service over Connect. The owner explicitly skipped their desktop step because it requires SSH. M3's signed desktop therefore remains unverified. The associated umbrella state reads `shipped but verify failed`; the retained publisher log does not identify individual failing verifier rows. This is distinct from the successful Windows/Linux attachment.

All seven GitHub PRs retained their previous exact heads and open/draft states on the same readback. No cleanup became eligible and no auth hold changed. No new runtime or device checks were run.

## Connect-first integration after acceptance

Anton approved #1348. Required Checks 41775964235 passed and the reviewed patch merged as `24a757c9a8d3f771e8ed31006a4af47c3d188d65`. Main Checks 41777521771 completed successfully. At readback the latest release was still 1.0.179. The designated publisher retains the next release. Fresh 1.0.179 baseline evidence confirmed M3 and M1 services over Connect. The canonical verifier passed 6/8, with the M3 service forward returning HTTP 000 and the pinned SSH desktop fallback timing out. Neither result attests an installed release containing #1348. Gmail and Team Rules Retry remain held.
