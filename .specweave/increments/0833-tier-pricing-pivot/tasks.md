# Tasks — 0833 Tier pricing pivot

8 tasks. Small surgical change to 0831 — no new modules, just rewires.

## Phase 1 — Backend (vskill-platform)

### T-001: `/api/v1/billing/quota` returns `skillLimit: null` for free tier
**Satisfies ACs**: AC-US1-01, AC-US4-05
**Test**: Given free user → response has `skillLimit: null` (was `50`). Pro/enterprise unchanged (still `null`). Vitest covers the 3 tier shapes.

### T-002: Update Vitest assertions for billing endpoints
**Satisfies ACs**: AC-US4-05
**Test**: `src/__tests__/billing/quota.test.ts` assertions for free tier expect `skillLimit: null`.

### T-003: Update `/pricing` page copy + JSON-LD
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Test**: Vitest SSR test for /pricing asserts: Free card has "Unlimited public skills" (no "50"), Pro card lead is "+ Private repository connections", Enterprise card lead is "+ SSO + audit log + dedicated support". Meta description updated.

## Phase 2 — Desktop (vskill)

### T-004: `useTier()` hook + `quota_can_create_skill` IPC interpret null limit as unlimited
**Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US4-03, AC-US4-04
**Test**: Cargo test for `quota_can_create_skill` with `skillLimit: null` returns `{allowed: true}` regardless of `currentCount`. Vitest test for `useTier()` derived state asserts `isUnlimited: true` when limit is null.

### T-005: Remove pre-create quota check from skill-create flow
**Satisfies ACs**: AC-US2-01
**Test**: Find the call site (likely in App.tsx where `quotaCanCreateSkill` was wired in 0831) and remove. The create path proceeds without any tier check. Existing skill-create vitest must still pass.

### T-006: Wire paywall trigger to private-repo connect action + update modal copy
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Test**: ConnectedRepoWidget's "Connect private repo" button: when `useTier().isFree && repo.isPrivate`, click → PaywallModal opens with new copy. Click "Maybe later" → closes. Public repo connect → no modal ever.

### T-007: Update e2e specs to reflect new trigger
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Test**: `e2e/desktop/auth-and-paywall.spec.ts` rewritten — "paywall on 51st create" deleted, "paywall on private-repo connect" added. `e2e/desktop/auth-flow-regression.spec.ts` Test 3 rewritten to private-repo trigger. Both files green.

## Phase 3 — Marketing copy sweep

### T-008: Sweep all "50 skill" / "skillLimit" copy across vskill + vskill-platform
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Test**: `grep -ri "50.skill\|skillLimit:\\?\\s*50\|free tier.*cap" repositories/anton-abyzov/{vskill,vskill-platform}/src` returns zero hits in user-facing strings. README + marketing pages updated.
