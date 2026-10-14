# SpecWithCode 1.0.13 release evidence

Published [v1.0.13](https://github.com/anton-abyzov/specwithcode/releases/tag/v1.0.13) from source `9cdc215c4171b441321aea65b4f6c8ba7ee2756c`, tree `bc6767d37c94eed0a3e3196e57bc127eaa6017a0`. All 11 public assets were downloaded without authentication and matched the produced bytes. Public source export: `f24e3502cff6cc08a3c599944bbf432787ee3a6f`.

The native 1.0.12 → 1.0.13 updater installed the exact published payload and relaunched `/Applications/SpecWithCode.app` as PID 51685. The held-open executable and ASAR identities match the installed files. Apple Development signature verification passed for team `NMCB2JZ7QG`; no Developer ID or notarization claim is made. The installed long-message collapse, expand and restore interactions passed.

The normal managed-service updater completed on M4 (PID 61309), M1 (62552) and M3 (41223), all on the same 1.0.13 source and runtime archive `0bd3b224f50f4da99b94c7f4dd6e80bef73808de82b73389ebf194cebac65fa9`. Fresh read-only M1/M3 captures verified all 7,482 manifest entries, process identity, preserved environment identity and exact served HTML/JavaScript bytes. These are release/runtime checks, separate from the six pending handoff routes.

The final source owner retained 466 passing tests across 15 files, eight release-version checks, six headless recovery flows and scoped six-module coverage. Independent final-source approval is retained. The existing 0907 review gate additionally has actual JSON records for 142 passing assertions across five source suites and 12 passing external assertions, covering all 12 required case labels against the exact candidate. No earlier candidate result was relabeled.

The desktop build completed successfully before its private fingerprint writer encountered a generated client symlink. The approved recovery preserved that symlink and materialized byte-equivalent output without rebuilding or changing desktop artifacts. Original build-time guards are labeled admission-derived; recovery snapshots are measured separately. Native-update auth-session changes are preserved and qualified; only the later managed-service comparison is proven heartbeat-only.

Private evidence root: `/Volumes/SanDisk APFS/SpecWithCodeReleases/0907-113`. The successor manifest is `evidence/final0907-preparation/release-evidence-manifest.json`; the proposed aggregate index is `evidence/final0907-preparation/product-evidence-index.proposed.json` (SHA-256 `6ee2ae075df34244fb7bd17e20807ccc6c83d77e342837a3465c0d18b7d99b68`). The historical 1.0.11 index and failed route records remain unchanged.

The release owner installed the successor as `product-evidence-index.json` at that evidence root and ran the unchanged T-07 command:

```sh
python3 scripts/fleet/verify-handoff-evidence.py --phase product-release --evidence '/Volumes/SanDisk APFS/SpecWithCodeReleases/0907-113'
```

The unchanged product-code, product-review and product-release gates all passed. The retained aggregate receipt is `evidence/final0907-preparation/aggregate-gates/receipt.json` (SHA-256 `2e6a15c70c0188560a403eb395f2fdb9125614c5d6b5c534536eabc843664688`). T-08 remains zero of six; no native route or increment closure is claimed here.
