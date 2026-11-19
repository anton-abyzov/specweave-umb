# Design review 2: 1422 one-way join

Reviewer: Codex GPT-6.2 Sol, effort high, on M5 (Muse Wonderful out on every machine until November 23, 2026). November 19, 2026, 9:19 PM UTC. Read the spec at `origin/fix/device-approval-several-devices` after round 4 (`0ffe07ceb3`, `c4e7e004fd`) and app `origin/main`. Thread: studio://thread/644195cc-3df8-418f-9708-3cd5ff059725/mcp%3Ae4892bbf-ef2e-44aa-9dd3-e541d5f496d8

Spot-checked by the owner thread at app `origin/main` `b0e6a6892`: `apps/server/src/auth/http.ts:712` is the `pairingCredential` handler (needs only `access:write`); `apps/web/src/cloud/ConnectRouteReconciler.tsx:185` is the automatic `register` of a relay route. Both match the findings that cite them.

Design: fix first

1. Vouch provenance: closed for the signer. N checks the signature against the app key J named before line minting and spends the bound ticket once. `spec.md:146`
2. Join approval used twice: closed for concurrent spending. The reservation is persisted before add or redeem; an interrupted reservation is not replayed. `spec.md:113`
3. Vouch revocation: not closed. The grant lock orders writes but cannot prevent a crash after the policy commits and before the auth mirror invalidates the vouch. Reconcile before serving auth, or commit both together. `apps/server/src/fleet/WorkGrants.ts:409`
4. `ownerCap`: not closed. The four checks cover the new build, but the old `/mcp` path takes the cap from the token. Require a compatible build before accepting capped credentials. `apps/server/src/fleet/WorkGrants.ts:519`
5. Tailscale pairing: not closed. The workers-only token keeps the ordinary management subject and scopes; the old issuer does not enforce `pur`. Use a credential format the old issuer rejects. `apps/server/src/auth/http.ts:712`
6. Pop-up race: not closed. Removing a route after registration cannot undo the approval request it already sent to J. Block automatic registration before relay minting; test that J never records a request. `apps/web/src/cloud/ConnectRouteReconciler.tsx:185`
7. Older approver window: closed against a new server. The list hides join requests, and approval without the flag returns `not-found` without charging a wrong attempt. `spec.md:125`

New findings
- High: First spend binds whichever line arrives, not necessarily the destination named in the approval. Validate the line's destination and verified ticket against the approval before reserving or adding it. `spec.md:113`
- High: If retry gives up the management token before the worker revoke succeeds, the retry loses the credential it needs to finish. Persist pending removal under the renewal lock, stop renewal, and acknowledge worker and management revocation separately, in that order. `apps/server/src/fleet/workerGrantMint.ts:499`
- Medium: The concurrency test puts its latch inside `addMachine`, which only the reservation winner should reach. Put the barrier after authorization but before reservation; assert exactly one add and one redeem. `spec.md:299`
- Medium: An open join ticket hides unrelated device requests, including a phone pairing started during the join. Hold only the attested app key's request and test that unrelated requests stay visible. `spec.md:217`
- Low: The threat table still puts key confirmation after a successful join. Align it with pre-mint `expectedKey` binding. `spec.md:273`

AC-05: does not hold as designed. Revocation is not crash-safe, and the offline fallback is not yet guaranteed.
AC-06: does not hold as designed. Agents are granted one way, but reverse Allow can still trigger an automatic approval prompt.
AC-10: does not hold as written across versions. The legacy fallback grants full device access; removing it 60 seconds later cannot undo access already used.
