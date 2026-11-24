# 0906 Verified project copies across M4, M1 and M3

## Problem
Cross-machine handoff transfers context and pushed branch references, but does not create code checkouts. Missing or stale umbrella repositories prevent equivalent coordinator and worker execution on another Mac. M4 and M1 contain concurrent owner-held work that cannot be flattened into a clean mirror.

## Scope
In: inventory published source for EasyChamp, JobWeave and SpecWeave; provision independent clean checkouts on M1 and M3; preserve existing work and credentials; verify versions, source identity and project execution; coordinate the Mac release with its existing owner.
Out: copying live databases, credential directories, uncommitted owner work, build caches or node_modules; stopping unrelated processes; taking over active increments; production application deployments.

## Acceptance Criteria
- [ ] AC-01: A manifest identifies the published branch and exact commit for each umbrella and canonical nested repository, plus source and ownership blockers.
- [ ] AC-02: M1 and M3 have independent clean copies matching the manifest; existing dirty or diverged destinations are preserved and reported.
- [ ] AC-03: Destination project folders are registered or discoverable, and bounded coordinator and worker execution is verified on each Mac with exact source/version receipts.
- [ ] AC-04: One coordinated SpecWithCode Mac release is published and installed where safe, with version/source readback and outstanding gates explicit.

## Approach
Use authenticated Git remote state as source truth. Freeze commits after completed work merges. Prefer new clean checkouts at normal home-relative paths; never network-share a live worktree or copy session databases. Existing owner-held destinations get a separate clean path. Keep private manifests, network coordinates and runtime evidence outside this public umbrella. Use pinned SSH identities and existing fleet keys. Build dependencies per host only for a concrete smoke test. SpecWithCode is Electron; use its existing release workflow. Release owners retain install control until a safe window is agreed. Check provider identity and availability per host before bounded native turns; do not alter billing settings.

## Tasks

### T-01 Inventory source and provision clean project copies
- AC: AC-01, AC-02 | Files: .specweave/increments/0906-mac-project-sync/spec.md, scripts/fleet-project-sync.py, README.md, AGENTS.md, CHANGELOG.md | Test: python3 scripts/fleet-project-sync.py --self-test

### T-02 Verify cross-machine coordinator and worker execution
- AC: AC-03 | Files: .specweave/increments/0906-mac-project-sync/runtime-verification.md | Test: python3 scripts/fleet-project-sync.py --verify-receipt /Users/antonabyzov/.local/share/specweave/fleet/project-sync-20261013/receipt.json

### T-03 Coordinate release and record final installed source
- AC: AC-04 | Files: .specweave/increments/0906-mac-project-sync/release-verification.md | Test: python3 scripts/fleet-project-sync.py --verify-release /Users/antonabyzov/.local/share/specweave/fleet/project-sync-20261013/release.json
