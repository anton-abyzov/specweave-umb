# Destination sign-in checklist and opt-in secret files

## Problem

A copied project is not runnable until the destination machine has the sign-ins and secret files it needs (October 19, 2026). Provider sign-ins live in the macOS Keychain (Claude Code `Claude Code-credentials`, gh) or in per-user files (Codex `~/.codex/auth.json`); copying them is unsafe (Keychain items are bound to the machine and app, OAuth refresh tokens rotate and a shared copy can get both sessions revoked) and would make the Limits by machine popover untrue. Project secret files such as `.env` are plain files the user keeps in the folder and needs to run, but nothing moves them today and nothing records where they went. Design: `~/Projects/github/studio-research-notes/project-join-handoff-pairing-2026-10-19.md` section 7.

## Scope

In: a readiness checklist for the destination machine (provider sign-ins, gh, git access to each repository's origin, tools named by the project's actions), starting each provider's own sign-in on the destination from the source app, an opt-in per-file secret step in the folder copy, a record of secret files sent per machine, scrubbing. Out: copying Keychain items or provider tokens (never), secret-manager integration (later), per-project grants (0951).

## Acceptance Criteria

- [ ] AC-01: After a copy (and on demand from Settings > Machines), the destination shows a checklist: each provider's sign-in state and account (Claude, Codex and any configured provider), gh sign-in, read access to every repository origin, and tools the project's actions call that are missing.
- [ ] AC-02: "Sign in on <machine>" starts that provider's own sign-in on the destination (its login flow or a terminal on the destination running the provider's login command); no credential value passes through the source machine, the browser storage or a thread.
- [ ] AC-03: The folder copy's secret step lists every secret-like file by path and size only, each unticked by default, with one confirmation naming the destination machine. Ticked files move over the same operation-scoped transfer and arrive with mode 0600.
- [ ] AC-04: A canary secret value placed in a sent file never appears in the database, thread transcripts, logs, operation records or error messages on either machine (automated check).
- [ ] AC-05: Each machine records which secret file paths were sent to which machine and when, never the values. Removing a machine shows that list with "Rotate these secrets if this machine is no longer trusted".
- [ ] AC-06: User docs explain why sign-ins are not copied, how to sign in on another machine, and the secret step.

## Approach

Server: `apps/server/src/fleet/folderTransfer/secrets.ts` (classification reused from 0949, opt-in selection, 0600 writes, sent-secrets ledger under the state directory), readiness probe service `apps/server/src/fleet/MachineReadiness.ts` built from existing provider status and auth probes plus `git ls-remote` per origin with the destination's own credentials. Web: `HandoffSecretsStep.tsx`, `MachineReadinessChecklist.tsx`, remove-machine warning. Scrubbing: route all transfer logs and errors through an existing redaction helper and add the canary test. Depends on 0949's transfer and dialog; work in 0949's lane after it merges or stacked on its branch.

## Decisions

### Asked
- none (the user asked to implement all recommendations, October 19, 2026)
### Defaulted
- D-01: Provider sign-ins and Keychain items are never copied; the user signs in on each machine.
- D-02: Secret files are opt-in per file, unticked by default.

## Tasks

### T-01 Readiness probe and checklist
- AC: AC-01, AC-02 | Files: apps/server/src/fleet/MachineReadiness.ts, tests, apps/web/src/components/settings/MachineReadinessChecklist.tsx | Test: vp test run apps/server/src/fleet/MachineReadiness.test.ts

### T-02 Secret step, 0600 writes, sent-secrets ledger and remove-machine warning
- AC: AC-03, AC-05 | Files: apps/server/src/fleet/folderTransfer/secrets.ts, tests, apps/web/src/components/studio/HandoffSecretsStep.tsx | Test: vp test run apps/server/src/fleet/folderTransfer/secrets.test.ts

### T-03 Canary scrubbing check and docs
- AC: AC-04, AC-06 | Files: secrets canary test, docs/user/moving-a-project.md | Test: canary test passes in the two-server verification

### T-04 PR, merge, release and installed check
- AC: all | Files: none | Test: PR Gate green; installed build shows the checklist for the M3

### T-05 Verify and close 0950
