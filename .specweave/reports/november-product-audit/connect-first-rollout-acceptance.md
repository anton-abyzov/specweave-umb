# Connect-first worker rollout acceptance

Candidate [draft PR #1348](https://github.com/anton-abyzov/specwithcode-dev/pull/1348), `codex/connect-first-worker-rollout`, exact head `eee098aa96b99a522984b159e07fe2043d0e5d16`. Follow-up to completed rollout increment 1119. The new auth behavior remains held pending manual acceptance.

## Behavior under review

- For a linked worker, the release uses the installed M4 CLI to issue a Connect-only, read-only status request. A successful response must attest the Connect transport. M4 is upgraded before worker rollout, so the normal release has the new CLI. An older CLI fails closed on standalone worker rollout.
- A structured relay-unreachable result on that initial status read permits pinned SSH fallback. Authentication, authorization, identity, proof-key and Team Rules refusals do not trigger SSH. If matching peer rules are required and Connect cannot establish them, the status result is an authorization refusal.
- The service route is pinned after selection. An update, cancellation, subsequent status or lost mutation response cannot move the operation to the other route. The nested CLI disables its own tailnet selection for Connect-only requests.
- A separate inventory-based pinned SSH operation handles signed macOS desktop updates because the relay cannot perform that operation. If Connect serviced the worker and the SSH desktop step has a recognized pre-connect network failure, the rollout reports an explicit desktop skip. Host-key, auth, interrupted transfers, install and signature failures still fail. A worker with no SSH inventory cannot use that desktop capability.
- The canonical release verifier still needs independent installed-bundle evidence. The live 1.0.178 Connect status readback establishes M1 and M3 service version only. M3 installed desktop signature and full release acceptance remain open.

## Verification

Exact independent re-review approved the route pin, peer rule refusal, and separate desktop behavior. Focused checks passed 84 rollout tests, 46 desktop tests and 62 TypeScript tests. The production server build passed. The [draft-preserving full Checks run](https://github.com/anton-abyzov/specwithcode-dev/actions/runs/41756422205) targets the exact head. No live policy, account, worker route, or application state was changed to test this candidate.

Full hosted Checks completed successfully at the exact draft head with 19 passed, one expected skip and zero failures. The normal macOS Scripts check passed. The draft is ready for manual acceptance of the routing behavior above. Acceptance permits normal integration and release after owner checks. It does not establish an installed desktop or approve the separate Gmail and Team Rules Retry drafts.
