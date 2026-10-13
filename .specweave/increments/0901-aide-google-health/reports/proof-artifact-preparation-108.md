# Proof artifact preparation for the coordinated 1.0.8 installation

Prepared offline on 2026-10-13. No live status/auth/provider/Google calls, token reads, browser activity or product source changes occurred. These changes do not establish that 1.0.8 is installed or that a Google read succeeded.

`aide-google-live.mjs` now records the actual full `server.environment.serverSourceCommit`, separately from the optional `--expected-source` gate. Missing or invalid runtime source becomes null; it is never replaced with the expected value. When expected source is supplied, mismatch/missing source fails before Google status or provider dispatch. Native/inspect require a source-bearing fresh status receipt and reject an actual source change since status. Invalid expected source is rejected before any auth session can be issued.

`verify-real-google.py` requires explicit `--expected-version` and `--expected-source FULL_40_HEX_COMMIT`, with no version/source default. Both real receipts must report that version and source. Output uses verified observed receipt fields. The original exact four Google calls, all three grants, health results, bounded reads, no additional tools/delegation, completed native run and owned-auth cleanup checks remain.

Validation performed:

- Node 22 `--check` passed for the runner.
- `python3 -B test-proof-artifacts.py` passed 14 offline synthetic cases, including source/version mismatch, missing source/arguments, failed run, missing grant/tool, extra tool/delegation, cleanup failure and result count overflow. Temporary synthetic receipts were removed; they are not live evidence.
- The actual failed 1.0.7 receipt pair still exits 1 under the explicit 1.0.7/source expectation because no observed source was recorded in those historical receipts. They remain unchanged, and the native run remains failed with zero Google calls.
- Runner invocation with invalid source exited 1 with `expected_source_requires_full_commit` before paths/auth/network were used.

Usage is in `google-live-plan.md`. After the root confirms installation, independently obtain the full actual release source commit from its installation evidence, then use the same explicit version and source in status, native and offline-validator invocations. Do not backfill historical receipts or relax provider route checks. T-06 stays incomplete until actual native Google proof passes.
