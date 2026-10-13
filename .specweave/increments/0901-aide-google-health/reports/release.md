# SpecWithCode 1.0.7 release evidence

Published October 12, 2026, 23:38 America/New_York. Both repositories expose `v1.0.7` as the latest non-draft release, with all 11 uploaded asset hashes and sizes matching local artifacts. Unauthenticated public reads verified the release API, checksums, service update plan and desktop update feed; installer and ZIP downloads return HTTP 200.

- Public release: https://github.com/anton-abyzov/specwithcode/releases/tag/v1.0.7
- Private release: https://github.com/anton-abyzov/specweave-studio/releases/tag/v1.0.7
- Merged PR: https://github.com/anton-abyzov/specweave-studio/pull/160
- Source: `54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f`; merge `e6b47ae63aa38467738506103dbc1bcdf07343f5`.
- Sanitized public snapshot: `2f55d08280aba5febed4b656512818b83d0822e0`.

## Findings and changes

The screenshot's calendar worker failed provider admission because its selected Claude subscription profile had exhausted permitted usage. It had not read Calendar. The separate coordinator and worker settings explain why selecting Codex for the coordinator did not fix the Claude worker. The integrated, independently reviewed 0899 patch preserves typed usage-limit and reset metadata for existing recovery controls. Historical failed workers are not retried and recovery policy is not changed.

Google was also unconfigured and disconnected in the live M4 service. The official 1.0.5 and 1.0.6 artifacts lacked their build-time Google OAuth client because isolated release checkouts did not inherit the ignored `.env`. Release 1.0.7 explicitly supplies only the approved Desktop OAuth client pair at build time. Both desktop and service artifacts contain the same verified pair; no real account tokens are included. The documented release gate asserts built-in setup without runtime Google configuration.

Google status now distinguishes missing client configuration, sign-in, project grants, scopes and API failures. Optional connection probes use content-free field projections for authorized Gmail, Calendar and Drive APIs. Prompts discover native Google tools, allow simple reads in the coordinator and distinguish account readiness from provider errors. Grants are rechecked after probes, and ungranted account identity stays private.

## Verification

326 focused tests pass across 15 files. Focused coverage: lines 84.86%, statements 83.21%, branches 72.55%, functions 76.19%, above the 60% configured thresholds. Server typecheck, brand audit and production web/server/desktop builds pass. Independent source review found no actionable defects. Independent artifact audit verifies the runtime, helpers, signatures, updater metadata and hashes.

Headless built-server Google verification passes: compiled client with runtime overrides absent, fake OAuth, read-only scopes, PKCE, loopback/pasted callbacks, grants, callback replay/forgery rejection, disconnect, own-client removal restoring built-in configuration, no page errors and no secrets logged. It uses fake Google and makes zero native provider turns. This is not evidence of real account consent or API access.

`verify-release.py` rechecks published artifacts plus stored browser and coverage receipts. The host Python certificate store was unavailable on the first public check; native macOS curl with normal TLS verification completed the readback. No certificate checks were disabled.

## Remaining user acceptance

After updating the desktop and its selected M4 service to 1.0.7, open Settings > Google account > Connect Google, then enable the desired Gmail, Calendar and Drive access for Aide. Run `studio_google_status` with `checkConnection: true` in that project and verify one requested real read per service. Do not infer authorization from another app's Google connectors.

The installed desktop was 1.0.6 and the running service remained 1.0.5 at final readback. This session published the update and did not restart or replace the live service while other owners were active. The release is available; installation and real Google access remain separate, unverified gates. Formal increment closure awaits the project's required manual acceptance for authentication changes. All four implementation/release tasks and five scoped acceptance criteria pass verification.

Concurrent maintenance evidence identified a separate 1.0.6 service-update attempt. The earlier 03:25 attempt failed preflight with `Owned service has unexpected descendants`. At 03:43 the distinct 03:29:55 retry finished preflight with `Guarded prestate changed: otherListeners`, pointers unchanged. Fresh local readback at 03:44:20 confirms that terminal receipt, removed install marker, and updater state `waiting-for-quiet` with message `New work started before the restart; trying again`. Do not start a competing installer, stop active work or bypass quiescence. This release does not include the separately pending PR157 updater-status recovery or PR136 default-model guard; no adoption or verification of those changes is claimed.

Artifacts and detailed local receipts remain under `/Users/antonabyzov/.specweave-studio/release-staging/0901-1.0.7` and `/Users/antonabyzov/.local/share/specweave-studio/verification/0901`. The managed worktree is preserved for acceptance and follow-up.
