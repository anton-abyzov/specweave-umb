# Gitleaks triage, November 6, 2026

Inputs: `gl-dev-own.json` (138 findings, private `anton-abyzov/specwithcode-dev`, mirror `dev.git`) and `gl-pub.json` (115 findings; 24 groups outside `.repos/`, 40 findings, public `anton-abyzov/specwithcode`, mirror `pub.git`). Every group was checked by reading the flagged line from the finding's commit. No secret values are reproduced here.

"On main tip?" means the flagged value is still in that file on `main` in that mirror.

## dev.git (41 groups, 138 findings)

| File | Rule | Count | Class | Reason | On main tip? |
|---|---|---|---|---|---|
| `apps/server/src/provider/acp/AcpStderr.test.ts` | aws-access-token | 1 | TEST_FIXTURE | Redaction test input: `AKIA` plus an ascending-alphabet placeholder, next to other fake tokens | file yes, value no |
| `.env.example` | generic-api-key | 6 | PUBLIC_BY_DESIGN | Clerk `pk_live` publishable key (decodes to upstream `clerk.t3.codes`), JWT template name, public CLI OAuth client id. File header says these are public identifiers | file yes, value no |
| `apps/android/transport/src/main/kotlin/com/specwithcode/transport/ConnectConfig.kt` | generic-api-key | 2 | PUBLIC_BY_DESIGN | Clerk `pk_live` publishable key for `clerk.spec-weave.com`, compiled into the client | yes |
| `apps/ios/SWCKit/Sources/SWCTransport/ConnectConfig.swift` | generic-api-key | 2 | PUBLIC_BY_DESIGN | Same Clerk publishable key as Android | yes |
| `apps/server/src/auth/PairingGrantStore.ts` | generic-api-key | 1 | FALSE_POSITIVE | `PAIRING_TOKEN_ALPHABET` character set constant | yes |
| `apps/server/src/auth/Layers/BootstrapCredentialService.ts` | generic-api-key | 1 | FALSE_POSITIVE | Same `PAIRING_TOKEN_ALPHABET` constant (older location) | file absent |
| `scripts/studio-verify/shared-fleet-workflow.mjs` | generic-api-key | 10 | FALSE_POSITIVE | `sharedSessionKey` is a SHA-256 of a DB row key, compared against `keySHA256` | yes |
| `scripts/studio-verify/shared-fleet-workflow.test.mjs` | generic-api-key | 4 | FALSE_POSITIVE | Same row-key SHA-256 used in tests | yes |
| `reports/studio-worktree-safety-0890/verification/final-verifier-lint/receipt.json` | generic-api-key | 2 | FALSE_POSITIVE | SHA-256 file digests in a receipt | file absent |
| `reports/studio-worktree-safety-0890/verification/installed-verifier-lint/source-proof.json` | generic-api-key | 2 | FALSE_POSITIVE | SHA-256 file digests | file absent |
| `reports/studio-worktree-safety-0890/verification/release-freeze.json` | generic-api-key | 1 | FALSE_POSITIVE | SHA-256 file digest | file absent |
| `.artifacts/featured-providers/site/assets/index-D4opcpkx.js` | generic-api-key | 6 | FALSE_POSITIVE | Bundled keybinding names (`mod+...`) | file absent |
| `.artifacts/host-awake/site/assets/index-DTQwxO0i.js` | generic-api-key | 3 | FALSE_POSITIVE | Bundled identifiers (`command` field names) | file absent |
| `.artifacts/output-formatting/site/assets/index-DQRDL_TN.js` | generic-api-key | 3 | FALSE_POSITIVE | Bundled keybinding names | file absent |
| `.artifacts/provider-usability/site/assets/index-BlqiC2Me.js` | generic-api-key | 3 | FALSE_POSITIVE | Bundled keybinding names | file absent |
| `.artifacts/provider-usability/site/assets/index-DB7uWzVv.js` | generic-api-key | 3 | FALSE_POSITIVE | Bundled keybinding names | file absent |
| `.cache/project-workspace/deps/Logger-DspqsRMA.js` | generic-api-key | 6 | FALSE_POSITIVE | Library doc-comment example `API_KEY: "sk-..."` with a sequential placeholder | file absent |
| `.cache/project-workspace/deps/Logger-BXOpj1Pz.js` | generic-api-key | 1 | FALSE_POSITIVE | Same doc-comment example | file absent |
| `pnpm-workspace.yaml` | generic-api-key | 1 | FALSE_POSITIVE | Package version/hash pin for `@clerk/electron-passkeys` | file yes, value no |
| `packages/shared/src/keybindings.ts` | generic-api-key | 6 | FALSE_POSITIVE | Keybinding names | yes |
| `apps/web/src/components/settings/KeybindingsSettings.logic.test.ts` | generic-api-key | 2 | FALSE_POSITIVE | Keybinding name | yes |
| `apps/ios/SWCKit/Sources/SWCTransport/Dpop.swift` | generic-api-key | 4 | FALSE_POSITIVE | Swift type name (`P256.Signing.PrivateKey`), not a key | yes |
| `packages/effect-codex-app-server/src/protocol.test.ts` | generic-api-key | 4 | TEST_FIXTURE | UUID `idempotencyKey` | yes |
| `apps/server/src/auth/websocketSession.test.ts` | generic-api-key | 3 | TEST_FIXTURE | RFC 6455 sample `Sec-WebSocket-Key` | yes |
| `apps/server/src/httpResponseErrorGuard.test.ts` | generic-api-key | 2 | TEST_FIXTURE | RFC 6455 sample `Sec-WebSocket-Key` | yes |
| `apps/server/src/cloud/publicConfig.test.ts` | generic-api-key | 7 | TEST_FIXTURE | `pk_test` keys for `*.example.test` hosts | yes |
| `apps/server/src/cloud/CliTokenManager.test.ts` | generic-api-key | 3 | TEST_FIXTURE | `pk_test` key for `clerk.example.test` | yes |
| `apps/server/src/decisions/jevClient.test.ts` | generic-api-key | 2 | TEST_FIXTURE | Redaction test strings (`ghp_` with `abcd1234`, `sk-or-v1-secret...`) | yes |
| `apps/server/src/sourceControl/GitHubSignIn.test.ts` | generic-api-key | 2 | TEST_FIXTURE | Fake `gho_`/`ghp_` tokens containing `secret1234`/`abcd1234` | yes |
| `apps/server/src/sourceControl/GitHubCredentialCopy.test.ts` | generic-api-key | 2 | TEST_FIXTURE | Fake `gho_` token containing `secret1234` | yes |
| `apps/server/src/htmlRender/HtmlRender.test.ts` | generic-api-key | 2 | TEST_FIXTURE | Placeholder `API_...abc123` written to a temp file | yes |
| `apps/desktop/src/voice/legacyVoicePreferences.test.ts` | generic-api-key | 3 | TEST_FIXTURE | `encryptedKey` is base64 of a plain English word | yes |
| `apps/mobile/src/features/cloud/linkEnvironment.test.ts` | generic-api-key | 1 | TEST_FIXTURE | Unsigned JWT (`alg: none`, 4-char signature, `sub` only) | file yes, value no |
| `apps/ios/SWCKit/Tests/SWCTransportTests/ConnectTests.swift` | generic-api-key | 4 | TEST_FIXTURE | Stub JWT (`{"v":1}` header, 3-char segments) | yes |
| `apps/ios/SWCKit/Tests/SWCTransportTests/MachineHTTPTests.swift` | generic-api-key | 7 | TEST_FIXTURE | Same stub JWT in a mocked token response | yes |
| `apps/android/app/src/test/kotlin/com/specwithcode/android/ViewModelTest.kt` | generic-api-key | 12 | TEST_FIXTURE | Pairing URLs with a placeholder `#token=` on LAN/example hosts | yes |
| `apps/android/transport/src/test/kotlin/com/specwithcode/transport/MachineHttpTest.kt` | generic-api-key | 4 | TEST_FIXTURE | Mock pairing token and `subject_token` in a test request | yes |
| `apps/android/transport/src/test/kotlin/com/specwithcode/transport/PairingLinkTest.kt` | generic-api-key | 2 | TEST_FIXTURE | Placeholder pairing token in a link-parsing case | yes |
| `infra/relay/src/hooks/HeldHooks.test.ts` | generic-api-key | 4 | TEST_FIXTURE | `0123...cdef` / `fedc...3210` hex placeholders | yes |
| `infra/relay/src/hooks/HookForwarder.test.ts` | generic-api-key | 2 | TEST_FIXTURE | `0123...cdef` hex placeholder | yes |
| `infra/relay/src/http/Api.test.ts` | generic-api-key | 2 | TEST_FIXTURE | `0123...cdef` hex placeholder | yes |

