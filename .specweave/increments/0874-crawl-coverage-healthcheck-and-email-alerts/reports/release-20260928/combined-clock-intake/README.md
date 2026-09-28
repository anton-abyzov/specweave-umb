# Final merged telemetry and intake artifact

Worker `504442ec-e26e-4ee7-8872-bae010516a61` serves 100% of production traffic from reviewed merged source `7f86c79ceeee190d6017d6e2f857a68ea522067a`. All four checks on that exact merged source passed. The combined local suite passed 6,045 tests with 14 existing skips. All fourteen reviewed telemetry, clock and intake source hashes match the retained artifact manifest.

The earlier `b4eefbb5` merged-source unit run was cancelled by the workflow's newer same-branch run, not passed. Its cancelled receipt is retained separately. Required PR79 checks and all final `7f86c79c` checks passed; these are distinct records.

The final build used Node 22.20.0 and the verified checkout-local dependency layout. Its manifest binds 4,023 artifact files and 124 Prisma assets. The failed `97e2143c…` artifact and guarded rollback to `72af68f0…` are retained in the sibling `intake-identity/packaging-incident/` directory. A successful build alone did not establish runtime correctness; the replacement passed public data, catalog redirect, disabled harness GET, existing-private-record denial and queue-health checks. All six queue consumer configurations remain unchanged.

T029 is complete through the CLI, with a fresh 142-test focused run and a local validator binding the reviewed source, PR and merged-source CI, active Worker version, runtime checks and natural heartbeat records. At 23:16:21Z and 23:18:30Z, all three registered VM records were valid and independently advanced. The intermediate 23:17:05Z read is retained: two VMs had not yet emitted their next heartbeat, so it was not used to claim two complete fleet samples. No heartbeat was injected and no email-capable evaluator was invoked.

The same VM3 sweep `026ba568-3ac5-4855-95fd-6c441c8007d2` and historical failed-attempt item count of 694 remain recorded. Telemetry reports a partial sweep, not completed coverage. Crawler and scanner processes were preserved.

T030 remains open here pending the separate natural-intake diagnosis and bounded closure decision. The original blocked item has advanced, but new unresolved items are being investigated. This document does not attribute the exact original acceptance time to the final Worker version and does not claim a clean or complete sweep. T017 and T027 remain separate open work.

The local receipt parser pads Cloudflare's fractional timestamps for Python 3.9 without changing their instants. This evidence-only compatibility correction did not alter product code. TypeScript still has 314 unchanged baseline diagnostics; no green typecheck is claimed.

T030 bounded canonical recovery was subsequently closed through the CLI at 2026-09-28T23:38:40.864Z. Its final proof is in `../intake-identity/final-delivery/`. Twenty-two new distinct-artifact failures are owned by T031; no clean sweep is claimed.
