# Real cross-machine handoff and local development readiness

## Problem

The earlier fleet checks proved independent destination execution, not continuation of an actual M4 assignment. M4 still contains active, unpublished work; M1 has preserved original checkouts and separate fleet copies. Git clones omit ignored development configuration. Shipped SpecWithCode 1.0.9 transfers a clipped transcript after usage-limit failure, without synchronizing Git or moving native workers.

## Scope

In: audit source ownership and destination paths; prepare explicit branch and commit checkpoints for EasyChamp, JobWeave and SpecWeave; test actual source-context continuation on both destination machines; provision bounded local development configuration and verify what can run; implement and release an ordinary product handoff with explicit destination selection and guarded source transfer, then repeat all six routes through that product flow. Out: taking over active work, sweeping unrelated changes into Git, copying account/session databases, production data mutations, or fabricating usage-limit UI state.

## Acceptance Criteria

- [ ] AC-01: A current audit distinguishes published code, local changes, original M1 folders, independent clone properties, and ownership; the normal-path reuse decision preserves existing work.
- [ ] AC-02: All six project/destination routes continue an actual M4 checkpoint, with exact root and nested source pins, carried context and next step, fresh destination workers and observed coordinator completion; the receipt labels manual continuation separately from the usage-limit UI.
- [ ] AC-03: Required ignored configuration is mapped to the proper application folders, existing secrets are preserved, transferred/generated configuration stays private, and per-host local runtime checks or concrete unmet dependencies are recorded.
- [ ] AC-04: Reproducible procedures and evidence boundaries are documented, all owned source changes are reviewed and pushed, and no foreign owner work or active assignment is overwritten.
- [ ] AC-05: An ordinary project coordinator offers explicit destination selection without requiring a usage-limit failure. Product preflight identifies the matching repository and exact root/nested commits, preserves dirty or diverged work, carries pending work and decisions, and performs code transfer only with explicit selection. Unsupported or blocked transfers show a concrete reason; no process-migration claim is made.
- [ ] AC-06: A fresh reviewer verifies the product change, including wrong-repository, dirty/diverged destination, missing source object, nested commit mismatch, active ownership and denied-transfer cases; applicable source and UI tests pass at the candidate commit.
- [ ] AC-07: The release owner publishes one verified Mac candidate, installs/readbacks the intended runtime on the participating machines, and records exact version/source/artifact evidence without competing builds or installs.
- [ ] AC-08: All six project/destination routes repeat the continuation through the candidate's ordinary app-owned handoff flow, with exact code/context, fresh workers and observed coordinator completion. The evidence distinguishes product-managed synchronization from external preparation and records the visible destination-selection check.

## Approach

Use the existing owned umbrella worktree on codex/real-machine-handoff. Keep private runtime receipts and configuration hashes under ~/.local/share/specweave/fleet/handoff-proof-20261013. Use clean owned source checkpoints and explicit feature branches; a branch name alone is insufficient for nested repositories. Repair the provisioner's single-branch fetch configuration so newly fetched feature branches can be tracked normally, preserving origins and other settings. Preserve the shared specweave-handoff pointer used by other owners: transport this bounded proof on explicit pushed branches with a no-push CLI handoff document, then read that exact checkpoint on the destination. Native destination workers start fresh from the source checkpoint; they do not inherit a running process. Do not claim general UI handoff support: 1.0.9 only exposes it after a real usage-limit failure. Resolve paths by exact environment/project identity rather than whichever duplicate repository happens to be listed first. Secrets travel only over SSH into ignored private files, never through Git or model prompts. Local service tests must use isolated local data targets.

Ownership: this chat owns the umbrella spec, ledger, provisioning/evidence code and final six-route acceptance. The existing release chat `01a133f7-afb4-7771-8e87-55cfabfd6858` owns Studio product implementation coordination, its fresh source review, build, release and installation. The umbrella owner records their exact task evidence without concurrent edits to this ledger. Completed manual proof remains valid but does not satisfy AC-05 through AC-08. Keep this increment open until those product gates pass; obtain the repository-required manual acceptance for the new UI against a concrete tested candidate.

Pre-UI finding on October 13: candidate d7edbf9 passed its recorded source checks, but destination settings inspection found that ProjectCoordinatorService launches with the global permission mode instead of the resolved project mode. T-05/T-06 remain historical test receipts because the CLI treats done tasks as terminal; T-09 tracks the correction and fresh review. The initial candidate is not accepted for release. Keep global settings unchanged, set approval-required only on the six owned target projects through the supported settings API, then repeat source/build/runtime gates against the corrected candidate before starting destination workers.

