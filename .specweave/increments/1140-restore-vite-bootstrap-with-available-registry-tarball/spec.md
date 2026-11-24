# 1140: Restore Vite bootstrap with available registry tarball

## Problem
Hosted Linux and Windows checks fail before product tests. Pinned Vite+1.0.0 bootstraps an unlocked pnpm10.33.0 wrapper; estree-walker3.0.3 resolves @types/estree1.0.10 whose official metadata exists but tarball returns404. The repository lock already uses available1.0.9.

## Scope
Bootstrap-only dependency repair, all existing setup-vp workflow steps, regressions and real isolated bootstrap proof. No toolchain version bump, product dependency/lock edit, live account mutation or active owner takeover.

## Acceptance Criteria
- [ ] AC-01: Exact pinned wrapper installs using available existing1.0.9 while product installs and unrelated package requirements remain untouched.
- [ ] AC-02: Existing setup-vp steps retain action versions/inputs and receive the bounded hook; independent source review and hosted checks pass.
- [ ] AC-03: Reviewed repair is merged, dependent branches receive normal main integration, and temporary checkout is removed after safe checks.

## Approach
Global pnpm readPackage hook only activates in the exact vp-global1.0.0 wrapper with vite-plus1.0.0 dependency. Pin only estree-walker3.0.3's @types/estree dependency to1.0.9. Step-scoped environment passes the hook during setup; product root is a no-op. Preserve all action versions, product manifests and lock bytes. Node regression exercises wrapper and non-wrapper contexts; reproduce real pinned pnpm install in scratch. Parent coordinates independent review and merge.

## Decisions
- Root explicitly assigned this bounded shared CI repair after user requested completion. An isolated temporary lane avoids tying the repair to UI acceptance.

## Tasks
### T-01 Repair and verify bootstrap dependency resolution
- AC: AC-01 | Files: scripts/studio-toolchain/bootstrap-pnpmfile.cjs, scripts/studio-toolchain/bootstrap-pnpmfile.test.mjs, .github/workflows/*.yml | Test: node --test scripts/studio-toolchain/bootstrap-pnpmfile.test.mjs scripts/studio-toolchain/preservation-audit.test.mjs

### T-02 Establish reviewed hosted readiness
- AC: AC-02 | Files: none | Test: independent exact-head review and applicable hosted CI

### T-03 Verify and close 1140
- AC: AC-03 | Files: none | Test: specweave verify 1140, merge evidence, safe worktree cleanup, specweave complete 1140

### T-04 Preserve workflow structure required by existing release regressions
- AC: AC-02 | Files: .github/workflows/*.yml | Test: node node_modules/vite-plus/bin/vp test run scripts/release-windows-linux.test.ts --maxWorkers=1 && node --test scripts/studio-toolchain/bootstrap-pnpmfile.test.mjs

Closure evidence (October 29): Parent authorized normal branch integration of the reviewed bootstrap while PR998 validated, instead of making every dependent lane wait for the main merge. All seven dependent current PR heads (#940, #945, #948, #959, #961, #991, #994) have a9e47a929310df6385814ae28cbc15c9143ff3f3 as an ancestor. PR998 then passed every applicable hosted check and merged as 2ff660b088fa12ed1c54c45db41ca05213c6ace6. Its exact clean checkout was retired after fresh bindings/owners/schedules/process/dependency checks, preserving local metadata and branch. Receipts: ~/.specwithcode/m4/evidence/worktree-audit-20261028-late/attention-usage/bootstrap-dependent-integration.json, pr998-merged.json, bootstrap-removal.json, review-bootstrap.md. This completes the shared bootstrap scope; unrelated feature delivery gates remain with their increments.
