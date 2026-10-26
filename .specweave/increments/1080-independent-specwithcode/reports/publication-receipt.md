# Publication receipt — increment 1080

Completed and independently reviewed on 26 October 2026.

SpecWithCode [public source](https://github.com/anton-abyzov/specwithcode/commit/dcac53c09a08364699b9f5072282b425acafffc7) is the sanitized snapshot of private main `952b28e51d8bda25b3e7d79cade3a78a25775770`. Product changes landed through release PR #800; the canonical fixture repair landed through #801. Redundant PR #786 was closed after exact final-main equivalence checks, with its branch and history retained.

[SpecWithCode 1.0.90](https://github.com/anton-abyzov/specwithcode/releases/tag/v1.0.90) is published and installed acceptance passed on M4, M1 and M3. Its signed release cut remains `8200bcd798e2ebe1a961a4d0eedec5e03fd560a0`; public release tag/assets remain at the original `1c40934b` snapshot. Final main contains additional merged source changes; those are not represented as installed runtime changes.

[SpecWeave 3.1.11](https://www.npmjs.com/package/specweave/v/3.1.11) is published. The actual registry tarball contains the AGENTS and CLAUDE identity/licensing guidance. Its existing CLI MIT license remains intact.

Public readback confirms the same repository ID, preserved history and two stars, only Anton as contributor, no root project license, independent README, and the exact inherited MIT notice bytes. The notice grants and previously distributed grants were preserved. Landing, download and four guide pages passed headless live verification.

Validation: acceptance criteria 3/3, tasks 12/12, zero skipped increment tasks; `specweave verify` PASS. Source-terms audit 4/4, packaging 8/8 and notice generator 22/22 passed on final main. CLI full unit CI passed 535 files and 10,447 tests, with 78 existing skips. Actual CI coverage was imported with provenance and validated using the published validator: 73.44% lines against the configured 60% target, not skipped. Both implementation and fresh delivery reviews are SHIP.

The release candidate passed actual canonical suites, type checking, signing/notarization and installed acceptance. PR #800's release-branch CI skips were not counted as test passes. No assertions, deadlines or configured thresholds were weakened.

Increment status was changed to completed by `specweave complete`. Optional Jira/ADO closure hooks reported missing credentials for zero linked user stories; no external items remain to close and no provider configuration was changed. The umbrella auto-discovery initially lacked a local coverage file; the actual CI coverage was subsequently imported and independently validated, with its provenance retained.

Other owners' checkouts and sessions were preserved. Exclusive mirror ownership was released after verified publication. No force-push, reset of published history, tag replacement or asset replacement was used by this lane.

[Canonical release and installed-acceptance receipt](/Users/antonabyzov/.specwithcode/m4/evidence/blocked-attention-20261026/release-verification.json).