Live picker finding on October 13: candidate a26cf5a transferred one SpecWeave checkpoint to M3, but the bounded observer stopped its coordinator before any worker or code edit. This is a failed continuation attempt, even though the transfer and visible selection were observed. Subsequent destination refresh exposed a product parser bug: Git's valid `(fetch) [blob:none]` output for the SpecWeave partial clones was rejected, removing verified identities and hiding destinations. T-10 fixes that parser with a real partial-clone regression and derives matching cross-host destinations independently of sidebar grouping. Preserve clone/promisor configuration, retain the failed attempt, and repeat all six routes on the newly reviewed candidate. T-09 remains its historical successful source-test receipt; a26cf5a is not accepted for release.

## Path decision

Preserve the original M1 EasyChamp directory: it contains local work and points to a different upstream. Keep the prepared fleet checkout registered until a separate archive-and-promote migration preserves the old linked worktree and changes the registration together.

## Tasks

### T-01 Record source, ownership, path and handoff architecture audit
- AC: AC-01 | Files: docs/operations/real-machine-handoff.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase audit

### T-02 Exercise actual M4 checkpoints on six destination routes
- AC: AC-02 | Files: scripts/fleet-project-sync.py, scripts/fleet/verify-handoff-evidence.py, tests/test_handoff_evidence.py, docs/operations/real-machine-handoff.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase handoff

### T-03 Provision and verify local development configuration
- AC: AC-03 | Files: docs/operations/real-machine-handoff.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase environment

### T-04 Review and publish the continuation procedure
- AC: AC-04 | Files: README.md, CHANGELOG.md, AGENTS.md, docs/operations/real-machine-handoff.md, .specweave/increments/0907-real-machine-handoff/spec.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase all

### T-05 Implement ordinary product handoff and guarded source transfer
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src, repositories/anton-abyzov/specweave-studio/apps/server/src, repositories/anton-abyzov/specweave-studio/packages/contracts/src | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase product-code

### T-06 Independently review product source and failure paths
- AC: AC-06 | Files: .specweave/increments/0907-real-machine-handoff/reports/product-review.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase product-review

### T-07 Publish and verify one Mac release
- AC: AC-07 | Files: repositories/anton-abyzov/specweave-studio/package.json, repositories/anton-abyzov/specweave-studio/apps/desktop, .specweave/increments/0907-real-machine-handoff/reports/product-release.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase product-release

### T-08 Verify six ordinary product handoff routes and destination selection
- AC: AC-08 | Files: scripts/fleet/verify-handoff-evidence.py, scripts/fleet/product_handoff_evidence.py, scripts/fleet/product_native_evidence.mjs, scripts/fleet/replay_product_native.mjs, tests/test_handoff_evidence.py, tests/test_product_handoff_evidence.py, tests/fixtures/product_native_source.json, tests/fixtures/product_native_destination.json, docs/operations/real-machine-handoff.md, .specweave/increments/0907-real-machine-handoff/reports/product-acceptance.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase product-handoff

### T-09 Honor scoped coordinator permission mode and revalidate the corrected candidate
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectCoordinatorService.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/ProjectCoordinatorService.test.ts, scripts/fleet/product_handoff_evidence.py, tests/test_product_handoff_evidence.py, tests/test_product_build_handoff_evidence.py, .specweave/increments/0907-real-machine-handoff/reports/product-review.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase product-code && python3 scripts/fleet/verify-handoff-evidence.py --phase product-review

### T-10 Recognize partial clones and discover handoff destinations independently of sidebar grouping
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/project/RepositoryIdentityResolver.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/RepositoryIdentityResolver.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src, scripts/fleet/product_handoff_evidence.py, scripts/fleet/product_native_evidence.mjs, tests/test_product_handoff_evidence.py, tests/test_product_build_handoff_evidence.py, tests/test_product_native_handoff_evidence.py, tests/test_product_review_handoff_evidence.py, .specweave/increments/0907-real-machine-handoff/reports/product-review.md | Test: python3 scripts/fleet/verify-handoff-evidence.py --phase product-code && python3 scripts/fleet/verify-handoff-evidence.py --phase product-review
