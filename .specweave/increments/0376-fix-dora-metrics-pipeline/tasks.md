# Tasks: Fix DORA metrics pipeline

### T-001: Fix CFR tier boundary in tier-classifier.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given classifyChangeFailureRate(15) -> Then returns 'Elite'. Given classifyChangeFailureRate(30) -> Then returns 'High'. Given classifyChangeFailureRate(45) -> Then returns 'Medium'.

**Files**: `src/metrics/utils/tier-classifier.ts`

---

### T-002: Fix Lead Time benchmark text in metrics.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given metrics.md Lead Time High benchmark -> When I read it -> Then it says "1 hour to 1 week"

**Files**: `.specweave/docs/public/metrics.md`

---

### T-003: Fix CFR benchmark text in metrics.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given metrics.md CFR benchmarks -> When I read them -> Then they say "0-15%", "15-30%", "30-45%"

**Files**: `.specweave/docs/public/metrics.md`

---

### T-004: Update stale goals in metrics.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given the goals section -> When I read it -> Then DF goal reflects Elite status achieved, Lead Time goal is new target, CFR reflects Elite maintained

**Files**: `.specweave/docs/public/metrics.md`
