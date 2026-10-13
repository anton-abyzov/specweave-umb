# Independent 1.0.7 artifact audit

Verified 2026-10-13 03:36 UTC (October 12, 23:36 America/New_York).

Result: local release artifacts and update plan pass the checks below. Publication, installation and real Google authorization are separate gates.

- Stage: `/Users/antonabyzov/.specweave-studio/release-staging/0901-1.0.7`.
- Source: `54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f`; source checkout clean at audit.
- Version: `1.0.7` in runtime manifest/package, CLI output, desktop package/Info.plist and update feed.

## Runtime and Google configuration

`scripts/studio-fleet/verify-bundle.mjs` passed with Node 22.20.0: 7,479 indexed files verified, legal notices present, standalone CLI version/help succeeded, and all six runtime roots loaded (`@cursor/sdk`, `@ff-labs/fff-node`, `@napi-rs/keyring`, `node-pty`, `playwright-core`, `zod`). No provider inference ran.

The compiled Google OAuth client pair is nonempty, satisfies the source validation patterns, and exactly matches the approved pair in the existing source checkout's `.env`. The desktop ZIP's embedded server carries the same pair as the standalone runtime. Values were never printed or copied into this report.

No `.env`, credential-store, `auth.json` or `credentials.json` paths appeared in the runtime manifest. Google refresh/access-token pattern scans found no candidate token in application files. One dependency match was verified as bytes inside a PNG base64 data URI in Playwright's HTML reporter, identical to the 1.0.6 dependency file; it is not a Google token. Pattern scanning is supplementary evidence, not an exhaustive secret detector.

## Desktop

- ZIP inspected in memory: `CFBundleIdentifier=com.specweave.studio`, version `1.0.7`, updater repository `anton-abyzov/specwithcode`.
- `studioBuild.signed=false` retains the bundle-swap updater. This does not mean the app lacks a code signature.
- Read-only DMG mount: `codesign --verify --deep --strict` passed. Signing authority is `Apple Development: Anton Abyzov (W39WQZNW64)`, matching the installed app. The owned mount was detached; no GUI was launched. Notarization was not asserted.
- `latest-mac.yml` SHA512 values and byte sizes match both ZIP and DMG. `SpecWithCode-arm64.dmg` is byte-identical to the versioned DMG.

## Helpers, checksums and update plan

All 10 entries in `SHA256SUMS` match their local files, including `studio-update.json`. All 57 helper manifest entries match the helper archive; helper and runtime source commits agree. `update_agent.validate_plan` and `validate_manifest` accepted the staged metadata.

The plan names platform `darwin-arm64`, runtime `studio-1.0.7-54aa7e7d7ba1.tar.gz`, and helper root `studio-1.0.7-deployment-helpers-54aa7e7d7ba1`. It permits exactly these source commits:

| Prior release | Allowed source |
| --- | --- |
| 1.0.3 | `a50d744af5b076546d701e1eb9134ad24bed1e10` |
| 1.0.4 | `f9ef1e206bbe4b3262e1832bd088aecb18520b06` |
| 1.0.5 | `c95d3fd701d21b758c1ccbe0710609018bcdc512` |
| 1.0.6 | `a5c64fb59639c798c2da05eca82ef6710dbef82c` |

Entrypoint is `scripts/studio-fleet/update.py`; the only argument is `--allow-existing-browser-heartbeat`. Project migrations are not enabled.

| Artifact | SHA256 |
| --- | --- |
| Runtime | `600a4c54e381cbaed29c7e530e19ae424e70ac80ba5da7d41104566b97951830` |
| Desktop ZIP | `7acdb5f7b1f27bf54fef0aff21c4528ce22c2e4e306d9f9e4b145cc970a0a8e6` |
| Desktop DMG | `217c5855cd4b36c2be10867a8486d6d32d874f8e72f7d4c7c2aca74b26f60bcc` |
| Helpers | `d859c6c31666284192d138ef89a417f471b53288bdcd32a90bf0fa9111c4f1c5` |

## Proof limits

This audit verifies packaged configuration, integrity and signing. It does not establish that Google has accepted consent, issued a refresh token, granted Gmail/Calendar/Drive scopes, enabled project access, or returned real account data. Those require the user's Google sign-in and subsequent read-only service checks. No service restart, live account mutation, provider turn or release mutation was performed by this audit.
