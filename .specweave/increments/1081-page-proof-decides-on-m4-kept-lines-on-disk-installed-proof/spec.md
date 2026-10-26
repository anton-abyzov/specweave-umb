# Page proof decides on M4: kept lines on disk, installed proof

## Problem

Carried over from 0993 (closed October 26, 2026 with T-03, T-04 and T-10 moved here). M4's 1.0.89 held install (receipt `/Users/antonabyzov/.specwithcode/m4/updates/receipts/update-1.0.89-20261026T045920178774Z.json`) was verified, and its pre-restart checks took 6 s and 0.5 s. But the page proof never ran: `afterProof = {"mode": "full", "reason": "memory"}`, readiness 512.9 s. `kept_lines.start()` keeps nothing unless available memory is at least 3 × the database file + 4 GiB, which is 65.1 GB for M4's 20.4 GB database against 63.8 GB available. 0993's T-09 (PR #763, shutdown writes) is in 1.0.89 and did not recur.

## Scope

In: kept lines on disk instead of in memory (PR #795), the measured run on M4's clone, a release with it, and an installed M4 receipt where the page proof decides. Out: the pre-restart re-reads under load (1077), the migration path's widen_from read.

## Acceptance Criteria

- [ ] AC-01 (0993 AC-04): After the restart, when the page proof decides, `readiness` finishes in under 10 s on a clone of M4's database with the new service's startup writes simulated, and the receipt fields are byte-identical to the full read's on the same database.
- [ ] AC-02: The kept lines live in a scratch folder on disk, with only offsets and digest marks in memory. A disk floor folded into the `backupSpace` admission replaces the memory floor. A refusal records `availableBytes` and `floorBytes` in `afterProof`.
- [ ] AC-03 (0993 AC-08): A signed and notarized release containing PR #795 is installed on M4. The receipt shows `readiness` under 10 s with `afterProof.mode = "pages"`, or names a fallback reason other than memory. `specweave-studio --version` reports that release.

## Approach

PR #795 (`fix/page-proof-disk`, worktree `~/.specwithcode/m4/worktrees/page-proof-disk`) implements AC-02: the before read writes each kept list, as the exact bytes it hashes, to `kept-lines-<pid>-…` in the service's `updates` folder, and `merged_digest` bisects through an mmap. The release goes through the release thread (`scripts/release/release.sh`).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: 0993 closes on the owner's "close all and complete" (October 26, 2026). Its unfinished T-03, T-04 and T-10 move here, with their ACs, unchanged.
### Open
- none

## Tasks

### T-01 Keep the page proof's lines on disk (PR #795)
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/kept_lines.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/after_proof.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-after-proof.py, repositories/anton-abyzov/specweave-studio/docs/studio/updates.md | Test: cd ~/.specwithcode/m4/worktrees/page-proof-disk/scripts/studio-fleet && python3 -B test-after-proof.py && python3 -B test-update.py && python3 -B test-update-apply.py && bash run-tests.sh --out "$(mktemp -d)"

### T-02 Measured run on the clone of M4's database
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-after-proof.py | Test: cd ~/.specwithcode/m4/worktrees/page-proof-disk/scripts/studio-fleet && /usr/bin/python3 -B test-after-proof.py --measure ~/.specwithcode/m4/scratch/fast-install-profile/clone

### T-03 Release and verify on M4
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/docs/studio/updates.md | Test: specweave-studio --version && python3 -c "import json,glob;r=json.load(open(sorted(glob.glob('/Users/antonabyzov/.specwithcode/m4/updates/receipts/update-*.json'))[-1]));print(r['timings'].get('readiness'), r.get('afterProof'))"
