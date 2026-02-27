# 0358 — Improve Submission Report

## Problem
The user-facing submission report at `/submit/[id]` shows scan findings as flat rows with plain-text `L{lineNumber}` — no links to source code. The admin page already has clickable GitHub permalinks. Additionally, identical pattern matches on different lines appear as separate rows, creating noise.

## Solution
1. Add clickable GitHub line references to the submission status page
2. Deduplicate findings by grouping same pattern+file, showing multiple line chips per group

## User Stories

### US-001: Clickable GitHub line references
As a skill submitter, I want to click on line numbers in scan findings so that I can jump directly to the flagged code in my GitHub repo.

**Acceptance Criteria:**
- [x] AC-US1-01: Each finding line number links to the exact GitHub source line
- [x] AC-US1-02: Links use commit SHA for stable permalinks (falls back to `main` when unavailable)
- [x] AC-US1-03: Non-GitHub repos or missing file info degrades gracefully to plain text
- [x] AC-US1-04: File path shown in finding card when available

### US-002: Finding deduplication
As a skill submitter, I want duplicate findings grouped together so I can quickly understand distinct issues without noise.

**Acceptance Criteria:**
- [x] AC-US2-01: Findings with same patternId+file are grouped into one card
- [x] AC-US2-02: Each group shows all line numbers as individual clickable chips
- [x] AC-US2-03: Total raw findings count preserved in header
- [x] AC-US2-04: Groups maintain severity ordering (critical first)
