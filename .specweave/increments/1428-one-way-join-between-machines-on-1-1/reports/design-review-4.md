# Design review 4: the one-way join, as moved to 1428

November 19, 2026. Reviewer: Codex `gpt-6.2-sol`, run 3 of the M5 thread "Design review of the one-way machine join" (runs 1 with Muse Wonderful and 2 with Codex failed before reviewing). It reviewed the design that moved unchanged from 1422 to this increment at umbrella `6613fc4`, against app `origin/main` `8ec70ec`.

This is not the Muse Wonderful review T-02 requires. It is input for T-01 (sort each finding against today's baseline) and T-02 (rework). It does not block 1422, which is wording only.

"AC-05", "AC-06" and "AC-10" are 1422's numbers; the reviewer mapped them to 1428 AC-03, AC-05 and AC-02.

## Verdict

Design: fix first.

## Findings (verbatim)

- **Critical — Workers-only is not an authorization boundary.** The design adds a marker but retains the management token's app scopes. The existing WebSocket ticket route requires no scope, and upgrade restores scopes from the session row. A pairing-refusal test can pass while the token still opens app RPCs. Fix: allowlist management operations at authentication and deny both ticket issuance and upgrade. `repositories/anton-abyzov/specwithcode/apps/server/src/fleet/fleetRedemption.ts:24`, `repositories/anton-abyzov/specwithcode/apps/server/src/auth/http.ts:650`, `repositories/anton-abyzov/specwithcode/apps/server/src/auth/SessionStore.ts:1350`.
- **High — The join can spend approval on an unverified line.** The design reserves against decoded destination and ticket fields before authenticating the issuer's binding. A substituted line can consume the one spend even if redemption later refuses it. Fix: authenticate the exact invitation, destination, ticket and app key before reservation, then verify the same binding at redeem. `repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetJoin.ts:150`, `repositories/anton-abyzov/specwithcode/apps/server/src/studioFleetJoin.ts:359`.
- **High — The installed-service path proves CLI credential possession, not app-key provenance.** `local-cli-credential` is a bearer issued for the CLI, not a desktop-only credential. The proposed `localApp` flag does not establish that the signing key belongs to the app that approved the join. Fix: enroll and bind the app key through trusted desktop IPC; test substitution of an unenrolled key. `repositories/anton-abyzov/specwithcode/apps/server/src/auth/LocalCliCredential.ts:13`, `repositories/anton-abyzov/specwithcode/apps/server/src/auth/http.ts:707`.
- **High — Vouch validity can outlast worker consent.** Narrowing sign-ins or lowering `ownerCap` can invalidate the binding through the generation check, but time can pass `endsAt` without any write. Fix: check live consent and policy expiry on use and renewal, and test expiry without a sweep. `repositories/anton-abyzov/specwithcode/apps/server/src/fleet/WorkGrants.ts:227`.
- **High — D-06 misses saved-route reconciliation.** A saved direct route can trigger a Connect mint through a separate branch while all three named selector tests pass. Fix: gate every automatic registration on current policy before minting; test saved routes and a stale snapshot. `repositories/anton-abyzov/specwithcode/apps/web/src/cloud/ConnectRouteReconciler.tsx:131`, `repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectRoutePlan.ts:19`.
- **Medium — The first mint can publish the wrong prompt.** Relay bootstrap runs before `/oauth/token` declares join purpose, and mint can already create an ordinary waiting request. Fix: defer listing until purpose is verified, require an exact purpose match at approval, and test a list poll between mint and exchange. `repositories/anton-abyzov/specwithcode/packages/client-runtime/src/authorization/service.ts:452`, `repositories/anton-abyzov/specwithcode/apps/server/src/cloud/CloudLink.ts:1820`.

The reviewer cited `WorkGrants.ts` with a doubled umbrella prefix (`repositories/anton-abyzov/specweave-umb/repositories/...`); it is written above with the usual prefix.

## Acceptance criteria (verbatim)

- AC-05 → 1428 AC-03: **Does not hold as designed.** App-key provenance and vouch expiry are incomplete.
- AC-06 → 1428 AC-05: **Does not hold as designed.** The reverse credential retains app reach, and an automatic registration path remains.
- AC-10 → 1428 AC-02: **Does not hold as designed.** The endpoint allowlist is the right boundary, but it does not fix the unverified spend or the pre-declaration approval prompt.

## For T-01 and T-02

- The Critical finding is the shipped gap already listed as owner item 16 (`1422-*/reports/design-review-3.md`, baseline section): the management key keeps app scopes, and the WebSocket ticket needs no scope (`http.ts:650`). The baseline should record it as today's behavior, not as a design defect.
- The saved-route finding is not checked yet: T-01 should confirm at `origin/main` that `ConnectRouteReconciler.tsx:131` can mint a Connect route from a saved direct route without the selectors D-06 names. Once saved, a Connect route is tried first (`insertRoute`, see 1422's PR 754), so the branch matters.
- The other four (spend before authentication, CLI-credential provenance, vouch expiry by time, purpose before listing) are design defects for T-02.
