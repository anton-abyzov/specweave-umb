# Tasks: Server-Persisted User Preferences (Theme)

### US-001: Server-Persisted Theme Preference (P1)

#### T-001: Create preferences type module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given various inputs to parsePreferences -> When called with null/undefined/invalid/valid -> Then returns typed UserPreferences with valid values only
- **File**: `src/lib/__tests__/preferences.test.ts`
- **TC-001**: parsePreferences returns defaults for null/undefined/non-object
- **TC-002**: parsePreferences extracts valid theme values (light, dark, system)
- **TC-003**: parsePreferences ignores invalid theme values
- **TC-004**: PreferencesPatchSchema validates theme enum and rejects unknown keys

#### T-002: Add preferences field to Prisma schema
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given User model -> When migrated -> Then preferences field exists with default {}
**Dependencies**: None

#### T-003: Create preferences API routes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given GET/PATCH /api/v1/user/preferences -> When authenticated/unauthenticated -> Then returns preferences/401
- **File**: `src/app/api/v1/user/preferences/__tests__/route.test.ts`
- **TC-005**: GET returns 401 without auth cookie
- **TC-006**: GET returns 200 with preferences for valid user
- **TC-007**: PATCH returns 401 without auth cookie
- **TC-008**: PATCH returns 200 and updates theme preference
- **TC-009**: PATCH returns 400 for invalid theme value
- **TC-010**: PATCH returns 400 for unknown keys (strict mode)
- **TC-011**: PATCH shallow-merges without clearing other keys
**Dependencies**: T-001, T-002

#### T-004: Update ThemeToggle for server sync
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed
**Test**: Given ThemeToggle mounted -> When authenticated user toggles -> Then localStorage updated instantly AND debounced PATCH fired; When unauthenticated -> Then no API calls
**Dependencies**: T-003

#### T-005: Run full test suite and verify
**User Story**: US-001 | **Satisfies ACs**: all | **Status**: [x] completed
**Dependencies**: T-004
