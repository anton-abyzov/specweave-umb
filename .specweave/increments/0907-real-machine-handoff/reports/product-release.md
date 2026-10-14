# SpecWithCode 1.0.13 release evidence

Published [v1.0.13](https://github.com/anton-abyzov/specwithcode/releases/tag/v1.0.13) from source `9cdc215c4171b441321aea65b4f6c8ba7ee2756c`, tree `bc6767d37c94eed0a3e3196e57bc127eaa6017a0`. All 11 public assets were downloaded without authentication and matched the produced bytes. Public source export: `f24e3502cff6cc08a3c599944bbf432787ee3a6f`.

The native 1.0.12 → 1.0.13 updater installed the exact published payload and relaunched `/Applications/SpecWithCode.app` as PID 51685. The held-open executable and ASAR identities match the installed files. Apple Development signature verification passed for team `NMCB2JZ7QG`; no Developer ID or notarization claim is made. The installed long-message collapse, expand and restore interactions passed.

The normal managed-service updater completed on M4 (PID 61309), M1 (62552) and M3 (41223), all on the same 1.0.13 source and runtime archive `0bd3b224f50f4da99b94c7f4dd6e80bef73808de82b73389ebf194cebac65fa9`. Fresh read-only M1/M3 captures verified all 7,482 manifest entries, process identity, preserved environment identity and exact served HTML/JavaScript bytes. These are release/runtime checks, separate from the six pending handoff routes.

The final source owner retained 466 passing tests across 15 files, eight release-version checks, six headless recovery flows and scoped six-module coverage. Independent final-source approval is retained. The existing 0907 review gate additionally has actual JSON records for 142 passing assertions across five source suites and 12 passing external assertions, covering all 12 required case labels against the exact candidate. No earlier candidate result was relabeled.

The desktop build completed successfully before its private fingerprint writer encountered a generated client symlink. The approved recovery preserved that symlink and materialized byte-equivalent output without rebuilding or changing desktop artifacts. Original build-time guards are labeled admission-derived; recovery snapshots are measured separately. Native-update auth-session changes are preserved and qualified; only the later managed-service comparison is proven heartbeat-only.

Private evidence set: `0907-113`. The successor manifest is `evidence/final0907-preparation/release-evidence-manifest.json`; the proposed aggregate index is `evidence/final0907-preparation/product-evidence-index.proposed.json` (SHA-256 `6ee2ae075df34244fb7bd17e20807ccc6c83d77e342837a3465c0d18b7d99b68`). The historical 1.0.11 index and failed route records remain unchanged.

The release owner installed the successor as `product-evidence-index.json` at that evidence root and ran the unchanged T-07 command:

```sh
python3 scripts/fleet/verify-handoff-evidence.py --phase product-release --evidence "$EVIDENCE_ROOT"
```

The unchanged product-code, product-review and product-release gates all passed. The retained aggregate receipt is `evidence/final0907-preparation/aggregate-gates/receipt.json` (SHA-256 `2e6a15c70c0188560a403eb395f2fdb9125614c5d6b5c534536eabc843664688`). T-08 remains zero of six; no native route or increment closure is claimed here.

## Pending 1.0.14 correction

The context-first correction is committed and pushed as `8ccc7de5552f5108af8fcdca40e8db26ef105999`, tree `5d501237bfd948544232d8290d3ae631ed32d402`, in private source PR 172. It remains a draft. The source passed 75 focused tests and independent review; T-16 separately passed its required 64-test closure command. The inert build driver passed 99 independent guard tests. The integrated evidence verifier passed 367 tests after fresh review of exact prompt binding and preservation intervals. Cleanup V7 is independently reviewed but not activated.

No 1.0.14 artifact has been built or published. The release disk has 5.9 GiB free after reclaiming eight verified expanded copies of retained historical archives; the reviewed builder requires 8 GiB. All source, archives, receipts and evidence remain preserved, including the two stage copies excluded by a permission mismatch. The user has been asked for additional space or another disk. T-17 and T-08 remain open; actual 1.0.14 installed readbacks and all six new native routes are required.

Private evidence set: `0907-114`. The approved build binding is `evidence/build-binding-8ccc-1.json` (SHA-256 `ec0ab4ef319e5027cc3e86532c38c446d68d311975f28017ef13346cb056b1de`). The combined prompt/preservation independent review has SHA-256 `e0b00bc6208c3c891e4024ce5e87b99e7ff740b3dcd071ef70f3b02fa03edf8e`. The V7 cleanup review has SHA-256 `1c121c3d21d9798d7076bcf300c969d43621cda9f2a97e682c3bb61d91a5edcf`. These are preparation and test results, not route acceptance.
