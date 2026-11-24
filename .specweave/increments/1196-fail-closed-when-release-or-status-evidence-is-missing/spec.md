# Fail closed when release or status evidence is missing

## Problem
A fleet endpoint can be marked healthy on HTTP errors, optimized Python disables legacy fleet receipt assertions, and the public status page claims health without worker or history evidence.

## Scope
Umbrella release and fleet verification plus SpecWeave Status probes and display.

## Acceptance Criteria
- [ ] AC-01: Release verification rejects an error response carrying the expected version.
- [ ] AC-02: Fleet verification refuses to run with assertions disabled.
- [ ] AC-03: Crawl workers require an explicitly running scheduler and unknown checks cannot produce all-healthy messaging.

## Approach
Fail on unsuccessful fleet HTTP requests. Reject optimized mode before assertion-based receipt validation. Preserve outage precedence while presenting unobserved or stale status honestly.

## Tasks

### T-01 Release verification
- AC: AC-01 | Files: scripts/release/release.sh, scripts/release/release-self-test.sh | Test: bash scripts/release/release-self-test.sh

### T-02 Fleet verification
- AC: AC-02 | Files: scripts/fleet/verify-handoff-evidence.py | Test: python3 -B -m unittest discover -s tests -p test_handoff_evidence.py

### T-03 Status evidence
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-status/scripts/collect.mjs, repositories/anton-abyzov/specweave-status/public/model.mjs, repositories/anton-abyzov/specweave-status/public/app.mjs, repositories/anton-abyzov/specweave-status/test/model.test.mjs | Test: npm --prefix repositories/anton-abyzov/specweave-status test
