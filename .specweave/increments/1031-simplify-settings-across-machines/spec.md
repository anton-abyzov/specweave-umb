# Simplify settings across machines

## Problem

Anton (October 23, 2026): "Maybe there are too many settings. Maybe we could simplify something, remove duplicates, or consolidate something. Think about multiple environments and multiple machines."

SpecWithCode's Settings dialog has grown section by section, one increment at a time (about 280 files under `apps/web/src/components/settings` at origin/main `0f6abb0fc`). Model and limit rules alone are edited in several places (Usage limits, Fallback order, Also served by, Model lanes, Task routing, picker favorites), and each setting lives in a different store with a different reach: one device, one machine's server, every paired machine, or one project. The UI rarely says which. The prior "Cursor support and settings design" worker (1009) never reached the settings redesign: it was blocked on folder access, shipped PR #634 (1023) instead, and left 1009 planned.

## Scope

In: a read-only, evidence-backed review of the current settings concept (global Settings, Project settings, per-thread controls, data model, cross-machine behavior); a list of duplicates and overlaps; a concrete simpler target design (scope model, navigation, consolidation and removal candidates, migration rules); a designed review page with before/after scope and layout examples; staged implementation increments with owners.

Out: product code changes, removing or renaming any setting key, changing saved settings on any machine, releases or restarts. Implementation starts only after Anton picks the decisions the review page lists.

## Acceptance Criteria

- [ ] AC-01: An inventory of every Settings section, Project settings section and per-thread control at origin/main `0f6abb0fc`, with label, stored key, storage class (device, machine, fleet-synced, project, account/secret, OS) and file:line, is saved in `reports/inventory.md`.
- [ ] AC-02: A duplicate and scope report names every concept editable in more than one place, says whether those places write the same key, and maps each storage class to its cross-machine behavior (synced, per machine, per device), with file:line evidence, in `reports/scope-matrix.md`.
- [ ] AC-03: A proposal in `reports/proposal.md` gives a target navigation, one scope model for devices, machines, projects and threads, the consolidation and removal list with migration rules that keep existing keys readable across version skew, and staged follow-up increments that name current owners (1009, 1025, 1029, 1003, 1030) and avoid their files until they land.
- [ ] AC-04: A self-contained review page `reports/settings-review.html` shows the recommendation, before/after navigation and scope examples, and the decisions Anton must make; headless light, dark and 390px screenshots of it are saved under `reports/shots/`.
- [ ] AC-05: No product file, saved setting or live database was changed: `git status` in the app checkout is clean and the report says so.

## Approach

Research from a read-only `git archive` snapshot of the app's origin/main at `~/.specwithcode/m4/scratch/settings-consolidation-20261023/src-main`, never the stale detached checkout. Four parallel read-only inventories (global dialog, data model and scopes, project settings, duplicates), then cross-checks of the claims the proposal depends on. Prior decisions are constraints: provider instances stay per machine (provider-config-per-machine), the personal assistant is machine-private (aide-machine-private-voice), favorites stay separate from fallback order (favorites-vs-fallback-order), basic use survives version skew (version-skew-policy), tracker sync stays secondary.

Rejected: redesigning the layout first. Layout cannot fix settings whose reach is unclear; the scope model comes first and the layout follows it.

## Decisions

### Asked
- none yet; the review page lists the decisions for Anton.
### Defaulted (change any before sw-do)
- D-01: Research and design only in this increment; implementation lands as follow-up increments after Anton's answers.
- D-02: The thread runs Claude Code Opus 5.5 with Ultra Code as Anton asked (verified with studio_thread_configuration).
### Open
- none

## Tasks

### T-01 Inventory current settings
- AC: AC-01 | Files: .specweave/increments/1031-simplify-settings-across-machines/reports/inventory.md | Test: test -s .specweave/increments/1031-simplify-settings-across-machines/reports/inventory.md

### T-02 Duplicates and cross-machine scope matrix
- AC: AC-02 | Files: .specweave/increments/1031-simplify-settings-across-machines/reports/scope-matrix.md | Test: test -s .specweave/increments/1031-simplify-settings-across-machines/reports/scope-matrix.md

### T-03 Target design and staged plan
- AC: AC-03 | Files: .specweave/increments/1031-simplify-settings-across-machines/reports/proposal.md | Test: test -s .specweave/increments/1031-simplify-settings-across-machines/reports/proposal.md

### T-04 Review page with before/after examples
- AC: AC-04, AC-05 | Files: .specweave/increments/1031-simplify-settings-across-machines/reports/settings-review.html, .specweave/increments/1031-simplify-settings-across-machines/reports/shots | Test: ls .specweave/increments/1031-simplify-settings-across-machines/reports/shots/*.png && git -C repositories/anton-abyzov/specweave-studio status --porcelain | wc -l

### T-05 Verify and close 1031
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1031-simplify-settings-across-machines/spec.md | Test: specweave verify 1031-simplify-settings-across-machines
