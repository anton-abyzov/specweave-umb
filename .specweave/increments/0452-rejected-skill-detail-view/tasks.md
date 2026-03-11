# Tasks: Rejected Skill Detail View

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Core Rejection Details

### US-001: Rejection reason and stage visibility (P1)

#### T-001: Add TRIGGER_STAGE_MAP constant and stage label helper

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] Not Started

**Description**: Create a `TRIGGER_STAGE_MAP` constant that maps `rejectionTrigger` string values to human-readable stage labels. Add a helper function `getTriggerLabel(trigger?: string): string | null` that returns the display label or null if the trigger is unknown/undefined.

**AC**: AC-US1-02

**Implementation Details**:
- Add constant in the page.tsx constants section:
  ```
  framework_plugin -> "Structure Check"
  tier1_scan -> "Security Scan (Tier 1)"
  tier2_scan -> "Security Scan (Tier 2)"
  manual_review -> "Manual Review"
  auto_reject -> "Automated Review"
  ```
- Add `getTriggerLabel` helper function

**Test Plan**:
- **File**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/rejection-helpers.test.ts`
- **Tests**:
  - **TC-001**: getTriggerLabel returns correct label for each known trigger
    - Given a known trigger value "tier1_scan"
    - When getTriggerLabel is called
    - Then it returns "Security Scan (Tier 1)"
  - **TC-002**: getTriggerLabel returns null for undefined trigger
    - Given trigger is undefined
    - When getTriggerLabel is called
    - Then it returns null
  - **TC-003**: getTriggerLabel returns null for unknown trigger
    - Given trigger is "unknown_value"
    - When getTriggerLabel is called
    - Then it returns null

**Dependencies**: None

---

#### T-002: Expand RejectedSkillView with full rejection details

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02 | **Status**: [ ] Not Started

**Description**: Rewrite the `RejectedSkillView` component to include: rejection reason in the amber banner, trigger stage as a labeled row, submission and rejection dates, skill name as heading, and repository URL as clickable link. Follow the `BlockedSkillView` layout patterns.

**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02

**Implementation Details**:
- Expand the amber banner to show `rejectionReason` or default message
- Add rows using `BlockedRow` pattern: Skill Name, Repository (linked), Trigger (using getTriggerLabel), Status, Submitted date, Rejected date
- Show skill name in `owner/repo/skill` format by parsing from `entry.skillName` or the URL params
- Handle undefined `rejectionReason` with fallback: "This skill was submitted for verification but did not pass the review process."
- Handle undefined `rejectionTrigger` by hiding the Trigger row
- Ensure both `createdAt` (submitted) and `updatedAt` (rejected) dates are shown

**Test Plan**:
- **File**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/rejected-skill-view.test.tsx`
- **Tests**:
  - **TC-004**: Renders rejection reason when provided
    - Given a RejectedSkillData with rejectionReason "Failed SAST scan: command injection detected"
    - When RejectedSkillView renders
    - Then the rejection reason text is visible in the banner
  - **TC-005**: Renders fallback message when rejectionReason is undefined
    - Given a RejectedSkillData without rejectionReason
    - When RejectedSkillView renders
    - Then the default message about not passing review is shown
  - **TC-006**: Renders trigger row when rejectionTrigger is present
    - Given rejectionTrigger is "tier1_scan"
    - When RejectedSkillView renders
    - Then a row showing "Security Scan (Tier 1)" is visible
  - **TC-007**: Hides trigger row when rejectionTrigger is undefined
    - Given rejectionTrigger is undefined
    - When RejectedSkillView renders
    - Then no trigger row is rendered
  - **TC-008**: Renders repository URL as clickable link
    - Given repoUrl is "https://github.com/user/repo"
    - When RejectedSkillView renders
    - Then the URL is rendered as an anchor with target="_blank"

**Dependencies**: T-001

---

### US-004: Rejection stage indicator (P2)

#### T-003: Add RejectionStageIndicator sub-component

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [ ] Not Started

**Description**: Create a `RejectionStageIndicator` component that shows a horizontal 4-stage pipeline (Submission > Structure > Security > Review) with the failure stage highlighted in amber. Maps `rejectionTrigger` to a stage index.

**AC**: AC-US4-01, AC-US4-02, AC-US4-03

**Implementation Details**:
- Define pipeline stages: `["Submission", "Structure", "Security", "Review"]`
- Map triggers to stage indices:
  - `framework_plugin` -> 1 (Structure)
  - `tier1_scan`, `tier2_scan` -> 2 (Security)
  - `manual_review`, `auto_reject` -> 3 (Review)
- Render as horizontal flex row with dots/labels, completed stages in muted color, failed stage in amber, remaining stages in faint color
- When `rejectionTrigger` is undefined, return `null` (hidden)
- Add to `RejectedSkillView` between the banner and detail rows

**Test Plan**:
- **File**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/rejection-helpers.test.ts`
- **Tests**:
  - **TC-009**: Stage indicator maps tier1_scan to Security stage
    - Given rejectionTrigger is "tier1_scan"
    - When stage index is resolved
    - Then it maps to index 2 (Security)
  - **TC-010**: Stage indicator returns null for undefined trigger
    - Given rejectionTrigger is undefined
    - When RejectionStageIndicator renders
    - Then it returns null
  - **TC-011**: Stage indicator maps framework_plugin to Structure stage
    - Given rejectionTrigger is "framework_plugin"
    - When stage index is resolved
    - Then it maps to index 1 (Structure)

**Dependencies**: T-001

---

### US-003: Resubmission guidance (P2)

#### T-004: Add resubmission guidance section

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] Not Started

**Description**: Add a "What to do next" section at the bottom of the `RejectedSkillView` component with guidance text, documentation link, and issue report link.

**AC**: AC-US3-01, AC-US3-02, AC-US3-03

**Implementation Details**:
- Add section after the detail rows, before the existing footer
- Include guidance text explaining common rejection reasons and how to fix them
- Link to vskill documentation (https://spec-weave.com/docs/skills/)
- Link to GitHub issues (https://github.com/anton-abyzov/vskill/issues) for error reports
- Style consistently with the existing footer section (mono font, faint text, border-top)

**Test Plan**:
- **File**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/rejected-skill-view.test.tsx`
- **Tests**:
  - **TC-012**: Guidance section is rendered with documentation link
    - Given any RejectedSkillData
    - When RejectedSkillView renders
    - Then a section with text "What to do next" and a link to spec-weave.com docs is present
  - **TC-013**: Guidance section includes issue report link
    - Given any RejectedSkillData
    - When RejectedSkillView renders
    - Then a link to github.com/anton-abyzov/vskill/issues is present

**Dependencies**: T-002

## Phase 2: Verification

#### T-005: Manual visual verification

**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All | **Status**: [ ] Not Started

**Description**: Manually verify the rejected skill detail page renders correctly on the deployed platform. Check with a real rejected skill submission, verify all sections appear, links work, and the visual style matches BlockedSkillView.

**Test Plan**:
- Navigate to a known rejected skill URL
- Verify amber banner with rejection reason
- Verify trigger stage row and stage indicator
- Verify dates, repo link, skill name heading
- Verify guidance section with working links
- Verify responsive layout on narrow viewport

**Dependencies**: T-002, T-003, T-004
