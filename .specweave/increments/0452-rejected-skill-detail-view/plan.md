# Implementation Plan: Rejected Skill Detail View

## Overview

Enrich the existing `RejectedSkillView` component in the vskill-platform skill detail page to show full rejection context: reason, trigger stage, dates, repository link, pipeline stage indicator, and resubmission guidance. This is a frontend-only change within a single file (`page.tsx`) plus a minor data layer extension if needed.

## Architecture

### Components

- **RejectedSkillView** (existing, to be expanded): Server component in `src/app/skills/[owner]/[repo]/[skill]/page.tsx`. Currently renders a minimal amber banner with skill name, repo URL, status, trigger, and submission date. Will be expanded to include a pipeline stage indicator, richer rejection details, and a guidance section.
- **RejectionStageIndicator** (new, inline): A small sub-component showing a simplified 4-stage pipeline (Submission > Structure > Security > Review) with the failure point highlighted. Defined in the same file alongside `BlockedRow` and other sub-components.
- **TRIGGER_STAGE_MAP** (new constant): Maps `rejectionTrigger` values to pipeline stage names and indices for the stage indicator.

### Data Model

No schema changes needed. The existing `RejectedSkillData` interface already provides all required fields:
- `skillName: string`
- `repoUrl: string`
- `createdAt: string`
- `updatedAt: string`
- `rejectionReason?: string`
- `rejectionTrigger?: string`

### API Contracts

No API changes. The page is a Next.js server component that calls `getRejectedSubmissionBySkillName` directly.

## Technology Stack

- **Framework**: Next.js 15 (App Router, server components)
- **Styling**: Inline CSS-in-JS (consistent with existing page.tsx patterns)
- **Data**: Prisma via `getRejectedSubmissionBySkillName`

**Architecture Decisions**:
- **Inline component, not separate file**: The `RejectedSkillView` is small enough to stay in `page.tsx` alongside `BlockedSkillView`. Extracting to a separate file is unnecessary churn.
- **No new data fetching**: All required data is already available in `RejectedSkillData`. If scan result excerpts were needed, we would extend the query, but the current scope does not require it.
- **Follow BlockedSkillView patterns**: Reuse the same style constants (`blockedRowBase`, `backLinkStyle`, etc.) and layout structure for visual consistency.

## Implementation Phases

### Phase 1: Core rejection details (US-001, US-002)
1. Expand the `RejectedSkillView` component with:
   - Rejection reason displayed prominently in the amber banner
   - Trigger stage as a labeled row (using `BlockedRow` pattern)
   - Both submission date and rejection date as labeled rows
   - Skill name as heading in owner/repo/skill format
   - Repository URL as clickable link
2. Add `TRIGGER_STAGE_MAP` constant mapping trigger strings to display labels

### Phase 2: Pipeline stage indicator (US-004)
1. Add `RejectionStageIndicator` sub-component
2. Map `rejectionTrigger` to stage index
3. Render as a horizontal pipeline with the failed stage highlighted in amber

### Phase 3: Resubmission guidance (US-003)
1. Add "What to do next" section below the rejection details
2. Link to vskill documentation
3. Link to GitHub issues for error reports

## Testing Strategy

- **Unit tests**: Test `TRIGGER_STAGE_MAP` mapping and `RejectionStageIndicator` stage resolution logic
- **Component rendering**: Verify `RejectedSkillView` renders correctly with all fields present, with optional fields missing, and with undefined trigger
- **Visual regression**: Manual verification that the new view matches the BlockedSkillView visual language

## Technical Challenges

### Challenge 1: Graceful fallback for missing metadata
**Solution**: Use conditional rendering for all optional fields (`rejectionReason`, `rejectionTrigger`). When trigger is undefined, hide the stage indicator entirely. When reason is undefined, show a generic message.
**Risk**: Low -- the existing component already handles `rejectionReason` being undefined.
