# 1478 red and green: relay lane (R11 to R17)

All commands run from `repositories/anton-abyzov/specwithcode/infra/relay` in the thread worktree, branch `1474d-preview-pairing` (from `origin/main` `2b7f17e8b`). Red is the new test against unmodified code; green is the same test after the fix.

## R15 `9b1ea43cc4`: queued APNs jobs skip delivery when the recheck fails

Command: `npx vp test run --config ../../vite.config.ts --dir . src/agentActivity/ApnsDeliveries.recheck.test.ts`

Red (2 failed of 2): both the queued alert and the queued Live Activity update were delivered to APNs while every activity-row read failed:

```
FAIL  ApnsDeliveries when the delivery-time recheck fails > skips a queued alert instead of delivering it
-   "apnsReason": "Stale APNs delivery job skipped.",
+   "apnsReason": null,
FAIL  ... > skips a queued Live Activity update instead of delivering it
+   "apnsReason": null,
```

Green: `Test Files 3 passed (3) / Tests 53 passed (53)` for `src/agentActivity/ApnsDeliveries` (new file plus the two existing ones). Update: all three delivery-time rechecks (state identity, aggregate rows, live-work start) fail closed since PR #912 review round 1 (D-04), and since round 2 a queued Live Activity start is sent only if every machine in its content is still linked to that user under the same key (`29862a0f7`).

Commit: `3bfd2b66c`.

## R16 `2a11e76561`: Android pushes send a per-device hash, not the account id

Command: `npx vp test run --config ../../vite.config.ts --dir . src/agentActivity/FcmDeliveries.test.ts`

Red:

```
FAIL  Android delivery routing > keeps completion alerts working with ongoing activity disabled
AssertionError: expected { Object (studio_kind, device_id, ...) } to not have property "user_id"
+ Received:
"user"
```

