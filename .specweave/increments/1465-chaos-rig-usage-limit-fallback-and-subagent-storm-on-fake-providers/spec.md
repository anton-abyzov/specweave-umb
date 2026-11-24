# Chaos rig: usage-limit fallback and subagent storm on fake providers

## Problem

Usage-limit fallback and subagent fan-out keep shipping races: queued sends racing a pre-switch (`31bfb2911`, `611fa65a6`), a coordinator stuck after a subscription change (1301), a subagent "Working 9h 57m" (1053), a dead background workflow that left its thread waiting forever (1302), and on November 24, 2026 a 918-turn Copilot/Cursor ping-pong on m4 (fixed in 1460, PR #875). Every fix got unit tests; none got a recurring run where limits change during the run. `STUDIO_SIMULATE_USAGE_LIMIT` is read at process start and stops a turn before it starts, so today no check can flip a limit mid-run.

Source: `.specweave/reports/threads/2026-11-24-chaos-loop-methodology-and-specwithcode-16f346-d9d984.md`, candidate 1. Spec draft: ACs are finalised after the T-01 spike.

## Scope

In: [what this increment ships]. Out: [what it does not include].

## Acceptance Criteria

- [ ] AC-01: [Specific, testable criterion]
- [ ] AC-02: [Specific, testable criterion]

## Approach

[Files that change, in order; key decisions; rejected alternatives; risks.]

## Decisions

### Asked
- [D-01 question → answer (user), or "none"]
### Defaulted (change any before sw-do)
- [D-02 decision → default (reversible), or "none"]
### Open
- none

## Tasks

### T-01 [First task]
- AC: AC-01 | Files: [src/file.ts, tests/e2e/file.test.ts] | Test: [command that checks AC-01 as a user would]

### T-02 [Second task]
- AC: AC-02 | Files: [src/other.ts] | Test: [command]