dev.git totals: TEST_FIXTURE 20 groups / 69 findings, PUBLIC_BY_DESIGN 3 / 10, FALSE_POSITIVE 18 / 59, REAL_SECRET 0.

## pub.git (24 groups outside `.repos/`, 40 findings)

All 24 groups are the same files and values as their dev.git rows above, and have the same classification. The Clerk key in both `ConnectConfig` files decodes to `clerk.spec-weave.com` here too. All 24 values are on the `main` tip.

| File | Rule | Count | Class | On main tip? |
|---|---|---|---|---|
| `apps/android/app/src/test/kotlin/com/specwithcode/android/ViewModelTest.kt` | generic-api-key | 6 | TEST_FIXTURE | yes |
| `apps/android/transport/src/main/kotlin/com/specwithcode/transport/ConnectConfig.kt` | generic-api-key | 1 | PUBLIC_BY_DESIGN | yes |
| `apps/android/transport/src/test/kotlin/com/specwithcode/transport/MachineHttpTest.kt` | generic-api-key | 2 | TEST_FIXTURE | yes |
| `apps/android/transport/src/test/kotlin/com/specwithcode/transport/PairingLinkTest.kt` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/desktop/src/voice/legacyVoicePreferences.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/ios/SWCKit/Sources/SWCTransport/ConnectConfig.swift` | generic-api-key | 1 | PUBLIC_BY_DESIGN | yes |
| `apps/ios/SWCKit/Sources/SWCTransport/Dpop.swift` | generic-api-key | 2 | FALSE_POSITIVE | yes |
| `apps/ios/SWCKit/Tests/SWCTransportTests/ConnectTests.swift` | generic-api-key | 2 | TEST_FIXTURE | yes |
| `apps/ios/SWCKit/Tests/SWCTransportTests/MachineHTTPTests.swift` | generic-api-key | 3 | TEST_FIXTURE | yes |
| `apps/server/src/auth/PairingGrantStore.ts` | generic-api-key | 1 | FALSE_POSITIVE | yes |
| `apps/server/src/auth/websocketSession.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/server/src/cloud/CliTokenManager.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/server/src/cloud/publicConfig.test.ts` | generic-api-key | 3 | TEST_FIXTURE | yes |
| `apps/server/src/decisions/jevClient.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/server/src/htmlRender/HtmlRender.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/server/src/httpResponseErrorGuard.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/server/src/sourceControl/GitHubCredentialCopy.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/server/src/sourceControl/GitHubSignIn.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `apps/web/src/components/settings/KeybindingsSettings.logic.test.ts` | generic-api-key | 1 | FALSE_POSITIVE | yes |
| `infra/relay/src/hooks/HeldHooks.test.ts` | generic-api-key | 2 | TEST_FIXTURE | yes |
| `infra/relay/src/hooks/HookForwarder.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `infra/relay/src/http/Api.test.ts` | generic-api-key | 1 | TEST_FIXTURE | yes |
| `packages/effect-codex-app-server/src/protocol.test.ts` | generic-api-key | 2 | TEST_FIXTURE | yes |
| `packages/shared/src/keybindings.ts` | generic-api-key | 3 | FALSE_POSITIVE | yes |

pub.git totals: TEST_FIXTURE 18 groups / 31 findings, PUBLIC_BY_DESIGN 2 / 2, FALSE_POSITIVE 4 / 7, REAL_SECRET 0.

## REAL_SECRET items needing rotation

None. No group held a live-looking private credential.

Notes, not rotation items:

- The `pk_live` Clerk publishable keys (`.env.example` for `clerk.t3.codes`; `ConnectConfig.kt` and `ConnectConfig.swift` for `clerk.spec-weave.com`) and the CLI OAuth client id are public by Clerk's design. They are not credentials.
- The `.env.example` key points at upstream T3 Code's Clerk instance, not SpecWithCode's, in every revision that gitleaks flagged. That is a provenance and config issue, not a leak.
- Committed `.artifacts/`, `.cache/` and `reports/` files only produced false positives, and none are on the dev `main` tip.
