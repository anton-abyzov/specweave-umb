---
id: US-006
feature: FS-340
title: Dynamic Import of bcryptjs
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-006: Dynamic Import of bcryptjs

**Feature**: [FS-340](./FEATURE.md)

platform operator
**I want** `bcryptjs` to be dynamically imported only when `hashPassword` or `verifyPassword` is called
**So that** the ~300KB library is not loaded on every request (only login route needs it)

---

## Acceptance Criteria

- [x] **AC-US6-01**: Top-level `import bcrypt from 'bcryptjs'` removed from `src/lib/auth.ts`
- [x] **AC-US6-02**: `hashPassword` and `verifyPassword` use `const bcrypt = await import('bcryptjs')` (or cache the import result in a module variable)
- [x] **AC-US6-03**: Other functions in `auth.ts` (JWT signing/verification) are unaffected and do not trigger bcrypt loading
- [x] **AC-US6-04**: Unit test verifies dynamic import is called only when `hashPassword` or `verifyPassword` is invoked

---

## Implementation

**Increment**: [0340-api-perf-optimization](../../../../../increments/0340-api-perf-optimization/spec.md)

