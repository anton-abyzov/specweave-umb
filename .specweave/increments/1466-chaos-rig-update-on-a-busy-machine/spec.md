# Chaos rig: update on a busy machine

## Problem

Updates on busy machines have failed repeatedly in the last two months: hours waiting for a quiet service (1085), a 261 s re-read rollback (1077), a 499 s install with 47k auth rows (1160), plus 1116, 1134 and the two unowned held-install gaps in the open product gaps list. Each fix got unit tests, none a recurring run.

`scripts/studio-fleet/rehearse_update.py` rehearses each release on a clone at release time, but on an idle clone: no running turns, no writes during the hold, no restart, and it replaces `update_agent.py`'s process and quiet checks with a sandbox. The real `quiet_then_install` step is never exercised against busy work. The mandatory 1.1 upgrade (decision Retire 1.0) is the launch-day rollout and must not stall or lose a turn.

Source: `.specweave/reports/threads/2026-11-24-chaos-loop-methodology-and-specwithcode-16f346-d9d984.md`, candidate 2.

## Scope

In: a rig that starts a scratch-home server (`--base-dir`) with fake-agent threads mid-turn, drives the real `update_agent.py` `quiet_then_install` against it, injects faults during the hold, and checks invariants from the scratch home's state and the agent's receipt. Seeded random fault timing, seed recorded per run. Reuses the fake-provider control file built in 1465.

Out: real subscriptions or the live M4/M5 homes; changing the update agent's behaviour (failures become follow-up increments); Windows and Linux updaters.

## Acceptance Criteria

- [ ] AC-01: The rig runs the real `update_agent.py` `quiet_then_install` against a scratch home with 20 fake-agent threads mid-turn, and the receipt records the seed, the fault schedule and the outcome.
- [ ] AC-02: Faults injected during the hold: writes and `.DS_Store` churn in the home, a server or database restart mid-hold, a seeded 47k-row auth table, and a release that adds a UNIQUE table.
- [ ] AC-03: Invariant checker: the install lands or rolls back by itself within a bounded time; no running turn is lost (every turn that was running finishes, or is resumed or marked interrupted with a reason); the receipt names the cause of any hold or rollback.
- [ ] AC-04: Re-running with the same seed reproduces the same fault schedule and verdict.
- [ ] AC-05: The rig runs on a schedule (nightly or per release candidate) as report-only, and a failing seed is reported with its replay command.

## Approach

Build on 1465's fake-provider control file and invariant-checker pattern. A Python driver next to `rehearse_update.py` builds the scratch home and seeds data, starts the server with fake providers, launches turns, then calls `update_agent.py` with its real quiet checks pointed at the scratch home and a mock update server (`scripts/mock-update-server.ts`). A fault scheduler (seeded) applies the AC-02 faults. The checker reads the scratch state through the server's own query path, never by opening a live database.

Risk: `update_agent.py` assumes launchd paths; the rig may need a narrow, test-only path override that already exists or is added as a parameter, not a behaviour change.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Report-only first; no CI gate until three clean nightly runs → default (reversible).
- D-02 Runs on m4 (has PyYAML and pnpm) → default.
### Open
- none

## Tasks

### T-01 Scratch home with busy fake work and seeded data
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/update-rig/home.py | Test: python3 repositories/anton-abyzov/specwithcode/scripts/studio-chaos/update-rig/home.py --self-test

### T-02 Drive the real quiet_then_install with a seeded fault scheduler
- AC: AC-01, AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/update-rig/run.py | Test: python3 repositories/anton-abyzov/specwithcode/scripts/studio-chaos/update-rig/run.py --seed 1 --scenario busy-hold

### T-03 Invariant checker and receipt
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/update-rig/check.py | Test: python3 repositories/anton-abyzov/specwithcode/scripts/studio-chaos/update-rig/check.py --self-test

### T-04 Scheduled report-only run
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/.github/workflows/chaos-nightly.yml | Test: run the workflow once and confirm a receipt artifact with seed and verdict
