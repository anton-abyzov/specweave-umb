# 1019 Investigate Claude native artifacts

## Problem
Determine which Claude Code outputs SpecWithCode can access, without assuming parity with Claude desktop or claude.ai Artifacts.

## Scope
Research installed shipped CLI/SDK, official schemas/docs, prior REA findings and existing adapter/Library paths. Produce a bounded offline proof and integration recommendation. No product implementation, model requests, session access, live database access or app restarts.

## Acceptance Criteria
- [ ] AC-01: Identify installed CLI/SDK versions and exact native event/file persistence evidence, distinguishing observed facts from unknowns.
- [ ] AC-02: Trace current adapter and Library/preview paths and demonstrate a safe offline proof of accessible output.
- [ ] AC-03: Deliver a sourced feasibility report, independently review it and close the research increment.

## Approach
Inspect only shipped software and relevant source. Compare supported official documentation. Use REA static analysis on a bounded shipped SDK target. Save sanitized evidence and offline probe in this increment reports directory. Preserve all existing owners and dirty files.

## Decisions
### Defaulted
- Research only; no paid model calls, broad transcript imports or product edits.
### Open
- None.

## Tasks
### T-01 Establish native artifact contracts
- AC: AC-01 | Files: reports/findings.md, reports/rea-sdk.json | Test: python3 reports/validate.py

### T-02 Trace integration and prove output access
- AC: AC-02 | Files: reports/findings.md, reports/proof.json, reports/validate.py | Test: python3 reports/validate.py

### T-03 Verify and close 1019
- AC: AC-03 | Files: reports/findings.md, reports/review.md | Test: specweave verify 1019
