# Stop product releases when required checks cannot be read

## Problem

A GitHub lookup failure is treated as an empty set of required checks, so the release can proceed without evidence that main is green.

## Scope

Product release main gate and mocked command regression.

## Acceptance Criteria

- [ ] AC-01: A GitHub API failure during either lookup stops the release. Successful direct push, release PR, and genuinely empty required checks retain their existing behavior.

## Approach

Keep GitHub CLI required-check semantics. Normalize only its explicit empty-check response and propagate other failures.

## Tasks

### T-01 Fail closed on GitHub lookup errors
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/release/release.sh, repositories/anton-abyzov/specwithcode-dev/scripts/release/release-self-test.sh | Test: bash scripts/release/release-self-test.sh
