# T030 canonical intake collision recovery — release pending

Reviewed source `05f9bb6ef6a25026c3cf35f0b63b62bebdb0c4cb` passed all four required PR79 checks and merged as `b4eefbb5` on 2026-09-28 at 23:07:24Z. The four-file patch resolves only exact canonical or compatible legacy submission identities and preserves retryable errors when identity cannot be established. The retained source report and independent review describe the contract, scope and test limits.

The first deployed artifact, Worker `97e2143c…`, returned public API errors. Root initiated a guarded rollback to the previously verified `72af68f0-09f7-4ffe-b7bb-ed7bd562f23b`. Source tests and a successful build did not establish runtime correctness. T030 remains open; these records do not claim a successful release or recovered natural intake.

`t030-dependency-topology.json` records the concrete build difference: the intake checkout resolves package links into the older request-memory checkout, while the verified telemetry checkout has its own local dependencies. A combined rebuild and runtime check from the verified layout is pending. This is evidence of a packaging difference; the exact runtime cause must be supported by the retained deployment diagnosis.

`t030-source-receipt.json` binds the original source, tests, CI, build and sanitized natural baseline by hash. The local full suite passed 6,044 tests with 14 existing skips; hosted CI passed 6,040 with the same 14 skips because it excludes the existing sibling-repository parity file. Independent tests passed 229 with one existing opt-in database skip, plus twelve actual-source probes. TypeScript still has the same 314 baseline diagnostics; it is not green.

Closure requires the final reviewed source in the deployed artifact, all required checks, exact Worker version at 100%, unchanged six consumers, successful public runtime checks, and the original retained pending item settling through a normal scheduled retry. The pure local `t030-validate-delivery.py` checks supplied receipts; it makes no production request. Its underlying natural verifier must show the same crawler/scanner process identities and sweep, original batch advancement, unchanged canonical row/public scope, and retained historical error/loss counters.

No full adaptive sweep or whole-corpus coverage is claimed. T017 and T027 remain separate open work. No source checkout, credential, database record, crawler state, checkpoint or scheduler was changed by this evidence packaging.
