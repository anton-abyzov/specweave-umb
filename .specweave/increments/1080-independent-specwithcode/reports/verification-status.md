# 1080 — completed, merged and published

## Delivered
- Product changes landed through private PR #800 (`8e861491a30d7e4a60d3f43b08bf67c2caece9f3`); canonical fixture PR #801 merged at `1fa61350a68e680e48b292f0f2913801a9caebe0`. Redundant PR #786 was closed only after exact final-main verification; its branch and history remain.
- Final private main: `952b28e51d8bda25b3e7d79cade3a78a25775770`. Public sanitized snapshot: `dcac53c09a08364699b9f5072282b425acafffc7`, fast-forward from release snapshot `1c40934b9d7bde54559c8b98d1eeb0a375366f9a`. No force-push or reset of published history.
- SpecWithCode 1.0.90 is published on both feeds. Actual installed acceptance passed on M4/M1/M3 against signed/notarized source `8200bcd798e2ebe1a961a4d0eedec5e03fd560a0`; the installed asar matches the signed artifact. The release tag/assets retain that cut. Final main contains later merged source changes; those are not claimed as installed runtime changes.
- SpecWeave 3.1.11 is public on npm and GitHub. Release PR #2158 merged at `6b0cf21aa31052e4d6df3e434ad2d7f109198618`; workflow 40298194474 succeeded after real registry/clean-install/headless-site checks. Actual downloaded tarball contains both updated instruction templates. Existing CLI MIT terms remain intact.

## Verified
- Same public repository ID 1414999661, fork=false, no root project license, stars 2 preserved, only Anton as contributor, old snapshot 39b0a05f retained as ancestor, independent README and exact inherited notice bytes.
- All 22 product/identity/notice/distribution files in final main match the validated 8200 candidate. Canonical fixture blob matches #801 exactly. Four versions align at 1.0.90, server UNLICENSED.
- Final source audit 4/4; packaging 8/8; notice generator 22/22. CLI full unit CI 535 files/10,447 tests passed, 78 existing skips; actual coverage 72.69/65.92/75.11/73.44. The actual CI summary was imported with provenance and validated with the published validator: 73.44% against 60%, passed=true/skipped=false.
- Landing/download and four guides passed headless live verification.
- `specweave verify 1080` passed: 3/3 ACs, 12/12 tasks, 0 skipped tasks, 3 real scoped command groups exit0. Independent final delivery review: SHIP, no findings.

## Closure and ownership
`specweave complete 1080` changed metadata to completed. Optional Jira/ADO hooks reported unconfigured credentials for zero linked user stories; no external items remain and no provider configuration was changed. The umbrella initially lacked an auto-discovered local coverage file; actual CI coverage was subsequently imported and independently validated, with provenance retained.

Mirror publication is complete and exclusive ownership was explicitly released. Other owners' branches, checkouts and sessions were preserved; canonical CLI cleanup used an identical manifest except additional protected worktree basenames. Only this lane's redundant CI was retired, with receipts retained. No assertions, deadlines or thresholds were weakened.

Reproducible acceptance workspace: `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-1080`; app checkout `repositories/anton-abyzov/specweave-studio` is pinned to final accepted main on `codex/1080-final-acceptance`. Source/root evidence is retained; no further implementation, release or watcher is assigned.

See `publication-receipt.md`, `verify.json`, `final-delivery-review.md`, `final-main-source-verification.json`, `final-main-product-match.json`, `public-verification.json`, `template-package-verification.json`, `coverage-summary.json` and `coverage-validation.json`. Canonical installed receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/blocked-attention-20261026/release-verification.json`.
