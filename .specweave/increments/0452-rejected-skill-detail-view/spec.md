---
increment: 0452-rejected-skill-detail-view
title: "Rejected skill detail view"
type: feature
priority: P1
status: planned
created: 2026-03-07
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Rejected Skill Detail View

## Overview

When a user navigates to a skill that was submitted but rejected during verification, the page currently shows a bare-bones amber `RejectedSkillView` component. This view lacks critical context that would help the skill author understand what happened and what to do next: there is no rejection stage breakdown, no resubmission guidance, no scan failure details, and no way to see related submissions. This increment enriches the rejected skill detail page to be on par with the `BlockedSkillView` in terms of information density while giving authors a clear path forward.

## User Stories

### US-001: Rejection reason and stage visibility (P1)
**Project**: vskill-platform

**As a** skill author
**I want** to see the specific rejection reason, trigger stage, and timestamp on the rejected skill page
**So that** I understand exactly why my skill was rejected and at which point in the pipeline it failed

**Acceptance Criteria**:
- [ ] **AC-US1-01**: The rejected skill detail page displays the `rejectionReason` from the state event metadata, or a sensible default message if none exists
- [ ] **AC-US1-02**: The `rejectionTrigger` (e.g. "tier1_scan", "framework_plugin", "manual_review") is displayed as a labeled row
- [ ] **AC-US1-03**: The submission date (`createdAt`) and rejection date (`updatedAt`) are both displayed in human-readable format
- [ ] **AC-US1-04**: The page renders correctly when `rejectionReason` and `rejectionTrigger` are both undefined (graceful fallback)

---

### US-002: Repository and source context (P1)
**Project**: vskill-platform

**As a** skill author
**I want** the rejected skill page to show the repository link and skill name prominently
**So that** I can quickly navigate to my source code and understand which submission this refers to

**Acceptance Criteria**:
- [ ] **AC-US2-01**: The skill name is displayed as a heading in `owner/repo/skill` format, matching the URL structure
- [ ] **AC-US2-02**: The repository URL is rendered as a clickable link opening in a new tab
- [ ] **AC-US2-03**: Metadata generates proper `<title>` and OpenGraph tags for rejected skills (already implemented in `generateMetadata`)

---

### US-003: Resubmission guidance (P2)
**Project**: vskill-platform

**As a** skill author
**I want** actionable guidance on how to fix and resubmit my skill
**So that** I have a clear path forward instead of a dead end

**Acceptance Criteria**:
- [ ] **AC-US3-01**: The rejected skill page includes a "What to do next" section with guidance text
- [ ] **AC-US3-02**: The guidance section links to the vskill documentation for skill requirements
- [ ] **AC-US3-03**: The page includes a link to report an issue if the author believes the rejection was in error

---

### US-004: Rejection stage indicator (P2)
**Project**: vskill-platform

**As a** platform visitor
**I want** to see a visual indicator showing at which pipeline stage the skill was rejected
**So that** I can quickly assess the nature of the rejection (early structural failure vs. late security failure)

**Acceptance Criteria**:
- [ ] **AC-US4-01**: A stage indicator shows a simplified pipeline (Submission > Structure > Security > Review) with the failure point highlighted
- [ ] **AC-US4-02**: The stage indicator maps `rejectionTrigger` values to the correct pipeline stage
- [ ] **AC-US4-03**: When `rejectionTrigger` is undefined, the stage indicator is hidden rather than showing an incorrect stage

## Functional Requirements

### FR-001: Enrich RejectedSkillView component
The existing `RejectedSkillView` in `src/app/skills/[owner]/[repo]/[skill]/page.tsx` must be expanded from its current minimal layout to include: rejection reason with stage tag, submission and rejection dates, repository link, pipeline stage indicator, and resubmission guidance. The component receives a `RejectedSkillData` object which already includes `skillName`, `repoUrl`, `createdAt`, `updatedAt`, `rejectionReason`, and `rejectionTrigger`.

### FR-002: Extend RejectedSkillData if needed
If additional data is required (e.g. scan result excerpts), the `getRejectedSubmissionBySkillName` query in `src/lib/data.ts` and the `RejectedSkillData` interface should be extended. The current query already joins `stateEvents` to extract rejection metadata.

### FR-003: Pipeline stage mapping
A mapping from `rejectionTrigger` string values to human-readable pipeline stage names: `"framework_plugin"` -> "Structure Check", `"tier1_scan"` -> "Security Scan (Tier 1)", `"tier2_scan"` -> "Security Scan (Tier 2)", `"manual_review"` -> "Manual Review", `"auto_reject"` -> "Automated Review".

## Success Criteria

- Rejected skill pages show rejection reason and stage for 100% of rejected submissions that have metadata
- Zero 404 errors for rejected skills (already handled -- this increment enriches the non-404 view)
- Resubmission guidance section is visible on all rejected skill pages

## Out of Scope

- Resubmission flow (actually re-triggering a new submission from the UI)
- Admin-side rejection management interface
- Email/notification to authors when their skill is rejected
- Listing rejected skills in the skills registry browse page

## Dependencies

- Existing `RejectedSkillData` interface and `getRejectedSubmissionBySkillName` in `src/lib/data.ts`
- Existing `RejectedSkillView` component in the skill detail page
- Existing `BlockedSkillView` as a design reference for layout patterns
