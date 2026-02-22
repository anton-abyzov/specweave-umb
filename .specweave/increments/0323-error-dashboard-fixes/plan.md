# Plan: 0323 Error Dashboard Fixes

## Approach
Three targeted fixes across two repos. Each fix is independent and addresses a distinct error class.

## Tasks
1. Disable guard in specweave repo (canonical + 6 distribution copies)
2. Migrate vitest config in vskill-platform
3. Fix 3 test files with incomplete Prisma mocks in vskill-platform
4. Run full test suite to verify

## Risk
Low — all changes are isolated fixes with clear root causes. No new features, no architectural changes.
