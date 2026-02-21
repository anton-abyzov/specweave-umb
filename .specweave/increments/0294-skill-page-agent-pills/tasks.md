# Tasks: Skill page Works-with colorful agent pills

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Extract shared constants

### T-001: Create shared agent branding lib
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Description**: Create `src/lib/agent-branding.ts` exporting `AGENT_COLORS` and `AGENT_ICONS` with the exact data from `src/app/page.tsx`.
**Test**: Given the shared lib exists -> When imported -> Then it exports both `AGENT_COLORS` and `AGENT_ICONS` as `Record<string, string>` with all current entries
**Dependencies**: None

### T-002: Update homepage to import from shared lib
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Description**: Remove inline `AGENT_COLORS` and `AGENT_ICONS` from `src/app/page.tsx`, replace with imports from `@/lib/agent-branding`.
**Test**: Given the homepage -> When rendered -> Then it displays identically to before (no visual regression)
**Dependencies**: T-001

## Phase 2: Update skill detail page

### T-003: Replace grey badges with brand-colored pills on skill detail page
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Description**: Import `AGENT_COLORS` and `AGENT_ICONS` in `src/app/skills/[name]/page.tsx`. Replace the plain grey square badge rendering in the "Works with" section with colorful pill badges that show icons and brand colors, matching the homepage style.
**Test**: Given a skill detail page -> When the "Works with" section renders -> Then each agent shows as a rounded pill with brand color tint, icon (if available), and graceful fallback for unknown agents
**Dependencies**: T-001

## Phase 3: Verification

### T-004: Build and visual verification
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-05 | **Status**: [x] completed
**Description**: Run `next build` to verify no type errors or build failures. Visually confirm both pages render correctly.
**Test**: Given all changes applied -> When `next build` runs -> Then it completes with zero errors
**Dependencies**: T-002, T-003
