# Real cross-machine handoff and local development readiness

## Problem

The earlier fleet checks proved independent destination execution, not continuation of an actual M4 assignment. M4 still contains active, unpublished work; M1 has preserved original checkouts and separate fleet copies. Git clones omit ignored development configuration. Shipped SpecWithCode 1.0.9 transfers a clipped transcript after usage-limit failure, without synchronizing Git or moving native workers.

## Scope

In: audit source ownership and destination paths; prepare explicit branch and commit checkpoints for EasyChamp, JobWeave and SpecWeave; test actual source-context continuation on both destination machines; provision bounded local development configuration and verify what can run. Out: taking over active work, sweeping unrelated changes into Git, copying account/session databases, production data mutations, or fabricating usage-limit UI state.

## Acceptance Criteria

- [ ] AC-01: A current audit distinguishes published code, local changes, original M1 folders, independent clone properties, and ownership; the normal-path reuse decision preserves existing work.
- [ ] AC-02: All six project/destination routes continue an actual M4 checkpoint, with exact root and nested source pins, carried context and next step, fresh destination workers and observed coordinator completion; the receipt labels manual continuation separately from the usage-limit UI.
- [ ] AC-03: Required ignored configuration is mapped to the proper application folders, existing secrets are preserved, transferred/generated configuration stays private, and per-host local runtime checks or concrete unmet dependencies are recorded.
- [ ] AC-04: Reproducible procedures and evidence boundaries are documented, all owned source changes are reviewed and pushed, and no foreign owner work or active assignment is overwritten.

## Approach

Use the existing owned umbrella worktree on codex/real-machine-handoff. Keep private runtime receipts and configuration hashes under ~/.local/share/specweave/fleet/handoff-proof-20261013. Use clean owned source checkpoints and explicit feature branches; a branch name alone is insufficient for nested repositories. Repair the provisioner's single-branch fetch configuration so newly fetched feature branches can be tracked normally, preserving origins and other settings. Preserve the shared specweave-handoff pointer used by other owners: transport this bounded proof on explicit pushed branches with a no-push CLI handoff document, then read that exact checkpoint on the destination. Native destination workers start fresh from the source checkpoint; they do not inherit a running process. Do not claim general UI handoff support: 1.0.9 only exposes it after a real usage-limit failure. Resolve paths by exact environment/project identity rather than whichever duplicate repository happens to be listed first. Secrets travel only over SSH into ignored private files, never through Git or model prompts. Local service tests must use isolated local data targets.

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
