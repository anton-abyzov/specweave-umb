# 0372: Trust Center — surface scan findings and skill identity

## Problem
The Trust Center blocked/rejected tabs show that a skill was flagged but give no detail about **why**. Expanding a blocked entry shows "Auto-blocklisted: 2 critical finding(s). Score: 65/100" with no way to see which patterns triggered. Admins making block/reprocess decisions see only counts, not evidence. Skill identity within multi-skill repos is also ambiguous (no skill path shown).

## User Stories

### US-001: Show scan findings in blocked skills expanded detail
As an admin reviewing blocked skills, I want to see the actual scan findings (pattern ID, severity, file, line number, code match) when I expand a blocked entry, so I can verify the block is justified.

**Acceptance Criteria:**
- [x] AC-US1-01: `/api/v1/blocklist/check` response includes `findings` array, `skillPath`, `submissionId`, and `commitSha` from the matching rejected submission's latest scan result
- [x] AC-US1-02: BlockedSkillsTab expanded detail renders each finding with pattern ID, severity badge, pattern name, file:line, and code match
- [x] AC-US1-03: When `commitSha` and `sourceUrl` are available, file:line links to the GitHub source permalink
- [x] AC-US1-04: Skill path is shown in the metadata grid when available
- [x] AC-US1-05: Column header renamed from "Source Registry" to "Source"

### US-002: Show scan findings in rejected skills expanded detail
As an admin reviewing rejected submissions, I want to see the actual scan findings inline, so I can make informed block/reprocess decisions without guessing.

**Acceptance Criteria:**
- [x] AC-US2-01: `GET /api/v1/admin/rejections` includes `findings` and `commitSha` in the scanResults select
- [x] AC-US2-02: RejectedSkillsTab expanded detail renders each finding with pattern ID, severity badge, file:line, and code match
- [x] AC-US2-03: Rejected tab shows `skillPath` for each entry (from submission record)

### US-003: Shared FindingsList component
As a developer, I want a shared component for rendering scan findings, so both tabs use consistent display logic.

**Acceptance Criteria:**
- [x] AC-US3-01: `FindingsList` component accepts findings array with optional repoUrl and commitSha for GitHub links
- [x] AC-US3-02: Findings are sorted by severity (critical first)
- [x] AC-US3-03: Component handles empty findings array gracefully
