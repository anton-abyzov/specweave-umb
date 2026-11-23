# Gemini sign-in reports Google's refusal of personal accounts and offers an API key or Antigravity

## Problem

On June 18, 2026 Google stopped serving Gemini CLI for personal Google accounts: free Gemini Code Assist for individuals, Google AI Pro and Google AI Ultra ([Google Developers Blog](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli)). The Google sign-in page still says "Authentication successful". Then every session fails with "This client is no longer supported for Gemini Code Assist for individuals. To continue using Gemini, please migrate to the Antigravity suite of products".

The app reports this as "Installed on M5. Not signed in yet. Gemini CLI did not accept the sign-in: ...". It offers **Retry sign-in**, which can never work. Evidence from M5, November 23, 2026:

- Gemini CLI 0.70.0 is installed. That is npm `latest`. `~/.local/bin/gemini` is a symlink into `~/.specwithcode/tools/gemini/0.70.0`.
- The app and Terminal use the same binary and the same `~/.gemini` folder.
- A fresh Terminal sign-in as the same account wrote `oauth_creds.json` and `settings.json` (`oauth-personal`). `gemini --skip-trust -p "..."` then fails with the same message. Upgrading the CLI cannot fix it.
- The server trace shows the refusal comes back from `session/new` in `AcpRegistryProbe.probeConfiguration`.

Where the status comes from:

- `apps/server/src/provider/acp/AcpRegistryProbe.ts:473-490`: `acpRegistryProbeFailure` turns any ACP `-32000` error, or any detail that mentions login or credentials, into `authentication_failed`.
- `apps/server/src/provider/Drivers/AcpRegistryDriver.ts:576-578`: that becomes `auth.status: "unauthenticated"`.
- `apps/server/src/provider/acp/AcpRegistryAuth.ts:157-161, 757-779`: the sign-in flow reports "<agent> did not accept the sign-in: <reason>".
- `apps/web/src/components/settings/providerSignInState.logic.ts:52-63` and `ProviderAuthenticationSection.tsx:131-133`: the web then shows "Not signed in yet".

So the app can tell "not installed" from "installed", but it cannot tell "signed in, refused by Google" from "not signed in". This hits every machine, and every Gemini instance that uses Google sign-in on a personal account.

## Scope

In:
- A structured "refused by the provider" outcome for Gemini's Google sign-in. The probe, the sign-in flow and turn start all recognize it.
- A status line that names it, with actions that can work: use a Gemini API key, which already exists as a credentials method, or add Antigravity, which is already a provider.
- Translations for every supported locale.

Out:
- Migrating threads or settings from Gemini to Antigravity automatically.
- Vertex AI setup UI.
- Reading the account's tier from Google before sign-in.

## Acceptance Criteria

- [ ] AC-01: The server marks the refusal with a new `refusal: "personal_account_unsupported"` on the probe error. The reason stays `authentication_failed`, so routing still skips the instance. It matches the ACP error code or data `UNSUPPORTED_CLIENT` when present, and falls back to the message ("no longer supported for Gemini Code Assist for individuals" or "migrate to the Antigravity"). Unit tests cover both shapes. A plain `-32000` login error still classifies as `authentication_failed`.
- [ ] AC-02: For that reason the provider snapshot reports `auth.status: "unauthenticated"` with a new optional `auth.refusal: "personal_account_unsupported"`. Older clients ignore it. Fallback and routing keep skipping the instance as they do today (`AcpRegistryDriver.ts:749`). It never shows as signed in.
- [ ] AC-03: A sign-in flow that ends in this refusal publishes `phase: "failed"`, `retryable: false` and `refusal: "personal_account_unsupported"`. The message reads: "Google accepted the sign-in, but no longer serves Gemini CLI on personal Google accounts (free, Google AI Pro or Ultra). Sign in with a Gemini API key, Vertex AI, or a Gemini Code Assist Standard or Enterprise licence."
- [ ] AC-04: Settings and the Add provider dialog show "Installed on {machine}. Google refused this account for Gemini CLI." instead of "Not signed in yet". **Retry sign-in** is hidden for the browser method. **Use an API key** starts the agent's credentials (API-key) method. Picking another method in the list (Vertex AI, a licensed Google login) still shows **Sign in**. Antigravity is not offered (D-03). A web test covers the state and both buttons.
- [ ] AC-05: A thread turn on such an instance fails with the same plain sentence, with code `provider_account_refused` and `retryable: false`, not Google's raw text. Routing already skips the instance because its status is `unauthenticated`. A server test covers it.
- [ ] AC-06: All new phrases exist in the nine locale files under `apps/web/src/i18n/phrases/providerSignIn/`.

## Approach

1. Contracts:
   - Add `"provider_refused_account"` to the ACP probe reason.
   - Add the optional `refusal` literal to the provider auth snapshot and to `ProviderAuthState` in `packages/contracts/src/providerSetup.ts` and `server.ts`. Use forward-compatible decoding.
2. Server: classify in `acpRegistryProbeFailure` before the auth regex. Map the reason in `AcpRegistryDriver.ts`. In `AcpRegistryAuth.ts`, set `retryable: false` and the refusal on the published failure. Look in `ProviderFailure.ts` for the turn-time mapping.
3. Web: add a `refused` kind to `providerSignInState.logic.ts`. In `ProviderAuthenticationSection.tsx`, add the status line and the two actions. Add the locale phrases.

Risks:
- Google can change the wording. The code match comes first, and the message match is only a fallback.
- A paid API-key user is not affected, because the refusal only follows the Google sign-in method.

Rejected:
- Marking the instance "signed in". That breaks the rule that a browser page alone never proves sign-in.
- Upgrading the CLI. 0.70.0 is already `latest`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Hide **Retry sign-in** for the refused Google method and keep the method picker → default (reversible)
- D-02 Offer API key and Antigravity as the two actions, and mention the Code Assist licence only in text → default (reversible)
- D-03 No Antigravity action: its desktop app gives no working provider here and its terms forbid third-party tools on the Google sign-in (1450 research); the Antigravity provider path belongs to 1450 → default
- D-04 Turn failures read only the already-chosen failure message, never other cause fields (ProviderFailure's privacy tests) → default
### Open
- none

## Tasks

### T-01 Classify the refusal on the server
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistryProbe.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistryProbe.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/AcpRegistryDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/providerAccountRefusal.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/providerAccountRefusal.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/acpRegistry.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/acp/AcpRegistryProbe.test.ts

### T-02 Sign-in flow and turn start report the refusal
- AC: AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/providerSetup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistryAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistryAuth.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderFailure.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderAuthFlow.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/acp/AcpRegistryAuth.test.ts

### T-03 Status line, actions and translations
- AC: AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/providerSignInState.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/providerSignInState.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderAuthenticationSection.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/providerSignIn/ | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/providerSignInState.logic.test.ts

## Delivery

PR https://github.com/anton-abyzov/specwithcode/pull/828, merged as `32b4a28d7`. Neon review: round 1 changes requested, round 2 approve; one low finding left (stale `retryable` label after a failed method refresh). Release requested: joined run 45137865621.
