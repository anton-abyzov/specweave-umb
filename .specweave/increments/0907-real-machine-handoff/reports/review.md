# Review: 0907 Real machine handoff

Verdict: ship for completed manual phase T-01–T-04 only · risk: low · 7 reviewed files · 0 unresolved findings in that scope

Scope annotation after the product expansion: this report approves the completed manual-continuation evidence, documentation and verifier, with the provisioner covered by the separate review below. It does **not** approve the new ordinary product handoff, destination picker, guarded product-managed synchronization, Mac candidate release or six-route product acceptance in T-05–T-08 / AC-05–AC-08. The earlier `--phase all` result covered only the then-existing audit, manual handoff and environment phases. Increment 0907 remains open for the new product gates, their independent review and concrete UI acceptance.

Reviewer context: delegated reviewer independent of the verifier, its synthetic tests, and the documentation authors. Reviewed `scripts/fleet/verify-handoff-evidence.py`, `tests/test_handoff_evidence.py`, `docs/operations/real-machine-handoff.md`, `README.md`, `CHANGELOG.md`, `AGENTS.md`, and this increment's original manual-phase specification. Review performed on 2026-10-13 after all six manual destination receipts and their retained command outputs were available, before T-05–T-08 expanded the scope.

The reviewer authored the provisioner repair and therefore does not approve that code here. The separate `dev_environment_audit` reviewer reported **ship, no findings** for `scripts/fleet-project-sync.py:135–154`, its call sites at 204–227 and 244–253, and independently ran its 13 safety tests successfully in 35.451 seconds. That review covered real local bare-Git feature fetch/tracking, unchanged authentication and other Git configuration, read-only inspection, and dirty/custom configuration refusal.

## Verification

- `python3 -m unittest discover -s tests -p test_handoff_evidence.py`: **46 tests passed**, independently rerun after the final fixes. These use invented data and are not presented as machine-handoff evidence.
- `python3 scripts/fleet/verify-handoff-evidence.py --phase all`: **audit, handoff, environment passed**, independently run against the retained private machine receipts.
- `git diff --check`: passed.
- All nine successful native cycles contain three completed runs: coordinator dispatch, one local worker, and the coordinator's automatic completion wake. The six destination assignments contain their actual M4 source relay; worker IDs are fresh and nested commits match across machines.
- Independently checked all 12 supplemental raw `orchestration.getTurnItem` responses. Their SHA-256 hashes, command item IDs, worker/run identities, inputs and zero exit statuses match the retained native projections. Their output contains the checkpoint and package data actually read by each destination worker. All six collection indices report revoked temporary control sessions. No command was rerun to manufacture output.
- The 92-clone fetch-mapping receipt records 46 verified changes per destination with source state and unrelated Git configuration preserved.

Private evidence root: `~/.local/share/specweave/fleet/handoff-proof-20261013`. Relevant files are the nine `*-source.json` / `*-destination.json` cycle receipts and their parent/worker projections, six `*-transport-*.json` receipts, six `*.outputs.json` indices with 12 hash-bound raw API responses, `normal-origin-fetch-mappings.json`, and `local-development-verification.json` with its referenced receipts.

## Findings resolved during this review

1. **Medium — package completion could pass without the destination reading its checkpoint or package.** A positive synthetic destination previously contained only Git/README reads, while package summary fields appeared in neither native answer. The verifier now derives the two required file reads, binds retained public-API output to the exact native command items, parses the checkpoint and package fields, and requires matching package/script evidence in both worker and coordinator output (`scripts/fleet/verify-handoff-evidence.py:32`, `:160`, `:177`). The regression suite rejects missing reads, missing or altered retained output, mismatched identities and invented package evidence.
2. **Medium — empty summary arrays could hide a pending native approval.** A retained parent projection with a pending runtime request was accepted when its receipt claimed quiescence. The verifier now checks raw parent and worker runs, provider turns, runtime requests, work items, child state and completion delivery (`scripts/fleet/verify-handoff-evidence.py:20`). Negative tests reject pending work while settled historical attempts remain valid.

Both failures were reproduced before the changes and rechecked after repair. No critical, high or medium finding remains in the reviewed scope.

## Fixture closure evidence

Reviewed the specifications and ledgers for the three owned portable-continuation fixtures:

| Project | Increment | Recorded task state |
| --- | --- | --- |
| EasyChamp | `0975-m4-portable-continuation-proof` | T-01, T-02, T-03 done with exit-0 evidence |
| JobWeave | `0037-m4-portable-continuation-proof` | T-01, T-02, T-03 done with exit-0 evidence |
| SpecWeave | `0907-m4-portable-continuation-proof` | T-01, T-02, T-03 done with exit-0 evidence |

For each fixture, independently compared its three committed/reportable receipt summaries with the corresponding full private native receipts: status, host, mode, project, source baseline, marker, decision, actual worker/relay outcome, quiescence and temporary-session revocation match. Diffs from each source baseline remain inside that fixture's increment, and all nested code HEADs remain at their recorded pins. This supports normal CLI verification and closure by the owning operator; this review does not alter ledger or increment status.

## Evidence limits

The documented result is manual portable continuation of a completed M4 checkpoint using fresh destination workers. It is not migration of a running provider session and does not claim use of the usage-limit-only device-continuation button. The documentation distinguishes source, tested transport, and later evidence commits; preserves the original M1 folders and unpublished M4 owner work; and limits local-runtime claims to the tested entrypoints and isolated JobWeave database. Production integrations, a local Supabase Auth service and the complete EasyChamp backend fleet remain outside that proof.

Publication, final increment closure and final repository cleanliness remain the owning operator's subsequent checks. This report approves the reviewed implementation and evidence, not an unobserved push or merge.

Nits: none.
