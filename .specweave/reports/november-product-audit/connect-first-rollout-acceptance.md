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

## Acceptance received

Anton explicitly approved #1348 at reviewed head `eee098aa96b99a522984b159e07fe2043d0e5d16` and requested merge, release, M3 signed desktop verification, and full release verification. The PR was marked ready, triggering [required PR checks](https://github.com/anton-abyzov/specwithcode-dev/actions/runs/41775964235). The separate Gmail and Team Rules Retry holds still apply.

Required Checks 41775964235 passed. #1348 merged at `24a757c9a8d3f771e8ed31006a4af47c3d188d65`. The full reviewed diff and squash merge share patch ID `46943cbc1ff7c8aefd83a3f7c6f7ea1127d81428`; all ten changed blobs match. Main Checks 41777521771 started automatically. The existing designated publisher owns the next release.

The published 1.0.179 baseline verified Connect service status on M3 and M1, both reporting installed and running 1.0.179. The canonical verifier at umbrella origin/main returned six passes and two fails. The M3 service local forward returned HTTP 000, and its pinned SSH desktop fallback timed out. M4 and M1 signed apps passed the required signature and Gatekeeper checks. These are baseline results for the current published release, separate from post-release acceptance of #1348. See studio-1.0.179-full-verify.json and studio-1.0.179-connect-readback.json.

Main Checks 41777521771 settled successfully (2 successful jobs and 13 path/event skips). The latest private release readback still showed 1.0.179. No release including the merge was observed, and the designated publisher's ownership was preserved. The merged source checkout was retained pending the release verification gate.
