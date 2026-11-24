# Keep fleet database continuity reads bounded when scratch storage fails

## Problem

Failed spill storage can trigger an unbounded table read or a retry that bypasses the memory budget.

## Scope

Keep fleet database continuity reads bounded when scratch storage fails and the associated regression tests.

## Acceptance Criteria

- [ ] AC-01: A spill failure aborts capture with context and leaves source data intact, without a full-table reread.

## Tasks

### T-01 Keep fleet database continuity reads bounded when scratch storage fails
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/database_continuity.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/test-database-spill.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/update_read.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/read_cache.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/test-spill-failure-propagation.py | Test: python3 scripts/studio-fleet/test-database-spill.py && python3 scripts/studio-fleet/test-spill-failure-propagation.py
