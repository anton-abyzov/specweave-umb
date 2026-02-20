# Plan — 0243: Skill Detail Page — Extensible Pioneer

## Execution Order

1. T-001: Types (trivial)
2. T-002: Scan breakdown module (new file)
3. T-003: Seed data updates (extensible + agent slugs)
4. T-004: Data layer merge
5. T-005: Page redesign (biggest change)
6. T-006: Build + deploy

## TDD approach

RED: Write tests for scan-breakdown.ts and data.ts additions first.
GREEN: Implement to pass tests.
Then implement UI (server component, not easily unit-tested — verify via build + manual).