Green: `Test Files 2 passed (2) / Tests 53 passed (53)` for `src/agentActivity/Fcm`. The payload carries `user_hash` = SHA-256 of `<userId>:<deviceId>` (lowercase hex) instead of `user_id`. Our native Android app (`apps/android`) reads no FCM data key; only the undistributed Expo module `apps/mobile/modules/studio-agent-notifications/.../AgentNotifications.kt:126` compares `user_id`, and needs the matching receiver change before it ships (outside this group's files). The smoke and watch scripts send the same hash.

Commit: `e204140a9`.

## R13 `7da318e2d5`: switching accounts revokes the previous link

Command: `npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLinks.integration.test.ts` (real in-memory SQLite D1 with the relay migrations)

Red (1 failed of 3):

```
FAIL  EnvironmentLinks on SQLite D1 > revokes the previous account's link when the machine links under another
AssertionError: expected null not to be null
```

Green: `Tests 8 passed (8)` for `src/environments/EnvironmentLinks` (the two keep-working cases, another account under a different key and the same account relinking, passed before and after). The upsert and the revocation of other accounts' active links for the same environment and key run as one `RelayDb.batch`; the upsert goes first so the webhook-hold inheritance still sees the previous link. Credentials stay because they belong to the key the new link uses. The credential insert is not in the batch: making it batchable needs a reshaped `EnvironmentCredentials.create`, and a failure there leaves a retryable link as today.

Linker side (`src/environments/EnvironmentLinker.test.ts`, "removes the previous account's tunnel after the machine moves accounts"): red `expected [ 'upsert:user_123' ] to deeply equal [ 'upsert:user_123', 'deprovision:user_old' ]`; green after the linker reads the other accounts' managed links before the upsert and removes their tunnels best effort afterwards.

Commits: `5314eb615` (links), `76dee7bff` (linker, shared with R12).

## R12 `aa685426e7`: no relink of an active environment under another key

Command: `npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLinker.test.ts`

Red: "refuses to move an active link to a different key" failed because the link succeeded, returning a managed endpoint and a fresh `environmentCredential`.

Green: `Tests 18 passed (18)` for `src/environments/EnvironmentLink`. The check runs right after origin validation, before the same-machine replacement loop, deprovisioning, provisioning and the upsert; the test asserts no upsert, provision or deprovision call. Keep-working case "relinks an active link proven by the same key" passes; relink after unlink is the existing `getForUser` returning `null` for a revoked row (`EnvironmentLinks.ts` `isNull(revokedAt)`), covered by every existing linker test.

Wire reason: `packages/contracts/src/relay.ts` is not this group's file, so the refusal uses the existing `descriptor_mismatch` reason (older machines decode it; the server shows "Relay rejected the environment link proof (descriptor_mismatch)") with the relay-internal stage `validate_existing_link` and a warning log naming `environment_key_mismatch`. Follow-up for the contract and `apps/server/src/cloud/relayResponse.ts` owners: a dedicated reason and a hint "unlink it in Connect, then restart SpecWithCode", since today's hint for every proof-invalid reason is "Check this machine's date and time".

Not ported: finishing a leftover tunnel teardown before every brand-new link. In ours an unlink of an online machine deliberately leaves its tunnel for later (`ManagedEndpointProvider.ts` "The machine being removed is often still online" comment at the `tunnels.delete` call), so forcing teardown first would refuse that machine's relink until its old connector drops. The tunnel name and hostname are derived from the user and environment, so a fresh tunnel would get the same address anyway. Held for the owner if wanted.

## R11 `4eccb0ecfc`: relay traces drop the caller's IP address and user agent

Command: `npx vp test run --config ../../vite.config.ts --dir . src/http/traceRequestPrivacy.test.ts`

Red (2 failed of 2, a plain route and a `/v1/hooks/` route): `AssertionError: expected true to be false` on `server.attributes.has("client.address")`.

Green: `Tests 2 passed (2)`; `src/http` `Tests 61 passed`. The tracer and deadline log now always see a copy of the request with `remoteAddress` cleared and `user-agent` removed (plus the existing hook URL redaction and sender trace-header drop on hooks); the route still receives the original, which the test asserts (address `203.0.113.9` and the user agent reach the handler). `Api.ts` went from 1,515 to 1,511 lines.

Commits: `9ace5a205`, `a61c9b45e` (test cases as `it.effect.each`).

## R14 `c9ba6b4b6e`: account deletion removes a live host's tunnel

Commands: `npx vp test run --config ../../vite.config.ts --dir . src/environments/ManagedEndpointProvider.disconnect.test.ts` (real provider and allocations on SQLite D1, a Cloudflare stub whose tunnel has a live connector) and `src/account/AccountDeletion.test.ts`.

Red:

```
FAIL  removing a tunnel whose host is still connected > an account deletion drops the connectors, deletes the tunnel and frees it
AssertionError: expected false to be true
FAIL  account deletion > removes a still-connected machine's tunnel with the account
AccountDeletionIncomplete: Managed endpoints remain for account user-1: env-a.
```

Green: both pass; keep-working case "an ordinary unlink leaves the tunnel for later" passes before and after (no disconnect, allocation kept). Account deletion passes `forceDisconnect: true` through `unlinkEnvironmentRecord` to `deprovision`; on Cloudflare's "has active connections" it calls the tunnel client's `disconnect` (rotate the tunnel secret, then delete its connections) and retries the delete. A third test runs the same through the Worker's `layerCloudflareBindings` to prove the binding carries `disconnect`.

To keep `ManagedEndpointProvider.ts` under 1,500 lines (it was 1,588), the Worker's Cloudflare bindings moved unchanged to `ManagedEndpointCloudflareBindings.ts`; the provider is now 1,442 lines.

Commits: `337cfe507` (provider, unlink, deletion, bindings move), `d47eff025` (binding swap, revertable alone: `ManagedTunnelBinding.ts` keeps Alchemy's token id `Cloudflare.Tunnel.ReadWriteTunnel` and its two permission groups, adds `disconnect`, and replaces `Cloudflare.Tunnel.ReadWriteTunnel`/`ReadWriteTunnelBinding` in `worker.ts`).

Proof limit: the binding swap is proven only by the relay deploy (`deploy-relay.yml` on `main`) and a real account deletion of a connected machine; unit tests stub Cloudflare.

## R17 `3380585e1b`: delete a user's relay data when Clerk deletes the user

Command: `npx vp test run --config ../../vite.config.ts --dir . src/webhooks src/Config.test.ts`

Red by absence: on `origin/main` the only deletion path is the in-app call (`infra/relay/src/http/Api.ts:826` `deleteAccount`), and `POST /v1/webhooks/clerk` falls through to `layerNotFoundRoute` (`Api.ts:184`, 404). The new test file imports the new module, so it cannot run against `main`.

Green: `Tests 36 passed (36)`. Cases: a signed `user.deleted` deletes that user's records (204); a valid signature among several (rotation) works; an unset or blank secret answers 503 and deletes nothing; a wrong key, a missing signature, an altered body and a changed `svix-id` answer 401; a timestamp 6 minutes early or late answers 401; another event type answers 204 and deletes nothing; `CLERK_WEBHOOK_SIGNING_SECRET` missing, empty or blank parses as unset, so the deploy still runs. The signature is checked over the raw body bytes (HMAC-SHA256 keyed by the base64 part of `whsec_...`, over `<svix-id>.<svix-timestamp>.<body>`, constant-time compare). A deletion failure answers 500 so Clerk retries.

Commit: `5be90e66b` (route `infra/relay/src/webhooks/ClerkWebhook.ts`, config, worker wiring, `.github/workflows/deploy-relay.yml` line `CLERK_WEBHOOK_SIGNING_SECRET: ${{ secrets.CLERK_WEBHOOK_SIGNING_SECRET }}` next to `CLERK_SECRET_KEY`, `infra/relay/README.md` production secrets list).

## Whole relay package

`npx vp test run --config ../../vite.config.ts --dir .` in `infra/relay`: `Test Files 53 passed (53) / Tests 660 passed (660)`. `npx tsc --noEmit -p tsconfig.json`: no errors. `vp lint infra/relay`: only pre-existing findings (`src/testing/sqliteD1.ts` node import style, unused `HookForwarder` import in `Api.ts`).

## Review follow-ups

From the review of PR #912 at `ddaa61ab6`. Each fix is its own commit; every red run is on the code before that fix. Commands run from `infra/relay`.

### 1. Client-address headers left request spans: `8054bc1a5`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/http`

Red: the privacy test now sends `cf-connecting-ip`, `cf-connecting-ipv6`, `cf-pseudo-ipv4`, `x-forwarded-for` (two hops), `x-real-ip`, `true-client-ip` and `forwarded`. Both cases failed: `AssertionError: expected '[["http.request.method","POST"],["url…' not to contain '203.0.113.9'` for `/v1/mobile/devices` and `/v1/hooks/hook-token-secret`.

Green: `Tests 61 passed (61)`. The traced copy drops the user agent and every client-address header (`forwarded`, `x-forwarded-for`, `x-real-ip`, `x-client-ip`, `x-cluster-client-ip`, `true-client-ip`, `fastly-client-ip`, `cf-connecting-ip`, `cf-connecting-ipv6`, `cf-pseudo-ipv4`) on API and hook paths alike. The handler still reads `cf-connecting-ip` from the original request. `Api.ts` stays at 1,511 lines. The hook forwarder's outbound call records no client span (`src/hooks/upstream.ts:122` disables its tracer), so the headers it forwards reach no span either.

### 2. Relink race: the write checks the key: `6aa5b3200`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/environments`

Red (SQLite D1 integration): `refuses to move an active link to another key in the write itself` failed with `AssertionError: expected false to be true`: linking user A with key-2 over A's active key-1 link succeeded and overwrote it. Linker red: `refuses when a racing link took the key slot before the write` failed because the store's refusal surfaced as `EnvironmentLinkKeyConflict` instead of the link refusal.

Green: `Tests 191 passed (191)`. The upsert's `ON CONFLICT DO UPDATE` carries `setWhere` (`revoked_at IS NOT NULL OR environment_public_key = <proof key>`) and `RETURNING`, so a write that does not apply returns no row and `upsert` fails with `EnvironmentLinkKeyConflict`. The batch's revoke of other accounts' links runs only when the account's own row now holds the proof key and is active, so a refused write ends nobody's link. The linker turns the conflict into the same refusal as its read check (`EnvironmentLinkProofInvalid`, `descriptor_mismatch`, stage `validate_existing_link`, warning `environment_key_mismatch`) and removes no other account's tunnel. A revoked link still relinks under a new key.

Left as is: the proof and challenge nonces are consumed before the key check. That is not fail-open (a refused link only spends a nonce the machine made for that attempt), so the order stays.

Residual (only inside the race window, since the read check runs before provisioning): provisioning runs before the write and reuses the account's existing tunnel for that environment, so a losing racer's `putConfiguration` (`src/environments/ManagedEndpointProvider.ts:1221`) can point the winner's tunnel at the loser's local origin port until the winner links again. The connector token is not returned to the refused caller, so this is an availability effect, not a takeover. Closing it would mean checking the key inside the allocation claim before configuring; not done here.

### 3. APNs live-start recheck fails closed: `d517eb58e`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/agentActivity`

Red: `skips a queued Live Activity start instead of delivering it` (activity rows unreadable) failed with `AssertionError: expected { deviceId: 'phone-1', …(5) } to match object { kind: 'live_activity_start', …(1) }`: the start was sent to APNs.

Green: `Tests 195 passed (195)`. `userStillHasLiveWork` logs `live-work recheck failed; skipping queued start` and skips; the stale path clears the queued-start flag so a later publish can queue a new start. `spec.md` D-04 now says all three rechecks fail closed.

### 4. A to B to A keeps the previous account's tunnel: `68d10c983`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLinker.test.ts`

Red: `keeps the previous account's tunnel when that account relinked meanwhile` failed with `expected [ 'upsert:user_123', …(1) ] to deeply equal [ 'upsert:user_123' ]`: the previous account's tunnel was removed although its link was active again.

Green: `Tests 192 passed (192)` across `src/environments`. After `prepareDeprovision`, the cleanup reads the previous account's link and deprovisions only when it is still revoked (`getForUser` returns `null`), as `unlinkEnvironmentRecord` does before its retry. A failed read removes nothing.

### 5. Clerk webhook replay: `040b3a23b`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/webhooks`

Red: `answers a replayed delivery without acting on it again` failed with `expected [ 'user_2gone', 'user_2gone' ] to deeply equal [ 'user_2gone' ]`.

Green: `Tests 8 passed (8)`. After the signature check, the handler consumes a nonce in the existing `DpopProofReplay` store (scope `clerk-webhook`, expiry = timestamp + 5 minutes). A replay answers 204 and does nothing; a failed store write answers 500 so Clerk retries.

Deviation from "dedupe by `svix-id`", for the coordinator to accept or reverse: the nonce is `<svix-id>.<svix-timestamp>`. Svix documents that `svix-id` "will be the same when the same webhook is being resent (e.g. due to a previous failure)" and that `svix-timestamp` is "the timestamp of the attempt" (https://docs.svix.com/receiving/verifying-payloads/how-manual); retries arrive up to hours later and would fail the 5-minute window otherwise, so keying on the id alone would turn Clerk's retry after a 500 into a 204 that deletes nothing. A captured request replayed as-is still matches, and a new timestamp needs the secret. The test `acts on Clerk's retry, which signs the same message with a new timestamp` covers this.

### 6. Clerk webhook deadline: `eeff50166`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/http/Api.test.ts`

Red: `gives POST /v1/webhooks/clerk the longer deadline` failed (504 at 9 s). Green: `Tests 49 passed (49)`. The deadline is chosen per path, so `/v1/webhooks/clerk` joins the provisioning paths at 25 s (the same value as the hook deadline). The two existing deadline tests folded into one table test, so `Api.test.ts` shrank from 1,982 to 1,960 lines; `Api.ts` stays at 1,511.

### Not changed

FCM `user_hash` stays unkeyed by design so the phone can check it; a known user id can be confirmed against it. `ManagedEndpointProvider.test.ts` (2,064 lines, a test file) is untouched.

### Whole relay package after the follow-ups

`npx vp test run --config ../../vite.config.ts --dir .`: `Test Files 53 passed (53) / Tests 668 passed (668)`. `npx tsc --noEmit -p tsconfig.json`: no errors. `npx vp lint .` in `infra/relay` after fix 6: only the pre-existing findings (unused `HookForwarder` import in `Api.ts`, node import style in `src/testing/sqliteD1.ts`).

Task `Files` touched beyond the earlier lists: `infra/relay/src/http/Api.test.ts` (fix 6) and `infra/relay/src/environments/EnvironmentLinks.integration.test.ts` (fix 2).

## Round-2 follow-ups

From the round-2 review of PR #912 at `afe1743c5`. Each fix is its own commit; every red run is on the code before that fix. Commands run from `infra/relay`.

### 1. Queued Live Activity starts check ownership: `155482293`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/agentActivity`

Red: `skips a queued start whose machine the user no longer has linked` (the user has live work only on `env-kept`; the queued start names `env-moved`) failed with `AssertionError: expected { deviceId: 'phone-1', …(5) } to match object { kind: 'live_activity_start', …(1) }`: the start went to APNs.

Green: `Tests 196 passed (196)`. The start recheck (`startIsCurrent`, which replaces `userStillHasLiveWork`) reads the user's activity rows once. `AgentActivityRows.listForUser` returns only rows whose environment the user still has actively linked under the same key, so the start is sent only when every environment in its content is among them and some work is still live. The update and alert paths keep their stricter state-identity checks. A start is still not required to match the rows' timestamps, because the rows move on between publish and delivery.

### 2. A losing relink leaves the tunnel's ingress alone: `d701401ef`

Commands: `npx vp test run --config ../../vite.config.ts --dir . src/environments/ManagedEndpointProvider.originGuard.test.ts src/environments/EnvironmentLinker.test.ts`

Red: the provider race test (real provider, allocations and links on SQLite D1) has the winner provision port 8319 and commit its key-1 link. The loser, which read no link earlier, then provisions the same tunnel for port 9999 under key-2. The loser's provision succeeded and rewrote the ingress. The linker test `refuses when a racing link committed another key before the tunnel is configured` failed the same way.

Green: `Tests 194 passed (194)` across `src/environments`. Option (a): `provision` takes `ownsOrigin`, which it reads right before the ingress write. False fails with `ManagedEndpointProvisioningFailed` (`configure-tunnel`, new reason `key-conflict`) and writes nothing. The linker passes "the account's active link for this environment is absent or has the proof's key", and turns `key-conflict` into the same refusal as its read check (`descriptor_mismatch`, `validate_existing_link`). The guarded link write from round 1 stays. Tunnel recovery passes no guard; it is authenticated by the environment's own credential. `ManagedEndpointProvider.ts` is 1,474 lines.

Residual: the guard is a D1 read and the ingress write is a Cloudflare call, so they cannot be atomic. A winner whose link commits between the loser's guard read and its ingress write (one Cloudflare request) can still be repointed. Two provisions that overlap earlier are handled by the allocation generation: the later reservation makes the earlier one's next claimed write fail with `claim-lost`, so that one never links.

### 3. A deleted account's unexpired tokens are refused: `fadfb1acf`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/http src/admin`

Red: `refuses a deleted account's writes with a token issued before the deletion` (deletion marker set, rows deleted, then the phone's earlier DPoP token used) failed with `AssertionError: expected { status: 200, body: { ok: true } } to match object { status: 401, … }`: the registration was written again.

Green: `Tests 131 passed (131)`. `PhoneRemovals.isAccountDeleted` reads `relay_account_deletions`. In-app deletion and the Clerk webhook both set that marker first, and nothing clears it. Three checks use it:

- Every DPoP call (`requireDpopPrincipalScope`, which covers mobile registration, Live Activity registration, connect and status) is refused with `invalid_bearer`.
- The token exchange refuses before it records a client key.
- The Clerk-bearer middleware refuses everything except `DELETE /v1/client/account`, so a client can still retry its own deletion.

The test checks that no device or client-key row is written and that connect never runs. A failed marker read follows the existing removal-check path (500, fail closed). `Api.ts` stays at 1,511 lines. The ConnectAdmin test's phone-removal mock gained `isAccountDeleted`, so `infra/relay/src/admin/ConnectAdmin.test.ts` is added to T-12's Files.

### 4. The Clerk replay record outlives the window: `0a5c626c4`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/webhooks`

Red: `keeps the replay record past the last second the signature is accepted` failed with `expected 1795580515000 to be greater than or equal to 1795580575000`: the record expired at timestamp + 300 s. The verifier still accepts deliveries through that whole second, and the prune deletes rows with `expires_at < now`.

Green: `Tests 9 passed (9)`. The record now expires at timestamp + 300 s + 60 s.

### 5. Recorded only: machine-move cleanup race

`EnvironmentLinker.ts` (the previous-account tunnel cleanup after a move) has a remaining race. If account A relinks just after B's linker has read A's link as revoked, and A's commit leaves the allocation generation unchanged, B's best-effort `deprovision` can delete A's fresh DNS record. This affects availability only: A's next link or tunnel recovery recreates the record. Not changed.

### Whole relay package after round 2

`npx vp test run --config ../../vite.config.ts --dir .`: `Test Files 54 passed (54) / Tests 673 passed (673)`. `npx tsc --noEmit -p tsconfig.json`: no errors. `npx vp lint .`: only the pre-existing findings (unused `HookForwarder` import in `Api.ts`, node import style in `src/testing/sqliteD1.ts`).

## Round-3 follow-ups

From the round-3 review of PR #912 (head `f9108a042`). Each fix is its own commit; every red run is on the code before that fix. Commands run from `infra/relay`.

### 1. A queued start never carries an old key's content: `036ccd9d0`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/agentActivity`

Red: `starts with the current key's content, never the queued content of an old key` failed with `expected '{"aps":{"timestamp":0,"event":"start"…' not to contain 'Thread under the old key'`. In that test the machine was relinked under a new key with the same environment id, so the environment-id check passed and the queued content went to APNs.

Green: `Tests 197 passed (197)`. The signed start job carries no keys, and changing its schema would invalidate queued jobs. So I did not add a key comparison to the job. Instead, the start is sent with content rebuilt at delivery from `AgentActivityRows.listForUser`. Those rows are joined to the user's active link on environment id and key (`src/agentActivity/AgentActivityRows.ts:210-217`), so an old key's rows cannot be selected. The rebuild happens before the alert is recomputed, so the alert also names only current content. The round-2 checks stay in place: the start is skipped when its environments are no longer linked or no work is live.

### 2. The client-key write refuses a deleted account: `2cbff5f65`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/http src/agentActivity src/admin`

Red: `mints no token when the deletion lands between the exchange's check and its write` failed with `expected { status: 200, body: { …(5) } } to match object { status: 401, … }`. In that test the marker read returns false while the marker row exists.

Green: `Tests 329 passed (329)`. `recordClientKey` is now a single statement: `INSERT … SELECT … WHERE NOT EXISTS (relay_account_deletions for the user) ON CONFLICT … DO UPDATE … RETURNING`. It returns whether a row was written. When nothing was written, `admitTokenExchange` refuses with `invalid_bearer`, so no token is minted.

### 3. A deleted owner's admin token is refused without a `sid` too: `df52a8128`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/admin`

Red: `refuses a deleted owner's unexpired token, with a session id or without` failed with `expected 200 to be 404` for the token without `sid`.

Green: `Tests 69 passed`. The admin middleware now always calls `clerkSessionStatus`, which takes an optional session id. A deleted account is refused whether or not the token names a session. A removed phone's session is refused as before, and a failed check still hides the routes.

### 4. Ownership is read inside the configure claim: `9437f5542`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/environments/ManagedEndpointProvider.originGuard.test.ts`

Red: `does not change the ingress when the winner commits during the loser's claim` failed. In that test the winner's link commits after the claim's generation read and before the ingress write; the ingress became the loser's port. While writing this test I found the existing race test had been sharing one database across tests; the file now builds a fresh database per test.

Green: `Tests 195 passed (195)` across `src/environments`. The `ownsOrigin` read now runs inside `withClaimedTunnel`, after its generation read (`src/environments/ManagedEndpointAllocations.ts:768-783`) and immediately before `putConfiguration`. A false result fails with `key-conflict` and writes nothing. `ManagedEndpointProvider.ts` is 1,457 lines.

Remaining window: from the ownership read (one D1 query) until Cloudflare applies `putConfiguration` (one HTTPS request). A D1 read and a Cloudflare call cannot share a transaction. Bumping the allocation generation on link commit would not close this window either, because the generation is also read before the Cloudflare call.

### 5. A refused publish-only link no longer removes the winner's tunnel: `9b12b175e`

Command: `npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLinker.test.ts`

Red: `a refused publish-only link leaves the winning link's tunnel alone` failed with `expected [ 'deprovision:user_123' ] to deeply equal []`. The teardown had run before the guarded write refused the link.

Green: `Tests 260 passed` (`src/environments` and `src/http`). The publish-only teardown now runs only after the guarded link write succeeds. A refused write therefore tears nothing down. A different key that commits later is refused by the guarded write, and `deprovision` keeps its own allocation-generation claim against concurrent provisions.

### 6. Another account linking the same environment id reaches nothing of the first account's

Account B can link environment id E, which belongs to account A, under B's own key, because the key-change refusal is scoped to `(userId, environmentId)`. I checked every place that reads by environment id. Each one also filters by the key or the account, so B's link reaches nothing of A's:

- **Pushes:** they go only to links proven by the publishing key (`src/environments/EnvironmentLinks.ts:216-224`).
- **Activity rows:** they are stored per key (`src/persistence/schema.ts:269`) and joined to the reader's link key (`src/agentActivity/AgentActivityRows.ts:210-217`).
- **Revocation:** a new link revokes only other accounts' links with the same key (`src/environments/EnvironmentLinks.ts:305-311`).
- **Webhook-hold opt-in:** it is inherited only from links with the same key (`src/environments/EnvironmentLinks.ts:244-248`).
- **Tunnels:** the allocation, tunnel name, hostname, DNS record and hook endpoint key all derive from `(namespace, userId, environmentId)` (`src/environments/ManagedEndpointProvider.ts:1084`). B gets its own tunnel and never touches A's ingress or DNS.
- **Environment credentials:** a credential authenticates only while an active link with the same environment id and key exists (`src/environments/EnvironmentCredentials.ts:210-224`).
- **Credential-scoped calls:** their owners and hook endpoints come from `findActiveManagedForEnvironment` with the caller's key (`src/http/PhoneRemovalApi.ts:241-247`, `src/hooks/HeldHooks.ts:99-115`, filter at `src/environments/EnvironmentLinks.ts:571-574`).
- **Hardware replacement:** it is scoped to the caller's own account (`src/environments/EnvironmentLinks.ts:349-350`).

No fail-open, so no change.

### Whole relay package after round 3

`npx vp test run --config ../../vite.config.ts --dir .`: `Test Files 54 passed (54) / Tests 678 passed (678)`. `npx tsc --noEmit -p tsconfig.json`: no errors. `npx vp lint .`: only the pre-existing findings (unused `HookForwarder` import in `Api.ts`, node import style in `src/testing/sqliteD1.ts`). T-12 Files now also list `infra/relay/src/admin/ConnectAdmin.ts` and `infra/relay/src/environments/ManagedEndpointProvider.originGuard.test.ts`.

Also `43d03967a`: `EnvironmentLinks.integration.test.ts` built one shared database for all its tests, the same problem found in item 4. It now builds a fresh database per test. All 5 tests still pass on their own state.

## Round-4 hardenings

### A. A queued start reads its rows after the job claim: `4ab3f7453`

Red: `reads no rows for a start whose job was already delivered` failed with `expected 1 to be +0`, because the rows were read before `claimSourceJob`. Green: `Tests 198 passed (198)` across `src/agentActivity`. A queued start now reads its current rows just after the claim and target check, and before the alert is recomputed. A start sent directly, without a source job, reads the same rows. The content still comes only from the user's current rows, matched by environment and key.

### B. Each ingress retry reads ownership first: `9c2fbb10b`

Red, on the Worker bindings with a stub tunnel API whose first PUT fails with a retryable error: `reads ownership again before a retried write, and stops when it changed` failed. The provision ended with the PUT error instead of `key-conflict`, and ownership was read only once. Green: `Tests 2 passed (2)`. The second test, `retries the write while ownership holds`, shows two ownership reads and two PUTs, then success.

The tunnel client gains `putConfigurationAfter(check, tunnelId, config)`. The Worker binding runs `check`, then a `putConfiguration` with Cloudflare's client retry switched off (`CloudflareRetry.none`). It retries that pair with the same schedule and transient-error test as `CLOUDFLARE_CALL_RETRY`, within the same 8-second limit. Provision passes its ownership read as `check`. Every other `putConfiguration` caller, including origin reconcile, keeps the client retry. `ManagedEndpointProvider.ts` is 1,476 lines.

## Round-4 classification

**Ingress window.** Only one account can drive this: the same signed-in account presenting two keys for one environment id at the same moment. That means two machines claiming one environment id, or a machine whose key was reset racing its old self. Another account cannot reach this account's allocation or tunnel, which are keyed by user and environment (`ManagedEndpointProvider.ts:1084`). Worst outcome: the account's own tunnel serves the losing machine's loopback port until the winning machine links again. On `main`, provision wrote the ingress with no ownership check at all, so any losing request repointed the tunnel. Residual: *Provision reads link ownership right before each ingress write attempt, inside the allocation claim; between that D1 read and Cloudflare applying that attempt's PUT (one HTTPS request), a link committed by the same account under another key can still be repointed to the losing request's local port until the winning machine links again.*

**Publish-only teardown.** Only one account and one key can drive this: the same machine sending a publish-only link and a managed link for the same environment at once. The teardown now runs only after the publish-only link's guarded write succeeds. Worst outcome: the managed link that commits in between loses the tunnel it just provisioned, until it links again or recovers its tunnel. On `main`, the teardown ran before the write and unconditionally, so a refused link could also remove the winner's tunnel. Residual: *A publish-only link releases the account's tunnel for that environment after its own link write succeeds; a managed link from the same machine committed in the moment between that write and the teardown can lose its newly provisioned tunnel until it links or recovers again.*

**Same-machine replacement.** Only one account can drive this. The hardware identity is self-asserted, but replacement only touches the caller's own links for that identity (`EnvironmentLinks.ts:349-350`). Worst outcome: a new link from a reinstalled machine deregisters the account's older link for that machine (link, credentials, tunnel, DNS) before its own provisioning and guarded write. If the new link is then refused, the older link is gone anyway, and the machine must link again. `main` has the same order, unchanged. Residual: *A link that presents the same hardware identity as one of the account's older links deregisters that older link before its own write; if the new link is then refused, the account must link the machine again.*

**APNs check-to-send.** Driven by the user's own machines publishing, or by one of the user's machines moving to another account. Worst outcome: between the delivery-time read of the user's current rows and APNs accepting the start, the work can end or the machine can move. The phone then gets a start built from rows the user owned at the moment of the read: at most one D1 read plus one APNs request old, never another account's content. On `main`, a queued start was sent with its publish-time content and no ownership recheck. Residual: *A queued Live Activity start is built from the recipient's current rows at delivery; work that ends, or a machine that moves accounts, between that read and APNs accepting the request can still produce one start showing content the recipient owned at the time of the read.*

### Whole relay package after round 4

`npx vp test run --config ../../vite.config.ts --dir .`: `Test Files 55 passed (55) / Tests 681 passed (681)`. `npx tsc --noEmit -p tsconfig.json`: no errors. `npx vp lint .`: only the pre-existing findings. T-12 Files now also list `infra/relay/src/environments/ManagedEndpointCloudflareBindings.test.ts`.

## Round-5 follow-ups

### 1. A losing provision repairs the ingress after its own write: `aba7d57dc`

Red, in `ManagedEndpointProvider.originGuard.test.ts`: `puts the owner's origin back when its own PUT landed after the winner committed` failed before the fix, because the tunnel's final ingress held the losing request's origin. In `EnvironmentLinker.test.ts`, `puts its own origin on the tunnel once its link write committed` failed because no `reconcileOrigin` call followed the link write. Green after the fix.

The convergence runs from both sides. A single "reconcile from D1 on conflict" step is not enough. When the loser marks the allocation ready before the winner's link write commits, the loser's own ownership read still passes, and D1 `allocation.origin` holds the loser's origin.

- **Loser side.** After its ingress PUT, provision reads link ownership again. If another key now owns the link, it PUTs the origin D1 holds for the allocation (`restoreOwnerIngress` in the new `ManagedEndpointIngress.ts`) and returns `key-conflict`.
- **Winner side.** Once its guarded link write commits, the linker calls `reconcileOrigin` with `force: true`. That puts its own verified origin back even when D1 already matches.

`formatOriginService` and `ingressFor` moved to `ManagedEndpointIngress.ts`. The bindings test `retries the write while ownership holds` now counts 3 ownership reads (two before PUTs, one after).

### 2. A previous-account cleanup puts back a DNS record that a returning link refreshed: `bec6538d1`

Red, in the new `ManagedEndpointProvider.cleanupRace.test.ts`, test `keeps A's DNS record when A's return lands inside B's cleanup`. Account A provisions, then the cleanup for B's link reads its target. A provisions again inside the cleanup's DNS delete, and then the delete lands. The test failed with `expected [] to include 'dev-alice-…studio.test'`. Green after the fix.

With `keepIfRefreshed`, deprovision re-reads the allocation after deleting the DNS record. If the generation moved past the one it claimed, it puts the CNAME back for the current tunnel and stops before the tunnel delete. Only the linker's previous-account cleanup passes the flag. Unlink and replaced-machine cleanup keep their current behavior, so the 2,064-line `ManagedEndpointProvider.test.ts` stays unchanged. `ManagedEndpointProvider.ts` is 1,495 lines.

### Residuals after round 5

- **Ingress:** *A losing provision re-reads link ownership after its own ingress PUT and puts back the origin D1 holds, and the winner reasserts its own origin once its link write commits. Both repairs are best effort, so if the winner's reassert fails after the loser's read already passed, the tunnel serves the losing machine's local port until the winning machine links again.*
- **A→B→A DNS:** *The previous-account cleanup re-reads the allocation after its DNS delete. If A's return refreshed it, the cleanup puts the record back and writes the new record id to the allocation, but only while the allocation still has the generation and tunnel it read, so a later unlink deletes the live record. A's hostname does not resolve between that delete and the restore (one D1 read and one Cloudflare write). If the restore fails, the hostname stays down until A links again. If a provision's own DNS step runs at the same moment as the restore, both can create a record and the allocation keeps only one id, so a later unlink can leave the other CNAME behind.*
- **Publish-only teardown:** *A managed relink that starts after the publish-only write can still lose its DNS record, or the tunnel itself, to the earlier request's cleanup; main had already attempted cleanup by the time that write became visible.*
- **Same-machine replacement:** *A matching self-asserted hardware identity selects another environment under the same account. Revocation targets the account and environment id, so it can also revoke a newer link at that id before the replacement write succeeds. The affected environment must relink.*
- **Live Activity:** *An in-flight start can carry the old account's authorized snapshot after work ends or the machine moves. If the same push-to-start token is reassigned to another account after the target check, APNs can also deliver the old account's content to that installation after it switches accounts.*

### Whole relay package after round 5

`npx vp test run --config ../../vite.config.ts --dir .`: `Test Files 56 passed (56) / Tests 684 passed (684)`. `npx tsc --noEmit -p tsconfig.json`: no errors. `npx vp lint .`: only the pre-existing findings. T-12 Files now also list `ManagedEndpointIngress.ts` and `ManagedEndpointProvider.cleanupRace.test.ts` (umbrella `c46179149`).

### 3. The restored record's id is written back: `170d1bf79`

Red, in `ManagedEndpointProvider.cleanupRace.test.ts`, test `leaves no DNS record once A unlinks after its record was put back`. It runs A→B→A with the delayed cleanup, then unlinks A. The test failed with `expected [ 'dns-2' ] to deeply equal []`. The allocation still held `dns-1`, the record the cleanup deleted, so the unlink's delete hit a missing record and left the restored `dns-2` behind. Green after the fix.

`restoreRefreshedDns` in `ManagedEndpointIngress.ts` puts the record back starting from the allocation's recorded id. When the live record's id differs, it calls the new `ManagedEndpointAllocations.restoreDns`. That is one `UPDATE … SET dns_record_id … WHERE user, environment, tunnel_id AND generation match RETURNING`, and it succeeds only if a row changed. It leaves the generation unchanged, so a provision still running on that generation is not cut off. The method is optional on the service, so the test stubs in the 2,064-line `ManagedEndpointProvider.test.ts` did not change. `cnameRecordFor` moved to `ManagedEndpointIngress.ts`. `ManagedEndpointProvider.ts` is 1,489 lines. T-12 Files now also list `ManagedEndpointAllocations.ts` (umbrella `8b9c8c10c`).

Relay package: `Test Files 56 passed (56) / Tests 685 passed (685)`. `npx tsc --noEmit -p tsconfig.json`: no errors. `npx vp lint .`: only the pre-existing findings.

## Round-6 split

PR #912, branch `1478-relay-privacy`. New head `46ca78a18`, rebuilt on the same base `e4caea076`. The round-5 notes above (`aba7d57dc`, `bec6538d1`, `170d1bf79` on the lane branch, replayed as `77bd3ea20`, `c820789bd`, `c29adf9c9`) are superseded: those three commits are not on the rebuilt branch. Range diff: `~/.specwithcode/m4/scratch/2026-11-24-1478/range-diff-round7.txt`. Work tree: `~/.specwithcode/m4/scratch/2026-11-25-1478/wt-r7`.

Rebuild: the 28 commits of `origin/main..c29adf9c9` except `77bd3ea20`, `c820789bd` and `c29adf9c9`, replayed with `replay.sh` (noreply identity). The replay had no conflicts. The rebuilt `d13ebed06` has the same tree as `92872eb70`. Added:

- `a0c18ea2d` removes the previous-account tunnel teardown: the teardown half of `bea8eb8e7`, and `b9c4fcdb2`. The `previousAccounts` read and its loop are gone from `EnvironmentLinker.ts`, along with both teardown tests. One test now pins the new behavior, `leaves the previous account's tunnel to that account when the machine moves`. The link revocation from `85a976a32` (`EnvironmentLinks.ts:298`) and the key-change refusal (`EnvironmentLinker.ts:307-322`, plus the write-side `EnvironmentLinkKeyConflict`) stay.
- `1db793d1c` adds account deletion tests for the tunnel of a link that a machine move revoked.
- `14e05a097` adds the A→B→A reuse test.
- `46ca78a18` brings `ManagedEndpointProvider.test.ts` back under its base size: 2,054 lines, against 2,057 on main. It had grown to 2,064 with the R14 commits.

Nothing kept depends on the teardown:

- `a8a59d62c` is the publish-only teardown for the link's own account (`EnvironmentLinker.ts:452`).
- `a15bdc383` and `e1d08f813` are the provision ownership guard (`ManagedEndpointProvider.ts:1250-1262`).
- The R13 tests (`EnvironmentLinks.integration.test.ts`) test link rows only.
- The allocations DNS-id handling was `c29adf9c9` and is dropped.

The full suite passes after each added commit.

### 1. Does the data path consult the link row?

No. A managed hostname is a proxied CNAME to `<tunnel>.cfargotunnel.com` (`ManagedEndpointProvider.ts:1310`). The tunnel ingress sends it straight to the machine's loopback origin (`ManagedEndpointProvider.ts:1268-1270`). The Worker is bound only to the relay API domain (`src/worker.ts:132`), so it is never on that path. After a revocation, including the one a machine move now performs, the old account's hostname keeps routing to the machine until that account's unlink, account deletion or the idle-tunnel sweep removes the tunnel. That is the same as main.

### 2. Do account deletion and the Clerk webhook find tunnels through active links only?

No. The Clerk webhook calls `deleteAccountRecords` (`src/webhooks/ClerkWebhook.ts:155`). That function lists environment ids from every link row of the account, revoked or not, plus every allocation row (`src/account/AccountDeletion.ts:127-134`). For each id, it unlinks with `forceDisconnect: true` (`AccountDeletion.ts:259-266`). The unlink deprovisions by account and environment whether or not a link is still active (`src/environments/EnvironmentUnlink.ts:31-58`). Rows are deleted only once no allocation is left (`AccountDeletion.ts` `deleteUserRows`, refused while an allocation remains).

No fix was needed, so the new tests are pinning tests, green from the start:

- `EnvironmentLinks.integration.test.ts` `still lists a moved account's environment for its account deletion` runs on real SQLite. I checked that it catches the active-only variant: adding `isNull(revokedAt)` to the query made it fail with `expected [] to deeply equal [ 'env-1' ]`.
- `AccountDeletion.test.ts` `removes the tunnel of a link that a machine move revoked` covers a revoked link with a still-connected tunnel: the tunnel is removed and the Clerk user is deleted.

### 3. Does A's relink after A→B→A reuse its tunnel and DNS record?

Yes. The hostname and tunnel name derive from the namespace, account and environment (`ManagedEndpointProvider.ts:1090-1113`), so A and B get separate allocations. A's return finds its own allocation and updates its recorded DNS record in place (`ensureDnsRecord`). The test `ManagedEndpointProvider.accountMove.test.ts` `reuses A's tunnel and DNS record when the machine returns to A` checks four things after A→B→A provisions:

- A gets the same endpoint as before.
- A gets the same tunnel id.
- A's allocation keeps the same DNS record id.
- There are exactly two tunnels and two CNAMEs, each pointing at its own account's tunnel.

### 4. Does any path delete DNS or tunnels by environment rather than by owner?

No:

- **Deprovision** claims the `(userId, environmentId)` allocation. It deletes that allocation's `dnsRecordId` (`ManagedEndpointProvider.ts:761`) and `tunnelId` (`:787`).
- **Release** is also owner-keyed (`:905-947`).
- **Duplicate-record cleanup** deletes only records with the same hostname (`:490-505`), and that hostname is owner-derived (`:1090-1113`).
- **Origin reconcile** reads the owner's allocation and checks its tunnel id (`:575-600`).
- **Unlink** uses `(userId, environmentId)` (`EnvironmentUnlink.ts:31-58`).
- **The admin unlink** passes the target account (`src/admin/ConnectAdminActions.ts:316-320`).
- **The idle reaper** releases by the allocation's owner (`ManagedEndpointReaper.ts:385-387`).

### Residual (1): a same-account loser's late ingress PUT

**On main.** Provision PUTs the requester's origin with no ownership check (main `ManagedEndpointProvider.ts:1199-1216`). The Cloudflare client retries that PUT (main `:1442-1443`). The link write comes after provisioning and does not compare keys (main `EnvironmentLinker.ts:387-412`). Two machines under one account presenting one environment id therefore both PUT, and the last PUT wins, even when it belongs to the losing machine.

**On the rebuilt branch, not widened.** The linker refuses a known key change before provisioning (`EnvironmentLinker.ts:307-322`). Provision reads ownership inside the configure claim, right before each PUT attempt (`ManagedEndpointProvider.ts:1250-1262`, `ManagedEndpointCloudflareBindings.ts:95-117`). The retries are not new: the same `CLOUDFLARE_CALL_RETRY` schedule and 8-second limit as main, with each attempt re-checking. The gap between a check and its PUT is one HTTPS request. There is no post-PUT repair and no post-commit reassert.

**Port validation.** The ingress port is checked only as an input: integer 1 to 65,535 (`packages/contracts/src/relay.ts:241-244`) with a loopback host (`EnvironmentLinker.ts:136-144, 293`; `ManagedEndpointProvider.ts:404-412`). The only registered port is the allocation's D1 `origin` (`src/persistence/schema.ts:176`), which the winner's own provision writes. Comparing against it is a D1 read, so it has the same race, and a machine may legitimately change ports between runs. A pure input check that constrains the port does not exist, so none was added.

### 5. Synchronous Cloudflare calls after the D1 commit

The previous-account teardown and the dropped post-commit reassert are gone. One remains. When a publish-only link replaces a managed one, its own teardown runs after the link write (`EnvironmentLinker.ts:452-466`, from `a8a59d62c`; main ran it before the write). It is best effort and errors are ignored. It calls Cloudflare only when that account still has an allocation for that environment; otherwise it is one D1 read. A slow Cloudflare there could still make a committed publish-only link time out. Reverting `a8a59d62c` would move it back before the write, as on main.

### Suite after the split

`npx vp test run --config ../../vite.config.ts --dir .`: `Test Files 56 passed (56) / Tests 683 passed (683)`. `npx tsc --noEmit -p tsconfig.json`: no errors. `npx vp lint .`: only the pre-existing findings.

Changed files over 1,500 lines:

| File | Main | Head |
|---|---|---|
| `ManagedEndpointProvider.test.ts` | 2,057 | 2,054 |
| `Api.test.ts` | 1,982 | 1,960 |
| `Api.ts` | 1,515 | 1,511 |

None grew; every other changed file is under 1,500. The umbrella spec's T-12 Files now list `ManagedEndpointProvider.accountMove.test.ts` and drop the three files the split removed (umbrella `25d219911`).
