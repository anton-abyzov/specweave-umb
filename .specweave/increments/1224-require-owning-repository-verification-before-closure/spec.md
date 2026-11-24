# Require owning repository verification before closure

## Problem
Umbrella verification can report success without running the checks for the product an increment changes. Completion can also permit open tasks and missing review.

## Scope
Enable the published strict closure policy in this umbrella. Route named nested repositories to their existing verification commands. Preserve coverage thresholds and current fleet and release checks.

## Acceptance Criteria
- [ ] AC-01: A product task that names the canonical or legacy SpecWithCode repository runs the product gate in that repository. A failing owner gate, open task, or missing fresh review prevents completion.
- [ ] AC-02: Existing fleet and release checks still run from the umbrella. The rollout documents the CLI version and how existing owners add explicit repository paths.

## Approach
Map each maintained repository to its actual test entry point. Keep project-wide fleet and release checks as root commands. Require new or updated product tasks to name repository-relative paths from the umbrella root. Let existing owners migrate their active tasks during normal work. Activate after npm publishes the strict CLI.

## Tasks

### T-01 Activate and verify the strict policy
- AC: AC-01, AC-02 | Files: .specweave/config.json, AGENTS.md, tests/strict-owner-verification.sh | Test: bash tests/strict-owner-verification.sh
