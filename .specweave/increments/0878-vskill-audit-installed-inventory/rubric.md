# Rubric: 0878 — vskill audit --installed

## Quality Contract

| Dimension | Bar |
|---|---|
| **Correctness** | All 17 ACs demonstrably pass; TC-001..TC-015 green; existing audit tests pass UNMODIFIED (default path byte-for-byte unchanged except the hint line). |
| **Reuse (DRY)** | Zero new pattern engines; tier1/blocklist/platform/computeSha/registry/lockfile/settings all reused; discovery constants shared with file-discovery, not copied. |
| **TDD discipline** | Every GREEN task preceded by a failing RED commit; enforcement mode honored (`testing.tddEnforcement`). |
| **Safety** | Read-only command; no symlink traversal; depth + size caps enforced; permission errors non-fatal; verified by TC-005. |
| **Offline promise** | `--offline` and network-down paths produce a complete pattern-tier report with explicit "Platform tier: skipped (offline)" — verified by TC-008/TC-011. |
| **Honest output** | Report language: findings "to review", never "malware detected" except blocklist hits; no account/upsell nag in the free flow (one dim hint line max). |
| **Coverage** | ≥90% lines on new modules (`installed-types`, `installed-inventory`, `installed-audit`, new formatter functions). |
| **Docs** | README + cli-reference updated; example invocation runs as documented (`npm run build` then `node dist/index.js audit --installed`). |
| **Sales artifact** | `--report` markdown includes hostname, date, unmanaged-count headline, per-skill sections — usable verbatim in a design-partner audit call. |
